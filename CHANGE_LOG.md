# Change Log

프로젝트 변경 이력을 기록합니다.

## 2026-01-27

- session-wrap 플러그인 업스트림 참조 및 스크립트 동기화
- dev.py에 `--cleanup` 옵션 추가 (레거시 karohani-dev 설정 제거)
- dev.py를 `--plugin-dir` 방식으로 전면 재작성 (마켓플레이스 조작 방식 폐기)
- dev.py에 원격 플러그인 충돌 방지 기능 추가
- README.md에 voice, tdd 플러그인 추가 및 CHANGE_LOG.md 생성

## 2026-01-26

- doc-updater 에이전트에 CHANGE_LOG.md 지원 추가

## 2026-01-22

- TDD 메타 플러그인 추가 - 프로젝트별 TDD 워크플로우 생성

## 2026-01-21

- TTS 훅 프로젝트 감지 수정 (설치된 플러그인용)
- voice-assistant 폴더를 voice로 이름 변경
- README에 한국어 플러그인 작성 가이드 추가
- TTS 훅 개선 및 요약 길이 20-30단어로 증가
- voice-assistant 리팩토링: 포터블 경로 및 uv run 사용

## 2026-01-18

- voice-assistant 경로 수정 및 /voice 단축 스킬 추가
- hooks.json 중첩 구조 수정 및 문서 업데이트
- voice-assistant 플러그인 추가 (STT/TTS 지원)
- 플러그인 설치 개선 및 SKILL.md 스키마 업데이트
- hello-mcp 플러그인 제거 및 개발환경 문서 추가
- Python 설치/제거 스크립트 추가
- 초기 커밋: Claude Code 플러그인 마켓플레이스