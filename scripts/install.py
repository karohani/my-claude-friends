#!/usr/bin/env python3
"""
Karohani Claude Code Plugin - 설치 스크립트

사용법:
    python scripts/install.py
    또는
    curl -fsSL https://raw.githubusercontent.com/jay/my-karohani-claude-code-plugin/main/scripts/install.py | python3
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 설정
REPO_URL = "https://github.com/jay/my-karohani-claude-code-plugin.git"
INSTALL_DIR = Path.home() / ".claude" / "plugins" / "karohani-claude-code-plugin"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# 색상 (터미널 지원 시)
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color

    @classmethod
    def disable(cls):
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ""


# Windows에서는 색상 비활성화
if sys.platform == "win32":
    Colors.disable()


def print_header():
    print(f"{Colors.BLUE}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║  Karohani Claude Code Plugin Installer     ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════╝{Colors.NC}")
    print()


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_info(msg: str):
    print(f"{Colors.BLUE}{msg}{Colors.NC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}{msg}{Colors.NC}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """명령어 실행"""
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def check_git() -> bool:
    """Git 설치 확인"""
    return shutil.which("git") is not None


def check_uv() -> bool:
    """uv 설치 확인"""
    return shutil.which("uv") is not None


def clone_or_update_repo():
    """레포지토리 클론 또는 업데이트"""
    if INSTALL_DIR.exists():
        print_info("기존 설치가 발견되었습니다. 업데이트합니다...")
        if run_command(["git", "pull", "origin", "main"], cwd=INSTALL_DIR):
            print_success("업데이트 완료")
        else:
            print_warning("업데이트 실패. 기존 설치를 사용합니다.")
    else:
        print_info("플러그인 다운로드 중...")
        INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)
        if run_command(["git", "clone", "--depth", "1", REPO_URL, str(INSTALL_DIR)]):
            print_success("다운로드 완료")
        else:
            print_error("다운로드 실패")
            sys.exit(1)


def install_mcp_dependencies():
    """MCP 서버 의존성 설치"""
    print_info("MCP 서버 의존성 설치 중...")
    mcp_dir = INSTALL_DIR / "plugins" / "hello-mcp"

    if check_uv():
        run_command(["uv", "venv"], cwd=mcp_dir)
        if run_command(["uv", "pip", "install", "-e", "."], cwd=mcp_dir):
            print_success("MCP 서버 설정 완료")
        else:
            print_warning("MCP 서버 설치 실패 (나중에 수동 설치 가능)")
    else:
        print_warning("uv가 없습니다. MCP 서버는 수동 설치 필요:")
        print(f"    cd {mcp_dir} && pip install -e .")


def update_settings():
    """Claude Code 설정 업데이트"""
    print_info("Claude Code 설정 업데이트 중...")

    # settings.json 읽기 또는 생성
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        settings = {}

    # extraKnownMarketplaces 추가
    if "extraKnownMarketplaces" not in settings:
        settings["extraKnownMarketplaces"] = {}

    settings["extraKnownMarketplaces"]["karohani-plugins"] = {
        "source": {
            "source": "directory",
            "path": str(INSTALL_DIR)
        }
    }

    # 저장
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print_success("마켓플레이스 등록 완료")


def print_completion():
    """설치 완료 메시지"""
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  설치 완료!                                 ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"설치 위치: {Colors.BLUE}{INSTALL_DIR}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}다음 단계:{Colors.NC}")
    print("  1. Claude Code 재시작")
    print("  2. 플러그인 설치:")
    print("     /plugin install hello-skill")
    print("     /plugin install hello-mcp")
    print("     /plugin install session-wrap")
    print()
    print(f"{Colors.YELLOW}또는 직접 사용:{Colors.NC}")
    print("  /wrap              # 세션 마무리")
    print("  /hello             # 인사 스킬")
    print()


def main():
    print_header()

    # Git 확인
    if not check_git():
        print_error("Git이 설치되어 있지 않습니다.")
        print(f"Git을 설치하거나 수동으로 다운로드하세요: {REPO_URL}")
        sys.exit(1)

    # 설치 진행
    clone_or_update_repo()
    install_mcp_dependencies()
    update_settings()
    print_completion()


if __name__ == "__main__":
    main()
