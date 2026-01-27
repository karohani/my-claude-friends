# Session Wrap Plugin

세션 마무리를 위한 멀티에이전트 분석 파이프라인.

## 설치 방법

### Plugin Directory (개발용)
```bash
claude --plugin-dir ./plugins/session-wrap
```

### Marketplace (배포용)
```bash
/plugin marketplace add jay/my-karohani-claude-code-plugin
/plugin install session-wrap
```

## 기능

5개의 전문화된 에이전트가 2단계로 분석을 수행합니다:

```
┌─────────────────────────────────────────────────────────┐
│                      Phase 1: Analysis                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ doc-updater  │  │ automation-  │  │  learning-   │   │
│  │              │  │    scout     │  │  extractor   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              followup-suggester                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Phase 2: Validation                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │              duplicate-checker                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Phase 1 - 병렬 분석 (4개 에이전트):**
- `doc-updater`: CLAUDE.md, context.md 업데이트 필요성 분석
- `automation-scout`: 반복 패턴 감지, 자동화 기회 식별
- `learning-extractor`: 학습 내용, 실수, 발견 추출
- `followup-suggester`: 미완료 작업, 다음 단계 제안

**Phase 2 - 검증 (1개 에이전트):**
- `duplicate-checker`: Phase 1 결과의 중복 검증

## 사용법

```bash
/wrap              # 대화형 세션 마무리
/wrap [message]    # 빠른 커밋
```

## 디렉토리 구조

```
plugins/session-wrap/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── doc-updater.md
│   ├── automation-scout.md
│   ├── learning-extractor.md
│   ├── followup-suggester.md
│   └── duplicate-checker.md
├── commands/
│   └── wrap.md
├── skills/
│   ├── session-wrap/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── multi-agent-patterns.md
│   ├── history-insight/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── extract-session.sh
│   │   └── references/
│   │       └── session-file-format.md
│   └── session-analyzer/
│       ├── SKILL.md
│       ├── scripts/
│       │   ├── extract-hook-events.sh
│       │   ├── extract-subagent-calls.sh
│       │   └── find-session-files.sh
│       └── references/
│           ├── analysis-patterns.md
│           └── common-issues.md
└── README.md
```

## 포함된 Skills

| Skill | 설명 | 유틸리티 |
|-------|------|---------|
| session-wrap | 메인 워크플로우 | multi-agent-patterns.md |
| history-insight | 세션 히스토리 분석 | extract-session.sh, session-file-format.md |
| session-analyzer | 디버그 로그 분석 | extract-*.sh, find-session-files.sh |

## When to Use

### /wrap
- 긴 코딩 세션 후 정리가 필요할 때
- 문서(CLAUDE.md) 업데이트 체크
- 다음 세션을 위한 TODO 정리
- 학습한 내용 기록

### history-insight
- 세션 파일(.jsonl) 구조 이해
- 대화 내용만 추출 (파일 크기 93% 감소)
- 메시지 타입 분석

### session-analyzer
- 디버그 로그에서 Hook 이벤트 추출
- SubAgent 호출 패턴 분석
- 세션 관련 파일 찾기

## 스크립트 사용법

### extract-session.sh
세션 파일에서 대화만 추출 (12MB → ~800KB):
```bash
./skills/history-insight/scripts/extract-session.sh session.jsonl
```

### find-session-files.sh
세션 ID로 관련 파일 찾기:
```bash
./skills/session-analyzer/scripts/find-session-files.sh abc12345
```

### extract-hook-events.sh
디버그 로그에서 Hook 이벤트 추출:
```bash
./skills/session-analyzer/scripts/extract-hook-events.sh debug.log
```

### extract-subagent-calls.sh
디버그 로그에서 SubAgent 호출 추출:
```bash
./skills/session-analyzer/scripts/extract-subagent-calls.sh debug.log
```

## References

- [multi-agent-patterns.md](skills/session-wrap/references/multi-agent-patterns.md) - 멀티에이전트 오케스트레이션 패턴
- [session-file-format.md](skills/history-insight/references/session-file-format.md) - Claude Code 세션 파일 구조
- [analysis-patterns.md](skills/session-analyzer/references/analysis-patterns.md) - 디버그 로그 분석 패턴
- [common-issues.md](skills/session-analyzer/references/common-issues.md) - 자주 발생하는 문제와 해결책

## Integration with plugin-dev

session-wrap은 [plugin-dev](https://github.com/team-attention/plugins-for-claude-natives) 플러그인의 에이전트들과 함께 사용할 수 있습니다:

- `gap-analyzer`: 플러그인 품질 분석
- `reviewer`: 코드 리뷰
- `worker`: 구현 작업

session-analyzer 스킬로 이들 에이전트의 호출 패턴을 분석할 수 있습니다.

## 라이선스

MIT - Team Attention
