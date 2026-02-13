---
name: agent-browser-container
description: This skill should be used when the user asks to "run browser in container", "secure chrome", "agent browser", "에이전트 브라우저", "브라우저 컨테이너", "container chrome", "browser sandbox", "KasmVNC", "browse safely", "안전한 브라우저", or wants to run Chrome inside a Docker container with visual access for safe isolated browsing controlled by Claude Code.
version: 0.1.0
user-invocable: true
---

# Agent Browser Container

A manager for safely running Chrome inside Docker containers with KasmVNC visual access.
Claude Code inside the container controls Chrome via Playwright, while the host user can see and interact through a browser-based VNC interface. This prevents agent injection attacks from reaching the host system.

## Prerequisites

- Docker Desktop or Docker Engine must be installed
- On macOS, host OAuth credentials are automatically injected

## Script Location

Script path: `${pluginDir}/scripts/browser.py`

## Usage

Execute the appropriate command via the Bash tool based on the user's request.

### Run

```bash
# Start a browser container in the current project
python3 ${pluginDir}/scripts/browser.py run .

# Run with a specific project path
python3 ${pluginDir}/scripts/browser.py run ~/my-project

# Open a zsh shell (without starting Claude)
python3 ${pluginDir}/scripts/browser.py run -s
```

### Manage

```bash
# List running containers
python3 ${pluginDir}/scripts/browser.py list

# Attach a shell to a container
python3 ${pluginDir}/scripts/browser.py shell [name]

# Stop a container
python3 ${pluginDir}/scripts/browser.py stop [name]

# Stop all containers
python3 ${pluginDir}/scripts/browser.py stopall

# Remove a container + volume
python3 ${pluginDir}/scripts/browser.py rm <name>

# Full cleanup (containers + volumes + images)
python3 ${pluginDir}/scripts/browser.py clean
```

### Build / Share

```bash
# Build image only
python3 ${pluginDir}/scripts/browser.py build

# Push to registry (requires BROWSER_IMAGE env var)
python3 ${pluginDir}/scripts/browser.py push

# Pull from registry
python3 ${pluginDir}/scripts/browser.py pull
```

## Architecture

```
Host (macOS)
  +-- Browser -> http://localhost:6901 (KasmVNC web UI)
  |              See & interact with container Chromium
  +-- CDP    -> http://localhost:9222 (Chrome DevTools Protocol)
  |              Control Chrome programmatically from host
  +-- Terminal -> docker exec -> Claude Code
                   Controls Chromium via Playwright/CDP (headless: false, DISPLAY=:1)

Container (Linux, --read-only)
  +-- KasmVNC Server (virtual display :1, streams to port 6901)
  +-- Chromium (auto-launched with CDP on port 9222)
  +-- socat (forwards 0.0.0.0:9223 -> 127.0.0.1:9222 for host CDP access)
  +-- Claude Code (controls Chromium via Playwright CDP)
  +-- iptables firewall (allowlist + CHROME_ALLOW_ALL option)
  +-- tmpfs: /tmp, /run, /home/node (writable but ephemeral)
  +-- Playwright cache at /opt/ms-playwright (persistent in image layer)
  +-- /downloads (bind mount to host, writable, UNTRUSTED)
```

## Features

- **KasmVNC visual access**: Modern HTML5 browser-based VNC with clipboard and file transfer support
- **CDP access**: Chrome DevTools Protocol exposed on port 9222 for programmatic control from host
- **Playwright automation**: Claude Code controls Chromium via CDP with `headless: false`
- **Security hardening**: `--read-only` FS, `--cap-drop ALL`, `no-new-privileges`, tmpfs mounts
- **Network isolation**: iptables firewall with allowlist + optional `CHROME_ALLOW_ALL` mode
- **Auto OAuth injection**: Injects Claude Code credentials from macOS Keychain into the container
- **tmux session**: Claude process persists after exit; reconnect to resume
- **Downloads directory**: Files downloaded by Chrome are saved to `./downloads/` on the host
- **Container naming**: `{folder-name}-{path-hash}-browser` format (e.g., `myproject-a3f1c-browser`)

## Environment Variables

- `ANTHROPIC_API_KEY`: Claude API key (can be used instead of OAuth)
- `BROWSER_IMAGE`: Custom image name (registry path for team sharing)
- `VNC_PW`: Set a fixed VNC password (default: random per session)
- `CHROME_ALLOW_ALL`: Set to `1` to allow all HTTP/HTTPS traffic (default: `1`)

## User Interaction Flow

1. Run `python3 browser.py run .` to start the container
2. Open `http://localhost:6901` in the host browser to see KasmVNC
3. Enter the VNC password shown in the terminal
4. Claude Code (inside container) launches Playwright Chromium with `headless: false`
5. Chromium appears in the KasmVNC web UI - watch automation in real time
6. When manual action is needed (login, CAPTCHA), interact with Chrome via KasmVNC
7. Tell Claude Code to continue after completing the manual action
8. Downloaded files appear in `./downloads/` (treat as UNTRUSTED)

## Security Model

- Container provides PID namespace, filesystem isolation, network isolation
- `--read-only` FS prevents persistent malware
- `--cap-drop ALL + NET_ADMIN` minimizes kernel attack surface
- `no-new-privileges` prevents privilege escalation
- `--pids-limit 500` prevents fork bombs
- `--memory 4g` prevents OOM attacks on host
- Downloads are isolated to `./downloads/` (treat as untrusted)
- Agent injection cannot escape the container sandbox

## Steps

1. Identify the user's intent (run / list / stop / remove / build)
2. Verify Docker is installed (`docker --version`)
3. Execute the appropriate command via the Bash tool
4. Show the result to the user including VNC access URL and password

## Notes

- The container runs Claude with `--dangerously-skip-permissions` mode (safe due to container isolation)
- Chromium uses `--no-sandbox` flag which is safe because the container IS the sandbox
- KasmVNC replaces the traditional Xvfb + x11vnc + websockify + noVNC stack with a single binary
- Even in environments where the firewall is not applied, Docker network isolation provides basic protection
- Development tools such as zsh, fzf, ripgrep, jq, and tmux are pre-installed
