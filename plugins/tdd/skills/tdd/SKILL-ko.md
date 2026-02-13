---
name: tdd
description: This skill should be used when the user asks to "tdd init", "setup tdd", "TDD 설정", "테스트 주도 개발 설정", "add tdd workflow", or wants to set up TDD for their project.
version: 1.0.0
user-invocable: true
---

# TDD 메타 플러그인 (/tdd)

프로젝트별 TDD 워크플로우 스킬을 생성한다. 스택을 감지하고 각 프로젝트에 맞춤화된 `.claude/skills/tdd/SKILL.md`를 생성한다.

## Trigger

`/tdd init`, "TDD 설정", "테스트 주도 개발 설정"

## Allowed Tools

Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion

## Usage

- `/tdd init` - 스택 감지 후 프로젝트 TDD 스킬 생성
- `/tdd init --with-hooks` - 자동 테스트 훅도 함께 생성

## Workflow

### 1. 프로젝트 스택 감지

감지 명령 실행:
```bash
ls package.json pyproject.toml pytest.ini Cargo.toml go.mod Makefile pom.xml build.gradle 2>/dev/null
```

주요 스택 식별:
- **Node.js**: package.json 존재
  - 확인: devDependencies에서 jest, vitest, mocha
  - 감지: lock 파일로 npm, yarn, pnpm 구분
- **Python**: pyproject.toml, pytest.ini, 또는 setup.py
  - 확인: 의존성에서 pytest, unittest
- **Go**: go.mod 존재
- **Rust**: Cargo.toml 존재
- **Java**: pom.xml 또는 build.gradle 존재

### 2. 사용자 선호도 확인

```
감지된 스택: [스택 이름]
테스트 프레임워크: [감지됨 또는 질문]

옵션:
1. 테스트 명령: [스택 기반 기본값]
2. 테스트 파일 패턴: [기본 패턴]
3. 자동 테스트 훅 포함? [예/아니오]
```

### 3. 프로젝트 TDD 스킬 생성

`${pluginDir}/templates/[stack].md` 템플릿을 사용하여 `.claude/skills/tdd/SKILL.md` 생성

템플릿에서 교체할 변수:
- `{{TEST_COMMAND}}` - 예: `npm test`, `pytest`, `go test ./...`
- `{{TEST_PATTERN}}` - 예: `**/*.test.ts`, `**/test_*.py`
- `{{FRAMEWORK}}` - 예: `Jest`, `pytest`, `go test`

### 4. 훅 생성 (선택)

`--with-hooks` 또는 사용자 확인 시, `.claude/hooks.json` 생성:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "{{TEST_COMMAND}}", "timeout": 60 }]
      },
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "{{TEST_COMMAND}}", "timeout": 60 }]
      }
    ]
  }
}
```

### 5. 설정 확인

요약 표시:
```
TDD 설정 완료!

생성된 파일:
- .claude/skills/tdd/SKILL.md
- .claude/hooks.json (요청 시)

사용법:
- /tdd           - TDD 사이클 시작
- /tdd red       - 실패하는 테스트 작성
- /tdd green     - 테스트 통과시키기
- /tdd refactor  - 코드 개선

자동 테스트: [활성화/비활성화]
```

## Templates Location

템플릿은 `${pluginDir}/templates/`에 저장됨:
- `nodejs.md` - Node.js (Jest, Vitest, Mocha)
- `python.md` - Python (pytest, unittest)
- `go.md` - Go
- `rust.md` - Rust
- `generic.md` - 폴백 템플릿
