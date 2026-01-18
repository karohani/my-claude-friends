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

## 라이선스

MIT

## 참고

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [Claude Code 문서](https://docs.anthropic.com/claude-code)
