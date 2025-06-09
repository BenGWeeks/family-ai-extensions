"""
Tests for Synthesis Tracker MCP server.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synthesis_tracker.server import SynthesisTrackerServer
from shared.storage_utils import StudyProgressDB
from shared.email_utils import SynthesisEmailMonitor


class TestSynthesisTrackerServer:
    """Test the main MCP server functionality."""
    
    @pytest.fixture
    def server(self):
        """Create test server instance."""
        with patch('synthesis_tracker.server.config') as mock_config:
            mock_config.database_path = ":memory:"
            mock_config.email_server = "test.server.com"
            mock_config.email_port = 993
            mock_config.email_username = "test@example.com"
            mock_config.email_password = "test_password"
            mock_config.email_use_ssl = True
            mock_config.synthesis_email = "student@example.com"
            mock_config.headless_browser = True
            mock_config.study_goal_minutes = 30
            mock_config.minimum_study_minutes = 15
            
            return SynthesisTrackerServer()
    
    @pytest.mark.asyncio
    async def test_get_tools(self, server):
        """Test that tools are properly defined."""
        tools = await server.get_tools()
        
        assert len(tools) == 6
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "check_synthesis_login",
            "get_study_progress", 
            "get_weekly_summary",
            "send_study_reminder",
            "get_current_streak",
            "force_update_progress"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_check_synthesis_login_no_data(self, server):
        """Test login check with no existing data."""
        result = await server.call_tool("check_synthesis_login", {})
        
        assert isinstance(result, dict)
        assert result["logged_in_today"] is False
        assert result["study_minutes"] == 0
        assert result["has_studied"] is False
    
    @pytest.mark.asyncio
    async def test_get_study_progress_no_data(self, server):
        """Test progress retrieval with no data."""
        result = await server.call_tool("get_study_progress", {})
        
        assert isinstance(result, dict)
        assert result["logged_in"] is False
        assert result["study_minutes"] == 0
        assert "No study session recorded" in result["message"]
    
    @pytest.mark.asyncio
    async def test_send_study_reminder(self, server):
        """Test sending study reminder."""
        result = await server.call_tool("send_study_reminder", {})
        
        assert isinstance(result, dict)
        assert result["reminder_sent"] is True
        assert "message" in result
        assert result["todays_reminder_count"] == 1
    
    @pytest.mark.asyncio
    async def test_get_current_streak(self, server):
        """Test streak calculation."""
        result = await server.call_tool("get_current_streak", {})
        
        assert isinstance(result, dict)
        assert "current_streak" in result
        assert "recent_activity" in result
        assert isinstance(result["recent_activity"], list)


class TestStudyProgressDB:
    """Test database functionality."""
    
    @pytest.fixture
    def db(self):
        """Create test database."""
        return StudyProgressDB(":memory:")
    
    def test_save_and_get_session(self, db):
        """Test saving and retrieving study sessions."""
        test_data = {
            "date": "2024-01-15",
            "logged_in": True,
            "study_time_minutes": 45,
            "lessons_completed": ["Algebra Basics", "Fractions"],
            "streak_days": 5,
            "total_points": 150
        }
        
        # Save session
        success = db.save_study_session(test_data)
        assert success is True
        
        # Retrieve session
        session = db.get_study_session("2024-01-15")
        assert session is not None
        assert session["logged_in"] is True
        assert session["study_minutes"] == 45
        assert session["lessons_completed"] == ["Algebra Basics", "Fractions"]
    
    def test_current_streak_calculation(self, db):
        """Test streak calculation logic."""
        # Add consecutive study days
        for i in range(5):
            date = f"2024-01-{15+i:02d}"
            db.save_study_session({
                "date": date,
                "logged_in": True,
                "study_time_minutes": 30
            })
        
        streak = db.get_current_streak()
        assert streak == 5
    
    def test_weekly_stats(self, db):
        """Test weekly statistics calculation."""
        # Add study sessions for a week
        for i in range(7):
            date = f"2024-01-{15+i:02d}"
            db.save_study_session({
                "date": date,
                "logged_in": True,
                "study_time_minutes": 30 if i < 5 else 0  # 5 study days
            })
        
        stats = db.get_weekly_stats()
        assert stats["days_logged_in"] == 5
        assert stats["total_minutes"] == 150
        assert stats["avg_minutes"] == 30


class TestEmailMonitor:
    """Test email monitoring functionality."""
    
    @pytest.fixture
    def email_monitor(self):
        """Create test email monitor."""
        return SynthesisEmailMonitor(
            server="test.server.com",
            port=993,
            username="test@example.com", 
            password="test_password"
        )
    
    def test_extract_synthesis_code(self, email_monitor):
        """Test extraction of verification codes from emails."""
        test_emails = [
            {
                "subject": "Synthesis Verification Code",
                "body": "Your verification code is: ABC123",
                "date": "Mon, 15 Jan 2024 10:00:00 +0000"
            },
            {
                "subject": "Login Code",
                "body": "Use this code to log in: XYZ789",
                "date": "Mon, 15 Jan 2024 09:00:00 +0000"
            }
        ]
        
        code = email_monitor.extract_synthesis_code(test_emails)
        assert code == "ABC123"  # Should get the most recent one


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test full workflow integration."""
    with patch('synthesis_tracker.server.config') as mock_config:
        mock_config.database_path = ":memory:"
        mock_config.email_server = "test.server.com"
        mock_config.email_port = 993
        mock_config.email_username = "test@example.com"
        mock_config.email_password = "test_password"
        mock_config.email_use_ssl = True
        mock_config.synthesis_email = "student@example.com"
        mock_config.headless_browser = True
        
        server = SynthesisTrackerServer()
        
        # Test the full workflow
        # 1. Check initial status (no data)
        status = await server.call_tool("check_synthesis_login", {})
        assert status["logged_in_today"] is False
        
        # 2. Simulate adding study data
        server.db.save_study_session({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "logged_in": True,
            "study_time_minutes": 25,
            "lessons_completed": ["Test Lesson"]
        })
        
        # 3. Check status again
        status = await server.call_tool("check_synthesis_login", {})
        assert status["logged_in_today"] is True
        assert status["study_minutes"] == 25
        
        # 4. Get progress
        progress = await server.call_tool("get_study_progress", {})
        assert progress["study_minutes"] == 25
        assert len(progress["lessons_completed"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])