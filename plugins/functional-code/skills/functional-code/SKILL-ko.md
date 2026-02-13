---
name: functional-code
description: This skill should be used when the user asks to "write functional code", "review code functionally", "functional programming", "함수형 프로그래밍", "함수형 코드 리뷰", "grokking simplicity", "separate effects", "pure functions", "순수 함수", "side effects", "부수효과", "immutable", "불변성", "action calculation data", "액션 계산 데이터", or wants to write or review code following functional programming principles that separate Actions, Calculations, and Data.
version: 1.0.0
user-invocable: true
---

# Functional Code

"Grokking Simplicity"(Eric Normand 저)의 함수형 프로그래밍 원칙에 따라 코드를 작성하고 리뷰하는 스킬. 모든 코드를 **액션**, **계산**, **데이터**로 분류하고, 부수효과를 격리하며, 로직은 순수하게, 데이터는 불변으로 유지하는 구조를 만든다.

## 모드

이 스킬은 두 가지 모드로 동작한다:

1. **작성 모드** — 처음부터 FP 원칙에 따라 새 코드를 작성하도록 안내한다.
2. **리뷰 모드** — 기존 코드에서 FP 원칙 위반을 분석하고 개선안을 제안한다.

사용자의 의도에서 모드를 판단한다. 모호한 경우 질문한다.

## 핵심 원칙

두 모드 모두 다음 7가지 원칙에 따라 수행한다:

| # | 원칙 | 핵심 아이디어 |
|---|------|--------------|
| 1 | **액션, 계산, 데이터** | 모든 함수를 분류하고, 액션에서 계산을 추출한다 |
| 2 | **암묵적 I/O 최소화** | 숨겨진 입출력을 명시적 파라미터와 리턴값으로 변환한다 |
| 3 | **불변성** | 절대 변이하지 않는다. 내부는 Copy-on-Write, 경계에서는 방어적 복사를 사용한다 |
| 4 | **계층적 설계** | 추상화 수준별로 함수를 레이어로 구성한다. 아래로만 호출한다 |
| 5 | **일급 함수** | 중복된 패턴을 고차 함수로 대체한다 |
| 6 | **함수형 반복** | 명령형 루프 대신 map/filter/reduce를 사용한다 |
| 7 | **양파 아키텍처** | 순수한 코어(계산 + 데이터)를 명령형 셸(액션)로 감싼다 |

상세 패턴과 예제는 아래에 명시된 `references/` 디렉토리를 참조한다.

## 코드의 세 가지 범주

모든 코드는 다음 세 가지 범주 중 하나에 속한다:

**액션 (Effect)** — 실행 시점이나 횟수에 따라 결과가 달라진다. I/O, 네트워크 호출, 데이터베이스 쿼리, 로깅, 가변 상태 읽기, 부수효과가 있는 모든 연산을 포함한다.

**계산 (순수 함수)** — 입력을 출력으로 결정론적으로 변환한다. 같은 입력은 항상 같은 출력을 생성한다. 부수효과 없음. 테스트, 조합, 재사용이 쉽다.

**데이터 (비활성 값)** — 순수한 값: 객체, 배열, 문자열, 숫자. 실행할 수 없다. 사실을 나타낸다.

```
액션:   sendEmail(to, body)        — 부수효과, 시점이 중요
계산:   calculateTotal(items)      — 순수, 테스트 가능
데이터: { id: 1, name: "Alice" }   — 비활성 사실
```

## 작성 모드 워크플로우

사용자가 새 코드를 작성할 때 안내한다:

### 1단계: 작업 분류

요구사항의 어떤 부분이 액션, 계산, 데이터인지 식별한다.

- **액션**: 파일 I/O, API 호출, 데이터베이스 연산, 로깅, 사용자 입력
- **계산**: 유효성 검사, 변환, 필터링, 집계, 비즈니스 규칙
- **데이터**: 설정 객체, DTO, 도메인 엔터티, 상수

### 2단계: 데이터를 먼저 설계

데이터 구조를 정의한다. 데이터가 기반이다 — 계산은 데이터를 처리하고, 액션은 데이터를 시스템 안팎으로 이동시킨다.

### 3단계: 계산 작성

모든 비즈니스 로직을 순수 함수로 작성한다. 각 함수는 명시적 입력을 받아 명시적 출력을 반환한다. 글로벌 읽기 없음, 인자 변이 없음, 부수효과 없음.

```typescript
// 계산 — 순수, 테스트 가능
function applyDiscount(price: number, rate: number): number {
  return price * (1 - rate);
}

// 계산 — 새 데이터 반환, 변이 없음
function addItem(cart: Item[], item: Item): Item[] {
  return [...cart, item];
}
```

### 4단계: 액션을 경계로 격리

모든 부수효과를 바깥 경계로 밀어낸다. 액션이 계산을 호출하지, 그 반대는 아니다.

```typescript
// 액션 — 경계에서, 계산을 호출
async function processOrder(orderId: string): Promise<void> {
  const order = await db.findOrder(orderId);       // 액션: 읽기
  const total = calculateTotal(order.items);        // 계산
  const receipt = formatReceipt(order, total);      // 계산
  await emailService.send(order.email, receipt);    // 액션: 쓰기
}
```

### 5단계: 불변성 적용

모든 데이터 변환에 Copy-on-Write를 적용한다. 기존 객체나 배열을 절대 변이하지 않는다.

```typescript
// 나쁜 예 — 원본 변이
function updateName(user: User, name: string): void {
  user.name = name;
}

// 좋은 예 — Copy-on-Write
function updateName(user: User, name: string): User {
  return { ...user, name };
}
```

### 6단계: 고차 함수 활용

명령형 루프를 map/filter/reduce로 대체한다. 공통 패턴을 재사용 가능한 고차 함수로 추출한다.

```typescript
const activeNames = users
  .filter(u => u.active)
  .map(u => u.name);
```

## 리뷰 모드 워크플로우

기존 코드를 리뷰할 때:

### 1단계: 읽고 이해

Read 도구를 사용하여 대상 코드를 읽는다. 분석하기 전에 전체 구조를 이해한다.

### 2단계: 모든 함수 분류

각 함수를 액션 또는 계산으로 라벨링한다. 발견된 모든 부수효과를 나열한다:
- 외부 읽기 (DB, 파일, 네트워크, 글로벌, 가변 상태)
- 외부 쓰기 (DB, 파일, 네트워크, DOM, 콘솔, 글로벌)
- 비결정성 (random, Date.now, 환경)

### 3단계: 7가지 원칙 점검

체계적으로 점검한다:

1. **액션/계산 분리** — 계산이 액션과 섞여 있는가? 순수 로직을 추출할 수 있는가?
2. **암묵적 I/O** — 글로벌에 대한 숨겨진 의존성, 가변 상태에 대한 클로저, 반환되지 않는 변이가 있는가?
3. **불변성** — 직접적인 배열/객체 변이가 있는가? Copy-on-Write가 빠져 있는가?
4. **계층적 설계** — 고수준 함수가 저수준 구현 세부사항을 직접 호출하는가?
5. **일급 함수** — 작은 콜백만 다른 중복 로직이 있는가?
6. **함수형 반복** — map/filter/reduce로 대체할 수 있는 명령형 루프가 있는가?
7. **양파 아키텍처** — I/O가 경계로 밀려나지 않고 비즈니스 로직과 섞여 있는가?

### 4단계: 보고서 생성

다음 구조로 발견사항을 제시한다:

```
## 함수형 코드 리뷰

### 요약
- 분석한 함수: N개
- 액션: N개 | 계산: N개
- 발견된 이슈: N개 (원칙별)

### 발견사항

#### [원칙 이름] — N번째 줄
**이슈**: [설명]
**현재**: [코드 스니펫]
**제안**: [개선된 코드 스니펫]
**이유**: [위반된 원칙 설명]
```

### 5단계: 다음 단계 제안

사용자에게 다음 중 어떤 것을 할지 묻는다:
- 모든 제안 수정 적용
- 특정 수정만 적용
- 특정 원칙에 대한 상세 설명

## 빠른 참조

### 액션 식별

함수가 다음 중 하나라도 수행하면 액션이다:
- 데이터베이스, 파일, 네트워크에 읽기 또는 쓰기
- 가변 글로벌/공유 상태 읽기
- 인자를 변이시킴
- console.log 또는 로깅 호출
- Date.now(), Math.random() 등 비결정적 API 사용
- 다른 액션을 호출

### 추출 패턴 (액션 → 계산)

1. 액션 안에 묻힌 계산을 식별한다
2. 명시적 파라미터를 가진 새 함수로 추출한다
3. 암묵적 입력(글로벌)을 함수 파라미터로 교체한다
4. 암묵적 출력(변이)을 리턴값으로 교체한다
5. 원래 액션에서 새 계산을 호출한다

### 불변성 빠른 규칙

- 배열: 스프레드 `[...arr]`, `filter`, `map`, `slice` 사용 — `push`, `pop`, `splice`, `sort` 제자리 변이 금지
- 객체: 스프레드 `{...obj}` 사용 — 프로퍼티 직접 할당 금지
- 중첩: 각 레벨을 복사하거나 라이브러리 사용 (예: Immer)
- 경계: 데이터가 신뢰 경계를 넘을 때 방어적 복사(깊은 복제) 사용

## 추가 자료

### 참조 파일

상세 패턴, 예제, 기법은 다음을 참조한다:

- **`references/actions-calculations-data.md`** — 상세 분류 가이드, 추출 기법, 암묵적 I/O 패턴
- **`references/immutability-patterns.md`** — Copy-on-Write, 방어적 복사, 언어별 도구
- **`references/stratified-design.md`** — 레이어 구성, 4가지 설계 패턴, 레이어로 리팩토링
- **`references/higher-order-functions.md`** — 일급 함수, 고차 함수 패턴, 루프 대체, 합성
- **`references/onion-architecture.md`** — 함수형 코어 / 명령형 셸, 의존성 방향, 구현 패턴
