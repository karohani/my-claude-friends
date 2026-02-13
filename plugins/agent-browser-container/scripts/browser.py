#!/usr/bin/env python3
"""
Agent Browser Container Manager

Runs Chrome inside a secure Docker container with KasmVNC for visual access
and Claude Code controlling Chrome via Playwright. The security model prevents
agent injection attacks from reaching the host.

From your project folder, just run this single script to:
  1. Auto-generate .devcontainer/ folder + required files
  2. Build Docker image (Chrome + KasmVNC + Playwright)
  3. Start container -> Claude Code auto-starts with browser access

Container name: {folder}-{path_hash}-browser  e.g.) myproject-a3f1c-browser

Usage:
  python3 browser.py                    # Start Claude with browser in current folder
  python3 browser.py run ~/project      # Start in a specific folder
  python3 browser.py run -s             # Connect with zsh shell (--shell)
  python3 browser.py list               # List running containers
  python3 browser.py shell [name]       # Attach to container
  python3 browser.py stop [name]        # Stop container
  python3 browser.py stopall            # Stop all containers
  python3 browser.py rm <name>          # Remove container + volumes
  python3 browser.py clean              # Full cleanup (containers+volumes+images)
  python3 browser.py push               # Push image to registry
  python3 browser.py pull               # Pull image from registry
"""

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

# ─── Configuration ────────────────────────────────────────
LABEL = "agent-browser"
DEFAULT_IMAGE = "agent-browser-sandbox"

# ─── Embedded files ──────────────────────────────────────

DOCKERFILE = textwrap.dedent("""\
    FROM node:24-bookworm-slim

    ARG CLAUDE_CODE_VERSION=latest

    RUN apt-get update && apt-get install -y --no-install-recommends \\
        git curl sudo ca-certificates wget openssl \\
        zsh fzf ripgrep jq tmux \\
        iptables iproute2 dnsutils socat \\
        locales \\
        fonts-noto-cjk fonts-noto-color-emoji \\
        openbox \\
        libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 \\
        libxdamage1 libxrandr2 libgbm1 libasound2 libxfixes3 \\
        libcups2 libxkbcommon0 libcairo2 libpango-1.0-0 \\
        xdg-utils \\
        && rm -rf /var/lib/apt/lists/*

    # KasmVNC (single binary replaces Xvfb + x11vnc + websockify + noVNC)
    RUN ARCH=$(dpkg --print-architecture) && \\
        wget -q "https://github.com/kasmtech/KasmVNC/releases/download/v1.4.0/kasmvncserver_bookworm_1.4.0_${ARCH}.deb" && \\
        apt-get update && apt-get install -y --no-install-recommends ./kasmvncserver_bookworm_*.deb && \\
        rm -f kasmvncserver_bookworm_*.deb && rm -rf /var/lib/apt/lists/*

    RUN sed -i '/ko_KR.UTF-8/s/^# //' /etc/locale.gen && locale-gen
    ENV LANG=ko_KR.UTF-8 LC_ALL=ko_KR.UTF-8

    RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

    ENV DISPLAY=:1
    ENV VNC_PORT=6901
    ENV VNC_RESOLUTION=1920x1080

    COPY init-firewall.sh /usr/local/bin/
    COPY start-kasmvnc.sh /usr/local/bin/
    USER root
    RUN chmod +x /usr/local/bin/init-firewall.sh /usr/local/bin/start-kasmvnc.sh && \\
        echo "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/node-firewall && \\
        chmod 0440 /etc/sudoers.d/node-firewall

    RUN mkdir -p /commandhistory /downloads && \\
        chown node:node /commandhistory /downloads
    RUN chsh -s /usr/bin/zsh node

    RUN mkdir -p /home/node/.vnc && chown node:node /home/node/.vnc

    RUN su - node -c 'echo "HISTFILE=/commandhistory/.zsh_history\\nHISTSIZE=10000\\nSAVEHIST=10000\\nsetopt appendhistory\\nautoload -Uz compinit && compinit" > ~/.zshrc'

    ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
    RUN mkdir -p /opt/ms-playwright && chown node:node /opt/ms-playwright

    USER node
    WORKDIR /workspace

    # Install Playwright + its bundled Chromium
    RUN npx playwright install chromium
""")

KASMVNC_SH = textwrap.dedent("""\
    #!/usr/bin/env bash
    set -uo pipefail

    VNC_PORT="${VNC_PORT:-6901}"
    VNC_RESOLUTION="${VNC_RESOLUTION:-1920x1080}"

    # Create dirs (tmpfs wipes /home/node on each start)
    mkdir -p /home/node/.vnc

    # Create a dummy KasmVNC user with write access (required internally even with auth disabled)
    printf 'dummypass\\ndummypass\\n' | kasmvncpasswd -u node -w -o 2>&1 || true

    # Write xstartup (openbox window manager for Chrome rendering)
    cat > /home/node/.vnc/xstartup << 'XSTARTUP'
    #!/bin/sh
    openbox-session &
    XSTARTUP
    chmod +x /home/node/.vnc/xstartup

    # Mark DE as already selected so select-de.sh is skipped
    touch /home/node/.vnc/.de-was-selected

    # Write KasmVNC config: disable SSL (localhost-only access)
    cat > /home/node/.vnc/kasmvnc.yaml << 'YAML'
    network:
      protocol: http
      ssl:
        require_ssl: false
        pem_certificate:
        pem_key:
    YAML

    # Start KasmVNC server (DisableBasicAuth + SecurityTypes None = no login required)
    kasmvncserver :1 \\
        -geometry "$VNC_RESOLUTION" \\
        -websocketPort "$VNC_PORT" \\
        -FrameRate 30 \\
        -AlwaysShared \\
        -DisableBasicAuth \\
        -SecurityTypes None \\
        -log '*:stderr:30' 2>&1 &

    sleep 3

    echo ""
    echo "========================================="
    echo "  KasmVNC ready!"
    echo "  URL: http://localhost:${VNC_PORT}"
    echo "  (No authentication required)"
    echo "========================================="
    echo ""

    # Launch Chromium with CDP (Chrome DevTools Protocol)
    export DISPLAY=:1
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
    CHROME_BIN=$(find "$PLAYWRIGHT_BROWSERS_PATH" -name "chrome" -type f 2>/dev/null | head -1)
    if [ -n "$CHROME_BIN" ]; then
        mkdir -p /tmp/chrome-data
        "$CHROME_BIN" \
            --no-sandbox \
            --disable-gpu \
            --disable-dev-shm-usage \
            --disable-software-rasterizer \
            --no-first-run \
            --no-default-browser-check \
            --user-data-dir=/tmp/chrome-data \
            --remote-debugging-port=9222 \
            --window-size=1920,1080 \
            --start-maximized \
            "about:blank" &
        sleep 2
        echo "Chrome launched with CDP on port 9222"
        echo "  CDP: http://localhost:9222"
        # Forward CDP from 0.0.0.0:9222 -> 127.0.0.1:9222 (Chrome ignores --remote-debugging-address)
        socat TCP-LISTEN:9223,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:9222 &
    else
        echo "WARNING: Chrome binary not found in $PLAYWRIGHT_BROWSERS_PATH"
    fi
""")

FIREWALL_SH = textwrap.dedent("""\
    #!/usr/bin/env bash
    set -uo pipefail

    echo "Initializing firewall (browser mode)..."

    if command -v iptables-legacy &>/dev/null; then
        IPT="iptables-legacy"
    else
        IPT="iptables"
    fi

    if ! $IPT -L -n &>/dev/null 2>&1; then
        echo "iptables unavailable -- skipping (container isolation active)"
        exit 0
    fi

    $IPT -F OUTPUT 2>/dev/null || true
    $IPT -P OUTPUT DROP

    $IPT -A OUTPUT -o lo -j ACCEPT
    $IPT -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    $IPT -A OUTPUT -p udp --dport 53 -j ACCEPT
    $IPT -A OUTPUT -p tcp --dport 53 -j ACCEPT
    $IPT -A OUTPUT -p tcp --dport 22 -j ACCEPT

    ALLOWED_DOMAINS=(
        "api.anthropic.com"
        "statsig.anthropic.com"
        "sentry.io"
        "registry.npmjs.org"
        "github.com"
        "api.github.com"
        "raw.githubusercontent.com"
        "objects.githubusercontent.com"
    )

    for domain in "${ALLOWED_DOMAINS[@]}"; do
        for ip in $(dig +short "$domain" A 2>/dev/null | grep -E '^[0-9]+\\\\.' || true); do
            $IPT -A OUTPUT -d "$ip" -j ACCEPT 2>/dev/null || true
        done
    done

    if [ "${CHROME_ALLOW_ALL:-0}" = "1" ]; then
        $IPT -A OUTPUT -p tcp --dport 80 -j ACCEPT
        $IPT -A OUTPUT -p tcp --dport 443 -j ACCEPT
        echo "Firewall ready (${#ALLOWED_DOMAINS[@]} domains + ALL HTTP/HTTPS allowed)"
    else
        echo "Firewall ready (${#ALLOWED_DOMAINS[@]} domains whitelisted, HTTP/HTTPS restricted)"
    fi
""")

DEVCONTAINER_JSON = textwrap.dedent("""\
    {
      "name": "Agent Browser Sandbox",
      "build": {
        "dockerfile": "Dockerfile",
        "args": { "CLAUDE_CODE_VERSION": "latest" }
      },
      "customizations": {
        "vscode": {
          "extensions": [
            "anthropic.claude-code",
            "ms-playwright.playwright"
          ],
          "settings": {
            "editor.formatOnSave": true,
            "terminal.integrated.defaultProfile.linux": "zsh"
          }
        }
      },
      "remoteUser": "node",
      "mounts": [
        "source=agent-browser-bashhistory-${devcontainerId},target=/commandhistory,type=volume",
        "source=agent-browser-config-${devcontainerId},target=/home/node/.claude,type=volume"
      ],
      "containerEnv": {
        "NODE_OPTIONS": "--max-old-space-size=4096",
        "CLAUDE_CONFIG_DIR": "/home/node/.claude",
        "DISPLAY": ":1",
        "VNC_PORT": "6901"
      },
      "forwardPorts": [6901],
      "postStartCommand": "sudo /usr/local/bin/init-firewall.sh && /usr/local/bin/start-kasmvnc.sh",
      "postCreateCommand": "echo 'export HISTFILE=/commandhistory/.bash_history' >> ~/.bashrc || true"
    }
""")


# ─── Utilities ────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def run_check(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def docker(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return run(["docker", *args], **kwargs)


def docker_check(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return run_check(["docker", *args], **kwargs)


def image_name() -> str:
    return os.environ.get("BROWSER_IMAGE", DEFAULT_IMAGE)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")


def path_hash(p: Path) -> str:
    return hashlib.sha256(str(p).encode()).hexdigest()[:5]


def container_name(project_dir: Path) -> str:
    return f"{slugify(project_dir.name)}-{path_hash(project_dir)}-browser"


def info(msg: str):
    print(f"\033[36m▸\033[0m {msg}")


def ok(msg: str):
    print(f"\033[32m✔\033[0m {msg}")


def warn(msg: str):
    print(f"\033[33m!\033[0m {msg}")


def err(msg: str):
    print(f"\033[31m✖\033[0m {msg}", file=sys.stderr)


def running_containers() -> list[str]:
    r = docker("ps", "--filter", f"label={LABEL}=true", "--format", "{{.Names}}",
               capture_output=True, text=True)
    return [n for n in r.stdout.strip().splitlines() if n]


def tty_flags() -> list[str]:
    """Return -it if stdin is a TTY, otherwise -i only."""
    return ["-it"] if sys.stdin.isatty() else ["-i"]


def get_host_credentials() -> tuple[str | None, str | None]:
    """Extract Claude Code OAuth credentials from macOS Keychain.
    Returns (full_json, access_token) tuple."""
    if platform.system() != "Darwin":
        return None, None
    try:
        r = subprocess.run(
            ["security", "find-generic-password",
             "-s", "Claude Code-credentials", "-w"],
            capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            raw = r.stdout.strip()
            creds = json.loads(raw)
            token = creds.get("claudeAiOauth", {}).get("accessToken")
            return raw, token
    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError):
        pass
    return None, None


def inject_credentials_file(ctr_name: str, creds_json: str):
    """Inject host OAuth credentials as .credentials.json into the container
    and set hasCompletedOnboarding to skip interactive login."""
    docker("exec", "-u", "root", ctr_name, "chown", "node:node",
           "/home/node/.claude", capture_output=True)
    # Inject .credentials.json
    run(["docker", "exec", "-i", ctr_name,
         "sh", "-c", "cat > /home/node/.claude/.credentials.json"],
        input=creds_json, text=True, capture_output=True)
    docker("exec", "-u", "root", ctr_name, "sh", "-c",
           "chmod 600 /home/node/.claude/.credentials.json && "
           "chown node:node /home/node/.claude/.credentials.json",
           capture_output=True)
    # Set hasCompletedOnboarding in .claude.json (skip interactive login screen)
    onboarding_script = (
        "const fs = require('fs');"
        "const p = '/home/node/.claude/.claude.json';"
        "let d = {};"
        "try { d = JSON.parse(fs.readFileSync(p, 'utf8')); } catch {}"
        "d.hasCompletedOnboarding = true;"
        "fs.writeFileSync(p, JSON.stringify(d));"
    )
    docker("exec", ctr_name, "node", "-e", onboarding_script,
           capture_output=True)


# ─── .devcontainer generation ─────────────────────────────

def ensure_devcontainer(project_dir: Path) -> Path:
    """Create .devcontainer-browser/ in the project if it does not exist.
    Uses a separate directory to avoid conflicts with .devcontainer/ from claude-container."""
    devc = project_dir / ".devcontainer-browser"

    if devc.exists() and (devc / "Dockerfile").exists():
        return devc

    info(f"Creating .devcontainer: {devc}")
    devc.mkdir(parents=True, exist_ok=True)

    (devc / "Dockerfile").write_text(DOCKERFILE)
    (devc / "init-firewall.sh").write_text(FIREWALL_SH)
    os.chmod(devc / "init-firewall.sh", 0o755)
    (devc / "start-kasmvnc.sh").write_text(KASMVNC_SH)
    os.chmod(devc / "start-kasmvnc.sh", 0o755)
    (devc / "devcontainer.json").write_text(DEVCONTAINER_JSON)

    ok(".devcontainer created")
    return devc


# ─── Image build ──────────────────────────────────────────

def ensure_image(project_dir: Path) -> str:
    """Build the image if it does not exist. Returns the image name."""
    img = image_name()
    r = docker("image", "inspect", img, capture_output=True)
    if r.returncode == 0:
        return img

    devc = ensure_devcontainer(project_dir)
    info(f"Building image: {img}")
    docker_check("build", "-t", img, "-f", str(devc / "Dockerfile"), str(devc))
    ok(f"Build complete: {img}")
    return img


# ─── Commands ─────────────────────────────────────────────

def cmd_run(project_path: str = ".", shell_mode: bool = False):
    project_dir = Path(project_path).resolve()
    if not project_dir.is_dir():
        err(f"Path not found: {project_dir}")
        sys.exit(1)

    name = container_name(project_dir)

    if shell_mode:
        exec_cmd = ["/usr/bin/zsh"]
    else:
        exec_cmd = ["tmux", "new-session", "-A", "-s", "claude",
                     "claude --dangerously-skip-permissions"]

    # Attach if already running
    if name in running_containers():
        warn(f"Already running: {name} -> attaching")
        docker("exec", *tty_flags(), name, *exec_cmd)
        return

    ensure_devcontainer(project_dir)
    img = ensure_image(project_dir)
    docker("rm", "-f", name, capture_output=True)

    # Create downloads dir on host
    downloads_dir = project_dir / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    creds_json, oauth_token = get_host_credentials()

    cmd = [
        "docker", "run", "-d",
        "--name", name,
        "--label", f"{LABEL}=true",
        # VNC port
        "-p", "6901:6901",
        # Chrome DevTools Protocol port
        "-p", "9222:9223",
        # Shared memory for Chromium
        "--shm-size", "2g",
        # Volumes
        "-v", f"{project_dir}:/workspace",
        "-v", f"agent-browser-config-{name}:/home/node/.claude",
        "-v", f"agent-browser-history-{name}:/commandhistory",
        "-v", f"{downloads_dir}:/downloads",
        # Security hardening
        "--cap-drop", "ALL",
        "--cap-add", "NET_ADMIN",
        "--cap-add", "SETUID",
        "--cap-add", "SETGID",
        "--security-opt", "no-new-privileges:true",
        "--read-only",
        # Writable tmpfs
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=500m",
        "--tmpfs", "/run:rw,noexec,nosuid,nodev,size=10m",
        "--tmpfs", "/home/node:rw,nosuid,nodev,size=1g,uid=1000,gid=1000",
        # Resource limits
        "--memory", "4g",
        "--memory-swap", "4g",
        "--pids-limit", "500",
        # Environment
        "-e", "CLAUDE_CONFIG_DIR=/home/node/.claude",
        "-e", "NODE_OPTIONS=--max-old-space-size=4096",
        "-e", "DISPLAY=:1",
        "-e", "VNC_PORT=6901",
        "-e", "VNC_RESOLUTION=1920x1080",
        "-e", "CHROME_ALLOW_ALL=1",
        "-e", "PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright",
    ]

    if api_key:
        cmd += ["-e", f"ANTHROPIC_API_KEY={api_key}"]
    elif oauth_token:
        cmd += ["-e", f"CLAUDE_CODE_OAUTH_TOKEN={oauth_token}"]

    cmd += [
        "-u", "root",  # Start as root for firewall (no-new-privileges blocks sudo)
        img,
        "/usr/bin/bash", "-c",
        "/usr/local/bin/init-firewall.sh; "
        "su -s /usr/bin/bash node -c '/usr/local/bin/start-kasmvnc.sh'; "
        "exec su -s /usr/bin/bash node -c '"
        "tmux new-session -d -s claude \"claude --dangerously-skip-permissions\"; "
        "exec sleep infinity'",
    ]

    docker_check(*cmd[1:], capture_output=True)

    if creds_json:
        inject_credentials_file(name, creds_json)
        ok("Host credentials injected")

    print()
    ok(f"Started: {name}")
    print(f"  Project:   {project_dir} -> /workspace")
    print(f"  Downloads: {downloads_dir}")
    print()

    # Read VNC info from container logs
    time.sleep(3)
    r = docker("logs", name, capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "KasmVNC" in line or "===" in line or "URL:" in line or "CDP:" in line or "Chrome launched" in line or "authentication" in line:
            print(f"  {line.strip()}")
    print()
    print(f"  Shell:  python3 browser.py shell {name}")
    print(f"  Stop:   python3 browser.py stop {name}")
    print()

    docker("exec", *tty_flags(), name, *exec_cmd)


def cmd_list():
    r = docker(
        "ps", "--filter", f"label={LABEL}=true",
        "--format", "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}",
        capture_output=True, text=True,
    )
    out = r.stdout.strip()
    if not out or out.count("\n") == 0:
        print("No running agent-browser containers")
        return
    print(out)


def cmd_shell(name: str = ""):
    containers = running_containers()
    if not name:
        if len(containers) == 0:
            err("No running containers")
            sys.exit(1)
        elif len(containers) == 1:
            name = containers[0]
        else:
            err("Multiple containers running -- specify a name:")
            for c in containers:
                print(f"  {c}")
            sys.exit(1)
    docker("exec", *tty_flags(), name, "/usr/bin/zsh")


def cmd_stop(name: str = ""):
    if not name:
        containers = running_containers()
        if not containers:
            print("No containers to stop")
            return
        err("Specify a name:")
        for c in containers:
            print(f"  {c}")
        sys.exit(1)
    docker("stop", name, capture_output=True)
    docker("rm", name, capture_output=True)
    ok(f"Stopped and removed: {name}")


def cmd_stopall():
    containers = running_containers()
    if not containers:
        print("No containers to stop")
        return
    for name in containers:
        docker("stop", name, capture_output=True)
        docker("rm", name, capture_output=True)
        ok(f"Stopped: {name}")


def cmd_rm(name: str = ""):
    """Remove a stopped container + its volumes."""
    if not name:
        r = docker("ps", "-a", "--filter", f"label={LABEL}=true",
                   "--format", "{{.Names}}\t{{.Status}}",
                   capture_output=True, text=True)
        lines = [l for l in r.stdout.strip().splitlines() if l]
        if not lines:
            print("No containers to remove")
            return
        err("Specify a name:")
        for l in lines:
            print(f"  {l}")
        sys.exit(1)

    docker("stop", name, capture_output=True)
    docker("rm", "-f", name, capture_output=True)
    # Remove associated volumes
    for prefix in ("agent-browser-config-", "agent-browser-history-"):
        docker("volume", "rm", f"{prefix}{name}", capture_output=True)
    ok(f"Removed: {name} (including volumes)")


def cmd_clean():
    """Remove all agent-browser containers + volumes + images."""
    r = docker("ps", "-a", "--filter", f"label={LABEL}=true",
               "--format", "{{.Names}}", capture_output=True, text=True)
    containers = [n for n in r.stdout.strip().splitlines() if n]

    if not containers:
        print("No containers to clean")
    else:
        for name in containers:
            docker("stop", name, capture_output=True)
            docker("rm", "-f", name, capture_output=True)
            for prefix in ("agent-browser-config-", "agent-browser-history-"):
                docker("volume", "rm", f"{prefix}{name}", capture_output=True)
            ok(f"Removed: {name}")

    # Remove images
    img = image_name()
    r = docker("image", "inspect", img, capture_output=True)
    if r.returncode == 0:
        docker("rmi", img, capture_output=True)
        ok(f"Image removed: {img}")

    ok("Cleanup complete")


def cmd_build(project_path: str = ".") -> str:
    project_dir = Path(project_path).resolve()
    devc = ensure_devcontainer(project_dir)
    img = image_name()
    info(f"Building image: {img}")
    docker_check("build", "-t", img, "-f", str(devc / "Dockerfile"), str(devc))
    ok(f"Build complete: {img}")
    return img


def cmd_push():
    img = image_name()
    if img == DEFAULT_IMAGE:
        err("Set BROWSER_IMAGE to a registry path")
        print("  e.g.: export BROWSER_IMAGE=ghcr.io/your-org/agent-browser-sandbox")
        sys.exit(1)
    cmd_build()
    info(f"Pushing: {img}")
    docker_check("push", img)
    ok(f"Done -- teammates: BROWSER_IMAGE={img} python3 browser.py pull && python3 browser.py run .")


def cmd_pull():
    img = image_name()
    info(f"Pulling: {img}")
    docker_check("pull", img)
    ok("Done")


def cmd_help():
    print(textwrap.dedent("""\
        Agent Browser Container Manager

        Usage: python3 browser.py <command> [args]

        Run:
          run [path]      Start Claude with browser in project (default: current dir)
          run -s [path]   Connect with zsh shell (--shell / -s)
          list (ls)       List running containers
          shell (sh)      Attach zsh to a running container (persists after exit)

        Stop/Remove:
          stop <name>     Stop + remove container
          stopall         Stop + remove all containers
          rm <name>       Remove container + volumes
          clean           Full cleanup: all containers + volumes + images

        Build/Share:
          build [path]    Build image only
          push            Push to registry (team sharing)
          pull            Pull from registry

        Container name: {folder}-{path_hash}-browser
          e.g.) ~/work/myproject -> myproject-a3f1c-browser

        Environment variables:
          ANTHROPIC_API_KEY   Claude API key
          BROWSER_IMAGE       Image name (registry path for team sharing)
          CHROME_ALLOW_ALL    Set to 1 to allow all HTTP/HTTPS (default: 1)
    """))


# ─── Main ─────────────────────────────────────────────────

def _dispatch_run(rest: list[str]):
    """Parse --shell/-s flag and dispatch to cmd_run."""
    shell_mode = "--shell" in rest or "-s" in rest
    path_args = [a for a in rest if a not in ("--shell", "-s")]
    project_path = path_args[0] if path_args else "."
    cmd_run(project_path, shell_mode=shell_mode)


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "run"
    rest = args[1:]

    commands = {
        "run":     lambda: _dispatch_run(rest),
        "list":    cmd_list,
        "ls":      cmd_list,
        "shell":   lambda: cmd_shell(rest[0] if rest else ""),
        "sh":      lambda: cmd_shell(rest[0] if rest else ""),
        "stop":    lambda: cmd_stop(rest[0] if rest else ""),
        "stopall": cmd_stopall,
        "kill":    lambda: cmd_stop(rest[0] if rest else ""),
        "killall": cmd_stopall,
        "rm":      lambda: cmd_rm(rest[0] if rest else ""),
        "remove":  lambda: cmd_rm(rest[0] if rest else ""),
        "clean":   cmd_clean,
        "build":   lambda: cmd_build(rest[0] if rest else "."),
        "push":    cmd_push,
        "pull":    cmd_pull,
        "help":    cmd_help,
        "-h":      cmd_help,
        "--help":  cmd_help,
    }

    fn = commands.get(cmd)
    if fn:
        fn()
    else:
        # If the argument is a path, treat it as "run"
        if Path(cmd).is_dir():
            _dispatch_run([cmd] + rest)
        else:
            err(f"Unknown command: {cmd}")
            cmd_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
