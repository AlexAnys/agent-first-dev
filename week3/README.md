# Week 3 - GitHub Daily Issue MCP Server

GitHub Daily Issue를 자동으로 관리하는 MCP(Model Context Protocol) 서버입니다. 오늘 날짜의 이슈를 조회/생성하고 댓글을 추가할 수 있습니다.

---

## Project Overview

이 MCP 서버는 GitHub API를 래핑하여 Daily Issue 관리를 자동화합니다. STDIO transport를 사용하며, Claude Desktop 또는 Cursor에서 연결하여 사용할 수 있습니다.

### Key Features

- 오늘 날짜 형식의 Daily Issue 자동 생성 (예: "2026년 1월 6일 (월) Daily Issue")
- 기존 Daily Issue가 있으면 조회, 없으면 자동 생성
- Daily Issue에 댓글 추가
- "daily" 라벨 자동 부착

### Project Structure

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP 서버 진입점
│   ├── github_client.py     # GitHub API 클라이언트
│   └── config.py            # 환경변수 설정
├── tests/
│   ├── __init__.py
│   └── test_github_client.py
├── .env                     # 환경변수 (GitHub 토큰)
└── README.md
```

---

## Prerequisites

- Python 3.12
- Conda (Anaconda or Miniconda)
- Poetry
- GitHub Personal Access Token (repo 권한 필요)

---

## Installation

### Step 1: Conda 환경 활성화

```bash
conda activate cs146s
```

### Step 2: 의존성 설치

프로젝트 루트에서:

```bash
poetry install --no-interaction
```

### Step 3: 환경변수 설정

`week3/.env` 파일을 생성하고 GitHub 토큰을 설정하세요:

```
GITHUB_TOKEN=your_github_personal_access_token

# Optional: 기본 저장소 설정
GITHUB_DEFAULT_OWNER=sejong-rcv
GITHUB_DEFAULT_REPO=2026.Internship.MultimodalRAG
```

**GitHub Personal Access Token 발급 방법:**

1. GitHub 접속 -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. "Generate new token (classic)" 클릭
3. 권한 선택: `repo` (Full control of private repositories) 체크
4. 토큰 생성 후 복사

---

## Running the Server

### 직접 실행

프로젝트 루트에서:

```bash
poetry run python -m week3.server.main
```

서버가 STDIO 입력을 기다리는 상태로 실행됩니다.

### MCP Inspector로 테스트

```bash
cd week3
mcp dev server/main.py
```

---

## MCP Client Configuration

### Cursor 설정

`~/.cursor/mcp.json` 파일에 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "github-daily-issue": {
      "command": "/opt/anaconda3/envs/cs146s/bin/python",
      "args": ["-m", "week3.server.main"],
      "cwd": "/Users/bagminsu/Dev/multimodal_rag_internship",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here",
        "PYTHONPATH": "/Users/bagminsu/Dev/multimodal_rag_internship"
      }
    }
  }
}
```

설정 후 Cursor를 재시작하면 MCP 서버가 연결됩니다.

### Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일에 추가:

```json
{
  "mcpServers": {
    "github-daily-issue": {
      "command": "poetry",
      "args": ["run", "python", "-m", "week3.server.main"],
      "cwd": "/Users/bagminsu/Dev/multimodal_rag_internship",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

---

## Tool Reference

### 1. get_or_create_today_issue

오늘 날짜의 Daily Issue를 조회하거나 생성합니다.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| owner | string | Yes | GitHub 저장소 소유자 (예: "sejong-rcv") |
| repo | string | Yes | 저장소 이름 (예: "2026.Internship.MultimodalRAG") |

**Example Input:**

```json
{
  "owner": "sejong-rcv",
  "repo": "2026.Internship.MultimodalRAG"
}
```

**Example Output:**

```json
{
  "success": true,
  "issue": {
    "number": 5,
    "title": "2026년 1월 6일 (월) Daily Issue",
    "state": "open",
    "url": "https://github.com/sejong-rcv/2026.Internship.MultimodalRAG/issues/5"
  }
}
```

**Behavior:**
- 오늘 날짜 제목의 이슈가 있으면 해당 이슈 정보 반환
- 없으면 새 이슈 생성 후 반환 (라벨: "daily")

---

### 2. add_comment_to_today_issue

오늘 날짜의 Daily Issue에 댓글을 추가합니다.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| owner | string | Yes | GitHub 저장소 소유자 |
| repo | string | Yes | 저장소 이름 |
| comment | string | Yes | 추가할 댓글 내용 (마크다운 지원) |

**Example Input:**

```json
{
  "owner": "sejong-rcv",
  "repo": "2026.Internship.MultimodalRAG",
  "comment": "## 오늘 한 일\n- [x] MCP 서버 구현\n- [x] 테스트 작성"
}
```

**Example Output:**

```json
{
  "success": true,
  "issue": {
    "number": 5,
    "title": "2026년 1월 6일 (월) Daily Issue",
    "url": "https://github.com/sejong-rcv/2026.Internship.MultimodalRAG/issues/5"
  },
  "comment": {
    "id": 12345,
    "body": "## 오늘 한 일\n- [x] MCP 서버 구현\n- [x] 테스트 작성",
    "url": "https://github.com/sejong-rcv/2026.Internship.MultimodalRAG/issues/5#issuecomment-12345"
  }
}
```

**Behavior:**
- 오늘 Daily Issue가 없으면 자동으로 생성
- 마크다운 형식의 댓글 지원

---

## Running Tests

### 전체 테스트 실행

```bash
poetry run pytest week3/tests/ -v
```

### 특정 테스트 파일 실행

```bash
poetry run pytest week3/tests/test_github_client.py -v
```

### 테스트 구조

테스트는 httpx mock을 사용하여 실제 GitHub API 호출 없이 진행됩니다:

- `TestGetTodayTitle` - 날짜 제목 생성 테스트
- `TestFindIssueByTitle` - 이슈 검색 테스트
- `TestCreateIssue` - 이슈 생성 테스트
- `TestAddComment` - 댓글 추가 테스트
- `TestGetOrCreateDailyIssue` - 통합 테스트 (조회/생성)
- `TestAddDailyComment` - 통합 테스트 (댓글 추가)

---

## Error Handling

### API 에러

- HTTP 4xx/5xx 에러 시 `success: false`와 에러 메시지 반환
- 네트워크 타임아웃: 기본 30초, `REQUEST_TIMEOUT` 환경변수로 조정 가능

### Rate Limit

GitHub API는 시간당 5,000 요청으로 제한됩니다. Rate limit 초과 시 에러 메시지가 반환됩니다.

### 인증 에러

`GITHUB_TOKEN`이 설정되지 않았거나 유효하지 않으면 에러가 반환됩니다.

---

## Configuration

환경변수는 `week3/.env` 파일 또는 MCP 클라이언트 설정에서 지정할 수 있습니다:

| Variable | Description | Default |
|----------|-------------|---------|
| GITHUB_TOKEN | GitHub Personal Access Token | (필수) |
| GITHUB_DEFAULT_OWNER | 기본 저장소 소유자 | "" |
| GITHUB_DEFAULT_REPO | 기본 저장소 이름 | "" |
| REQUEST_TIMEOUT | API 요청 타임아웃 (초) | 30 |

---

## Example Invocation Flow

### Cursor에서 사용하기

1. Cursor 설정에 MCP 서버 추가 (위의 설정 참고)
2. Cursor 재시작
3. 채팅에서 요청:
   - "오늘 Daily Issue 확인해줘"
   - "오늘 이슈에 '작업 완료' 댓글 달아줘"

### 예시 대화

```
User: 오늘 Daily Issue 있는지 확인해줘