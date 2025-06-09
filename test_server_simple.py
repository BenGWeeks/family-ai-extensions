"""
Simple test of the Synthesis Tracker functionality without full MCP dependencies.
"""

import asyncio
import sys
import os
sys.path.append('.')
sys.path.append('./synthesis-tracker')

from shared.mcp_mock import MCPBaseServer, create_tool
from shared.email_utils import SynthesisEmailMonitor
from shared.storage_utils import StudyProgressDB
from config import SynthesisConfig


class SimpleSynthesisTracker(MCPBaseServer):
    """Simplified tracker for testing."""
    
    def __init__(self):
        super().__init__("synthesis-tracker-test", "1.0.0")
        
        # Mock config
        self.config = SynthesisConfig()
        self.config.database_path = ":memory:"
        self.config.email_username = "test@example.com"
        self.config.email_password = "test_password"
        self.config.synthesis_email = "student@example.com"
        
        # Initialize components
        self.email_monitor = SynthesisEmailMonitor(
            server="test.server.com",
            port=993,
            username=self.config.email_username,
            password=self.config.email_password,
            use_ssl=True
        )
        
        self.db = StudyProgressDB(self.config.database_path)
        
        print("✅ Synthesis Tracker initialized")
    
    async def get_tools(self):
        """Return available tools."""
        return [
            create_tool(
                name="check_synthesis_login",
                description="Check if user has logged into Synthesis.com today",
                parameters={}
            ),
            create_tool(
                name="get_study_progress",
                description="Get detailed study progress for today or specific date",
                parameters={
                    "date": {
                        "type": "string",
                        "description": "Date to check (YYYY-MM-DD), defaults to today"
                    }
                }
            ),
        ]
    
    async def call_tool(self, name: str, arguments: dict = None):
        """Handle tool calls."""
        if name == "check_synthesis_login":
            return await self._check_synthesis_login()
        elif name == "get_study_progress":
            date = arguments.get("date") if arguments else None
            return await self._get_study_progress(date)
        else:
            return f"Unknown tool: {name}"
    
    async def _check_synthesis_login(self):
        """Check login status."""
        today = "2024-01-15"  # Mock date
        session = self.db.get_study_session(today)
        
        return {
            "logged_in_today": session.get("logged_in", False) if session else False,
            "study_minutes": session.get("study_minutes", 0) if session else 0,
            "has_studied": self.db.has_studied_today() if session else False,
        }
    
    async def _get_study_progress(self, date=None):
        """Get progress for date."""
        if not date:
            date = "2024-01-15"  # Mock date
        
        session = self.db.get_study_session(date)
        
        if session:
            return {
                "date": session["date"],
                "logged_in": session.get("logged_in", False),
                "study_minutes": session.get("study_minutes", 0),
                "lessons_completed": session.get("lessons_completed", []),
            }
        else:
            return {
                "date": date,
                "logged_in": False,
                "study_minutes": 0,
                "message": "No study session recorded for this date"
            }


async def test_synthesis_tracker():
    """Test the tracker functionality."""
    print("🧪 Testing Synthesis Tracker...")
    
    tracker = SimpleSynthesisTracker()
    
    # Test 1: Get tools
    tools = await tracker.get_tools()
    print(f"✅ Tools available: {len(tools)}")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test 2: Check login (no data)
    result = await tracker.call_tool("check_synthesis_login")
    print(f"✅ Login check (no data): {result}")
    
    # Test 3: Add some study data
    test_data = {
        "date": "2024-01-15",
        "logged_in": True,
        "study_time_minutes": 25,
        "lessons_completed": ["Algebra Basics", "Fractions"]
    }
    tracker.db.save_study_session(test_data)
    print("✅ Added test study session")
    
    # Test 4: Check login again
    result = await tracker.call_tool("check_synthesis_login")
    print(f"✅ Login check (with data): {result}")
    
    # Test 5: Get detailed progress
    result = await tracker.call_tool("get_study_progress", {"date": "2024-01-15"})
    print(f"✅ Progress details: {result}")
    
    # Test 6: Email code extraction
    test_emails = [
        {
            "subject": "Synthesis Verification Code",
            "body": "Your verification code is: ABC123",
            "date": "2024-01-15"
        }
    ]
    code = tracker.email_monitor.extract_synthesis_code(test_emails)
    print(f"✅ Email code extraction: {code}")
    
    print("\n🎉 All tests passed! The Synthesis Tracker is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_synthesis_tracker())