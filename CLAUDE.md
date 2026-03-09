# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

## Repository Status

This repository is currently being initialized. No source code has been committed yet.

- **Remote**: `http://local_proxy@127.0.0.1:37385/git/sgdl08/sgdl01-dedao`
- **Default branch**: `claude/claude-md-mmiwei2ekt63w2jr-WDMEW`

## Git Workflow

### Branching Convention

- Feature branches must start with `claude/` and include the session ID suffix
- Example: `claude/<description>-<session-id>`
- Never push to `main` or `master` without explicit permission

### Commit Practices

- Write clear, descriptive commit messages in imperative mood (e.g., "Add user authentication")
- Keep commits focused and atomic — one logical change per commit
- Do not amend published commits; create new ones instead

### Pushing Changes

Always use:
```bash
git push -u origin <branch-name>
```

If push fails due to network errors, retry with exponential backoff: 2s, 4s, 8s, 16s.

## Development Setup

> **Note**: Update this section once the project stack is established.

Steps to set up the development environment will go here, including:
- Dependency installation commands
- Environment variable configuration (`.env` setup)
- Database initialization if applicable
- Any required services

## Running the Project

> **Note**: Update this section once entry points are defined.

Commands to start the application in development mode will go here.

## Testing

> **Note**: Update this section once a test framework is in place.

Commands to run the test suite will go here. All tests must pass before pushing.

## Code Style & Linting

> **Note**: Update this section once linting tools are configured.

Linting and formatting commands will go here. Enforce code style before committing.

## Project Conventions

### General

- Prefer editing existing files over creating new ones
- Avoid over-engineering — implement only what is currently needed
- Do not add speculative features, extra error handling, or backwards-compatibility shims unless required
- Do not add docstrings or comments to code you didn't change

### Security

- Never commit secrets, credentials, or `.env` files
- Validate input at system boundaries (user input, external APIs); trust internal code
- Avoid common vulnerabilities: SQL injection, XSS, command injection (OWASP Top 10)

### File Organization

> **Note**: Update this section as the project structure evolves.

Document key directories and their purposes here once the codebase is established.

## Updating This File

Keep this file current as the project evolves:
- Add the tech stack and framework details once established
- Document all `npm run` / `make` / `poetry run` (or equivalent) commands
- Record any non-obvious architectural decisions
- Note any environment-specific quirks or known issues
