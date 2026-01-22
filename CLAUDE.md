# Karohani Claude Code Plugin

Claude Code 플러그인 개발 실험실. Skills, Hooks, Agents, Commands를 다루는 마켓플레이스.

## 설치 방법

```bash
# 마켓플레이스 추가
/plugin marketplace add jay/my-karohani-claude-code-plugin

# 플러그인 설치
/plugin install hello-skill
/plugin install session-wrap
/plugin install youtube-digest
/plugin install voice
/plugin install tdd

# 세션 마무리 사용
/wrap              # 대화형 세션 분석
/wrap [message]    # 빠른 커밋

# YouTube 영상 분석 (yt-dlp 필요)
/youtube [URL]         # 자막 추출 + 요약
/youtube [URL] --quiz  # 퀴즈 포함

# 음성 입출력 (sox, whisper-cpp 필요)
/voice                 # 상태 확인
/voice ask             # 음성으로 질문
/voice on|off          # TTS 켜기/끄기

# TDD 메타 플러그인
/tdd init              # 스택 감지 → .claude/skills/tdd/ 생성
/tdd init --with-hooks # hooks.json도 생성 (자동 테스트)
```

## 프로젝트 구조 (마켓플레이스)

```
.
├── .claude-plugin/
│   ├── plugin.json           # 루트 메타데이터
│   └── marketplace.json      # 플러그인 목록 정의
├── plugins/
│   ├── hello-skill/          # Skills 방식 예제
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/hello/SKILL.md
│   ├── session-wrap/         # 멀티에이전트 워크플로우
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/           # 5개 전문화 에이전트
│   │   │   ├── doc-updater.md
│   │   │   ├── automation-scout.md
│   │   │   ├── learning-extractor.md
│   │   │   ├── followup-suggester.md
│   │   │   └── duplicate-checker.md
│   │   ├── commands/wrap.md
│   │   └── skills/
│   │       ├── session-wrap/SKILL.md
│   │       ├── history-insight/SKILL.md
│   │       └── session-analyzer/SKILL.md
│   ├── youtube-digest/       # YouTube 영상 요약
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/           # 4개 전문화 에이전트
│   │   │   ├── transcript-extractor.md
│   │   │   ├── proper-noun-corrector.md
│   │   │   ├── summary-generator.md
│   │   │   └── quiz-generator.md
│   │   ├── commands/youtube.md
│   │   └── skills/
│   │       └── youtube-digest/SKILL.md
│   ├── voice/                # 음성 입출력
│   │   ├── .claude-plugin/plugin.json
│   │   ├── pyproject.toml    # uv run 의존성
│   │   ├── config.json       # STT/TTS 설정
│   │   ├── hooks/hooks.json  # Stop, Notification, PostToolUse → TTS 자동 실행
│   │   ├── scripts/          # Python 스크립트
│   │   │   ├── speak.py      # TTS (Haiku 요약 + say)
│   │   │   ├── record.py     # 녹음 (sox)
│   │   │   ├── transcribe.py # STT (whisper/OpenAI)
│   │   │   └── config_loader.py
│   │   ├── commands/voice.md
│   │   └── skills/
│   │       └── voice/SKILL.md
│   └── tdd/                  # TDD 메타 플러그인
│       ├── .claude-plugin/plugin.json
│       ├── templates/        # 스택별 TDD 스킬 템플릿
│       │   ├── nodejs.md
│       │   ├── python.md
│       │   └── generic.md
│       ├── commands/tdd.md
│       └── skills/
│           └── tdd/SKILL.md  # 프로젝트별 스킬 생성 워크플로우
├── scripts/
│   ├── install.py            # 설치 스크립트
│   ├── uninstall.py          # 제거 스크립트
│   └── dev.py                # 개발 모드 설정
├── CLAUDE.md                 # 이 파일
├── README.md
└── pyproject.toml
```

## 플러그인 목록

| 플러그인 | 타입 | 설명 |
|---------|------|------|
| hello-skill | Skills | 간단한 인사 스킬 - `/hello` 트리거 |
| session-wrap | Skills + Agents | 멀티에이전트 세션 분석 - `/wrap` 트리거 |
| youtube-digest | Skills + Agents | YouTube 영상 요약 - `/youtube` 트리거 |
| voice | Skills + Hooks | 음성 입출력 (STT/TTS) - `/voice` 트리거 |
| tdd | Skills (Meta) | TDD 메타 플러그인 - 프로젝트별 `.claude/skills/tdd/` 생성 |

## 다섯 가지 플러그인 컴포넌트

### 1. Skills (SKILL.md)
- **위치**: `plugins/<name>/skills/<skill-name>/SKILL.md`
- **용도**: 프롬프트/워크플로우 정의, 코드 없이 동작
- **트리거**: `/skillname` 슬래시 커맨드
- **예제**: `plugins/hello-skill/`, `plugins/session-wrap/skills/`

### 2. Hooks (hooks.json)
- **위치**: `plugins/<name>/hooks/hooks.json`
- **용도**: 이벤트 기반 자동 실행 (Stop, PreToolUse 등)
- **트리거**: Claude Code 이벤트
- **예제**: `plugins/voice/hooks/` (Stop, Notification, PostToolUse 이벤트로 TTS 실행)

### 3. MCP 서버 (Python)
- **위치**: `plugins/<name>/src/server.py`
- **용도**: 커스텀 도구, API 호출, 외부 서비스 연동
- **설정**: plugin.json의 `mcpServers` 필드

### 4. Agents (agents/*.md)
- **위치**: `plugins/<name>/agents/<agent-name>.md`
- **용도**: 전문화된 분석/처리 에이전트 정의
- **특징**: Task 도구로 병렬 실행 가능
- **예제**: `plugins/session-wrap/agents/` (5개 에이전트)

### 5. Commands (commands/*.md)
- **위치**: `plugins/<name>/commands/<command>.md`
- **용도**: 슬래시 커맨드 정의, Skills의 진입점
- **예제**: `plugins/session-wrap/commands/wrap.md`

## 새 플러그인 추가하기

### 1. 디렉토리 생성
```bash
mkdir -p plugins/<name>/.claude-plugin
mkdir -p plugins/<name>/skills/<name>  # Skills용
mkdir -p plugins/<name>/src            # MCP용
mkdir -p plugins/<name>/agents         # Agents용
mkdir -p plugins/<name>/commands       # Commands용
```

### 2. plugin.json 작성
```json
{
  "name": "<name>",
  "version": "0.1.0",
  "description": "설명",
  "mcpServers": { ... }  // MCP 서버인 경우
}
```

### 3. marketplace.json에 등록
```json
{
  "owner": { "name": "작성자", "email": "email@example.com" },
  "plugins": [
    {
      "name": "<name>",
      "source": "./plugins/<name>",
      "version": "1.0.0",
      "author": { "name": "작성자", "email": "email@example.com" },
      "category": "productivity"
    }
  ]
}
```
**주의**: `path` 대신 `source` 필드 사용, `owner` 필수

## 개발 인사이트

### 배운 것들
- MCP 서버는 `.mcp.json` 또는 plugin.json의 `mcpServers`로 설정
- Skills는 SKILL.md 하나로 슬래시 커맨드 정의 가능
- `uv`로 Python 의존성 관리하면 편함
- Agents는 markdown으로 정의하고 Task 도구로 실행
- hooks.json 구조: `{"hooks": {"EventName": [{"hooks": [{type, command}]}]}}` (중첩 구조)
- macOS Homebrew Python 같은 externally-managed 환경에서는 venv 필수
- dev.py는 "karohani-dev" 마켓플레이스 별도 생성 (karohani-plugins와 분리)
- 마켓플레이스 캐시 (~/.claude/plugins/cache/)는 때로 수동 업데이트 필요
- Stop 이벤트 hook은 트랜스크립트 파일(~/.claude/projects/)에서 마지막 응답 추출 (더 안정적)
- 백그라운드 TTS: subprocess.Popen(start_new_session=True) 패턴 사용
- Korean 언어감지: Unicode 범위(0xAC00-0xD7A3) 체크하면 효율적
- **마켓플레이스 설치 시 .venv 복사 안됨** (.gitignore 제외) → pyproject.toml + `uv run` 패턴 사용
- `uv run --directory ${pluginDir}` 패턴: venv 없이 의존성 자동 설치/실행 (hooks는 `${CLAUDE_PLUGIN_ROOT}`)
- **Hook 실행 시 cwd는 프로젝트가 아닌 캐시 디렉토리** (`~/.claude/plugins/cache/`) → `os.getcwd()` 사용 불가
- **CLAUDE_PROJECT_ROOT 환경변수 없음** - 프로젝트 경로 접근 시 `~/.claude/projects/` 전체 탐색 필요

### Claude Code 플러그인 시스템 파일 구조
```
~/.claude/
├── plugins/
│   ├── known_marketplaces.json    # 등록된 마켓플레이스 목록
│   ├── installed_plugins.json     # 설치된 플러그인 목록
│   └── marketplaces/
│       └── {marketplace-name}/    # 마켓플레이스별 플러그인 저장
└── settings.json                  # enabledPlugins로 활성화 관리
```

### 실패한 시도
- settings.local.json에 mcpServers 넣으면 안됨 (스키마 오류)
- marketplace.json에서 `path` 대신 `source` 필드 사용해야 함
- hooks.json의 "hooks"를 단순 배열/객체로 정의하면 안됨 (중첩 필요: EventName → [{hooks: [...]}])
- 현재 Python 환경에서 venv 없이 패키지 설치하면 externally-managed 오류 발생 (Homebrew)
- 캐시 불일치 시 명시적 cache 삭제나 Claude Code 재시작 필요
- hooks.json에서 `${pluginDir}` 사용 불가 → `${CLAUDE_PLUGIN_ROOT}` 사용 (venv는 절대경로 필요)
- Hook에서 `os.getcwd()` 기반 프로젝트 디렉토리 탐지 불가 → 캐시 디렉토리에서 실행되므로 `~/.claude/projects/` 전체 검색 필요

### 유용한 패턴
- `${pluginDir}` 변수는 commands/skills에서 사용, hooks에서는 `${CLAUDE_PLUGIN_ROOT}` 사용
- 멀티에이전트 파이프라인: Phase 1 병렬 실행 → Phase 2 검증 패턴 (session-wrap 참고)
- Task 도구로 에이전트 병렬 실행 가능
- SKILL.md description 패턴: `"This skill should be used when the user asks to..."` 형식이 Claude 스킬 매칭 정확도 향상
- 다국어 트리거 키워드: 한국어/영어 병기 시 더 많은 상황에서 매칭됨 (예: `"wrap up"`, `"세션 마무리"`, `"마무리해줘"`)
- `/skill` 단축키: plugin.json의 name을 `voice`로 하면 `voice:voice` 스킬이 `/voice`로 접근 가능
- claude-agent-sdk로 Haiku 요약 호출하면 anthropic 직접 호출보다 간결함

### 개발 모드 (dev.py)
```bash
python scripts/dev.py          # 현재 디렉토리를 마켓플레이스로 직접 등록
python scripts/dev.py --off    # 개발 모드 비활성화
```
- 파일 수정 시 복사 없이 바로 반영됨
- Claude Code 재시작 필요

## 참고 자료

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [MCP Python SDK](https://github.com/anthropics/mcp-python-sdk)
- [Claude Code 문서](https://docs.anthropic.com/claude-code)
