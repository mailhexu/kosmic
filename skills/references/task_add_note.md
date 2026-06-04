# Task: Add Note

Create or update atomic notes, and log daily progress.

## When to Use This Task

**AUTO-TRIGGERS - Run Add Note IF:**

| If you... | Then add note for... |
|-----------|---------------------|
| Read source code | Algorithm/pattern learned |
| Make a decision | Decision + rationale |
| Fix a bug | Cause + solution |
| Write docs | Core concepts |
| Finish session | Session summary |

**Rule**: Knowledge in your head → must be in notes.

## Step 1: Check Existing

Read `{VAULT}/Projects/{TARGET}/notes/{TOPIC}.md`

- **Exists & Consistent**: Update content, set `last_validated: now`
- **Exists & Conflict**: Append `## Conflict` section or create `{TOPIC}_conflict.md`
- **Not Exists**: Create new note

## Step 2: Check Notation

Before writing, check notation.md for existing variable definitions:

    cat {VAULT}/Projects/{TARGET}/notes/notation.md

**Rules**:
- If notation exists, use the same symbol and definition
- If new notation, add to notation.md first
- If existing notation is wrong, update notation.md AND all related notes

## Step 3: Create Note

### Template

    # {Topic Title}
    
    ---
    confidence: 0.8
    created: {TIMESTAMP}
    last_validated: {TIMESTAMP}
    validation_procedure: "How to verify"
    project: {TARGET}
    status: validated
    validated_by: automatic
    tags: []
    ---
    
    ## Overview
    This note describes {brief description of the concept and its purpose}.
    
    ## Principles
    This concept follows these key principles:
    - {Principle 1 with explanation}
    - {Principle 2 with explanation}
    
    ## Details
    {Main content written in full sentences explaining the concept clearly. 
    Break into paragraphs for readability. Include examples where helpful.
    Use inline links like [[note_name|display text]] when referencing related concepts.}
    
    ## Variables
    The following variables are used in this note (see [[notation]] for full definitions):
    
    | Symbol | Description | Units |
    |--------|-------------|-------|
    | `x` | The position of the object in space | meters (m) |
    
    ## Equations
    The fundamental equation for this concept is:
    
    $$
    E = mc^2
    $$
    
    In this equation, E represents the energy, m represents the mass, and c represents the speed of light.
    
    ## Workflow
    The following diagram shows the workflow for this process:
    
        ```mermaid
        flowchart TD
            A[Start: Initialize variables] --> B[Process: Apply equation]
            B --> C[End: Return result]
        ```
    
    ## Conventions
    When implementing this concept, follow these conventions:
    - {Convention 1}: {Explanation of why and how}
    
    ## Linked Concepts
    - [[related_note]]: {Brief explanation of how this note relates}
    - [[notation]]: Standard variable notations used in this note

### Principles

- **One Concept**: Each note covers ONE concept only
- **Self-Contained**: Understandable without external context
- **Full Sentences**: Use complete sentences, not just bullet points
- **Explicit Variables**: All variables, subscripts, superscripts documented
- **Equations**: Always use Markdown display math with `$$` delimiters for standalone equations. Do not leave raw LaTeX equation paragraphs without `$$`.
- **Workflows**: Use Mermaid diagrams for processes
- **Links**: 
  - Use `[[note_name]]` for section-level links
  - Use `[[note_name|display text]]` for inline links
  - Do NOT use `![[]]` (that's for images)

## Step 4: Update TOC

Add entry to `{VAULT}/Projects/{TARGET}/notes/TOC.md`:

    ## Category
    - [[{TOPIC}]] - This note explains {brief description of what it covers}.

## Step 5: Update Daily Log

Append to `{VAULT}/Projects/{TARGET}/log/{TARGET}-{DATE}.md`:

    ## Session {N}
    - Created/Updated: [[{TOPIC}]] - {Brief description}
    - {Other activities}

Also ensure the project log `{VAULT}/Projects/{TARGET}/log/{TARGET}-{DATE}.md` links to any notes created or updated:

    - Created/Updated: [[notes/{TOPIC}|{TOPIC}]] - {Brief description}

## Step 6: Review

### Checklist

1. **Completeness**: All required sections present?
2. **Clarity**: Sentences complete and clear?
3. **Variables**: All documented with units?
4. **Equations**: Are all standalone equations wrapped with `$$` display-math delimiters?
5. **Links**: Do all `[[links]]` point to existing notes?
6. **Workflows**: Mermaid diagrams syntactically correct?
7. **Metadata**: Frontmatter correct?
8. **TOC**: Updated with this note?
9. **Notation**: Consistent with notation.md?

### Check Commands

    # Check for broken links
    grep -oP '\[\[\K[^\]]+' {VAULT}/Projects/{TARGET}/notes/{TOPIC}.md | while read link; do
        [ ! -f "{VAULT}/Projects/{TARGET}/notes/$link.md" ] && echo "Missing: $link"
    done

### If Issues Found

- Fix immediately before considering note complete
- If referenced note doesn't exist, create it or adjust link
- If notation inconsistent, update this note or notation.md + all related notes
