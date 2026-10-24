"""Native Project and general idea capture for the Kosmic Projection CLI."""
from __future__ import annotations

import errno
import json
import os
import re
import stat
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .kosmic_specs import SLUG as PROJECT_ID_RE, SpecError, read_document
except ImportError:
    from kosmic_specs import SLUG as PROJECT_ID_RE, SpecError, read_document

IDEAS_DIR_NAME = "ideas"
GENERAL_IDEAS_DIR_NAME = "GeneralIdeas"
MAX_SLUG_LENGTH = 80
MAX_TITLE_LENGTH = 80
MAX_NAME_ATTEMPTS = 10000


class IdeaError(RuntimeError):
    """A rejected idea-capture request with a stable, idea-specific code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


def _slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title)
    text = "".join(char for char in text if not unicodedata.combining(char))
    collapsed: list[str] = []
    for char in text.lower():
        if "a" <= char <= "z" or "0" <= char <= "9":
            collapsed.append(char)
        elif collapsed and collapsed[-1] != "-":
            collapsed.append("-")
    slug = "".join(collapsed).rstrip("-")[:MAX_SLUG_LENGTH].rstrip("-")
    return slug or "idea"


def _derive_title(text: str) -> str:
    for line in text.splitlines():
        candidate = " ".join(line.strip().lstrip("#").split())
        if candidate:
            return candidate[:MAX_TITLE_LENGTH].rstrip()
    return "idea"


def _title_value(title: str | None, text: str) -> str:
    if title is not None:
        if not title.strip():
            raise IdeaError("IDEA_TITLE_BLANK", "--title must not be blank")
        return " ".join(title.split())
    return _derive_title(text)


def _read_project_id(root: Path) -> str:
    entry = root / "ProjectEntry.md"
    try:
        document = read_document(root, entry)
    except (SpecError, OSError, UnicodeError) as error:
        raise IdeaError(
            "IDEA_PROJECT_ID_INVALID",
            f"{entry}: ProjectEntry.md must be a readable regular file with a valid project_id",
        ) from error
    value = document.metadata.get("project_id")
    project_id = str(value).strip() if value is not None else ""
    if not project_id or not PROJECT_ID_RE.fullmatch(project_id):
        raise IdeaError("IDEA_PROJECT_ID_INVALID", f"{entry}: missing or invalid project_id")
    return project_id


def _existing_kind(directory_fd: int, name: str) -> str:
    try:
        descriptor = os.open(
            name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd
        )
    except FileNotFoundError:
        return "absent"
    except OSError as error:
        if error.errno == errno.ELOOP:
            return "symlink"
        raise
    try:
        mode = os.fstat(descriptor).st_mode
    finally:
        os.close(descriptor)
    if stat.S_ISREG(mode):
        return "regular file"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISFIFO(mode):
        return "FIFO"
    return "special file"


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError(errno.EIO, "short write while staging idea")
        view = view[written:]


def _filesystem_error(error: OSError, operation: str, path: Path, *, published: bool = False) -> OSError:
    state = f"note may already be published at {path}; " if published else ""
    detail = error.strerror or str(error)
    return OSError(error.errno or errno.EIO, f"{state}{operation} for {path}: {detail}")


def _publish(directory_fd: int, directory: Path, slug: str, data: bytes) -> Path:
    staging = f".idea-stage-{os.getpid()}-{os.urandom(8).hex()}"
    base_path = directory / f"{slug}.md"
    descriptor = -1
    current_path = base_path
    staged = False
    published_path: Path | None = None
    try:
        descriptor = os.open(
            staging,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
        staged = True
        _write_all(descriptor, data)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1

        attempt = 1
        for _ in range(MAX_NAME_ATTEMPTS):
            name = f"{slug}.md" if attempt == 1 else f"{slug}-{attempt}.md"
            candidate = directory / name
            current_path = candidate
            try:
                os.link(staging, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
                published_path = candidate
                break
            except FileExistsError:
                kind = _existing_kind(directory_fd, name)
                if kind == "absent":
                    continue
                if kind != "regular file":
                    raise IdeaError(
                        "IDEA_UNSAFE_CANDIDATE",
                        f"{candidate}: existing candidate is a {kind}; refusing to replace or bypass it",
                    )
                attempt += 1
        if published_path is None:
            raise IdeaError("IDEA_NAME_EXHAUSTED", f"{base_path}: no free numeric suffix")

        try:
            os.unlink(staging, dir_fd=directory_fd)
            staged = False
            os.fsync(directory_fd)
        except OSError as error:
            raise _filesystem_error(error, "publication finalization failed", published_path, published=True) from error
        return published_path
    except IdeaError:
        raise
    except OSError as error:
        affected = published_path or current_path
        raise _filesystem_error(error, "idea capture filesystem operation failed", affected,
                                published=published_path is not None) from error
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if staged:
            try:
                os.unlink(staging, dir_fd=directory_fd)
            except OSError as error:
                affected = published_path or base_path
                raise _filesystem_error(
                    error, "owned staging cleanup failed", affected,
                    published=published_path is not None,
                ) from error


def _render_note(title: str, text: bytes, created: datetime, project_id: str | None) -> bytes:
    stamp = created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    day = created.date().isoformat()
    lines = ["---", "type: idea", "status: draft"]
    if project_id is not None:
        lines.append(f"project_id: {project_id}")
    lines.append(f"title: {json.dumps(title, ensure_ascii=False)}")
    lines.append(f"created: {json.dumps(stamp)}")
    lines.extend(["---", "", f"# {title}", "", "## History", "", f"### {day}", ""])
    document = "\n".join(lines).encode("utf-8") + b"\n" + text
    if not document.endswith(b"\n"):
        document += b"\n"
    return document


def _open_root(root: Path, scope: str) -> int:
    try:
        return os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except FileNotFoundError as error:
        raise IdeaError("IDEA_ROOT_MISSING", f"selected {scope} root does not exist: {root}") from error
    except NotADirectoryError as error:
        raise IdeaError("IDEA_ROOT_INVALID", f"selected {scope} root is not a directory: {root}") from error
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise IdeaError("IDEA_ROOT_UNSAFE", f"selected {scope} root is a symbolic link: {root}") from error
        raise _filesystem_error(error, f"opening selected {scope} root", root) from error


def _open_destination(root_fd: int, root: Path, child: str) -> int:
    path = root / child
    try:
        try:
            os.mkdir(child, mode=0o755, dir_fd=root_fd)
        except FileExistsError:
            pass
        return os.open(
            child, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd
        )
    except OSError as error:
        if error.errno in (errno.ELOOP, errno.ENOTDIR):
            raise IdeaError(
                "IDEA_UNSAFE_DESTINATION",
                f"{path}: destination must be a real directory, not a symlink or other file",
            ) from error
        raise _filesystem_error(error, "opening idea destination", path) from error


def capture_idea(
    text: str,
    *,
    project_root: str | Path | None = None,
    vault_root: str | Path | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Save one new Project or general idea and return its native result."""
    if (project_root is None) == (vault_root is None):
        raise IdeaError("IDEA_TARGET_INVALID", "pass exactly one of project_root or vault_root")
    if not isinstance(text, str) or not text.strip():
        raise IdeaError("IDEA_TEXT_BLANK", "--text must be a non-blank string")
    try:
        text_bytes = text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise IdeaError("IDEA_TEXT_ENCODING_INVALID", "--text must be valid UTF-8 text") from error
    effective_title = _title_value(title, text)
    try:
        effective_title.encode("utf-8")
    except UnicodeEncodeError as error:
        raise IdeaError("IDEA_TITLE_ENCODING_INVALID", "--title must be valid UTF-8 text") from error

    scope = "project" if project_root is not None else "general"
    selected = project_root if project_root is not None else vault_root
    assert selected is not None
    root = Path(selected).expanduser().resolve()
    root_fd = _open_root(root, scope)
    try:
        project_id = _read_project_id(root) if scope == "project" else None
        child = IDEAS_DIR_NAME if scope == "project" else GENERAL_IDEAS_DIR_NAME
        created = datetime.now(timezone.utc)
        created_text = created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        note = _render_note(effective_title, text_bytes, created, project_id)
        slug = _slugify(effective_title)
        destination_fd = _open_destination(root_fd, root, child)
        try:
            path = _publish(destination_fd, root / child, slug, note)
        finally:
            try:
                os.close(destination_fd)
            except OSError as error:
                if "path" in locals():
                    raise _filesystem_error(
                        error, "closing idea destination", path, published=True
                    ) from error
    finally:
        try:
            os.close(root_fd)
        except OSError as error:
            if "path" in locals():
                raise _filesystem_error(
                    error, "closing selected root", path, published=True
                ) from error

    result: dict[str, Any] = {
        "scope": scope,
        "idea_path": str(path),
        "title": effective_title,
        "created": created_text,
    }
    if project_id is not None:
        result["project_id"] = project_id
    return result
