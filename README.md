# Discord Server Builder Discord Companion Bot

Automated Discord server builder & manager for Discord Server Builder CTF platform.

## Features
- Auto-provisions Discord server structure (roles, channels, permissions)
- Admin portal for config management (create/delete/rename channels, roles, webhooks)
- JSON-based config (import/export for easy migration)
- Slash commands for admins
- Webhook support for event notifications

## Quick Start

### Prerequisites
- Discord Bot Token (get from https://discord.com/developers/applications)
- Docker & Docker Compose (or Python 3.11+)

### Setup

1. **Extract the zip**
```bash
unzip discord-server-builder-companion.zip
cd discord-server-builder-companion
```

2. **Add your Discord token to .env**
```bash
# .env file already exists, just edit it:
nano .env
# Set: DISCORD_BOT_TOKEN=your_actual_token_here
```

3. **Start with Docker**
```bash
docker compose up -d
```

Portal: http://localhost:5000
Bot: Runs in container (will wait for token if not provided)

4. **Configure via Portal**
- Go to http://localhost:5000
- Set Discord Server Builder API URL & token (in Config tab)
- Customize roles, channels, permissions
- Click `/setup` in Discord to build the server
- OR use portal commands to manage everything

5. **Local setup (no Docker)**

Bot (Terminal 1):
```bash
cd bot
pip install -r requirements.txt
python main.py
```

Portal (Terminal 2):
```bash
cd portal
pip install -r requirements.txt
python app.py
```

## Usage

### Admin Portal
- **Config**: Set CTF API URL & token
- **Channels**: Add/delete/rename channels
- **Roles**: Add/delete roles with colors
- **Permissions**: Set role permissions per category
- **Webhooks**: Add event webhooks (solves, first blood, etc.)
- **Import/Export**: Backup & restore full configuration

### Slash Commands (in Discord)
- `/setup` - Build the server
- `/rebuild` - Rebuild from scratch
- `/sync` - Sync with CTF API
- `/wh_add <trigger> <url>` - Add webhook
- `/wh_list` - List webhooks
- `/wh_del <id>` - Delete webhook

## File Structure
```
discord-server-builder-companion/
├── bot/                 - Discord bot (Python)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── portal/              - Admin panel (Flask)
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   ├── requirements.txt
│   └── Dockerfile
├── config/              - Shared config & state
│   ├── cfg.json         - Main config
│   ├── webhooks.json    - Webhooks list
│   └── state.json       - Last sync state
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration (cfg.json)

```json
{
  "api": {
    "url": "http://discord-server-builder:3000/api/v1",
    "token": "YOUR_API_TOKEN"
  },
  "roles": {
    "Organizer": "#DC143C",
    "Player": "#1E90FF",
    "Spectator": "#808080"
  },
  "chans": {
    "GENERAL": ["announcements", "rules", "general-chat"],
    "CHALLENGES": ["challenges", "hints-and-help"]
  },
  "perms": {
    "GENERAL": {
      "Organizer": {"view": true, "send": true},
      "Player": {"view": true, "send": true}
    }
  }
}
```

## API Endpoints (Bot)
- `GET /health` - Health check
- `GET /cfg` - Get current config

## Notes
- Bot requires full Discord admin permissions
- Config is JSON-based for easy migration
- All changes via portal are reflected in bot immediately
- Webhooks fire on configurable events

## Troubleshooting

**Bot won't start**
- Check DISCORD_BOT_TOKEN in .env
- Verify token is valid in Discord Developer Portal

**Portal can't reach bot**
- Check docker-compose.yml networks
- Ensure both containers running: `docker ps`

**Config not syncing**
- Verify config/ directory exists and is writable
- Check file permissions

## License
MIT
