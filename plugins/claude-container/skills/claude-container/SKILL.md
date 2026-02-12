---
name: claude-container
description: This skill should be used when the user asks to "run claude in docker", "container", "컨테이너", "docker claude", "sandbox", "샌드박스", "격리 실행", "claude container", "devcontainer", or wants to run Claude Code inside a Docker container for safe isolated execution.
version: 1.0.0
user-invocable: true
---

# Claude Container

A manager for safely running Claude Code inside Docker containers.
Handles .devcontainer generation, image building, and container management all through a single script (`claude.py`).

## Prerequisites

- Docker Desktop or Docker Engine must be installed
- On macOS, host OAuth credentials are automatically injected

## Script Location

Script path: `${pluginDir}/scripts/claude.py`

## Usage

Execute the appropriate command via the Bash tool based on the user's request.

### Run

```bash
# Start a Claude container in the current project
python3 ${pluginDir}/scripts/claude.py run .

# Run with a specific project path
python3 ${pluginDir}/scripts/claude.py run ~/my-project

# Open a zsh shell (without starting Claude)
python3 ${pluginDir}/scripts/claude.py run -s
```

### Manage

```bash
# List running containers
python3 ${pluginDir}/scripts/claude.py list

# Attach a shell to a container
python3 ${pluginDir}/scripts/claude.py shell [name]

# Stop a container
python3 ${pluginDir}/scripts/claude.py stop [name]

# Stop all containers
python3 ${pluginDir}/scripts/claude.py stopall

# Remove a container + volume
python3 ${pluginDir}/scripts/claude.py rm <name>

# Full cleanup (containers + volumes + images)
python3 ${pluginDir}/scripts/claude.py clean
```

### Build / Share

```bash
# Build image only
python3 ${pluginDir}/scripts/claude.py build

# Push to registry (requires CLAUDE_IMAGE env var)
python3 ${pluginDir}/scripts/claude.py push

# Pull from registry
python3 ${pluginDir}/scripts/claude.py pull
```

## Features

- **Auto .devcontainer generation**: Automatically creates Dockerfile, firewall script, and devcontainer.json
- **Network isolation**: iptables firewall allows only essential domains (Anthropic API, GitHub, etc.)
- **Auto OAuth injection**: Injects Claude Code credentials from macOS Keychain into the container
- **tmux session**: Claude process persists after exit; reconnect to resume
- **Container naming**: `{folder-name}-{path-hash-5-chars}` format (e.g., `imoogi-a3f1c`)

## Environment Variables

- `ANTHROPIC_API_KEY`: Claude API key (can be used instead of OAuth)
- `CLAUDE_IMAGE`: Custom image name (registry path for team sharing)

## Steps

1. Identify the user's intent (run / list / stop / remove / build)
2. Verify Docker is installed (`docker --version`)
3. Execute the appropriate command via the Bash tool
4. Show the result to the user

## Notes

- The container runs Claude with `--dangerously-skip-permissions` mode (safe due to container isolation)
- Even in environments where the firewall is not applied, Docker network isolation provides basic protection
- Development tools such as zsh, fzf, ripgrep, jq, and tmux are pre-installed
