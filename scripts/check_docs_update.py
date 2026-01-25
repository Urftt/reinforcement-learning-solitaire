#!/usr/bin/env python3
"""Pre-commit hook to ensure documentation is updated when code changes."""

import subprocess
import sys
from pathlib import Path


def get_staged_files() -> set[str]:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def has_code_changes(staged_files: set[str]) -> bool:
    """Check if any Python code files are being committed."""
    code_extensions = {".py", ".pyi"}
    return any(
        Path(f).suffix in code_extensions and not f.startswith("tests/") for f in staged_files
    )


def has_doc_changes(staged_files: set[str]) -> bool:
    """Check if documentation files are being updated."""
    doc_files = {
        "docs/PROJECT_CONTEXT.md",
        "docs/FEATURES.md",
        "docs/ARCHITECTURE.md",
        "README.md",
    }
    return bool(staged_files & doc_files)


def main() -> int:
    """Check if documentation needs to be updated."""
    try:
        staged_files = get_staged_files()

        # If no files staged, allow commit
        if not staged_files:
            return 0

        # If code changed but docs didn't, prompt user
        if has_code_changes(staged_files) and not has_doc_changes(staged_files):
            print("\n" + "=" * 70)
            print("⚠️  CODE CHANGES DETECTED - DOCUMENTATION CHECK")
            print("=" * 70)
            print("\nYou're committing code changes. Have you updated the documentation?")
            print("\nRelevant docs to consider:")
            print("  • docs/PROJECT_CONTEXT.md  - Project goals and current status")
            print("  • docs/FEATURES.md         - Feature status and roadmap")
            print("  • docs/ARCHITECTURE.md     - Technical decisions and design")
            print("  • README.md                - User-facing documentation")
            print("\n" + "=" * 70)

            response = input("\nDocs updated or not needed? (yes/no): ").strip().lower()

            if response in ["yes", "y"]:
                print("✓ Proceeding with commit...")
                return 0
            else:
                print("\n❌ Commit blocked. Please update documentation and try again.")
                print("   If docs truly don't need updating, stage any doc file with a")
                print("   minor change to bypass this check.\n")
                return 1

        return 0

    except subprocess.CalledProcessError:
        # If git command fails, allow commit (e.g., initial commit)
        return 0
    except KeyboardInterrupt:
        print("\n\n❌ Commit cancelled.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
