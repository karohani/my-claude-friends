#!/usr/bin/env python3
"""
Karohani Claude Code Plugin - 제거 스크립트

사용법:
    python scripts/uninstall.py
"""

import json
import shutil
import sys
from pathlib import Path

INSTALL_DIR = Path.home() / ".claude" / "plugins" / "karohani-claude-code-plugin"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"


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


def main():
    print(f"{Colors.BLUE}Karohani Claude Code Plugin 제거 중...{Colors.NC}")
    print()

    # 1. 플러그인 디렉토리 삭제
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
        print(f"{Colors.GREEN}✓ 플러그인 디렉토리 삭제 완료{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}플러그인 디렉토리가 없습니다.{Colors.NC}")

    # 2. settings.json에서 마켓플레이스 제거
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            if "extraKnownMarketplaces" in settings:
                if "karohani-plugins" in settings["extraKnownMarketplaces"]:
                    del settings["extraKnownMarketplaces"]["karohani-plugins"]

                    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                        json.dump(settings, f, indent=2, ensure_ascii=False)

                    print(f"{Colors.GREEN}✓ 마켓플레이스 등록 해제 완료{Colors.NC}")
                else:
                    print(f"{Colors.YELLOW}마켓플레이스 등록이 없습니다.{Colors.NC}")
        except (json.JSONDecodeError, KeyError):
            print(f"{Colors.YELLOW}settings.json 파싱 실패{Colors.NC}")

    print()
    print(f"{Colors.GREEN}제거 완료!{Colors.NC}")
    print("Claude Code를 재시작하세요.")


if __name__ == "__main__":
    main()
