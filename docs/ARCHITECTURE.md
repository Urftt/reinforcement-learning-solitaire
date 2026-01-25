# Architecture

> **Purpose**: Document technical decisions and design so Claude Code understands the codebase structure.
> **Update frequency**: Update when making significant architectural decisions or changes.

## Project Structure

```
.
├── src/my_project/       # Main source code
│   ├── __init__.py       # Package initialization
│   └── main.py           # Entry point
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── pyproject.toml        # Project configuration
```

## Key Architectural Decisions

### [Decision Title]
**Date**: YYYY-MM-DD

**Context**: What situation led to this decision?

**Decision**: What was decided?

**Rationale**: Why was this approach chosen?

**Alternatives considered**:
- Alternative 1: Why it wasn't chosen
- Alternative 2: Why it wasn't chosen

**Consequences**: What are the implications of this decision?

---

## Design Patterns

**Patterns used in this project**:
<!-- Document any design patterns you're following -->

Example:
- **Repository Pattern**: For data access (location: `src/repositories/`)
- **Factory Pattern**: For object creation (location: `src/factories/`)

## Code Organization

**Module structure**:
<!-- How is code organized? -->

**Naming conventions**:
<!-- Any specific naming patterns? -->

**File organization rules**:
<!-- How to decide what goes where? -->

## External Dependencies

**Key libraries**:
<!-- List important external dependencies and why they're used -->

| Library | Purpose | Why chosen |
|---------|---------|------------|
| Example | Doing X | Best option for Y |

## Data Flow

**How data moves through the system**:
<!-- Diagrams or descriptions of data flow -->

```
User Input → Validation → Processing → Storage → Output
```

## Testing Strategy

**Test organization**:
<!-- How are tests structured? -->

**What to test**:
<!-- Guidelines on what needs tests -->

**What not to test**:
<!-- Things explicitly not tested and why -->

## Performance Considerations

**Known bottlenecks**:
<!-- Areas that might need optimization -->

**Optimization decisions**:
<!-- Where performance was prioritized and why -->

## Security Considerations

**Security measures**:
<!-- What security practices are in place? -->

**Known limitations**:
<!-- What security concerns exist? -->

## Future Architecture Plans

**Planned refactoring**:
<!-- Areas identified for future improvement -->

**Scalability considerations**:
<!-- How might this need to change as it grows? -->

## Notes for Claude Code

**Code style preferences**:
<!-- Specific patterns or styles to follow when generating code -->

**Refactoring guidelines**:
<!-- When is it okay to refactor? What to preserve? -->

**When to ask before changing**:
<!-- Architectural decisions that need human approval -->
