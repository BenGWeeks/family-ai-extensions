# Family AI Extensions

A collection of MCP (Model Context Protocol) servers for family-oriented AI tools and integrations.

## Overview

This repository contains MCP servers that extend AI assistants with family-specific functionality like educational tracking, chore management, and parental monitoring tools.

## MCP Servers

### 🎓 Synthesis Tracker
Monitor and track educational progress on Synthesis.com tutoring platform.

**Features:**
- Daily login verification
- Study time tracking
- Progress notifications
- Automated reminders

**Status:** 🚧 In Development

### 🏠 Chore Tracker (Planned)
Household chore management and allowance tracking.

### 📚 Homework Helper (Planned)
General homework assistance and deadline tracking.

### 📱 Screen Time Monitor (Planned)
Device usage monitoring and parental controls.

## Installation

### Prerequisites
- Python 3.8+
- Open WebUI with MCP support (via mcpo)
- Docker (optional, for containerized deployment)

### Quick Start

```bash
# Clone repository
git clone <repo-url>
cd family-ai-extensions

# Install dependencies
pip install -r requirements.txt

# Run specific MCP server
python synthesis-tracker/server.py
```

### Open WebUI Integration

1. **Install mcpo** (MCP-to-OpenAPI proxy):
   ```bash
   # Follow Open WebUI mcpo installation guide
   ```

2. **Configure MCP servers** in mcpo config:
   ```json
   {
     "mcpServers": {
       "synthesis-tracker": {
         "command": "python",
         "args": ["synthesis-tracker/server.py"]
       }
     }
   }
   ```

3. **Add tools in Open WebUI**:
   - Go to Settings → Tools
   - Add each MCP tool endpoint
   - Configure with Whiskers agent

## Project Structure

```
family-ai-extensions/
├── synthesis-tracker/          # Synthesis.com monitoring
│   ├── server.py              # MCP server implementation
│   ├── synthesis_client.py    # Web automation client
│   ├── email_monitor.py       # Email code extraction
│   └── config.py              # Configuration
├── shared/                    # Common utilities
│   ├── email_utils.py         # Email handling
│   ├── notification_utils.py  # Push notifications
│   ├── storage_utils.py       # Data persistence
│   └── mcp_base.py           # Base MCP server class
├── tests/                     # Test suite
├── docker/                    # Container configurations
└── docs/                      # Documentation
```

## Development

### Adding New MCP Servers

1. Create new directory for your server
2. Implement MCP protocol using `shared/mcp_base.py`
3. Add configuration and documentation
4. Update main README and mcpo config

### Testing

```bash
# Run tests
python -m pytest tests/

# Test specific server
python -m pytest tests/test_synthesis_tracker.py
```

## Security

- All credentials stored in environment variables
- Email access via app-specific passwords
- No sensitive data in logs or git history
- Container isolation for production deployments

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please create GitHub issues with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details