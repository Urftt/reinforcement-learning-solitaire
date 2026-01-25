# Python Project Template

A comprehensive Python project template optimized for **Claude Code workflows**, designed for personal projects, POCs, and experimental development.

## 🎯 What Makes This Template Special?

This template is specifically designed to help **Claude Code understand and maintain your projects across sessions**. It includes:

- **Documentation structure** that preserves context between CC sessions
- **Pre-commit hooks** that ensure docs stay in sync with code
- **Feature and requirement templates** for structured development
- **Claude Code instructions** to maximize AI assistance effectiveness

Perfect for data scientists and developers who want to push coding agents to their limits!

## ✨ Features

- **📦 uv**: Ultra-fast Python package management
- **🔍 Code Quality**: Ruff (linting + formatting) + mypy (type checking)
- **🧪 Testing**: pytest with coverage reporting
- **🔄 CI/CD**: GitHub Actions for automated testing and quality checks
- **📚 Documentation**: Structured docs that help Claude Code understand your project
- **🪝 Pre-commit Hooks**: Automatic quality checks and documentation reminders
- **📋 Templates**: Feature and requirements templates for planning work

## 🚀 Quick Start

### 1. Use This Template

Click "Use this template" on GitHub or:

```bash
git clone https://github.com/yourusername/python-project-template.git my-new-project
cd my-new-project
```

### 2. Customize for Your Project

Edit [`pyproject.toml`](pyproject.toml):
- Update `name` to your project name
- Update `description` with what your project does
- Update `authors` with your information

### 3. Set Up the Environment

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify everything works
uv run pytest
uv run ruff check .
```

### 4. Fill Out Documentation

**This is crucial for Claude Code to help you effectively!**

Edit these files:
- [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) - Your project vision and goals
- [`docs/FEATURES.md`](docs/FEATURES.md) - What you're building
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Technical decisions

### 5. Start Building!

```bash
# Create a new feature
# 1. Plan it: copy docs/templates/FEATURE_TEMPLATE.md to docs/features/
# 2. Implement it
# 3. Test it: uv run pytest
# 4. Commit it (docs will be checked automatically)
```

## 📖 Working with Claude Code

### Starting a New Session

Tell Claude Code:

> "Please review the docs in `.claude/` and `docs/` to understand the project context before we begin."

Or simply:

> "Read the project docs and confirm you understand where we are."

### During Development

The template helps Claude Code:
- **Remember context** from previous sessions via documentation
- **Make informed decisions** based on your project goals
- **Maintain code quality** through automated checks
- **Keep docs updated** via pre-commit prompts

### Best Practices

1. **Update docs regularly** - They're CC's memory between sessions
2. **Use feature templates** - Helps CC understand complex work
3. **Let pre-commit run** - It reminds CC to update docs
4. **Review git history** - CC can learn from commit messages

## 📁 Project Structure

```
.
├── .claude/                  # Claude Code instructions
│   ├── CODE_INSTRUCTIONS.md  # How CC should work in this project
│   └── README.md             # Overview of .claude directory
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD
├── docs/
│   ├── PROJECT_CONTEXT.md    # Project vision and status
│   ├── FEATURES.md           # Feature tracking
│   ├── ARCHITECTURE.md       # Technical decisions
│   ├── features/             # Individual feature docs
│   ├── requirements/         # Requirements docs
│   └── templates/            # Templates for docs
├── scripts/
│   └── check_docs_update.py  # Pre-commit doc checker
├── src/                      # Your source code (flat structure)
│   ├── __init__.py           # Package initialization
│   └── main.py               # Example module (rename/organize as needed)
├── tests/                    # Test suite
├── .pre-commit-config.yaml   # Pre-commit hooks
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🛠️ Development Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy src/

# Run all quality checks
uv run ruff check . && uv run ruff format . && uv run mypy src/ && uv run pytest

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files

# Update dependencies
uv lock
uv sync
```

## 📝 Documentation Workflow

### Pre-Commit Documentation Check

When committing code changes, you'll be prompted:

```
⚠️  CODE CHANGES DETECTED - DOCUMENTATION CHECK
You're committing code changes. Have you updated the documentation?

Relevant docs to consider:
  • docs/PROJECT_CONTEXT.md  - Project goals and current status
  • docs/FEATURES.md         - Feature status and roadmap
  • docs/ARCHITECTURE.md     - Technical decisions
  • README.md                - User-facing documentation

Docs updated or not needed? (yes/no):
```

This ensures documentation stays in sync with code - crucial for Claude Code effectiveness!

### Creating Feature Documentation

For non-trivial features:

```bash
# Copy the template
cp docs/templates/FEATURE_TEMPLATE.md docs/features/FEATURE-001-my-feature.md

# Fill it out (helps CC understand your goals)
# Implement the feature
# Update the feature doc as you go
# Mark it complete when done
```

### Creating Requirements Documentation

For major features or new projects:

```bash
# Copy the template
cp docs/templates/REQUIREMENTS_TEMPLATE.md docs/requirements/REQ-my-project.md

# Work with Claude Code to fill it out
# Use it as source of truth during implementation
```

## 🎨 Customization

### Code Quality Tools

Edit in [`pyproject.toml`](pyproject.toml):
- **Ruff**: `[tool.ruff]` section
- **mypy**: `[tool.mypy]` section
- **pytest**: `[tool.pytest.ini_options]` section

### Pre-commit Hooks

Edit [`.pre-commit-config.yaml`](.pre-commit-config.yaml) to add/remove hooks.

### CI/CD

Edit [`.github/workflows/ci.yml`](.github/workflows/ci.yml) to customize:
- Python versions tested
- Additional checks
- Deployment steps

## 🤝 Template for GitHub

### Making This a Template Repository

1. Go to repository Settings
2. Check "Template repository"
3. Users can now click "Use this template" to create new projects

### Using as a Template

When using this template:
1. Click "Use this template" → "Create a new repository"
2. Follow the Quick Start steps above
3. Customize for your project
4. Start building with Claude Code!

## 💡 Use Cases

This template is perfect for:

- **Pet Projects**: Quick experimentation with proper structure
- **Learning Projects**: Document what you learn as you go
- **POCs**: Professional structure for proof of concepts
- **Coding Agent Projects**: Maximum effectiveness with Claude Code
- **Portfolio Projects**: Production-quality setup from day one

## 📚 Additional Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [Claude Code documentation](https://claude.ai/claude-code)

## 🙏 Philosophy

This template is built on these principles:

1. **Documentation is for AI assistants too** - Not just humans
2. **Quality gates help, not hinder** - Automated checks catch issues early
3. **Templates reduce friction** - Structured planning helps execution
4. **Context preservation** - Future you (and future CC) will thank you

## 📄 License

This template is provided as-is for personal and commercial use. Customize as needed!

---

**Ready to build something amazing?** Fill out the docs, fire up Claude Code, and start coding! 🚀
