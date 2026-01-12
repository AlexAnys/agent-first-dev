# Warp vs Claude Code 비교 및 Warp 활용 가이드

## Warp vs Claude Code

### Claude Code
- **특징**: CLI 기반 Agent
- **기술 스택**: Python/Node 기반 CLI, LLM API 기반
- **실행 방식**: Terminal 창 안에서 실행되는 Process
- **작동 방식**: Active Agent로 목표를 주면 자동으로 작업 수행
- **가능한 작업**: 파일 수정/생성/삭제, 터미널 명령어 직접 실행
- **모니터링**: CLI Tab을 지켜보며 상태 관리 필요
- **장점**: 작업 속도가 빠름
- **단점**: API 토큰 비용 발생

### Warp
- **특징**: 터미널 에뮬레이터
- **기술 스택**: Rust 기반, 자체 UI 엔진 탑재
- **실행 방식**: OS 위에 실행되는 창
- **장점**:
  - 매우 빠른 성능 (Rust 기반)
  - 변경 사항 검토 시 별도 App 없이 Warp 내에서 확인 가능
  - 복잡한 쿼리에 대해 계획 제안 가능
  - Toast 알림으로 Agent 작업 상태 파악 가능
  - `@`를 통해 특정 심볼(코드라인) 참조 가능 → 구체적인 질문 가능
- **가격**: 무료 (AI 기능은 제한 존재, 유료 구독 필요)
- **AI 모델**: Claude를 포함한 여러 AI model 사용 가능
- **성능**: Warp + GPT의 성능 및 품질이 매우 높고 일관적

### 주요 차이점

| 항목 | Claude Code | Warp |
|------|-------------|------|
| **구조** | OS ↔ Terminal ↔ Shell (zsh) ↔ Claude | OS ↔ Warp ↔ Agent |
| **UI** | CLI 기반 | 자체 UI 엔진 (마우스 클릭, 드래그 가능) |
| **환경 변수** | Non-interactive Shell (환경 독립적) | Interactive Shell (개인화된 환경 사용) |
| **AI 기능** | Agent 측면에서 강함 | 터미널 앱으로 사용하기에 최적화 |

### 환경 변수 문제

- **Claude Code**: Non-interactive Shell 사용 → 시스템 설정이나 환경 변수 문제 발생 가능
- **Warp**: Interactive Shell 사용 → Shell의 개인화된 환경을 모두 읽어 환경 변수 문제 발생 없음

→ 각각의 지향점이 다르기 때문에 발생한 차이

---

## Shell의 개념

- **Shell**: Kernel과 User 사이의 통역사 역할
- **Terminal vs Shell**:
  - **Terminal**: 검은 화면을 보여주고 키보드 입력을 받는 window
  - **Shell**: Terminal 안에서 실제로 돌아가는 software

---

## How Warp uses Warp to build Warp

Warp 팀의 AI 기능 활용 내부 지침 및 가이드라인

### The Mandate

- 모든 코딩 작업은 Warp에 프롬프트를 입력하는 것으로 시작
- 10분이 지나도 안되면 멈추고 피드백 채널에 신고
- Warp 실패 시 Claude나 Cursor 등 타 툴 사용
- 그래도 안되면 손코딩

→ **MultiThread 개발 가능**

### Guidelines

1. **결과물 책임은 본인에게 있음**
   - AI가 짠 코드도 본인이 짠 것처럼 완벽하게 이해해야 함
   - 주석, 테스트, 컨벤션 등 모든 면에서 손코딩과 동급이어야 함

2. **결과를 요구하지 말고 설계를 지시**
   - ❌ BAD: "기능 만들어줘" → 쓰레기
   - ✅ GOOD: "데이터 모델은 ~~게 하고 API는 ~~ 쓰고, Test는 ~~ 배치해서 만들어줘"
   - **설계는 인간이 하고 구현만 AI에게 시키자**

3. **One-Shot 기피**
   - 작고 독립적인 단위로 쪼개서 일을 시키고, 중간중간 계속 확인
   - **TDD를 통해 AI가 딴 길로 새는 것을 막자**

4. **AI에게 계획을 물어보자**
   - 무작정 코드부터 짜게 하지 말고 구현 계획을 물어보고 평가

### Tips

1. **Rules**
   - 린트 규칙, 임포트 순서는 Warp Drive에 규칙으로 박아두자

2. **MCP 적극 활용**
   - Sentry, Linear, Notion 등을 연동
   - 에러나 이슈 발생 시 AI가 직접 로그를 가져오고, 이슈 PR을 할 수 있도록 설정

3. **Multi-instance**
   - 프로젝트를 여러 개 복사해두고, 터미널 창 여러 개 띄워서 병렬로 작업
   - Git WorkTree 활용

---

## Git WorkTree

### 개념
- Multi-Agent 작업 시 편리함
- 각 agent 별로 git clone을 일일히 하는 것은 용량, 환경설정 측에서 비효율적

### 활용 방법
- Git WorkTree를 활용해 `.git`은 하나만 공유하면서 작업 폴더만 여러 개 생성
- 서로 다른 branch를 동시에 켜놓고 수정 가능

### 장점
- 용량 절약 (`.git` 폴더 공유)
- 환경설정 효율성
- 병렬 작업 가능
