# Karohani Claude Code Plugin

Claude Code 플러그인 개발 실험실. Skills, Hooks, MCP 서버, Agents를 모두 다루는 마켓플레이스.

## 빠른 시작 (로컬 설치)

```bash
# 1. 저장소 클론
git clone https://github.com/jay/my-karohani-claude-code-plugin.git
cd my-karohani-claude-code-plugin

# 2. 로컬 설치 (개발 모드 - 파일 수정 즉시 반영)
python scripts/dev.py

# 3. Claude Code 재시작 후 사용
/hello             # 인사 스킬
/wrap              # 세션 마무리
/youtube [URL]     # YouTube 영상 요약
```

## 설치 방법

### 방법 1: 개발 모드 (권장 - 로컬 수정 가능)

현재 디렉토리를 직접 마켓플레이스로 등록합니다. 파일 수정 시 바로 반영됩니다.

```bash
git clone https://github.com/jay/my-karohani-claude-code-plugin.git
cd my-karohani-claude-code-plugin
python scripts/dev.py          # 개발 모드 활성화
python scripts/dev.py --off    # 개발 모드 비활성화
```

### 방법 2: 설치 스크립트 (복사 설치)

`~/.claude/plugins/`에 복사하여 설치합니다.

```bash
# 원격 설치 (GitHub에서)
curl -fsSL https://raw.githubusercontent.com/jay/my-karohani-claude-code-plugin/main/scripts/install.py | python3

# 로컬 설치 (현재 디렉토리에서)
git clone https://github.com/jay/my-karohani-claude-code-plugin.git
cd my-karohani-claude-code-plugin
python scripts/install.py --local
```

### 방법 3: 마켓플레이스

```bash
# 마켓플레이스 추가
/plugin marketplace add jay/my-karohani-claude-code-plugin

# 플러그인 설치
/plugin install hello-skill
/plugin install session-wrap
/plugin install youtube-digest
```

### 제거

```bash
python scripts/uninstall.py
```

## 플러그인 목록

| 플러그인 | 타입 | 설명 |
|---------|------|------|
| hello-skill | Skills | 간단한 인사 스킬 - `/hello` 트리거 |
| session-wrap | Skills + Agents | 멀티에이전트 세션 분석 - `/wrap` 트리거 |
| youtube-digest | Skills + Agents | YouTube 영상 요약 - `/youtube` 트리거 |

## 주요 기능

### /wrap - 세션 마무리
5개의 전문화된 에이전트가 병렬로 세션을 분석합니다:
- 문서 업데이트 제안
- 자동화 기회 식별
- 학습 내용 추출
- 후속 작업 제안

```bash
/wrap              # 대화형 세션 마무리
/wrap [message]    # 빠른 커밋
```

### /youtube - YouTube 영상 요약
YouTube 영상을 분석하여 마크다운 문서로 정리합니다.

```bash
# 전제 조건
brew install yt-dlp

# 사용
/youtube [URL]         # 자막 추출 + 요약
/youtube [URL] --quiz  # 퀴즈 포함
```

## 프로젝트 구조

```
.
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── plugins/
│   ├── hello-skill/          # Skills 예제
│   ├── session-wrap/         # 멀티에이전트 워크플로우
│   └── youtube-digest/       # YouTube 영상 요약
├── scripts/
│   ├── install.py            # 설치 스크립트
│   ├── uninstall.py          # 제거 스크립트
│   └── dev.py                # 개발 모드 설정
├── CLAUDE.md                 # Claude Code용 상세 문서
└── README.md
```

## 개발환경

플러그인을 직접 개발하거나 수정하려면 개발 모드를 사용하세요.

### 개발 모드 (권장)

```bash
git clone https://github.com/jay/my-karohani-claude-code-plugin.git
cd my-karohani-claude-code-plugin
python scripts/dev.py          # 개발 모드 활성화
```

개발 모드는 현재 디렉토리를 직접 마켓플레이스로 등록합니다:
- 파일 수정 시 Claude Code 재시작하면 바로 반영
- 복사 없이 원본 파일 직접 사용

### 수동 설정 (선택)

`~/.claude/settings.json`에 직접 추가:
```json
{
  "extraKnownMarketplaces": {
    "karohani-dev": {
      "source": {
        "source": "directory",
        "path": "/your/path/to/my-karohani-claude-code-plugin"
      }
    }
  }
}
```

### 개발 워크플로우

- `plugins/` 디렉토리에 새 플러그인 추가 가능
- `.claude-plugin/marketplace.json`에 새 플러그인 등록 필요
- SKILL.md, agents/*.md 수정 후 Claude Code 재시작

## 플러그인 작성 가이드

Claude Code 플러그인은 5가지 컴포넌트로 구성됩니다. 필요에 따라 조합하여 사용합니다.

### 플러그인 기본 구조

```
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json          # 필수: 플러그인 메타데이터
├── skills/
│   └── my-skill/
│       └── SKILL.md         # 슬래시 커맨드 정의
├── commands/
│   └── my-command.md        # 커맨드 진입점
├── agents/
│   └── my-agent.md          # 전문화된 에이전트
├── hooks/
│   └── hooks.json           # 이벤트 기반 자동화
└── src/
    └── server.py            # MCP 서버 (Python)
```

### 1. plugin.json (필수)

모든 플러그인의 시작점입니다.

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "플러그인 설명"
}
```

### 2. Skills (SKILL.md)

코드 없이 프롬프트만으로 기능을 정의합니다. `/skillname`으로 호출됩니다.

**파일 위치**: `skills/<skill-name>/SKILL.md`

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do something", "무언가 해줘", or wants to perform a specific task.
version: 1.0.0
user-invocable: true
---

# My Skill

스킬 설명과 워크플로우를 작성합니다.

## Allowed Tools

Bash, Read, Write, Edit, Glob, Grep, Task, AskUserQuestion

## Workflow

1. **첫 번째 단계**: 설명
2. **두 번째 단계**: 설명

## Examples

- `/my-skill` - 기본 사용
- `/my-skill [args]` - 인자와 함께 사용
```

**팁**: `description`에 `"This skill should be used when the user asks to..."` 패턴을 사용하면 Claude가 스킬을 더 정확하게 매칭합니다.

### 3. Hooks (hooks.json)

Claude Code 이벤트에 자동으로 반응합니다.

**파일 위치**: `hooks/hooks.json`

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python ${CLAUDE_PLUGIN_ROOT}/scripts/my-script.py",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'AskUserQuestion이 사용됨'",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**주요 이벤트**:
| 이벤트 | 발생 시점 |
|--------|----------|
| `Stop` | Claude 응답 완료 |
| `PreToolUse` | 도구 사용 전 |
| `PostToolUse` | 도구 사용 후 |
| `Notification` | 알림 표시 시 |
| `SessionStart` | 세션 시작 |
| `SessionEnd` | 세션 종료 |

**주의**: hooks.json에서는 `${CLAUDE_PLUGIN_ROOT}` 변수를 사용합니다 (`${pluginDir}` 아님).

### 4. Agents (agents/*.md)

Task 도구로 호출되는 전문화된 에이전트를 정의합니다.

**파일 위치**: `agents/<agent-name>.md`

```markdown
---
name: my-agent
description: 이 에이전트는 특정 분석/처리를 담당합니다.
model: haiku  # 또는 sonnet, opus
tools:
  - Read
  - Grep
  - Glob
---

# My Agent

## 역할

이 에이전트의 역할과 책임을 설명합니다.

## 입력

- 분석할 데이터 설명

## 출력 형식

JSON 또는 마크다운으로 결과를 반환합니다:

```json
{
  "findings": [],
  "recommendations": []
}
```

## 지침

1. 첫 번째 지침
2. 두 번째 지침
```

**사용 예시** (SKILL.md에서):
```markdown
Task 도구로 my-agent를 호출합니다:
- subagent_type: "my-plugin:my-agent"
- prompt: "분석할 내용"
```

### 5. Commands (commands/*.md)

슬래시 커맨드의 진입점을 정의합니다. Skills의 간단한 버전입니다.

**파일 위치**: `commands/<command>.md`

```markdown
---
name: my-command
description: 커맨드 설명
allowed_tools:
  - Bash
  - Read
---

# /my-command

## Usage

`/my-command [args]`

## Workflow

1. 단계 설명
2. 단계 설명
```

### 6. MCP 서버 (선택)

외부 API 연동이나 복잡한 로직이 필요한 경우 Python MCP 서버를 사용합니다.

**plugin.json에 추가**:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "--directory", "${pluginDir}", "python", "${pluginDir}/src/server.py"],
      "env": {}
    }
  }
}
```

**src/server.py 예시**:
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("my-server")

@server.tool()
async def my_tool(param: str) -> str:
    """도구 설명"""
    return f"결과: {param}"

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 마켓플레이스 등록

플러그인을 마켓플레이스에 등록하려면 `.claude-plugin/marketplace.json`에 추가합니다:

```json
{
  "owner": {
    "name": "작성자",
    "email": "email@example.com"
  },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "version": "1.0.0",
      "author": {
        "name": "작성자",
        "email": "email@example.com"
      },
      "category": "productivity"
    }
  ]
}
```

### 개발 팁

1. **개발 모드 사용**: `python scripts/dev.py`로 파일 수정 즉시 반영
2. **다국어 트리거**: description에 한국어/영어 키워드 병기로 매칭률 향상
3. **uv run 패턴**: venv 없이 의존성 자동 관리 (마켓플레이스 배포 호환)
4. **병렬 에이전트**: Task 도구로 여러 에이전트 동시 실행 가능
5. **PostToolUse matcher**: 특정 도구에만 훅 적용 가능

### 예제 플러그인

| 플러그인 | 컴포넌트 | 참고 포인트 |
|---------|---------|------------|
| hello-skill | Skills | 가장 간단한 스킬 예제 |
| session-wrap | Skills + Agents | 멀티에이전트 병렬 실행 |
| youtube-digest | Skills + Agents | 외부 도구(yt-dlp) 연동 |
| voice | Skills + Hooks | 이벤트 기반 자동화 |

## 동작 방식

### Claude Code 플러그인 시스템 구조

```
~/.claude/
├── plugins/
│   ├── known_marketplaces.json    # 등록된 마켓플레이스 목록
│   ├── installed_plugins.json     # 설치된 플러그인 목록
│   └── marketplaces/
│       └── {marketplace-name}/    # 마켓플레이스별 플러그인 저장
└── settings.json                  # enabledPlugins로 활성화 관리
```

### 플러그인 로딩 과정

1. **세션 시작**: Claude Code가 `~/.claude/settings.json`의 `enabledPlugins` 확인
2. **플러그인 스캔**: 활성화된 플러그인의 `plugin.json` 로드
3. **컴포넌트 등록**:
   - Skills → 슬래시 커맨드로 등록
   - Hooks → 이벤트 리스너로 등록
   - MCP 서버 → 백그라운드 프로세스로 실행
   - Agents → Task 도구에서 사용 가능하도록 등록

### Skills 동작 방식

```
사용자 입력: /my-skill args
     ↓
Claude Code: SKILL.md 로드
     ↓
Claude: SKILL.md의 워크플로우에 따라 실행
     ↓
결과 출력
```

- SKILL.md의 `description`을 기반으로 자연어 매칭도 수행
- `Allowed Tools` 섹션에 명시된 도구만 사용 가능

### Hooks 동작 방식

```
이벤트 발생 (예: Stop)
     ↓
Claude Code: hooks.json에서 해당 이벤트 찾기
     ↓
매칭되는 훅의 command 실행
     ↓
(선택) stdout을 Claude에게 전달
```

- `matcher`로 특정 도구에만 훅 적용 가능 (예: `"matcher": "AskUserQuestion"`)
- `${CLAUDE_PLUGIN_ROOT}`는 플러그인 루트 경로로 치환됨

### Agents 동작 방식

```
SKILL.md에서 Task 도구 호출
     ↓
subagent_type: "plugin-name:agent-name"
     ↓
Claude Code: agents/agent-name.md 로드
     ↓
새 컨텍스트에서 에이전트 실행
     ↓
결과를 호출한 컨텍스트로 반환
```

- 에이전트는 독립적인 컨텍스트에서 실행됨
- `model` 필드로 haiku/sonnet/opus 선택 가능 (비용/속도 조절)

### MCP 서버 동작 방식

```
Claude Code 세션 시작
     ↓
plugin.json의 mcpServers 확인
     ↓
지정된 command로 MCP 서버 프로세스 실행
     ↓
Claude가 MCP 도구를 일반 도구처럼 사용
```

- stdio 기반 통신 (JSON-RPC)
- 세션 종료 시 MCP 서버도 함께 종료

### 변수 치환

| 변수 | 사용 위치 | 설명 |
|------|----------|------|
| `${pluginDir}` | SKILL.md, commands/*.md | 플러그인 루트 경로 |
| `${CLAUDE_PLUGIN_ROOT}` | hooks.json | 플러그인 루트 경로 |

## 참고 자료

### 공식 문서

- [Claude Code 공식 문서](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code Hooks 가이드](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### 커뮤니티 플러그인

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives) - 다양한 플러그인 예제
- [anthropics/claude-code-plugins](https://github.com/anthropics/claude-code) - 공식 저장소

### 도구

- [uv](https://github.com/astral-sh/uv) - 빠른 Python 패키지 매니저
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 다운로더 (youtube-digest 플러그인용)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - 로컬 음성인식 (voice 플러그인용)

## 라이선스

MIT

## 참고

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [Claude Code 문서](https://docs.anthropic.com/claude-code)
