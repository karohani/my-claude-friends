#!/usr/bin/env python3
"""
Karohani Claude Code Plugin - 개발 모드 설정

공식 --plugin-dir 플래그를 사용하여 플러그인을 로드합니다.
known_marketplaces.json 조작 없이 안정적으로 작동합니다.

사용법:
    python scripts/dev.py              # 기본: alias 방식
    python scripts/dev.py --alias      # ~/.zshrc에 alias 추가
    python scripts/dev.py --wrapper    # ~/.local/bin/claude-dev 생성
    python scripts/dev.py --off        # 모두 제거
    python scripts/dev.py --status     # 현재 상태 확인
    python scripts/dev.py --cleanup    # 이전 방식 설정 정리
"""

import argparse
import json
import os
import stat
import sys
from pathlib import Path


# Claude Code 설정 파일
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"
KNOWN_MARKETPLACES_FILE = Path.home() / ".claude" / "plugins" / "known_marketplaces.json"
BACKUP_FILE = Path.home() / ".claude" / "plugins" / "karohani-dev-backup.json"


# 플러그인 목록
PLUGINS = ["hello-skill", "session-wrap", "youtube-digest", "voice", "tdd", "claude-container"]

# 설정 파일 경로
ZSHRC_FILE = Path.home() / ".zshrc"
BASHRC_FILE = Path.home() / ".bashrc"
WRAPPER_DIR = Path.home() / ".local" / "bin"
WRAPPER_FILE = WRAPPER_DIR / "claude-dev"

# alias 마커 (시작/끝 식별용)
ALIAS_MARKER_START = "# karohani-dev: Claude Code plugin development mode - START"
ALIAS_MARKER_END = "# karohani-dev: Claude Code plugin development mode - END"


class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    RED = "\033[0;31m"
    NC = "\033[0m"


def get_project_dir() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent.resolve()


def get_plugin_dirs() -> list[Path]:
    """플러그인 디렉토리 목록 반환"""
    project_dir = get_project_dir()
    return [project_dir / "plugins" / plugin for plugin in PLUGINS]


def build_plugin_dir_args() -> str:
    """--plugin-dir 인자 문자열 생성"""
    plugin_dirs = get_plugin_dirs()
    args = []
    for plugin_dir in plugin_dirs:
        if plugin_dir.exists():
            args.append(f'--plugin-dir "{plugin_dir}"')
    return " ".join(args)


def get_shell_rc_file() -> Path:
    """현재 셸의 RC 파일 반환"""
    shell = os.environ.get("SHELL", "/bin/zsh")
    if "zsh" in shell:
        return ZSHRC_FILE
    elif "bash" in shell:
        return BASHRC_FILE
    else:
        # 기본값으로 zshrc 사용
        return ZSHRC_FILE


def read_rc_file(rc_file: Path) -> str:
    """RC 파일 읽기"""
    if rc_file.exists():
        return rc_file.read_text(encoding="utf-8")
    return ""


def write_rc_file(rc_file: Path, content: str):
    """RC 파일 쓰기"""
    rc_file.write_text(content, encoding="utf-8")


def has_alias(rc_file: Path) -> bool:
    """alias가 이미 존재하는지 확인"""
    content = read_rc_file(rc_file)
    return ALIAS_MARKER_START in content


def add_alias(rc_file: Path):
    """RC 파일에 alias 추가"""
    content = read_rc_file(rc_file)

    # 이미 존재하면 제거 후 다시 추가
    if has_alias(rc_file):
        content = remove_alias_from_content(content)

    plugin_args = build_plugin_dir_args()
    alias_block = f"""
{ALIAS_MARKER_START}
alias claude='claude {plugin_args}'
{ALIAS_MARKER_END}
"""

    content = content.rstrip() + "\n" + alias_block
    write_rc_file(rc_file, content)


def remove_alias_from_content(content: str) -> str:
    """content에서 alias 블록 제거"""
    lines = content.split("\n")
    result = []
    skip = False

    for line in lines:
        if ALIAS_MARKER_START in line:
            skip = True
            continue
        if ALIAS_MARKER_END in line:
            skip = False
            continue
        if not skip:
            result.append(line)

    # 연속된 빈 줄 정리
    cleaned = "\n".join(result)
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")

    return cleaned


def remove_alias(rc_file: Path):
    """RC 파일에서 alias 제거"""
    if not has_alias(rc_file):
        return False

    content = read_rc_file(rc_file)
    content = remove_alias_from_content(content)
    write_rc_file(rc_file, content)
    return True


def has_wrapper() -> bool:
    """wrapper 스크립트가 존재하는지 확인"""
    return WRAPPER_FILE.exists()


def create_wrapper():
    """wrapper 스크립트 생성"""
    WRAPPER_DIR.mkdir(parents=True, exist_ok=True)

    plugin_args = build_plugin_dir_args()
    wrapper_content = f"""#!/bin/bash
# karohani-dev: Claude Code plugin development mode
exec claude {plugin_args} "$@"
"""

    WRAPPER_FILE.write_text(wrapper_content, encoding="utf-8")
    # 실행 권한 부여
    WRAPPER_FILE.chmod(WRAPPER_FILE.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def remove_wrapper():
    """wrapper 스크립트 제거"""
    if WRAPPER_FILE.exists():
        WRAPPER_FILE.unlink()
        return True
    return False


def check_path_includes_wrapper_dir() -> bool:
    """PATH에 wrapper 디렉토리가 포함되어 있는지 확인"""
    path = os.environ.get("PATH", "")
    return str(WRAPPER_DIR) in path


def enable_alias_mode():
    """alias 모드 활성화"""
    rc_file = get_shell_rc_file()
    project_dir = get_project_dir()

    add_alias(rc_file)

    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  개발 모드 활성화! (alias 방식)            ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"프로젝트: {Colors.BLUE}{project_dir}{Colors.NC}")
    print(f"RC 파일: {Colors.BLUE}{rc_file}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}다음 단계:{Colors.NC}")
    print(f"  1. 새 터미널을 열거나 다음 명령 실행:")
    print(f"     {Colors.BLUE}source {rc_file}{Colors.NC}")
    print()
    print(f"  2. claude 명령 실행:")
    print(f"     {Colors.BLUE}claude{Colors.NC}")
    print()
    print(f"  3. 슬래시 커맨드 테스트:")
    print("     /hello             # 인사 스킬")
    print("     /wrap              # 세션 마무리")
    print("     /youtube [URL]     # YouTube 요약")
    print("     /voice             # 음성 입출력")
    print("     /tdd init          # TDD 스킬 생성")
    print()
    print(f"{Colors.YELLOW}참고:{Colors.NC}")
    print(f"  - 원본 claude 실행: {Colors.BLUE}\\claude{Colors.NC} 또는 {Colors.BLUE}command claude{Colors.NC}")
    print(f"  - 비활성화: {Colors.BLUE}python scripts/dev.py --off{Colors.NC}")
    print()


def enable_wrapper_mode():
    """wrapper 모드 활성화"""
    project_dir = get_project_dir()

    create_wrapper()

    print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║  개발 모드 활성화! (wrapper 방식)          ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"프로젝트: {Colors.BLUE}{project_dir}{Colors.NC}")
    print(f"Wrapper: {Colors.BLUE}{WRAPPER_FILE}{Colors.NC}")
    print()

    if not check_path_includes_wrapper_dir():
        print(f"{Colors.YELLOW}⚠ PATH 설정 필요:{Colors.NC}")
        print(f"  다음을 ~/.zshrc 또는 ~/.bashrc에 추가하세요:")
        print(f"  {Colors.BLUE}export PATH=\"$HOME/.local/bin:$PATH\"{Colors.NC}")
        print()

    print(f"{Colors.YELLOW}사용 방법:{Colors.NC}")
    print(f"  {Colors.BLUE}claude-dev{Colors.NC}  # 개발 모드로 실행")
    print(f"  {Colors.BLUE}claude{Colors.NC}      # 일반 모드로 실행")
    print()
    print(f"  슬래시 커맨드 테스트:")
    print("     /hello             # 인사 스킬")
    print("     /wrap              # 세션 마무리")
    print("     /youtube [URL]     # YouTube 요약")
    print("     /voice             # 음성 입출력")
    print("     /tdd init          # TDD 스킬 생성")
    print()
    print(f"{Colors.YELLOW}비활성화:{Colors.NC}")
    print(f"  {Colors.BLUE}python scripts/dev.py --off{Colors.NC}")
    print()


def disable_dev_mode():
    """개발 모드 비활성화 (alias와 wrapper 모두 제거)"""
    rc_file = get_shell_rc_file()

    alias_removed = remove_alias(rc_file)
    wrapper_removed = remove_wrapper()

    print(f"{Colors.GREEN}개발 모드 비활성화 완료{Colors.NC}")
    print()

    if alias_removed:
        print(f"  ✓ alias 제거됨 ({rc_file})")
    if wrapper_removed:
        print(f"  ✓ wrapper 제거됨 ({WRAPPER_FILE})")

    if not alias_removed and not wrapper_removed:
        print(f"  {Colors.YELLOW}(이미 비활성화 상태){Colors.NC}")
    else:
        print()
        if alias_removed:
            print(f"{Colors.YELLOW}새 터미널을 열거나 다음 명령 실행:{Colors.NC}")
            print(f"  {Colors.BLUE}source {rc_file}{Colors.NC}")
    print()


def cleanup_legacy_settings():
    """이전 방식(karohani-dev 마켓플레이스)의 설정 정리"""
    cleaned = []

    # settings.json 정리
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                settings = {}

        modified = False

        # enabledPlugins에서 @karohani-dev 항목 제거
        if "enabledPlugins" in settings:
            to_remove = [k for k in settings["enabledPlugins"] if "@karohani-dev" in k]
            for key in to_remove:
                del settings["enabledPlugins"][key]
                cleaned.append(f"enabledPlugins: {key}")
                modified = True

        # extraKnownMarketplaces에서 karohani-dev 제거
        if "extraKnownMarketplaces" in settings:
            if "karohani-dev" in settings["extraKnownMarketplaces"]:
                del settings["extraKnownMarketplaces"]["karohani-dev"]
                cleaned.append("extraKnownMarketplaces: karohani-dev")
                modified = True
            # extraKnownMarketplaces가 비어있으면 제거
            if not settings["extraKnownMarketplaces"]:
                del settings["extraKnownMarketplaces"]

        if modified:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

    # known_marketplaces.json에서 karohani-dev 제거
    if KNOWN_MARKETPLACES_FILE.exists():
        with open(KNOWN_MARKETPLACES_FILE, "r", encoding="utf-8") as f:
            try:
                marketplaces = json.load(f)
            except json.JSONDecodeError:
                marketplaces = {}

        if "karohani-dev" in marketplaces:
            del marketplaces["karohani-dev"]
            cleaned.append("known_marketplaces: karohani-dev")
            with open(KNOWN_MARKETPLACES_FILE, "w", encoding="utf-8") as f:
                json.dump(marketplaces, f, indent=2, ensure_ascii=False)

    # 백업 파일 제거
    if BACKUP_FILE.exists():
        BACKUP_FILE.unlink()
        cleaned.append(f"backup file: {BACKUP_FILE}")

    print(f"{Colors.GREEN}레거시 설정 정리 완료{Colors.NC}")
    print()

    if cleaned:
        print(f"{Colors.YELLOW}제거된 항목:{Colors.NC}")
        for item in cleaned:
            print(f"  ✓ {item}")
        print()
        print(f"{Colors.YELLOW}Claude Code를 재시작하세요.{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}(정리할 항목 없음){Colors.NC}")
    print()


def show_status():
    """현재 상태 표시"""
    rc_file = get_shell_rc_file()
    project_dir = get_project_dir()

    alias_active = has_alias(rc_file)
    wrapper_active = has_wrapper()

    print(f"{Colors.BLUE}╔════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║  개발 모드 상태                            ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════╝{Colors.NC}")
    print()
    print(f"프로젝트: {Colors.BLUE}{project_dir}{Colors.NC}")
    print()
    print(f"Alias ({rc_file}):")
    if alias_active:
        print(f"  {Colors.GREEN}✓ 활성화{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}✗ 비활성화{Colors.NC}")
    print()
    print(f"Wrapper ({WRAPPER_FILE}):")
    if wrapper_active:
        print(f"  {Colors.GREEN}✓ 활성화{Colors.NC}")
        if not check_path_includes_wrapper_dir():
            print(f"  {Colors.YELLOW}⚠ PATH에 {WRAPPER_DIR} 없음{Colors.NC}")
    else:
        print(f"  {Colors.YELLOW}✗ 비활성화{Colors.NC}")
    print()

    # 플러그인 상태
    print("플러그인:")
    for plugin in PLUGINS:
        plugin_dir = project_dir / "plugins" / plugin
        if plugin_dir.exists():
            print(f"  {Colors.GREEN}✓{Colors.NC} {plugin}")
        else:
            print(f"  {Colors.RED}✗{Colors.NC} {plugin} (없음)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="개발 모드 설정 (--plugin-dir 방식)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python scripts/dev.py              # alias 방식 (기본)
  python scripts/dev.py --alias      # alias 방식
  python scripts/dev.py --wrapper    # wrapper 방식 (claude-dev 명령)
  python scripts/dev.py --off        # 비활성화
  python scripts/dev.py --status     # 상태 확인
  python scripts/dev.py --cleanup    # 이전 방식 설정 정리
"""
    )
    parser.add_argument("--alias", action="store_true", help="~/.zshrc에 alias 추가")
    parser.add_argument("--wrapper", action="store_true", help="~/.local/bin/claude-dev 생성")
    parser.add_argument("--off", action="store_true", help="개발 모드 비활성화")
    parser.add_argument("--status", action="store_true", help="현재 상태 확인")
    parser.add_argument("--cleanup", action="store_true", help="이전 방식(karohani-dev 마켓플레이스) 설정 정리")
    args = parser.parse_args()

    if args.cleanup:
        cleanup_legacy_settings()
    elif args.status:
        show_status()
    elif args.off:
        disable_dev_mode()
    elif args.wrapper:
        enable_wrapper_mode()
    else:
        # 기본값 또는 --alias
        enable_alias_mode()


if __name__ == "__main__":
    main()
