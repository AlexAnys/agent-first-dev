"""Tests for GitHub client functions."""

import pytest
import httpx
from datetime import datetime

from ..server.github_client import (
    get_today_title,
    find_issue_by_title,
    create_issue,
    add_comment,
    get_or_create_daily_issue,
    add_daily_comment,
)


class TestGetTodayTitle:
    """Phase 1: 날짜 제목 생성 테스트"""
    
    def test_get_today_title_format(self):
        """반환값이 'YYYY년 M월 D일 (요일) Daily Issue' 형식인지 확인"""
        title = get_today_title()
        
        # 오늘 날짜 정보
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day
        
        # 형식 검증
        assert f"{year}년" in title
        assert f"{month}월" in title
        assert f"{day}일" in title
        assert "Daily Issue" in title
        assert "(" in title and ")" in title  # 요일 괄호 포함
    
    def test_get_today_title_weekday_korean(self):
        """요일이 한글로 표시되는지 확인"""
        title = get_today_title()
        
        korean_weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        has_weekday = any(f"({wd})" in title for wd in korean_weekdays)
        
        assert has_weekday, f"요일이 포함되지 않음: {title}"
    
    def test_get_today_title_returns_string(self):
        """문자열을 반환하는지 확인"""
        title = get_today_title()
        
        assert isinstance(title, str)
        assert len(title) > 0


class TestFindIssueByTitle:
    """Phase 2: 이슈 검색 테스트"""
    
    def test_find_issue_by_title_found(self, httpx_mock):
        """제목이 일치하는 이슈가 있으면 이슈 정보 반환"""
        # Mock 응답 설정
        mock_response = [
            {
                "number": 42,
                "title": "2026년 1월 6일 (월) Daily Issue",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/42"
            },
            {
                "number": 41,
                "title": "2026년 1월 5일 (일) Daily Issue",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/41"
            }
        ]
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=mock_response
        )
        
        # 함수 호출
        result = find_issue_by_title("owner", "repo", "2026년 1월 6일 (월) Daily Issue")
        
        # 검증
        assert result is not None
        assert result["number"] == 42
        assert result["title"] == "2026년 1월 6일 (월) Daily Issue"
    
    def test_find_issue_by_title_not_found(self, httpx_mock):
        """제목이 일치하는 이슈가 없으면 None 반환"""
        # Mock 응답 설정 (다른 제목의 이슈들만 있음)
        mock_response = [
            {
                "number": 41,
                "title": "2026년 1월 5일 (일) Daily Issue",
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/41"
            }
        ]
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=mock_response
        )
        
        # 함수 호출
        result = find_issue_by_title("owner", "repo", "2026년 1월 6일 (월) Daily Issue")
        
        # 검증
        assert result is None
    
    def test_find_issue_by_title_empty_list(self, httpx_mock):
        """이슈가 하나도 없으면 None 반환"""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=[]
        )
        
        result = find_issue_by_title("owner", "repo", "2026년 1월 6일 (월) Daily Issue")
        
        assert result is None


class TestCreateIssue:
    """Phase 3: 이슈 생성 테스트"""
    
    def test_create_issue_success(self, httpx_mock):
        """이슈 생성 성공 시 이슈 정보 반환"""
        mock_response = {
            "number": 43,
            "title": "2026년 1월 6일 (월) Daily Issue",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/43",
            "body": "Daily issue body",
            "labels": [{"name": "daily"}]
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues",
            json=mock_response,
            status_code=201
        )
        
        result = create_issue(
            owner="owner",
            repo="repo",
            title="2026년 1월 6일 (월) Daily Issue",
            body="Daily issue body"
        )
        
        assert result is not None
        assert result["number"] == 43
        assert result["title"] == "2026년 1월 6일 (월) Daily Issue"
        assert result["labels"][0]["name"] == "daily"
    
    def test_create_issue_without_body(self, httpx_mock):
        """body 없이 이슈 생성"""
        mock_response = {
            "number": 44,
            "title": "2026년 1월 6일 (월) Daily Issue",
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/44",
            "body": None
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues",
            json=mock_response,
            status_code=201
        )
        
        result = create_issue(
            owner="owner",
            repo="repo",
            title="2026년 1월 6일 (월) Daily Issue"
        )
        
        assert result is not None
        assert result["number"] == 44
    
    def test_create_issue_api_error(self, httpx_mock):
        """API 에러 시 예외 발생"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues",
            json={"message": "Not Found"},
            status_code=404
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            create_issue(
                owner="owner",
                repo="repo",
                title="2026년 1월 6일 (월) Daily Issue"
            )


class TestAddComment:
    """Phase 4: 댓글 추가 테스트"""
    
    def test_add_comment_success(self, httpx_mock):
        """댓글 추가 성공"""
        mock_response = {
            "id": 12345,
            "body": "오늘 할 일: 코드 리뷰",
            "html_url": "https://github.com/owner/repo/issues/42#issuecomment-12345",
            "created_at": "2026-01-06T10:00:00Z"
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues/42/comments",
            json=mock_response,
            status_code=201
        )
        
        result = add_comment(
            owner="owner",
            repo="repo",
            issue_number=42,
            body="오늘 할 일: 코드 리뷰"
        )
        
        assert result is not None
        assert result["id"] == 12345
        assert result["body"] == "오늘 할 일: 코드 리뷰"
    
    def test_add_comment_invalid_issue(self, httpx_mock):
        """존재하지 않는 이슈에 댓글 시 에러"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues/9999/comments",
            json={"message": "Not Found"},
            status_code=404
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            add_comment(
                owner="owner",
                repo="repo",
                issue_number=9999,
                body="댓글 내용"
            )
    
    def test_add_comment_empty_body(self, httpx_mock):
        """빈 댓글 시 에러"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues/42/comments",
            json={"message": "Validation Failed"},
            status_code=422
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            add_comment(
                owner="owner",
                repo="repo",
                issue_number=42,
                body=""
            )


class TestGetOrCreateDailyIssue:
    """Phase 5: 오늘 이슈 조회/생성 통합 테스트"""
    
    def test_get_or_create_daily_issue_exists(self, httpx_mock):
        """이슈가 이미 존재하면 해당 이슈 반환"""
        today_title = get_today_title()
        
        # 이슈 목록 조회 mock (이슈 존재)
        mock_issues = [
            {
                "number": 42,
                "title": today_title,
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/42"
            }
        ]
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=mock_issues
        )
        
        result = get_or_create_daily_issue("owner", "repo")
        
        assert result is not None
        assert result["number"] == 42
        assert result["title"] == today_title
    
    def test_get_or_create_daily_issue_creates(self, httpx_mock):
        """이슈가 없으면 새로 생성"""
        today_title = get_today_title()
        
        # 이슈 목록 조회 mock (이슈 없음)
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=[]
        )
        
        # 이슈 생성 mock
        mock_created_issue = {
            "number": 43,
            "title": today_title,
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/43",
            "labels": [{"name": "daily"}]
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues",
            json=mock_created_issue,
            status_code=201
        )
        
        result = get_or_create_daily_issue("owner", "repo")
        
        assert result is not None
        assert result["number"] == 43
        assert result["title"] == today_title


class TestAddDailyComment:
    """Phase 6: 오늘 이슈에 댓글 추가 통합 테스트"""
    
    def test_add_daily_comment_success(self, httpx_mock):
        """오늘 이슈 찾아서 댓글 추가 성공"""
        today_title = get_today_title()
        
        # 이슈 목록 조회 mock (이슈 존재)
        mock_issues = [
            {
                "number": 42,
                "title": today_title,
                "state": "open",
                "html_url": "https://github.com/owner/repo/issues/42"
            }
        ]
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=mock_issues
        )
        
        # 댓글 추가 mock
        mock_comment = {
            "id": 12345,
            "body": "오늘 할 일 완료!",
            "html_url": "https://github.com/owner/repo/issues/42#issuecomment-12345"
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues/42/comments",
            json=mock_comment,
            status_code=201
        )
        
        result = add_daily_comment("owner", "repo", "오늘 할 일 완료!")
        
        assert result is not None
        assert result["comment"]["id"] == 12345
        assert result["comment"]["body"] == "오늘 할 일 완료!"
        assert result["issue"]["number"] == 42
    
    def test_add_daily_comment_creates_issue_if_not_exists(self, httpx_mock):
        """이슈가 없으면 생성 후 댓글 추가"""
        today_title = get_today_title()
        
        # 이슈 목록 조회 mock (이슈 없음)
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=all&per_page=100",
            json=[]
        )
        
        # 이슈 생성 mock
        mock_created_issue = {
            "number": 43,
            "title": today_title,
            "state": "open",
            "html_url": "https://github.com/owner/repo/issues/43",
            "labels": [{"name": "daily"}]
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues",
            json=mock_created_issue,
            status_code=201
        )
        
        # 댓글 추가 mock
        mock_comment = {
            "id": 12346,
            "body": "첫 댓글!",
            "html_url": "https://github.com/owner/repo/issues/43#issuecomment-12346"
        }
        httpx_mock.add_response(
            method="POST",
            url="https://api.github.com/repos/owner/repo/issues/43/comments",
            json=mock_comment,
            status_code=201
        )
        
        result = add_daily_comment("owner", "repo", "첫 댓글!")
        
        assert result is not None
        assert result["comment"]["id"] == 12346
        assert result["issue"]["number"] == 43
