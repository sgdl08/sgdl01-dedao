# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

This repository is currently empty — no source code, dependencies, or tooling have been established yet. Sections below marked with **[TODO]** should be filled in once the project stack is defined.

## Git Workflow

- All branches must start with `claude/` and end with the session ID suffix: `claude/<description>-<session-id>`
- Never push to `main` or `master` without explicit permission
- Push with: `git push -u origin <branch-name>`
- On network failures, retry push up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

## Commands

**[TODO]** Once the stack is established, document:

```bash
# Install dependencies
<command>

# Run the application
<command>

# Run all tests
<command>

# Run a single test
<command>

# Lint / format
<command>
```

## Architecture

**[TODO]** Once source code exists, describe:
- The overall system design and data flow
- Key modules and how they interact
- Any non-obvious architectural decisions
- External services and integrations

## Updating This File

Update this file whenever the project structure, commands, or architecture change in a non-obvious way.
