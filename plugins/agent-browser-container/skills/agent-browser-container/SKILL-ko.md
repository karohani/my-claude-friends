---
name: agent-browser-container
description: This skill should be used when the user asks to "run browser in container", "secure chrome", "agent browser", "에이전트 브라우저", "브라우저 컨테이너", "container chrome", "browser sandbox", "KasmVNC", "browse safely", "안전한 브라우저", or wants to run Chrome inside a Docker container with visual access for safe isolated browsing controlled by Claude Code.
version: 0.1.0
user-invocable: true
---

# Agent Browser Container

KasmVNC 시각적 접근을 통해 Docker 컨테이너 내부에서 Chrome을 안전하게 실행하는 관리자입니다.
컨테이너 내부의 Claude Code가 Playwright를 통해 Chrome을 제어하며, 호스트 사용자는 브라우저 기반 VNC 인터페이스를 통해 확인하고 상호작용할 수 있습니다. 이를 통해 에이전트 인젝션 공격이 호스트 시스템에 도달하는 것을 방지합니다.

## 사전 요구사항

- Docker Desktop 또는 Docker Engine이 설치되어 있어야 합니다
- macOS에서는 호스트 OAuth 자격 증명이 자동으로 주입됩니다

## 스크립트 위치

스크립트 경로: `${pluginDir}/scripts/browser.py`

## 사용법

사용자 요청에 따라 Bash 도구를 통해 적절한 명령을 실행하세요.

### 실행

```bash
# 현재 프로젝트에서 브라우저 컨테이너 시작
python3 ${pluginDir}/scripts/browser.py run .

# 특정 프로젝트 경로로 실행
python3 ${pluginDir}/scripts/browser.py run ~/my-project

# zsh 셸 열기 (Claude 시작 없이)
python3 ${pluginDir}/scripts/browser.py run -s
```

### 관리

```bash
# 실행 중인 컨테이너 목록
python3 ${pluginDir}/scripts/browser.py list

# 컨테이너에 셸 연결
python3 ${pluginDir}/scripts/browser.py shell [name]

# 컨테이너 중지
python3 ${pluginDir}/scripts/browser.py stop [name]

# 모든 컨테이너 중지
python3 ${pluginDir}/scripts/browser.py stopall

# 컨테이너 + 볼륨 제거
python3 ${pluginDir}/scripts/browser.py rm <name>

# 전체 정리 (컨테이너 + 볼륨 + 이미지)
python3 ${pluginDir}/scripts/browser.py clean
```

### 빌드 / 공유

```bash
# 이미지만 빌드
python3 ${pluginDir}/scripts/browser.py build

# 레지스트리에 푸시 (BROWSER_IMAGE 환경 변수 필요)
python3 ${pluginDir}/scripts/browser.py push

# 레지스트리에서 풀
python3 ${pluginDir}/scripts/browser.py pull
```

## 아키텍처

```
호스트 (macOS)
  +-- 브라우저 -> http://localhost:6901 (KasmVNC 웹 UI)
  |               컨테이너 Chromium을 보고 상호작용
  +-- CDP      -> http://localhost:9222 (Chrome DevTools Protocol)
  |               호스트에서 Chrome을 프로그래밍 방식으로 제어
  +-- 터미널   -> docker exec -> Claude Code
                    Playwright/CDP로 Chromium 제어 (headless: false, DISPLAY=:1)

컨테이너 (Linux, --read-only)
  +-- KasmVNC 서버 (가상 디스플레이 :1, 인증 없음, 포트 6901로 스트리밍)
  +-- Chromium (CDP와 함께 자동 실행, 포트 9222)
  +-- socat (0.0.0.0:9223 -> 127.0.0.1:9222 호스트 CDP 접근 포워딩)
  +-- Claude Code (tmux 세션 "claude", --dangerously-skip-permissions로 자동 시작)
  +-- iptables 방화벽 (허용 목록 + CHROME_ALLOW_ALL 옵션)
  +-- tmpfs: /tmp, /run, /home/node (쓰기 가능하지만 임시)
  +-- Playwright 캐시: /opt/ms-playwright (이미지 레이어에 영구 저장)
  +-- /downloads (호스트에 바인드 마운트, 쓰기 가능, 신뢰하지 않음)
```

## 기능

- **KasmVNC 시각적 접근**: 클립보드 및 파일 전송을 지원하는 최신 HTML5 브라우저 기반 VNC
- **Playwright 자동화**: Claude Code가 `headless: false`로 CDP를 통해 Chromium 제어
- **보안 강화**: `--read-only` FS, `--cap-drop ALL`, `no-new-privileges`, tmpfs 마운트
- **네트워크 격리**: 허용 목록이 있는 iptables 방화벽 + 선택적 `CHROME_ALLOW_ALL` 모드
- **자동 OAuth 주입**: macOS Keychain에서 Claude Code 자격 증명을 컨테이너로 주입
- **tmux 세션**: Claude 프로세스가 종료 후에도 유지되며, 재연결하여 재개 가능
- **다운로드 디렉토리**: Chrome에서 다운로드한 파일이 호스트의 `./downloads/`에 저장됨
- **컨테이너 이름 지정**: `{folder-name}-{path-hash}-browser` 형식 (예: `myproject-a3f1c-browser`)
- **CDP 접근**: Chrome DevTools Protocol이 포트 9222로 노출되어 호스트에서 프로그래밍 방식으로 제어 가능

## 환경 변수

- `ANTHROPIC_API_KEY`: Claude API 키 (OAuth 대신 사용 가능)
- `BROWSER_IMAGE`: 사용자 정의 이미지 이름 (팀 공유를 위한 레지스트리 경로)
- `CHROME_ALLOW_ALL`: `1`로 설정하면 모든 HTTP/HTTPS 트래픽 허용 (기본값: `1`)

## 사용자 상호작용 흐름

1. `python3 browser.py run .`을 실행하여 컨테이너 시작
2. 호스트 브라우저에서 `http://localhost:6901`을 열어 KasmVNC 확인 (비밀번호 불필요)
3. Claude Code가 tmux 세션을 통해 컨테이너 내부에서 자동 시작
4. Claude Code가 `headless: false`로 Playwright Chromium 실행
5. Chromium이 KasmVNC 웹 UI에 나타남 - 실시간으로 자동화 관찰
6. 수동 작업이 필요한 경우(로그인, CAPTCHA), KasmVNC를 통해 Chrome과 상호작용
7. 수동 작업 완료 후 Claude Code에게 계속하라고 지시
8. 다운로드한 파일이 `./downloads/`에 나타남 (UNTRUSTED로 취급)

## 보안 모델

- 컨테이너는 PID 네임스페이스, 파일시스템 격리, 네트워크 격리 제공
- `--read-only` FS는 지속적인 멀웨어 방지
- `--cap-drop ALL + NET_ADMIN`은 커널 공격 표면 최소화
- `no-new-privileges`는 권한 상승 방지
- `--pids-limit 500`은 포크 폭탄 방지
- `--memory 4g`는 호스트에 대한 OOM 공격 방지
- 다운로드는 `./downloads/`로 격리됨 (신뢰할 수 없는 것으로 취급)
- 에이전트 인젝션은 컨테이너 샌드박스를 벗어날 수 없음

## 단계

1. 사용자의 의도 파악 (run / list / stop / remove / build)
2. Docker 설치 확인 (`docker --version`)
3. Bash 도구를 통해 적절한 명령 실행
4. VNC 접근 URL을 포함한 결과를 사용자에게 표시

## 참고 사항

- 컨테이너는 `--dangerously-skip-permissions` 모드로 Claude를 실행합니다 (컨테이너 격리로 인해 안전)
- Claude Code는 tmux 세션에서 자동 시작되며, 컨테이너 내부에서 `tmux attach -t claude`로 재연결 가능
- Chromium은 `--no-sandbox` 플래그를 사용하며, 컨테이너 자체가 샌드박스이므로 안전합니다
- KasmVNC 인증이 비활성화됨 (localhost 전용 접근); 비밀번호 불필요
- KasmVNC는 기존의 Xvfb + x11vnc + websockify + noVNC 스택을 단일 바이너리로 대체합니다
- 방화벽이 적용되지 않는 환경에서도 Docker 네트워크 격리가 기본 보호 제공
- zsh, fzf, ripgrep, jq, tmux와 같은 개발 도구가 사전 설치되어 있습니다
