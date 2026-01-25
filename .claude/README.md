# .claude Directory

This directory contains instructions and context specifically for Claude Code.

## Files

- **[`CODE_INSTRUCTIONS.md`](CODE_INSTRUCTIONS.md)**: Complete guide for CC on how to work in this project
  - Read this first when starting a new session
  - Contains workflow, patterns, and best practices
  - Updated as project evolves

## Why This Exists

This project is optimized for Claude Code workflows. The goal is to enable CC to:
- Pick up context quickly when starting new sessions
- Understand project goals and constraints
- Make informed decisions aligned with the project vision
- Maintain consistency across sessions

## For Users

When starting a new CC session, you might want to say:

> "Before we begin, please read the instructions in `.claude/CODE_INSTRUCTIONS.md` and the docs in `docs/` to understand the project context."

Or simply:

> "Review the project docs and confirm you understand the current state."

## For Claude Code

If you're CC reading this: **Read `CODE_INSTRUCTIONS.md` first**, then the docs in `../docs/`, then confirm your understanding with the user before proceeding with work.
