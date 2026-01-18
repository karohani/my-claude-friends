# Karohani Claude Code Plugin

Claude Code 플러그인 개발 실험실. Skills, Hooks, Agents, Commands를 다루는 마켓플레이스.

## 설치 방법

```bash
# 마켓플레이스 추가
/plugin marketplace add jay/my-karohani-claude-code-plugin

# 플러그인 설치
/plugin install hello-skill
/plugin install session-wrap

# 세션 마무리 사용
/wrap              # 대화형 세션 분석
/wrap [message]    # 빠른 커밋
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
│   └── session-wrap/         # 멀티에이전트 워크플로우
│       ├── .claude-plugin/plugin.json
│       ├── agents/           # 5개 전문화 에이전트
│       │   ├── doc-updater.md
│       │   ├── automation-scout.md
│       │   ├── learning-extractor.md
│       │   ├── followup-suggester.md
│       │   └── duplicate-checker.md
│       ├── commands/wrap.md
│       └── skills/
│           ├── session-wrap/SKILL.md
│           ├── history-insight/SKILL.md
│           └── session-analyzer/SKILL.md
├── CLAUDE.md                 # 이 파일
├── README.md
└── pyproject.toml
```

## 플러그인 목록

| 플러그인 | 타입 | 설명 |
|---------|------|------|
| hello-skill | Skills | 간단한 인사 스킬 - `/hello` 트리거 |
| session-wrap | Skills + Agents | 멀티에이전트 세션 분석 - `/wrap` 트리거 |

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
- **예제**: (아직 없음 - 추가 예정)

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
  "plugins": [
    { "name": "<name>", "path": "./plugins/<name>" }
  ]
}
```

## 개발 인사이트

### 배운 것들
- MCP 서버는 `.mcp.json` 또는 plugin.json의 `mcpServers`로 설정
- Skills는 SKILL.md 하나로 슬래시 커맨드 정의 가능
- `uv`로 Python 의존성 관리하면 편함
- Agents는 markdown으로 정의하고 Task 도구로 실행

### 실패한 시도
- settings.local.json에 mcpServers 넣으면 안됨 (스키마 오류)

### 유용한 패턴
- `${pluginDir}` 변수로 플러그인 경로 참조
- 멀티에이전트 파이프라인: Phase 1 병렬 실행 → Phase 2 검증 패턴 (session-wrap 참고)
- Task 도구로 에이전트 병렬 실행 가능

## 참고 자료

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [MCP Python SDK](https://github.com/anthropics/mcp-python-sdk)
- [Claude Code 문서](https://docs.anthropic.com/claude-code)
