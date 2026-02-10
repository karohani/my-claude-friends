---
name: claude-container
description: This skill should be used when the user asks to "run claude in docker", "container", "컨테이너", "docker claude", "sandbox", "샌드박스", "격리 실행", "claude container", "devcontainer", or wants to run Claude Code inside a Docker container for safe isolated execution.
version: 1.0.0
user-invocable: true
---

# Claude Container

Docker 컨테이너에서 Claude Code를 안전하게 실행하는 매니저.
단일 스크립트(`claude.py`)로 .devcontainer 생성, 이미지 빌드, 컨테이너 관리를 모두 처리한다.

## Prerequisites

- Docker Desktop 또는 Docker Engine이 설치되어 있어야 한다
- macOS의 경우 호스트 OAuth 자격증명을 자동 주입한다

## Script Location

스크립트 경로: `${pluginDir}/scripts/claude.py`

## Usage

사용자의 요청에 따라 적절한 명령을 Bash 도구로 실행한다.

### 실행

```bash
# 현재 프로젝트에서 Claude 컨테이너 시작
python3 ${pluginDir}/scripts/claude.py run .

# 특정 프로젝트 경로로 실행
python3 ${pluginDir}/scripts/claude.py run ~/my-project

# zsh 셸로 접속 (Claude 실행 없이)
python3 ${pluginDir}/scripts/claude.py run -s
```

### 관리

```bash
# 실행 중인 컨테이너 목록
python3 ${pluginDir}/scripts/claude.py list

# 컨테이너에 셸 접속
python3 ${pluginDir}/scripts/claude.py shell [이름]

# 정지
python3 ${pluginDir}/scripts/claude.py stop [이름]

# 전체 정지
python3 ${pluginDir}/scripts/claude.py stopall

# 컨테이너 + 볼륨 제거
python3 ${pluginDir}/scripts/claude.py rm <이름>

# 전체 정리 (컨테이너 + 볼륨 + 이미지)
python3 ${pluginDir}/scripts/claude.py clean
```

### 빌드/공유

```bash
# 이미지만 빌드
python3 ${pluginDir}/scripts/claude.py build

# 레지스트리 푸시 (CLAUDE_IMAGE 환경변수 필요)
python3 ${pluginDir}/scripts/claude.py push

# 레지스트리에서 풀
python3 ${pluginDir}/scripts/claude.py pull
```

## Features

- **자동 .devcontainer 생성**: Dockerfile, 방화벽 스크립트, devcontainer.json 자동 생성
- **네트워크 격리**: iptables 방화벽으로 Anthropic API, GitHub 등 필수 도메인만 허용
- **OAuth 자동 주입**: macOS Keychain에서 Claude Code 자격증명을 컨테이너에 주입
- **tmux 세션**: exit해도 Claude 프로세스 유지, 재접속 시 이어서 사용
- **컨테이너 이름**: `{폴더명}-{경로hash5자}` 형식 (예: `imoogi-a3f1c`)

## Environment Variables

- `ANTHROPIC_API_KEY`: Claude API 키 (OAuth 대신 사용 가능)
- `CLAUDE_IMAGE`: 커스텀 이미지 이름 (팀 공유 시 레지스트리 경로)

## Steps

1. 사용자의 의도를 파악한다 (실행/목록/정지/제거/빌드)
2. Docker 설치 여부를 확인한다 (`docker --version`)
3. 적절한 명령을 Bash 도구로 실행한다
4. 결과를 사용자에게 보여준다

## Notes

- 컨테이너는 `--dangerously-skip-permissions` 모드로 Claude를 실행한다 (컨테이너 격리로 안전)
- 방화벽이 적용되지 않는 환경에서도 Docker 네트워크 격리로 기본 보호됨
- zsh, fzf, ripgrep, jq, tmux 등 개발 도구가 사전 설치됨
