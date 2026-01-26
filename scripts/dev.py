#!/usr/bin/env python3
"""
Karohani Claude Code Plugin - 개발 모드 설정

현재 디렉토리를 직접 마켓플레이스로 등록하여
파일 수정 시 바로 반영되도록 합니다.

사용법:
    python scripts/dev.py          # 개발 모드 활성화
    python scripts/dev.py --off    # 개발 모드 비활성화
"""

import argparse
import json
import sys
from pathlib import Path


SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# 원격 마켓플레이스 이름들 (충돌 방지용)
REMOTE_MARKETPLACES = [
    "karohani/my-claude-friends",
    "karohani-plugins",
]

# 플러그인 목록
PLUGINS = ["hello-skill", "session-wrap", "youtube-digest", "voice", "tdd"]


class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def get_project_dir() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent.resolve()


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_settings(settings: dict):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def enable_dev_mode():
    """개발 모드 활성화 - 현재 디렉토리를 마켓플레이스로 등록"""
    project_dir = get_project_dir()
    settings = load_settings()

    if "enabledPlugins" not in settings:
        settings["enabledPlugins"] = {}

    # 원격 마켓플레이스 플러그인 비활성화
    disabled_remotes = []
    for plugin in PLUGINS:
        for marketplace in REMOTE_MARKETPLACES:
            remote_key = f"{plugin}@{marketplace}"
            if settings["enabledPlugins"].get(remote_key):
                settings["enabledPlugins"][remote_key] = False
                disabled_remotes.append((plugin, marketplace))

    if "extraKnownMarketplaces" not in settings:
        settings["extraKnownMarketplaces"] = {}

    # 개발 디렉토리 직접 등록 (복사 아님)
    settings["extraKnownMarketplaces"]["karohani-dev"] = {
        "source": {
            "source": "directory",
            "path": str(project_dir)
        }
    }

    # 개발 모드 플러그인 활성화
    for plugin in PLUGINS:
        settings["enabledPlugins"][f"{plugin}@karohani-dev"] = True

    save_settings(settings)

    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  개발 모드 활성화!                          ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"프로젝트: {Colors.BLUE}{project_dir}{Colors.NC}")
    print()
    if disabled_remotes:
        print(f"{Colors.YELLOW}원격 플러그인 비활성화:{Colors.NC}")
        for plugin, marketplace in disabled_remotes:
            print(f"  - {plugin}@{marketplace}")
        print()
    print(f"{Colors.YELLOW}다음 단계:{Colors.NC}")
    print("  1. Claude Code 재시작 (/exit 후 다시 실행)")
    print("  2. 슬래시 커맨드 사용:")
    print("     /hello             # 인사 스킬")
    print("     /wrap              # 세션 마무리")
    print("     /youtube [URL]     # YouTube 요약 (yt-dlp 필요)")
    print("     /voice             # 음성 입출력 (sox, whisper-cpp 필요)")
    print("     /tdd init          # TDD 스킬 생성")
    print()
    print(f"{Colors.YELLOW}파일 수정 시:{Colors.NC}")
    print("  - SKILL.md, agents/*.md 등 수정하면 바로 반영")
    print("  - 세션 재시작 필요 없음 (대부분의 경우)")
    print()


def disable_dev_mode(restore_remote: bool = True):
    """개발 모드 비활성화"""
    settings = load_settings()

    if "extraKnownMarketplaces" in settings:
        settings["extraKnownMarketplaces"].pop("karohani-dev", None)

    if "enabledPlugins" not in settings:
        settings["enabledPlugins"] = {}

    # 개발 모드 플러그인 비활성화
    for plugin in PLUGINS:
        settings["enabledPlugins"].pop(f"{plugin}@karohani-dev", None)

    # 원격 마켓플레이스 플러그인 복원
    restored = []
    if restore_remote:
        for plugin in PLUGINS:
            for marketplace in REMOTE_MARKETPLACES:
                remote_key = f"{plugin}@{marketplace}"
                if remote_key in settings["enabledPlugins"]:
                    settings["enabledPlugins"][remote_key] = True
                    restored.append((plugin, marketplace))

    save_settings(settings)

    print(f"{Colors.GREEN}개발 모드 비활성화 완료{Colors.NC}")
    if restored:
        print(f"\n{Colors.YELLOW}원격 플러그인 복원:{Colors.NC}")
        for plugin, marketplace in restored:
            print(f"  - {plugin}@{marketplace}")
    print("\nClaude Code를 재시작하세요.")


def main():
    parser = argparse.ArgumentParser(description="개발 모드 설정")
    parser.add_argument("--off", action="store_true", help="개발 모드 비활성화")
    parser.add_argument("--no-restore", action="store_true", help="원격 플러그인 복원 안함 (--off와 함께 사용)")
    args = parser.parse_args()

    if args.off:
        disable_dev_mode(restore_remote=not args.no_restore)
    else:
        enable_dev_mode()


if __name__ == "__main__":
    main()
