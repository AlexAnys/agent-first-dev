"""GitHub Daily Issue MCP Server.

STDIO transport를 사용하는 MCP 서버입니다.
Claude Desktop 또는 Cursor에서 연결하여 사용할 수 있습니다.
"""

from __future__ import annotations

import logging
from typing import Any

import sys
from pathlib import Path

# 패키지 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP

from server.config import settings
from server.github_client import get_or_create_daily_issue, add_daily_comment


# 로깅 설정 (STDIO 서버이므로 stderr로 출력)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# MCP 서버 초기화
mcp = FastMCP("GitHub Daily Issue Server")


@mcp.tool()
def get_or_create_today_issue(owner: str, repo: str) -> dict[str, Any]:
    """오늘 날짜의 Daily Issue를 조회하거나 생성합니다.
    
    Args:
        owner: GitHub 저장소 소유자 (예: "sejong-rcv")
        repo: 저장소 이름 (예: "2026.Internship.MultimodalRAG")
        
    Returns:
        오늘의 Daily Issue 정보 (number, title, html_url 등)
    """
    try:
        settings.validate()
        issue = get_or_create_daily_issue(owner, repo)
        return {
            "success": True,
            "issue": {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "url": issue["html_url"]
            }
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Failed to get/create daily issue: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
def add_comment_to_today_issue(owner: str, repo: str, comment: str) -> dict[str, Any]:
    """오늘 날짜의 Daily Issue에 댓글을 추가합니다.
    
    이슈가 없으면 자동으로 생성한 후 댓글을 추가합니다.
    
    Args:
        owner: GitHub 저장소 소유자 (예: "sejong-rcv")
        repo: 저장소 이름 (예: "2026.Internship.MultimodalRAG")
        comment: 추가할 댓글 내용
        
    Returns:
        이슈와 댓글 정보
    """
    try:
        settings.validate()
        
        if not comment.strip():
            return {"success": False, "error": "댓글 내용이 비어있습니다."}
        
        result = add_daily_comment(owner, repo, comment)
        return {
            "success": True,
            "issue": {
                "number": result["issue"]["number"],
                "title": result["issue"]["title"],
                "url": result["issue"]["html_url"]
            },
            "comment": {
                "id": result["comment"]["id"],
                "body": result["comment"]["body"],
                "url": result["comment"]["html_url"]
            }
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Failed to add comment: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # STDIO transport로 서버 실행
    mcp.run()
