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

# 설정 (install.py와 동일)
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


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}{msg}{Colors.NC}")


def remove_plugin_directory():
    """플러그인 디렉토리 삭제"""
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
        print_success("플러그인 디렉토리 삭제 완료")
    else:
        print_warning("플러그인 디렉토리가 없습니다.")


def remove_from_known_marketplaces():
    """known_marketplaces.json에서 마켓플레이스 제거"""
    if not KNOWN_MARKETPLACES_FILE.exists():
        return

    try:
        with open(KNOWN_MARKETPLACES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if MARKETPLACE_NAME in data:
            del data[MARKETPLACE_NAME]
            with open(KNOWN_MARKETPLACES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print_success("마켓플레이스 등록 해제 완료")
    except (json.JSONDecodeError, KeyError):
        print_warning("known_marketplaces.json 파싱 실패")


def remove_from_installed_plugins():
    """installed_plugins.json에서 플러그인 제거"""
    if not INSTALLED_PLUGINS_FILE.exists():
        return

    try:
        with open(INSTALLED_PLUGINS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "plugins" not in data:
            return

        removed = False
        for plugin in PLUGINS:
            plugin_key = f"{plugin}@{MARKETPLACE_NAME}"
            if plugin_key in data["plugins"]:
                del data["plugins"][plugin_key]
                removed = True

        if removed:
            with open(INSTALLED_PLUGINS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print_success("설치된 플러그인 목록에서 제거 완료")
    except (json.JSONDecodeError, KeyError):
        print_warning("installed_plugins.json 파싱 실패")


def remove_from_settings():
    """settings.json에서 플러그인 비활성화"""
    if not SETTINGS_FILE.exists():
        return

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)

        modified = False

        # enabledPlugins에서 제거
        if "enabledPlugins" in settings:
            for plugin in PLUGINS:
                plugin_key = f"{plugin}@{MARKETPLACE_NAME}"
                if plugin_key in settings["enabledPlugins"]:
                    del settings["enabledPlugins"][plugin_key]
                    modified = True

        # extraKnownMarketplaces에서 제거 (이전 버전 호환)
        if "extraKnownMarketplaces" in settings:
            if MARKETPLACE_NAME in settings["extraKnownMarketplaces"]:
                del settings["extraKnownMarketplaces"][MARKETPLACE_NAME]
                modified = True

        if modified:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print_success("플러그인 비활성화 완료")
    except (json.JSONDecodeError, KeyError):
        print_warning("settings.json 파싱 실패")


def main():
    print(f"{Colors.BLUE}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║  Karohani Claude Code Plugin Uninstaller   ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════╝{Colors.NC}")
    print()

    remove_plugin_directory()
    remove_from_known_marketplaces()
    remove_from_installed_plugins()
    remove_from_settings()

    print()
    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  제거 완료!                                 ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print("Claude Code를 재시작하세요.")


if __name__ == "__main__":
    main()
