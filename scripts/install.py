#!/usr/bin/env python3
"""
Karohani Claude Code Plugin - 설치 스크립트

사용법:
    python scripts/install.py              # 원격 설치 (GitHub에서)
    python scripts/install.py --local      # 로컬 설치 (현재 디렉토리에서)
    curl -fsSL https://raw.githubusercontent.com/jay/my-karohani-claude-code-plugin/main/scripts/install.py | python3
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# 설정
REPO_URL = "https://github.com/jay/my-karohani-claude-code-plugin.git"
MARKETPLACE_NAME = "karohani-plugins"
INSTALL_DIR = Path.home() / ".claude" / "plugins" / "marketplaces" / MARKETPLACE_NAME
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"
KNOWN_MARKETPLACES_FILE = Path.home() / ".claude" / "plugins" / "known_marketplaces.json"
INSTALLED_PLUGINS_FILE = Path.home() / ".claude" / "plugins" / "installed_plugins.json"

# 플러그인 목록
PLUGINS = ["hello-skill", "session-wrap", "youtube-digest"]


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"

    @classmethod
    def disable(cls):
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ""


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
    try:
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_git() -> bool:
    return shutil.which("git") is not None




def get_script_dir() -> Path:
    """스크립트가 있는 디렉토리의 부모 (프로젝트 루트) 반환"""
    return Path(__file__).parent.parent.resolve()


def install_from_local(source_dir: Path):
    """로컬 디렉토리에서 설치"""
    print_info(f"로컬 설치: {source_dir}")

    if INSTALL_DIR.exists():
        print_info("기존 설치 삭제 중...")
        shutil.rmtree(INSTALL_DIR)

    print_info("파일 복사 중...")
    INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)

    # .git, .venv, __pycache__ 등 제외하고 복사
    def ignore_patterns(directory, files):
        return [f for f in files if f in [".git", ".venv", "__pycache__", ".egg-info", "*.pyc"]]

    shutil.copytree(source_dir, INSTALL_DIR, ignore=ignore_patterns)
    print_success("파일 복사 완료")


def install_from_remote():
    """GitHub에서 클론하여 설치"""
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
            print_warning("GitHub에 레포가 없을 수 있습니다. --local 옵션을 사용하세요.")
            sys.exit(1)


def check_yt_dlp():
    """yt-dlp 설치 확인"""
    if shutil.which("yt-dlp"):
        print_success("yt-dlp 설치됨")
    else:
        print_warning("yt-dlp가 설치되어 있지 않습니다.")
        print("    /youtube 스킬을 사용하려면: brew install yt-dlp")


def update_known_marketplaces():
    """마켓플레이스 등록"""
    print_info("마켓플레이스 등록 중...")

    if KNOWN_MARKETPLACES_FILE.exists():
        with open(KNOWN_MARKETPLACES_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        KNOWN_MARKETPLACES_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {}

    data[MARKETPLACE_NAME] = {
        "source": {
            "source": "directory",
            "path": str(INSTALL_DIR)
        },
        "installLocation": str(INSTALL_DIR),
        "lastUpdated": __import__("datetime").datetime.now().isoformat() + "Z"
    }

    with open(KNOWN_MARKETPLACES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print_success("마켓플레이스 등록 완료")


def update_installed_plugins():
    """플러그인 설치 등록"""
    print_info("플러그인 설치 등록 중...")

    if INSTALLED_PLUGINS_FILE.exists():
        with open(INSTALLED_PLUGINS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"version": 2, "plugins": {}}
    else:
        INSTALLED_PLUGINS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 2, "plugins": {}}

    if "plugins" not in data:
        data["plugins"] = {}

    now = __import__("datetime").datetime.now().isoformat() + "Z"

    for plugin in PLUGINS:
        plugin_key = f"{plugin}@{MARKETPLACE_NAME}"
        plugin_path = INSTALL_DIR / "plugins" / plugin

        data["plugins"][plugin_key] = [{
            "scope": "user",
            "installPath": str(plugin_path),
            "version": "1.0.0",
            "installedAt": now,
            "lastUpdated": now
        }]

    with open(INSTALLED_PLUGINS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print_success("플러그인 설치 등록 완료")


def update_settings():
    """Claude Code 설정 업데이트 - 플러그인 활성화"""
    print_info("플러그인 활성화 중...")

    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}
    else:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        settings = {}

    if "enabledPlugins" not in settings:
        settings["enabledPlugins"] = {}

    for plugin in PLUGINS:
        settings["enabledPlugins"][f"{plugin}@{MARKETPLACE_NAME}"] = True

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    print_success("플러그인 활성화 완료")


def print_completion():
    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  설치 완료!                                 ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"설치 위치: {Colors.BLUE}{INSTALL_DIR}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}다음 단계:{Colors.NC}")
    print("  1. Claude Code 재시작")
    print("  2. 슬래시 커맨드 사용:")
    print("     /hello             # 인사 스킬")
    print("     /wrap              # 세션 마무리")
    print("     /youtube [URL]     # YouTube 요약 (yt-dlp 필요)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Karohani Claude Code Plugin 설치")
    parser.add_argument("--local", action="store_true", help="현재 디렉토리에서 로컬 설치")
    args = parser.parse_args()

    print_header()

    if args.local:
        # 로컬 설치
        source_dir = get_script_dir()
        if not (source_dir / ".claude-plugin").exists():
            print_error("플러그인 디렉토리가 아닙니다.")
            print(f"현재 위치: {source_dir}")
            sys.exit(1)
        install_from_local(source_dir)
    else:
        # 원격 설치
        if not check_git():
            print_error("Git이 설치되어 있지 않습니다.")
            print(f"Git을 설치하거나 --local 옵션을 사용하세요.")
            sys.exit(1)
        install_from_remote()

    check_yt_dlp()
    update_known_marketplaces()
    update_installed_plugins()
    update_settings()
    print_completion()


if __name__ == "__main__":
    main()
