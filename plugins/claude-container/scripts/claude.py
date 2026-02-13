#!/usr/bin/env python3
"""
Claude Code Container Manager

프로젝트 폴더에서 이 스크립트 하나만 실행하면:
  1. .devcontainer/ 폴더 + 필요한 파일 자동 생성
  2. Docker 이미지 빌드
  3. 컨테이너 실행 → Claude Code 자동 시작

컨테이너명: {폴더명}-{경로hash5자}  예) imoogi-a3f1c

사용법:
  python3 claude.py                    # 현재 폴더에서 Claude 시작
  python3 claude.py run ~/project      # 특정 폴더에서 Claude 시작
  python3 claude.py run -s              # zsh 셸로 접속 (--shell)
  python3 claude.py list               # 실행 중 목록
  python3 claude.py shell [이름]       # 접속
  python3 claude.py stop [이름]        # 정지
  python3 claude.py stopall            # 전체 정지
  python3 claude.py rm <이름>          # 컨테이너 + 볼륨 제거
  python3 claude.py clean              # 전체 정리 (컨테이너+볼륨+이미지)
  python3 claude.py push               # 이미지 레지스트리 푸시
  python3 claude.py pull               # 이미지 풀
"""

import json
import os
import platform
import re
import subprocess
import sys
import textwrap
from pathlib import Path

# ─── 설정 ───────────────────────────────────────────────────
LABEL = "claude-dev"
DEFAULT_IMAGE = "claude-code-sandbox"

# ─── 임베디드 파일들 ────────────────────────────────────────

DOCKERFILE = textwrap.dedent("""\
    FROM node:24-bookworm-slim

    ARG CLAUDE_CODE_VERSION=latest

    RUN apt-get update && apt-get install -y --no-install-recommends \\
        git curl sudo ca-certificates \\
        zsh fzf ripgrep jq tmux \\
        iptables iproute2 dnsutils \\
        locales \\
        && rm -rf /var/lib/apt/lists/*

    RUN sed -i '/ko_KR.UTF-8/s/^# //' /etc/locale.gen && locale-gen
    ENV LANG=ko_KR.UTF-8 LC_ALL=ko_KR.UTF-8

    RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

    COPY init-firewall.sh /usr/local/bin/
    USER root
    RUN chmod +x /usr/local/bin/init-firewall.sh && \\
        echo "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/node-firewall && \\
        chmod 0440 /etc/sudoers.d/node-firewall

    RUN mkdir -p /commandhistory && chown node:node /commandhistory
    RUN chsh -s /usr/bin/zsh node

    RUN su - node -c 'echo "HISTFILE=/commandhistory/.zsh_history\\nHISTSIZE=10000\\nSAVEHIST=10000\\nsetopt appendhistory\\nautoload -Uz compinit && compinit" > ~/.zshrc'

    USER node
    WORKDIR /workspace
""")

FIREWALL_SH = textwrap.dedent("""\
    #!/usr/bin/env bash
    set -uo pipefail

    echo "🔒 Initializing firewall..."

    if command -v iptables-legacy &>/dev/null; then
        IPT="iptables-legacy"
    else
        IPT="iptables"
    fi

    if ! $IPT -L -n &>/dev/null 2>&1; then
        echo "⚠️  iptables 권한 없음 — 방화벽 건너뜀 (컨테이너 격리로 보호됨)"
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
        for ip in $(dig +short "$domain" A 2>/dev/null | grep -E '^[0-9]+\\.' || true); do
            $IPT -A OUTPUT -d "$ip" -j ACCEPT 2>/dev/null || true
        done
    done

    echo "✅ Firewall ready (${#ALLOWED_DOMAINS[@]} domains whitelisted)"
""")

DEVCONTAINER_JSON = textwrap.dedent("""\
    {
      "name": "Claude Code Sandbox",
      "build": {
        "dockerfile": "Dockerfile",
        "args": { "CLAUDE_CODE_VERSION": "latest" }
      },
      "customizations": {
        "vscode": {
          "extensions": [
            "anthropic.claude-code",
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
            "eamodio.gitlens"
          ],
          "settings": {
            "editor.formatOnSave": true,
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "terminal.integrated.defaultProfile.linux": "zsh"
          }
        }
      },
      "remoteUser": "node",
      "mounts": [
        "source=claude-code-bashhistory-${devcontainerId},target=/commandhistory,type=volume",
        "source=claude-code-config-${devcontainerId},target=/home/node/.claude,type=volume"
      ],
      "containerEnv": {
        "NODE_OPTIONS": "--max-old-space-size=4096",
        "CLAUDE_CONFIG_DIR": "/home/node/.claude"
      },
      "postStartCommand": "sudo /usr/local/bin/init-firewall.sh",
      "postCreateCommand": "echo 'export HISTFILE=/commandhistory/.bash_history' >> ~/.bashrc || true"
    }
""")


# ─── 유틸 ───────────────────────────────────────────────────

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


def run_check(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kwargs)


def docker(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return run(["docker", *args], **kwargs)


def docker_check(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return run_check(["docker", *args], **kwargs)


def image_name() -> str:
    return os.environ.get("CLAUDE_IMAGE", DEFAULT_IMAGE)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")


def path_hash(p: Path) -> str:
    import hashlib
    return hashlib.sha256(str(p).encode()).hexdigest()[:5]


def container_name(project_dir: Path) -> str:
    return f"{slugify(project_dir.name)}-{path_hash(project_dir)}"


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
    """stdin이 TTY면 -it, 아니면 -i만"""
    return ["-it"] if sys.stdin.isatty() else ["-i"]


def get_host_credentials() -> str | None:
    """macOS Keychain에서 Claude Code OAuth 자격증명을 추출"""
    if platform.system() != "Darwin":
        return None
    try:
        r = subprocess.run(
            ["security", "find-generic-password",
             "-s", "Claude Code-credentials", "-w"],
            capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            # JSON 형식 유효성 확인
            json.loads(r.stdout.strip())
            return r.stdout.strip()
    except (subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None


def inject_credentials(container_name: str):
    """호스트 OAuth 자격증명을 컨테이너에 주입"""
    creds = get_host_credentials()
    if not creds:
        return
    # 볼륨 소유권 수정 (root로 생성됨)
    docker("exec", "-u", "root", container_name, "chown", "node:node",
           "/home/node/.claude", capture_output=True)
    # stdin으로 파이프하여 쉘 인용부호 문제 회피
    # Claude Code는 .credentials.json (dot prefix) 파일에서 인증 정보를 읽음
    run(["docker", "exec", "-i", container_name,
         "sh", "-c", "cat > /home/node/.claude/.credentials.json"],
        input=creds, text=True, capture_output=True)
    docker("exec", "-u", "root", container_name, "sh", "-c",
           "chmod 600 /home/node/.claude/.credentials.json && "
           "chown node:node /home/node/.claude/.credentials.json",
           capture_output=True)
    ok("호스트 인증 정보 주입 완료")


# ─── .devcontainer 생성 ─────────────────────────────────────

def ensure_devcontainer(project_dir: Path) -> Path:
    """프로젝트에 .devcontainer/ 가 없으면 생성"""
    devc = project_dir / ".devcontainer"

    if devc.exists() and (devc / "Dockerfile").exists():
        return devc

    info(f".devcontainer 생성: {devc}")
    devc.mkdir(parents=True, exist_ok=True)

    (devc / "Dockerfile").write_text(DOCKERFILE)
    (devc / "init-firewall.sh").write_text(FIREWALL_SH)
    os.chmod(devc / "init-firewall.sh", 0o755)
    (devc / "devcontainer.json").write_text(DEVCONTAINER_JSON)

    ok(".devcontainer 생성 완료")
    return devc


# ─── 이미지 빌드 ────────────────────────────────────────────

def ensure_image(project_dir: Path):
    """이미지 없으면 빌드"""
    img = image_name()
    r = docker("image", "inspect", img, capture_output=True)
    if r.returncode == 0:
        return

    devc = ensure_devcontainer(project_dir)
    info(f"이미지 빌드: {img}")
    docker_check("build", "-t", img, "-f", str(devc / "Dockerfile"), str(devc))
    ok(f"빌드 완료: {img}")


# ─── 커맨드 ─────────────────────────────────────────────────

def cmd_run(project_path: str = ".", shell_mode: bool = False):
    project_dir = Path(project_path).resolve()
    if not project_dir.is_dir():
        err(f"경로 없음: {project_dir}")
        sys.exit(1)

    name = container_name(project_dir)
    if shell_mode:
        exec_cmd = ["/usr/bin/zsh"]
    else:
        # tmux 세션 안에서 claude 실행 → detach해도 프로세스 유지, 재접속 시 이어서 사용
        exec_cmd = ["tmux", "new-session", "-A", "-s", "claude",
                     "claude --dangerously-skip-permissions"]

    # 이미 실행 중이면 접속
    if name in running_containers():
        warn(f"이미 실행 중: {name} → 접속")
        docker("exec", *tty_flags(), name, *exec_cmd)
        return

    ensure_devcontainer(project_dir)
    ensure_image(project_dir)

    # 정지된 컨테이너 정리
    docker("rm", "-f", name, capture_output=True)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    cmd = [
        "docker", "run", "-d",
        "--name", name,
        "--label", f"{LABEL}=true",
        "--cap-add", "NET_ADMIN",
        "-v", f"{project_dir}:/workspace",
        "-v", f"claude-config-{name}:/home/node/.claude",
        "-v", f"claude-history-{name}:/commandhistory",
        "-e", "CLAUDE_CONFIG_DIR=/home/node/.claude",
        "-e", "NODE_OPTIONS=--max-old-space-size=4096",
    ]

    if api_key:
        cmd += ["-e", f"ANTHROPIC_API_KEY={api_key}"]

    cmd += [
        image_name(),
        "/usr/bin/bash", "-c",
        "sudo /usr/local/bin/init-firewall.sh; "
        "[ -f /home/node/.zshrc ] || printf 'HISTFILE=/commandhistory/.zsh_history\\nHISTSIZE=10000\\nSAVEHIST=10000\\nsetopt appendhistory\\nautoload -Uz compinit && compinit\\n' > /home/node/.zshrc; "
        "exec sleep infinity",
    ]

    docker_check(*cmd[1:], capture_output=True)
    inject_credentials(name)

    print()
    ok(f"시작: \033[32m{name}\033[0m")
    print(f"  프로젝트: {project_dir} → /workspace")
    print()
    print(f"  셸접속: python3 claude.py shell")
    print(f"  zsh모드: python3 claude.py run -s")
    print(f"  정지:   python3 claude.py stop {name}")
    print(f"  exit해도 컨테이너는 계속 실행됩니다")
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
        print("실행 중인 Claude 컨테이너 없음")
        return
    print(out)


def cmd_shell(name: str = ""):
    containers = running_containers()
    if not name:
        if len(containers) == 0:
            err("실행 중인 컨테이너 없음")
            sys.exit(1)
        elif len(containers) == 1:
            name = containers[0]
        else:
            err("여러 컨테이너 실행 중 — 이름을 지정하세요:")
            for c in containers:
                print(f"  {c}")
            sys.exit(1)
    docker("exec", *tty_flags(), name, "/usr/bin/zsh")


def cmd_stop(name: str = ""):
    if not name:
        containers = running_containers()
        if not containers:
            print("정지할 컨테이너 없음")
            return
        err("이름을 지정하세요:")
        for c in containers:
            print(f"  {c}")
        sys.exit(1)
    docker("stop", name, capture_output=True)
    docker("rm", name, capture_output=True)
    ok(f"정지 및 제거: {name}")


def cmd_stopall():
    containers = running_containers()
    if not containers:
        print("정지할 컨테이너 없음")
        return
    for name in containers:
        docker("stop", name, capture_output=True)
        docker("rm", name, capture_output=True)
        ok(f"정지: {name}")


def cmd_rm(name: str = ""):
    """정지된 컨테이너 + 볼륨 제거"""
    if not name:
        # 라벨 기준으로 전체 (실행 중 포함) 조회
        r = docker("ps", "-a", "--filter", f"label={LABEL}=true",
                   "--format", "{{.Names}}\t{{.Status}}",
                   capture_output=True, text=True)
        lines = [l for l in r.stdout.strip().splitlines() if l]
        if not lines:
            print("제거할 컨테이너 없음")
            return
        err("이름을 지정하세요:")
        for l in lines:
            print(f"  {l}")
        sys.exit(1)

    docker("stop", name, capture_output=True)
    docker("rm", "-f", name, capture_output=True)
    # 연관 볼륨도 제거
    for prefix in ("claude-config-", "claude-history-"):
        docker("volume", "rm", f"{prefix}{name}", capture_output=True)
    ok(f"제거: {name} (볼륨 포함)")


def cmd_clean():
    """모든 Claude 컨테이너 + 볼륨 + 이미지 정리"""
    r = docker("ps", "-a", "--filter", f"label={LABEL}=true",
               "--format", "{{.Names}}", capture_output=True, text=True)
    containers = [n for n in r.stdout.strip().splitlines() if n]

    if not containers:
        print("정리할 컨테이너 없음")
    else:
        for name in containers:
            docker("stop", name, capture_output=True)
            docker("rm", "-f", name, capture_output=True)
            for prefix in ("claude-config-", "claude-history-"):
                docker("volume", "rm", f"{prefix}{name}", capture_output=True)
            ok(f"제거: {name}")

    # 이미지 제거
    img = image_name()
    r = docker("image", "inspect", img, capture_output=True)
    if r.returncode == 0:
        docker("rmi", img, capture_output=True)
        ok(f"이미지 제거: {img}")

    ok("정리 완료")


def cmd_build(project_path: str = "."):
    project_dir = Path(project_path).resolve()
    devc = ensure_devcontainer(project_dir)
    img = image_name()
    info(f"이미지 빌드: {img}")
    docker_check("build", "-t", img, "-f", str(devc / "Dockerfile"), str(devc))
    ok(f"빌드 완료: {img}")


def cmd_push():
    img = image_name()
    if img == DEFAULT_IMAGE:
        err("CLAUDE_IMAGE를 레지스트리 경로로 설정하세요")
        print("  예: export CLAUDE_IMAGE=ghcr.io/your-org/claude-code-sandbox")
        sys.exit(1)
    cmd_build()
    info(f"푸시: {img}")
    docker_check("push", img)
    ok("완료 — 팀원: CLAUDE_IMAGE={img} python3 claude.py pull && python3 claude.py run .")


def cmd_pull():
    img = image_name()
    info(f"풀: {img}")
    docker_check("pull", img)
    ok("완료")


def cmd_help():
    print(textwrap.dedent("""\
        Claude Code Container Manager

        사용법: python3 claude.py <command> [args]

        실행:
          run [경로]      프로젝트에서 Claude 시작 (기본: 현재 폴더)
          run -s [경로]   zsh 셸로 접속 (--shell / -s)
          list (ls)       실행 중인 컨테이너 목록
          shell (sh)      실행 중 컨테이너에 zsh 접속 (exit해도 유지)

        정지/제거:
          stop <이름>     컨테이너 정지 + 제거
          stopall         전체 정지 + 제거
          rm <이름>       컨테이너 + 볼륨 제거
          clean           모든 컨테이너 + 볼륨 + 이미지 완전 삭제

        빌드/공유:
          build [경로]    이미지 빌드만
          push            레지스트리에 푸시 (팀 공유)
          pull            레지스트리에서 받기

        컨테이너 이름: {폴더명}-{경로hash5자}
          예) ~/work/imoogi → imoogi-a3f1c

        환경변수:
          ANTHROPIC_API_KEY   Claude API 키
          CLAUDE_IMAGE        이미지 이름 (팀 공유 시 레지스트리 경로)
    """))


# ─── 메인 ───────────────────────────────────────────────────

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
        # 인자가 경로면 run으로 취급
        if Path(cmd).is_dir():
            _dispatch_run([cmd] + rest)
        else:
            err(f"알 수 없는 명령: {cmd}")
            cmd_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
