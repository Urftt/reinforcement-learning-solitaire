# Instructions for Claude Code

> **Purpose**: Guide Claude Code to work effectively in this project across sessions.
> **Audience**: Future Claude Code instances working on this project.

## 🎯 How to Start a New Session

When starting work on this project, **ALWAYS**:

1. **Read these docs first** (in this order):
   - [`docs/PROJECT_CONTEXT.md`](../docs/PROJECT_CONTEXT.md) - Understand the why and current state
   - [`docs/FEATURES.md`](../docs/FEATURES.md) - Know what's done and what's next
   - [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) - Understand technical decisions

2. **Check for context clues**:
   - Read recent git commit messages: `git log --oneline -10`
   - Check for TODO/FIXME comments in code
   - Look for any `docs/features/*.md` files related to current work

3. **Confirm understanding** with the user:
   - "I've reviewed the docs. We're currently [status]. Should I continue with [next task]?"

## 📝 Documentation Requirements

### BEFORE Every Commit

You **MUST** check if documentation needs updating. The pre-commit hook will prompt you.

**Ask yourself**:
- Did I add/remove/change functionality? → Update `FEATURES.md`
- Did I make an architectural decision? → Update `ARCHITECTURE.md`
- Did project goals or status change? → Update `PROJECT_CONTEXT.md`
- Did I change user-facing behavior? → Update `README.md`

### When to Create Feature Docs

For **non-trivial features** (>2 files or >50 lines changed):
1. Copy `docs/templates/FEATURE_TEMPLATE.md` to `docs/features/FEATURE-XXX-name.md`
2. Fill it out BEFORE implementing
3. Get user approval on the approach
4. Update it as you implement
5. Mark as "Completed" when done

### When to Create Requirements Docs

For **major features or new projects**:
1. Copy `docs/templates/REQUIREMENTS_TEMPLATE.md` to `docs/requirements/REQ-project-name.md`
2. Work with the user to fill it out
3. Use it as the source of truth during implementation

## 🔧 Development Workflow

### Setting Up the Environment

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run code quality checks
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

### Before Committing Code

1. **Run quality checks**: `uv run ruff check . && uv run ruff format .`
2. **Run tests**: `uv run pytest`
3. **Update documentation** (see above)
4. **Review your changes**: `git diff`
5. **Commit with clear message** describing the "why"

### Code Style Guidelines

**Follow these patterns** (unless docs say otherwise):
- Use type hints for function signatures
- Keep functions small and focused
- Write docstrings for public functions
- Prefer readability over cleverness
- Don't over-engineer - solve the current problem

**Testing**:
- Write tests for new functionality
- Update tests when changing behavior
- Use descriptive test names: `test_<what>_<expected_outcome>`

## 🤖 Working with the User

### Communication Style

The user values:
- **Clarity**: Explain what you're doing and why
- **Efficiency**: Don't over-explain simple changes
- **Proactivity**: Suggest improvements when you see opportunities
- **Documentation**: Keep docs in sync with code

### When to Ask vs. Proceed

**ASK before**:
- Making architectural decisions
- Adding new dependencies
- Removing existing functionality
- Implementing features with multiple valid approaches
- Changing user-facing behavior

**PROCEED without asking**:
- Fixing obvious bugs
- Improving code quality (refactoring)
- Adding tests
- Updating documentation
- Implementing clearly-specified features

### Pushing Your Limits

The user wants to **push Claude Code to its limits**. This means:

1. **Be proactive**: Suggest improvements beyond the immediate ask
2. **Be thorough**: Don't skip edge cases or error handling
3. **Be contextual**: Use the docs to make informed decisions
4. **Be helpful**: If you notice something off, point it out
5. **Be honest**: If something is unclear, ask rather than guess

## 🎨 Project-Specific Patterns

### File Organization

```
src/                   # Flat structure - organize as you grow
  ├── __init__.py      # Package initialization
  ├── main.py          # Example module
  ├── ...              # Add more modules as needed

  # As project grows, consider organizing into subdirectories:
  ├── core/            # Core business logic (optional)
  ├── utils/           # Utility functions (optional)
  └── models/          # Data models (optional)
```

**Philosophy**: Start flat, add structure when complexity demands it.

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Error Handling

<!-- Update with project-specific error handling patterns -->

```python
# Preferred pattern
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Failed to do X: {e}")
    raise CustomError("User-friendly message") from e
```

## 🚨 Common Pitfalls

**Avoid these**:
- [ ] Committing without updating docs
- [ ] Adding dependencies without justification
- [ ] Implementing features without checking `FEATURES.md`
- [ ] Ignoring test failures
- [ ] Making breaking changes without discussion

## 🔗 Useful Commands

```bash
# Check what's changed
git status
git diff

# Run full quality check
uv run ruff check . && uv run ruff format . && uv run mypy src/ && uv run pytest

# Update dependencies
uv lock
uv sync

# Clean up
find . -type d -name __pycache__ -exec rm -r {} +
rm -rf .pytest_cache .ruff_cache .mypy_cache
```

## 📚 Additional Context

### Project Philosophy

<!-- Add project-specific philosophy or principles -->

### Learning Goals

<!-- If this is a learning project, what are we learning? -->

### External Resources

<!-- Links to relevant docs, tutorials, inspirations -->

## 🆘 When Things Go Wrong

If you're stuck or uncertain:
1. Re-read the relevant docs
2. Check git history for context: `git log --grep="keyword"`
3. Ask the user for clarification
4. Suggest options with trade-offs

Remember: **It's better to ask than to guess wrong!**

---

## Meta: Improving These Instructions

If you notice these instructions are unclear or could be improved:
1. **Point it out** to the user
2. **Suggest improvements**
3. **Update this file** after user approval

These instructions should evolve with the project!
