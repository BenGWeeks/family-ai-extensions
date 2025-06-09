"""
Final integration test for all Synthesis Tracker components.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append('.')

# Test all major components
def test_all_components():
    print("🧪 Running comprehensive integration test...\n")
    
    # Test 1: Database functionality
    print("1️⃣ Testing Database...")
    from shared.storage_utils import StudyProgressDB
    
    db = StudyProgressDB(":memory:")
    
    # Add multiple study sessions
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        db.save_study_session({
            "date": date,
            "logged_in": True,
            "study_time_minutes": 20 + (i * 5),  # Increasing time
            "lessons_completed": [f"Lesson {i+1}"]
        })
    
    # Test retrieval
    today = datetime.now().strftime("%Y-%m-%d")
    session = db.get_study_session(today)
    assert session is not None, "Should have today's session"
    
    # Test weekly stats
    stats = db.get_weekly_stats()
    assert stats["days_logged_in"] == 7, f"Expected 7 days, got {stats['days_logged_in']}"
    
    # Test streak
    streak = db.get_current_streak()
    assert streak >= 7, f"Expected streak >= 7, got {streak}"
    
    print("   ✅ Database tests passed")
    
    # Test 2: Email utilities
    print("2️⃣ Testing Email Utilities...")
    from shared.email_utils import SynthesisEmailMonitor
    
    monitor = SynthesisEmailMonitor("test.com", 993, "test@test.com", "pass")
    
    # Test code extraction
    test_emails = [
        {"subject": "Synthesis Login", "body": "Your code: ABC123", "date": "2024-01-15"},
        {"subject": "Verification", "body": "Login code: XYZ789", "date": "2024-01-14"}
    ]
    
    code = monitor.extract_synthesis_code(test_emails)
    assert code == "ABC123", f"Expected ABC123, got {code}"
    
    print("   ✅ Email utilities tests passed")
    
    # Test 3: Notification system
    print("3️⃣ Testing Notification System...")
    from shared.notification_utils import NotificationManager
    
    notifier = NotificationManager()
    
    # Test message formatting
    reminder = notifier.format_study_reminder(streak=5)
    assert "5-Day" in reminder["title"], "Should include streak in title"
    
    achievement = notifier.format_achievement_notification("new_streak", 10)
    assert "10-Day" in achievement["title"], "Should include streak value"
    
    summary = notifier.format_progress_summary({
        "total_minutes": 150,
        "days_logged_in": 6,
        "current_streak": 4
    })
    assert "6 days" in summary and "150 minutes" in summary, "Should include stats"
    
    print("   ✅ Notification system tests passed")
    
    # Test 4: Configuration
    print("4️⃣ Testing Configuration...")
    sys.path.append('./synthesis-tracker')
    from config import SynthesisConfig
    
    # Test with environment variables
    os.environ["EMAIL_USERNAME"] = "test@example.com"
    os.environ["STUDY_GOAL_MINUTES"] = "45"
    
    config = SynthesisConfig()
    assert config.email_username == "test@example.com", "Should read env vars"
    assert config.study_goal_minutes == 45, "Should parse int values"
    
    print("   ✅ Configuration tests passed")
    
    print("\n🎉 All integration tests passed!")
    print("\n📊 Summary:")
    print(f"   • Database: Tested sessions, stats, and streak calculation")
    print(f"   • Email: Tested code extraction from multiple email formats")
    print(f"   • Notifications: Tested reminder, achievement, and summary formatting")
    print(f"   • Configuration: Tested environment variable loading and parsing")
    print(f"\n✅ The Synthesis Tracker is ready for deployment!")


async def test_async_functionality():
    """Test async components."""
    print("\n5️⃣ Testing Async Functionality...")
    
    # Import the mock server
    sys.path.append('.')
    from test_server_simple import SimpleSynthesisTracker
    
    tracker = SimpleSynthesisTracker()
    
    # Test async tool calls
    tools = await tracker.get_tools()
    assert len(tools) >= 2, "Should have at least 2 tools"
    
    # Test with mock data
    result = await tracker.call_tool("check_synthesis_login")
    assert "logged_in_today" in result, "Should return login status"
    
    result = await tracker.call_tool("get_study_progress", {"date": "2024-01-15"})
    assert "date" in result, "Should return progress data"
    
    print("   ✅ Async functionality tests passed")


if __name__ == "__main__":
    # Run synchronous tests
    test_all_components()
    
    # Run async tests
    asyncio.run(test_async_functionality())
    
    print(f"\n🚀 Ready to commit and deploy the Synthesis Tracker!")
    print(f"   Next steps:")
    print(f"   1. Install dependencies: pip install -r requirements.txt")
    print(f"   2. Setup email forwarding for Synthesis codes")
    print(f"   3. Configure .env file with credentials")
    print(f"   4. Install mcpo for Open WebUI integration") 
    print(f"   5. Add tools to Whiskers agent in Open WebUI")