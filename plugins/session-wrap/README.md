# Session Wrap Plugin

세션 마무리를 위한 멀티에이전트 분석 파이프라인.

## 기능

5개의 전문화된 에이전트가 2단계로 분석을 수행합니다:

**Phase 1 - 병렬 분석 (4개 에이전트):**
- `doc-updater`: CLAUDE.md, context.md 업데이트 필요성 분석
- `automation-scout`: 반복 패턴 감지, 자동화 기회 식별
- `learning-extractor`: 학습 내용, 실수, 발견 추출
- `followup-suggester`: 미완료 작업, 다음 단계 제안

**Phase 2 - 검증 (1개 에이전트):**
- `duplicate-checker`: Phase 1 결과의 중복 검증

## 사용법

```
/wrap              # 대화형 세션 마무리
/wrap [message]    # 빠른 커밋
```

## 포함된 Skills

| Skill | 설명 |
|-------|------|
| session-wrap | 메인 워크플로우 |
| history-insight | 세션 히스토리 분석 |
| session-analyzer | SKILL.md 명세 대비 검증 |

## 라이선스

MIT - Team Attention
