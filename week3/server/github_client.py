"""GitHub API client for Daily Issue MCP Server."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx

try:
    from .config import settings
except ImportError:
    from server.config import settings


# 로깅 설정
logger = logging.getLogger(__name__)

# 한글 요일 매핑
KOREAN_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def get_today_title() -> str:
    """오늘 날짜로 Daily Issue 제목 생성.
    
    Returns:
        str: "YYYY년 M월 D일 (요일) Daily Issue" 형식의 제목
        
    Example:
        >>> get_today_title()
        "2026년 1월 6일 (월) Daily Issue"
    """
    today = datetime.now()
    weekday = KOREAN_WEEKDAYS[today.weekday()]
    
    return f"{today.year}년 {today.month}월 {today.day}일 ({weekday}) Daily Issue"


def find_issue_by_title(
    owner: str,
    repo: str,
    title: str
) -> Optional[Dict[str, Any]]:
    """제목으로 이슈 검색.
    
    Args:
        owner: GitHub 저장소 소유자
        repo: 저장소 이름
        title: 검색할 이슈 제목
        
    Returns:
        이슈 정보 딕셔너리 또는 None (찾지 못한 경우)
        
    Raises:
        httpx.HTTPStatusError: API 요청 실패 시
    """
    url = f"{settings.GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"
    params = {"state": "all", "per_page": 100}
    
    try:
        with httpx.Client(timeout=settings.REQUEST_TIMEOUT) as client:
            response = client.get(
                url,
                headers={**settings.get_headers(), "Content-Type": "application/json; charset=utf-8"},
                params=params
            )
            response.raise_for_status()
            
            issues = response.json()
            
            for issue in issues:
                if issue.get("title") == title:
                    logger.info(f"Found issue #{issue['number']}: {title}")
                    return issue
            
            logger.info(f"Issue not found: {title}")
            return None
            
    except httpx.HTTPStatusError as e:
        logger.error(f"GitHub API error: {e.response.status_code}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise


def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """새 이슈 생성.
    
    Args:
        owner: GitHub 저장소 소유자
        repo: 저장소 이름
        title: 이슈 제목
        body: 이슈 본문 (선택)
        labels: 라벨 목록 (기본값: ["daily"])
        
    Returns:
        생성된 이슈 정보 딕셔너리
        
    Raises:
        httpx.HTTPStatusError: API 요청 실패 시
    """
    url = f"{settings.GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"
    
    if labels is None:
        labels = ["daily"]
    
    payload: Dict[str, Any] = {"title": title, "labels": labels}
    if body:
        payload["body"] = body
    
    try:
        with httpx.Client(timeout=settings.REQUEST_TIMEOUT) as client:
            response = client.post(
                url,
                headers={**settings.get_headers(), "Content-Type": "application/json; charset=utf-8"},
                json=payload
            )
            response.raise_for_status()
            
            issue = response.json()
            logger.info(f"Created issue #{issue['number']}: {title}")
            return issue
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to create issue: {e.response.status_code}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise


def add_comment(
    owner: str,
    repo: str,
    issue_number: int,
    body: str
) -> Dict[str, Any]:
    """이슈에 댓글 추가.
    
    Args:
        owner: GitHub 저장소 소유자
        repo: 저장소 이름
        issue_number: 이슈 번호
        body: 댓글 내용
        
    Returns:
        생성된 댓글 정보 딕셔너리
        
    Raises:
        httpx.HTTPStatusError: API 요청 실패 시
    """
    url = f"{settings.GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    payload = {"body": body}
    
    try:
        with httpx.Client(timeout=settings.REQUEST_TIMEOUT) as client:
            response = client.post(
                url,
                headers={**settings.get_headers(), "Content-Type": "application/json; charset=utf-8"},
                json=payload
            )
            response.raise_for_status()
            
            comment = response.json()
            logger.info(f"Added comment to issue #{issue_number}")
            return comment
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to add comment: {e.response.status_code}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise


def get_or_create_daily_issue(
    owner: str,
    repo: str
) -> Dict[str, Any]:
    """오늘 날짜의 Daily Issue를 조회하거나 생성.
    
    1. 오늘 날짜 제목으로 이슈 검색
    2. 있으면 해당 이슈 반환
    3. 없으면 새로 생성 후 반환
    
    Args:
        owner: GitHub 저장소 소유자
        repo: 저장소 이름
        
    Returns:
        오늘의 Daily Issue 정보 딕셔너리
        
    Raises:
        httpx.HTTPStatusError: API 요청 실패 시
    """
    today_title = get_today_title()
    
    # 1. 기존 이슈 검색
    existing_issue = find_issue_by_title(owner, repo, today_title)
    
    if existing_issue:
        logger.info(f"Found existing daily issue: #{existing_issue['number']}")
        return existing_issue
    
    # 2. 없으면 새로 생성
    logger.info(f"Creating new daily issue: {today_title}")
    new_issue = create_issue(owner, repo, today_title)
    
    return new_issue


def add_daily_comment(
    owner: str,
    repo: str,
    body: str
) -> Dict[str, Any]:
    """오늘 날짜의 Daily Issue에 댓글 추가.
    
    1. 오늘 Daily Issue 조회 또는 생성
    2. 해당 이슈에 댓글 추가
    
    Args:
        owner: GitHub 저장소 소유자
        repo: 저장소 이름
        body: 댓글 내용
        
    Returns:
        이슈와 댓글 정보를 포함한 딕셔너리
        {
            "issue": {...},
            "comment": {...}
        }
        
    Raises:
        httpx.HTTPStatusError: API 요청 실패 시
    """
    # 1. 오늘 Daily Issue 조회 또는 생성
    issue = get_or_create_daily_issue(owner, repo)
    
    # 2. 댓글 추가
    comment = add_comment(owner, repo, issue["number"], body)
    
    logger.info(f"Added comment to daily issue #{issue['number']}")
    
    return {
        "issue": issue,
        "comment": comment
    }
