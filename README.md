# Karohani Claude Code Plugin

Claude Code 플러그인 개발 실험실. Skills, Hooks, MCP 서버, Agents를 모두 다루는 마켓플레이스.

## 설치

```bash
# 마켓플레이스 추가
/plugin marketplace add jay/my-karohani-claude-code-plugin

# 플러그인 설치
/plugin install hello-skill
/plugin install hello-mcp
/plugin install session-wrap
```

## 플러그인 목록

| 플러그인 | 타입 | 설명 |
|---------|------|------|
| hello-skill | Skills | 간단한 인사 스킬 - `/hello` 트리거 |
| hello-mcp | MCP 서버 | greet, echo 도구 제공 |
| session-wrap | Skills + Agents | 멀티에이전트 세션 분석 - `/wrap` 트리거 |

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

## 프로젝트 구조

```
.
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── plugins/
│   ├── hello-skill/          # Skills 예제
│   ├── hello-mcp/            # MCP 서버 예제
│   └── session-wrap/         # 멀티에이전트 워크플로우
├── CLAUDE.md                 # Claude Code용 상세 문서
└── README.md
```

## 라이선스

MIT

## 참고

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [Claude Code 문서](https://docs.anthropic.com/claude-code)
