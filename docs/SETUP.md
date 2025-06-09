# Setup Guide - Family AI Extensions

This guide will help you set up the Synthesis Tracker MCP server for integration with Open WebUI and Whiskers.

## Prerequisites

### System Requirements
- Python 3.8+
- Open WebUI v0.6+
- Email account with IMAP access
- Synthesis.com account for your child

### Dependencies Installation

```bash
# Clone the repository
git clone https://github.com/BenGWeeks/family-ai-extensions.git
cd family-ai-extensions

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Email Setup

### 1. Email Forwarding Configuration

Set up email forwarding for Synthesis.com verification codes:

1. **Gmail Rule Example**:
   - Go to Gmail Settings → Filters and Blocked Addresses
   - Create filter: `from:synthesis.com AND subject:verification`
   - Action: Forward to your monitoring email address

2. **Outlook Rule Example**:
   - Go to Outlook Rules
   - Create rule: `From contains "synthesis.com" AND Subject contains "verification"`
   - Forward to monitoring email

### 2. App Password Setup

Create an app password for email access:

**Gmail**:
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate password for "Mail"

**Outlook**:
1. Go to Microsoft Account security
2. Security dashboard → Advanced security options
3. App passwords → Create new password

## Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### Required Settings

```env
# Email Configuration for Login Code Monitoring
EMAIL_SERVER=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your-monitoring-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_USE_SSL=true

# Synthesis.com Credentials
SYNTHESIS_EMAIL=your-child@email.com
SYNTHESIS_URL=https://synthesis.com

# Database Settings
DATABASE_PATH=./synthesis_data.db

# Notification Settings
NOTIFICATION_ENABLED=true
NOTIFICATION_TIMES=09:00,15:00,19:00

# Browser Automation
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30

# Study Goals
MINIMUM_STUDY_MINUTES=15
STUDY_GOAL_MINUTES=30
```

## Open WebUI Integration

### 1. Install mcpo (MCP-to-OpenAPI Proxy)

```bash
# Install mcpo according to Open WebUI documentation
npm install -g @open-webui/mcpo
```

### 2. Configure MCP Server

```bash
# Start mcpo with our configuration
mcpo --config mcpo-config.json --port 3001
```

### 3. Add Tools to Open WebUI

1. Open Open WebUI → Settings → Tools
2. Add new tool server:
   - **URL**: `http://localhost:3001/synthesis-tracker`
   - **Name**: `Synthesis Tracker`
3. Configure each tool endpoint:
   - `check_synthesis_login`
   - `get_study_progress`
   - `get_weekly_summary`
   - `send_study_reminder`
   - `get_current_streak`
   - `force_update_progress`

## Whiskers Integration

### Configure Whiskers Agent

1. Go to Open WebUI → Agents
2. Find or create "Whiskers" agent
3. Add Synthesis Tracker tools to available functions
4. Update system prompt to include study tracking capabilities:

```
You are Whiskers, a friendly AI tutor assistant. You can track study progress on Synthesis.com and send encouraging reminders.

Available functions:
- check_synthesis_login: Check if user studied today
- get_study_progress: Get detailed progress information
- send_study_reminder: Send study reminders
- get_current_streak: Check study streak
- get_weekly_summary: Weekly progress report

Use these tools proactively to encourage consistent study habits.
```

## Testing

### 1. Test Email Monitoring

```bash
# Test email connection
python -c "
from shared.email_utils import SynthesisEmailMonitor
from synthesis_tracker.config import config

monitor = SynthesisEmailMonitor(
    config.email_server, config.email_port,
    config.email_username, config.email_password
)

if monitor.connect():
    print('✅ Email connection successful')
    emails = monitor.search_emails(since_hours=24)
    print(f'Found {len(emails)} recent emails')
else:
    print('❌ Email connection failed')
"
```

### 2. Test Database

```bash
# Test database initialization
python -c "
from shared.storage_utils import StudyProgressDB
from synthesis_tracker.config import config

db = StudyProgressDB(config.database_path)
print('✅ Database initialized successfully')

# Test saving data
test_data = {
    'date': '2024-01-15',
    'logged_in': True,
    'study_time_minutes': 30
}
db.save_study_session(test_data)
print('✅ Database write test successful')
"
```

### 3. Test MCP Server

```bash
# Run server in test mode
python synthesis-tracker/server.py
```

### 4. Run Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_synthesis_tracker.py::TestSynthesisTrackerServer::test_check_synthesis_login_no_data -v
```

## Usage

### Daily Workflow

1. **Automatic Monitoring**: Server checks for login codes in email
2. **Progress Tracking**: When user logs into Synthesis, progress is recorded
3. **Proactive Reminders**: Whiskers sends reminders if no study activity
4. **Weekly Reports**: Summary of study habits and achievements

### Manual Commands (via Whiskers)

```
"Whiskers, did I study today?"
"Show me my weekly progress"
"Send me a study reminder"
"What's my current streak?"
"Force update my progress"
```

## Troubleshooting

### Common Issues

1. **Email Connection Fails**:
   - Verify app password is correct
   - Check if 2FA is enabled
   - Ensure IMAP is enabled

2. **Browser Automation Fails**:
   - Install Playwright browsers: `playwright install`
   - Check if Synthesis.com changed their login flow
   - Try non-headless mode for debugging

3. **Database Errors**:
   - Check file permissions for database path
   - Ensure directory exists
   - Verify SQLite installation

4. **MCP Integration Issues**:
   - Verify mcpo is running on correct port
   - Check Open WebUI tool configuration
   - Review mcpo logs for errors

### Debug Mode

```bash
# Run with debug logging
DEBUG=true LOG_LEVEL=DEBUG python synthesis-tracker/server.py
```

### Screenshots for Debugging

```bash
# Enable screenshots for browser debugging
HEADLESS_BROWSER=false python synthesis-tracker/server.py
```

## Security Considerations

- Store credentials in environment variables only
- Use app passwords, not main account passwords
- Restrict email account permissions to IMAP only
- Regularly rotate app passwords
- Monitor login attempts on email accounts

## Updating

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Playwright browsers
playwright install --force

# Pull latest changes
git pull origin main
```

## Support

For issues and questions:
1. Check this documentation first
2. Review error logs and debug output
3. Create GitHub issue with detailed information
4. Include system information and configuration (without credentials)