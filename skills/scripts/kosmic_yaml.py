#!/usr/bin/env python3
"""Safe, indentation-aware YAML subset parser for Kosmic frontmatter.

Standard library only. One parser backs every public reader (the Shared
Skill Library ``Document`` and the Project CLI ``MarkdownDocument``) so all
consumers observe identical metadata semantics.

Supported constructs:

* block mappings, nested to any depth, with duplicate keys rejected inside
  each mapping (nested mappings scope their own keys, so a ``title`` under
  ``sources`` never collides with a root ``title``)
* block sequences, including sequences of mappings and nested sequences
* flow collections (JSON-compatible), quoted commas/colons, and values
  spanning multiple lines
* scalars: empty/``null``/legacy ``none``/``~`` -> ``None``,
  ``true``/``false`` -> ``bool``, canonical integers, dotted floats,
  single/double quoted strings with escapes; leading-zero numerals such as
  ``001`` and dates such as ``2026-01-15`` stay strings
* full-line and trailing comments
* literal (``|``) and folded (``>``) block scalars with chomping and
  explicit indentation indicators

Unsupported constructs raise :class:`YAMLParseError` instead of being
flattened or silently dropped: tags (``!``, ``!!str``, ``!python/...``),
anchors (``&``) and aliases (``*``), complex keys (``? ``), merge keys
(``<<``), multi-line plain scalars, tab indentation, unterminated quotes or
flow collections, and documents whose root is not a mapping.

Note: the closing ``---`` delimiter of a frontmatter block is found by line
scan before parsing, so a ``---`` line inside a block scalar still terminates
the header. This matches the historical scanner and generated corpora.
"""

from __future__ import annotations

import json
import re
from typing import Any

__all__ = ["YAMLParseError", "parse_mapping", "parse_scalar", "render_value", "render_entry"]


class YAMLParseError(ValueError):
    """Raised when frontmatter text is invalid or uses unsupported YAML."""


class _Incomplete(Exception):
    """Internal: a flow collection needs more lines to be complete."""


_INT_RE = re.compile(r"[+-]?(?:0|[1-9][0-9]*)\Z")
_FLOAT_RE = re.compile(r"[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_NULL_WORDS = frozenset({"null", "none", "~"})
_BOOL_WORDS = frozenset({"true", "false"})
_BLOCK_HEADER_RE = re.compile(r"[|>](?:[0-9]*[+-]?|[+-][0-9]*)\Z")
_INDICATOR_FIRST = "-?:,[]{}#&*!|>'\"%@`"
_PLAIN_STOP = ",]}"
_DOUBLE_ESCAPES = {
    "\\": "\\", '"': '"', "/": "/", "n": "\n", "t": "\t", "r": "\r",
    "b": "\b", "f": "\f", "0": "\0", "a": "\a", "v": "\v", "e": "\x1b",
    " ": " ",
}


def _fail(context: str, line_no: int, message: str) -> YAMLParseError:
    return YAMLParseError(f"{context}: line {line_no}: {message}")


def _indent_of(content: str, context: str, line_no: int) -> int:
    body = content.lstrip(" ")
    if body.startswith("\t"):
        raise _fail(context, line_no, "tab indentation is not allowed")
    return len(content) - len(body)


def _is_noise(content: str) -> bool:
    return not content.strip() or content.lstrip().startswith("#")


def _strip_comment(token: str) -> str:
    """Cut a trailing `` #`` comment from a plain (unquoted) token."""
    for index, char in enumerate(token):
        if char == "#" and (index == 0 or token[index - 1] in " \t"):
            return token[:index].rstrip()
    return token.rstrip()


def _resolve_plain(token: str) -> Any:
    lowered = token.lower()
    if lowered in _NULL_WORDS:
        return None
    if lowered in _BOOL_WORDS:
        return lowered == "true"
    if _INT_RE.fullmatch(token):
        return int(token)
    if _FLOAT_RE.fullmatch(token):
        return float(token)
    return token


def _decode_hex_char(text: str, start: int, digits: int, context: str, line_no: int) -> str:
    chunk = text[start:start + digits]
    try:
        code = int(chunk, 16)
    except ValueError:
        raise _fail(context, line_no, f"invalid hex escape digits: {chunk}") from None
    if len(chunk) != digits or code > 0x10FFFF:
        raise _fail(context, line_no, f"invalid hex escape digits: {chunk}")
    return chr(code)


def _scan_double_quoted(text: str, start: int, context: str, line_no: int, complete: bool) -> tuple[str, int]:
    decoded: list[str] = []
    index = start + 1
    length = len(text)
    while index < length:
        char = text[index]
        if char == '"':
            return "".join(decoded), index + 1
        if char == "\\":
            if index + 1 >= length:
                break
            escape = text[index + 1]
            if escape in _DOUBLE_ESCAPES:
                decoded.append(_DOUBLE_ESCAPES[escape])
                index += 2
                continue
            if escape == "x" and index + 3 < length:
                decoded.append(_decode_hex_char(text, index + 2, 2, context, line_no))
                index += 4
                continue
            if escape == "u" and index + 5 < length:
                decoded.append(_decode_hex_char(text, index + 2, 4, context, line_no))
                index += 6
                continue
            if escape == "U" and index + 9 < length:
                decoded.append(_decode_hex_char(text, index + 2, 8, context, line_no))
                index += 10
                continue
            raise _fail(context, line_no, f"unsupported double-quoted escape: \\{escape}")
        decoded.append(char)
        index += 1
    if complete:
        raise _fail(context, line_no, "unterminated double-quoted string")
    raise _Incomplete()


def _scan_single_quoted(text: str, start: int, context: str, line_no: int, complete: bool) -> tuple[str, int]:
    decoded: list[str] = []
    index = start + 1
    length = len(text)
    while index < length:
        char = text[index]
        if char == "'":
            if index + 1 < length and text[index + 1] == "'":
                decoded.append("'")
                index += 2
                continue
            return "".join(decoded), index + 1
        decoded.append(char)
        index += 1
    if complete:
        raise _fail(context, line_no, "unterminated single-quoted string")
    raise _Incomplete()


def _scan_quoted(text: str, start: int, context: str, line_no: int, complete: bool = True) -> tuple[Any, int]:
    if text[start] == '"':
        return _scan_double_quoted(text, start, context, line_no, complete)
    return _scan_single_quoted(text, start, context, line_no, complete)


class _FlowParser:
    """Recursive-descent parser for flow collections (JSON-compatible YAML)."""

    def __init__(self, text: str, context: str, line_no: int) -> None:
        self.text = text
        self.pos = 0
        self.context = context
        self.line_no = line_no

    def parse(self) -> tuple[Any, int]:
        value = self._node()
        return value, self.pos

    def _skip_blank(self) -> None:
        text, length = self.text, len(self.text)
        while self.pos < length:
            char = text[self.pos]
            if char in " \t\n":
                self.pos += 1
            elif char == "#" and (self.pos == 0 or text[self.pos - 1] in " \t\n"):
                newline = text.find("\n", self.pos)
                self.pos = length if newline < 0 else newline + 1
            else:
                return

    def _node(self, key_position: bool = False) -> Any:
        self._skip_blank()
        if self.pos >= len(self.text):
            raise _Incomplete()
        char = self.text[self.pos]
        if char in "&*!":
            raise _fail(self.context, self.line_no,
                        f"unsupported YAML construct {char!r} in flow collection")
        if char == "?" and (self.pos + 1 >= len(self.text)
                            or self.text[self.pos + 1] in " \t\n"):
            raise _fail(self.context, self.line_no, "complex keys ('? ') are not supported")
        if char in "[{":
            return self._collection()
        if char in "\"'":
            value, end = _scan_quoted(self.text, self.pos, self.context, self.line_no, complete=False)
            self.pos = end
            return value
        return self._plain(key_position)

    def _collection(self) -> Any:
        opening = self.text[self.pos]
        closing = "]" if opening == "[" else "}"
        self.pos += 1
        items: list[Any] = []
        mapping: dict[Any, Any] = {}
        while True:
            self._skip_blank()
            if self.pos >= len(self.text):
                raise _Incomplete()
            if self.text[self.pos] == closing:
                self.pos += 1
                return mapping if opening == "{" else items
            key = self._node(key_position=opening == "{")
            self._skip_blank()
            if opening == "{" and self.pos < len(self.text) and self.text[self.pos] == ":":
                self.pos += 1
                value = self._node()
                self._assign_flow_key(mapping, key, value)
            elif opening == "{":
                self._assign_flow_key(mapping, key, None)
            else:
                items.append(key)
            self._skip_blank()
            if self.pos >= len(self.text):
                raise _Incomplete()
            char = self.text[self.pos]
            if char == ",":
                self.pos += 1
                continue
            if char == closing:
                self.pos += 1
                return mapping if opening == "{" else items
            raise _fail(self.context, self.line_no,
                        f"expected ',' or {closing!r} in flow collection, found {char!r}")

    def _assign_flow_key(self, mapping: dict[Any, Any], key: Any, value: Any) -> None:
        if key in mapping:
            raise _fail(self.context, self.line_no,
                        f"duplicate key {key!r} in the same flow mapping")
        mapping[key] = value

    def _plain(self, key_position: bool) -> Any:
        text, length = self.text, len(self.text)
        start = self.pos
        while self.pos < length:
            char = text[self.pos]
            if char in _PLAIN_STOP or char == "," or char == "\n":
                break
            if char == "#" and self.pos > start and text[self.pos - 1] in " \t":
                break
            if char == ":" and (key_position or self.pos + 1 >= length
                                or text[self.pos + 1] in " \t\n" or text[self.pos + 1] in ",]}"):
                break
            self.pos += 1
        token = text[start:self.pos].rstrip()
        return _resolve_plain(token)


def _parse_flow_value(lines: list[str], index: int, first_rest: str, context: str) -> tuple[Any, int]:
    """Parse a flow value that may continue on subsequent lines.

    Returns the value and the index of the last consumed line.
    """
    start_line = index + 1
    buffer = first_rest
    while True:
        parser = _FlowParser(buffer, context, start_line)
        try:
            value, end = parser.parse()
        except _Incomplete:
            if index + 1 < len(lines):
                index += 1
                buffer += "\n" + lines[index]
                continue
            raise _fail(context, start_line, "unterminated flow collection") from None
        tail = buffer[end:].strip()
        if tail and not tail.startswith("#"):
            raise _fail(context, start_line,
                        f"unexpected content after flow value: {tail[:24]!r}")
        # ``index`` already points at the last continuation line consumed
        # above (the start line itself for a single-line flow).
        return value, index + 1


def _parse_inline_scalar(rest: str, context: str, line_no: int) -> Any:
    stripped = rest.strip()
    first = stripped[0]
    if first in "\"'":
        value, end = _scan_quoted(stripped, 0, context, line_no)
        tail = stripped[end:].strip()
        if tail and not tail.startswith("#"):
            raise _fail(context, line_no, f"unexpected content after quoted value: {tail[:24]!r}")
        return value
    if first in "&*!":
        raise _fail(context, line_no,
                    f"unsupported YAML construct {first!r}; tags, anchors and aliases are rejected")
    return _resolve_plain(_strip_comment(stripped))


def _next_content_line(lines: list[str], index: int) -> int | None:
    while index < len(lines):
        if _is_noise(lines[index]):
            index += 1
            continue
        return index
    return None


def _parse_block_scalar(lines: list[str], index: int, header: str, parent_indent: int,
                        context: str) -> tuple[str, int]:
    style = header[0]
    modifiers = header[1:]
    chomp = ""
    explicit = 0
    for char in modifiers:
        if char in "+-":
            chomp = char
        else:
            explicit = int(char)
    index += 1
    total = len(lines)
    collected: list[str] = []
    content_indent = parent_indent + explicit if explicit else None
    while index < total:
        content = lines[index]
        if not content.strip():
            collected.append("")
            index += 1
            continue
        indent = _indent_of(content, context, index + 1)
        if content_indent is None:
            content_indent = indent
        if indent < content_indent:
            break
        collected.append(content[content_indent:])
        index += 1
    trailing_blanks = 0
    while collected and collected[-1] == "":
        collected.pop()
        trailing_blanks += 1
    if style == "|":
        body = "\n".join(collected)
    else:
        body = ""
        for line in collected:
            if line == "":
                body += "\n"
            elif body and not body.endswith("\n"):
                body += " " + line
            else:
                body += line
    if chomp == "-":
        return body, index
    if chomp == "+":
        return body + "\n" * (trailing_blanks + 1) if (body or trailing_blanks) else "", index
    return body + "\n" if body else "", index


def _split_key(content: str, indent: int, context: str, line_no: int) -> tuple[str, str]:
    body = content[indent:]
    if body[0] in "!&*":
        raise _fail(context, line_no,
                    f"unsupported YAML construct {body[0]!r}; tags, anchors and aliases are rejected")
    if body[0] == "?" and (len(body) == 1 or body[1] in " \t"):
        raise _fail(context, line_no, "complex keys ('? ') are not supported")
    if body[0] in "\"'":
        key, end = _scan_quoted(body, 0, context, line_no)
        remainder = body[end:].lstrip()
        if not remainder.startswith(":"):
            raise _fail(context, line_no, "expected ':' after quoted key")
        if not key:
            raise _fail(context, line_no, "empty mapping key")
        return key, remainder[1:]
    separator = -1
    for position, char in enumerate(body):
        if char == ":" and (position + 1 == len(body) or body[position + 1] in " \t"):
            separator = position
            break
    if separator < 0:
        separator = body.find(":")
    if separator < 0:
        raise _fail(context, line_no, "expected a 'key: value' mapping entry")
    key = body[:separator].strip()
    if not key:
        raise _fail(context, line_no, "empty mapping key")
    return key, body[separator + 1:]


def _parse_block_mapping(lines: list[str], index: int, indent: int, context: str,
                         at_root: bool, empty_scalar: Any = None) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    total = len(lines)
    while index < total:
        content = lines[index]
        if _is_noise(content):
            index += 1
            continue
        line_no = index + 1
        current_indent = _indent_of(content, context, line_no)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise _fail(context, line_no, "unexpected indentation")
        stripped = content.lstrip()
        if stripped == "-" or stripped.startswith("- "):
            if at_root:
                raise _fail(context, line_no, "frontmatter root must be a mapping, not a sequence")
            break
        key, rest = _split_key(content, indent, context, line_no)
        if key == "<<":
            raise _fail(context, line_no, "merge keys ('<<') are not supported")
        if key in mapping:
            raise _fail(context, line_no, f"duplicate key {key!r} in the same mapping")
        value, index = _parse_value(lines, index, indent, rest, context, line_no, empty_scalar)
        mapping[key] = value
    return mapping, index


def _parse_value(lines: list[str], index: int, indent: int, rest: str, context: str,
                 line_no: int, empty_scalar: Any = None) -> tuple[Any, int]:
    stripped = rest.strip()
    if not stripped or stripped.startswith("#"):
        following = _next_content_line(lines, index + 1)
        if following is not None:
            following_indent = _indent_of(lines[following], context, following + 1)
            body = lines[following].lstrip()
            if following_indent > indent:
                if body == "-" or body.startswith("- "):
                    return _parse_block_sequence(lines, following, following_indent, context, empty_scalar)
                return _parse_block_mapping(lines, following, following_indent, context,
                                            at_root=False, empty_scalar=empty_scalar)
            if following_indent == indent and (body == "-" or body.startswith("- ")):
                return _parse_block_sequence(lines, following, following_indent, context, empty_scalar)
        return empty_scalar, index + 1
    first = stripped[0]
    if first in "[{":
        return _parse_flow_value(lines, index, rest, context)
    if first in "|>" and _BLOCK_HEADER_RE.fullmatch(_strip_comment(stripped)):
        return _parse_block_scalar(lines, index, _strip_comment(stripped), indent, context)
    return _parse_inline_scalar(rest, context, line_no), index + 1


def _parse_block_sequence(lines: list[str], index: int, seq_indent: int,
                          context: str, empty_scalar: Any = None) -> tuple[list[Any], int]:
    items: list[Any] = []
    total = len(lines)
    while index < total:
        content = lines[index]
        if _is_noise(content):
            index += 1
            continue
        line_no = index + 1
        current_indent = _indent_of(content, context, line_no)
        if current_indent < seq_indent:
            break
        if current_indent > seq_indent:
            raise _fail(context, line_no, "unexpected indentation in sequence")
        stripped = content.lstrip()
        if not (stripped == "-" or stripped.startswith("- ")):
            break
        remainder = content[current_indent + 1:]
        if not remainder.strip() or remainder.strip().startswith("#"):
            following = _next_content_line(lines, index + 1)
            if following is not None:
                following_indent = _indent_of(lines[following], context, following + 1)
                if following_indent > seq_indent:
                    body = lines[following].lstrip()
                    if body == "-" or body.startswith("- "):
                        value, index = _parse_block_sequence(lines, following, following_indent,
                                                             context, empty_scalar)
                    else:
                        value, index = _parse_block_mapping(lines, following, following_indent, context,
                                                            at_root=False, empty_scalar=empty_scalar)
                    items.append(value)
                    continue
            items.append(empty_scalar)
            index += 1
            continue
        item_col = current_indent + 1
        while item_col < len(content) and content[item_col] == " ":
            item_col += 1
        body = content[item_col:]
        if body == "-" or body.startswith("- "):
            lines[index] = " " * item_col + body
            value, index = _parse_block_sequence(lines, index, item_col, context, empty_scalar)
        elif _split_key_starts(body):
            lines[index] = " " * item_col + body
            value, index = _parse_block_mapping(lines, index, item_col, context,
                                                at_root=False, empty_scalar=empty_scalar)
        elif body[0] in "|>" and _BLOCK_HEADER_RE.fullmatch(_strip_comment(body)):
            value, index = _parse_block_scalar(lines, index, _strip_comment(body), current_indent, context)
        elif body[0] in "[{":
            value, index = _parse_flow_value(lines, index, body, context)
        else:
            value = _parse_inline_scalar(body, context, line_no)
            index += 1
        items.append(value)
    return items, index


def _split_key_starts(body: str) -> bool:
    """True when a sequence item body begins a ``key: value`` mapping entry."""
    if body[0] in "\"'":
        try:
            _, end = _scan_quoted(body, 0, "frontmatter", 0)
        except YAMLParseError:
            return False
        remainder = body[end:].lstrip()
        return remainder.startswith(":")
    for position, char in enumerate(body):
        if char == ":" and (position + 1 == len(body) or body[position + 1] in " \t"):
            return True
    return False


def parse_mapping(text: str, context: str = "frontmatter",
                  empty_scalar: Any = None) -> dict[str, Any]:
    """Parse frontmatter ``text`` into a mapping; raise YAMLParseError otherwise.

    A bare ``key:`` with no value resolves to ``empty_scalar`` (``None`` for
    the shared library reader; the CLI reader passes ``""`` to preserve its
    historical blank-string semantics). Explicit ``null``/``~``/``none``
    values always resolve to ``None``.
    """
    if not isinstance(text, str):
        raise YAMLParseError(f"{context}: frontmatter text must be a string")
    lines = text.splitlines()
    if not any(not _is_noise(line) for line in lines):
        return {}
    mapping, index = _parse_block_mapping(lines, 0, 0, context, at_root=True,
                                          empty_scalar=empty_scalar)
    while index < len(lines):
        if _is_noise(lines[index]):
            index += 1
            continue
        raise _fail(context, index + 1, "unexpected content after the frontmatter mapping")
    return mapping


def parse_scalar(raw: str) -> Any:
    """Resolve a single raw CLI value; blank input stays the empty string."""
    value = raw.strip()
    if not value:
        return ""
    first = value[0]
    if first in "[{":
        parser = _FlowParser(value, "scalar", 1)
        try:
            parsed, end = parser.parse()
        except _Incomplete as error:
            raise YAMLParseError("scalar: unterminated flow collection") from error
        tail = value[end:].strip()
        if tail:
            raise YAMLParseError(f"scalar: unexpected content after flow value: {tail[:24]!r}")
        return parsed
    if first in "\"'":
        return _parse_inline_scalar(value, "scalar", 1)
    return _resolve_plain(_strip_comment(value))


def _needs_quotes(text: str) -> bool:
    if not text:
        return True
    lowered = text.lower()
    if lowered in _NULL_WORDS or lowered in _BOOL_WORDS:
        return True
    if _INT_RE.fullmatch(text) or _FLOAT_RE.fullmatch(text):
        return True
    if text[0] in _INDICATOR_FIRST or text[-1] == ":":
        return True
    if text[0] == " " or text[-1] == " " or "\n" in text:
        return True
    if ": " in text or " #" in text:
        return True
    # values render into flow collections, where , ] } { [ end plain scalars
    return any(char in text for char in ",[]{}")


def render_value(value: Any) -> str:
    """Render a value as JSON-compatible flow YAML on a single line."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False) if _needs_quotes(value) else value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(render_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{render_value(str(key))}: {render_value(item)}" for key, item in value.items()
        ) + "}"
    raise YAMLParseError(f"cannot render value of type {type(value).__name__} as YAML")


def render_entry(key: str, value: Any, indent: str = "") -> list[str]:
    """Render ``key: value`` as block-style YAML lines (each ending in \\n).

    Scalars and lists of scalars render compactly on one line; nested
    mappings and sequences render as structured block YAML so a reload
    preserves the shape.
    """
    key_text = render_value(str(key))
    if isinstance(value, dict) and value:
        lines = [f"{indent}{key_text}:\n"]
        for child_key, child_value in value.items():
            lines.extend(render_entry(str(child_key), child_value, indent + "  "))
        return lines
    if isinstance(value, list) and any(isinstance(item, (dict, list)) and item for item in value):
        lines = [f"{indent}{key_text}:\n"]
        for item in value:
            lines.extend(_render_sequence_item(item, indent + "  "))
        return lines
    return [f"{indent}{key_text}: {render_value(value)}\n"]


def _render_sequence_item(item: Any, indent: str) -> list[str]:
    if isinstance(item, dict) and item:
        lines: list[str] = []
        for index, (child_key, child_value) in enumerate(item.items()):
            block = render_entry(str(child_key), child_value, indent + "  ")
            if index == 0:
                block[0] = indent + "- " + block[0][len(indent) + 2:]
            lines.extend(block)
        return lines
    if isinstance(item, list) and item:
        lines = []
        for index, child in enumerate(item):
            block = _render_sequence_item(child, indent + "  ")
            if index == 0:
                block[0] = indent + "- " + block[0][len(indent) + 2:]
            lines.extend(block)
        return lines
    return [f"{indent}- {render_value(item)}\n"]
