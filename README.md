# Discord Server Builder

Automated Discord server structure builder with admin portal. Creates roles, channels, categories, permissions, and styled welcome messages with a single command.

## Features

- **Auto-provisions** complete Discord server structure (roles, channels, categories, permissions)
- **Styled channel names** with emojis (e.g., `📢・announcements`, `💬・general-chat`)
- **Welcome messages** automatically posted and pinned to each channel
- **Clean pins** - removes the "pinned a message" notification automatically
- **Admin portal** for config management via web UI
- **Nuke command** to wipe everything and start fresh
- **JSON-based config** for easy backup/migration

## Quick Start

### Prerequisites

- Discord Bot Token ([get one here](https://discord.com/developers/applications))
- Docker & Docker Compose

### Setup

1. **Clone the repo**
```bash
git clone https://github.com/oOz0n3Oo/DiscordServerBuild.git
cd DiscordServerBuild
```

2. **Add your Discord token**
```bash
nano .env
# Set: DISCORD_BOT_TOKEN=your_actual_token_here
```

3. **Start with Docker**
```bash
docker compose up -d
```

4. **Invite bot to your server** with these permissions:
   - Administrator (recommended), OR:
   - Manage Roles
   - Manage Channels
   - View Channels
   - Send Messages
   - Manage Messages
   - Read Message History

5. **Run `/setup` in Discord** to build the server

## Slash Commands

| Command | Description |
|---------|-------------|
| `/setup` | Build server structure from config (roles, channels, permissions, messages) |
| `/nuke` | Delete ALL channels, categories, and roles - complete clean slate |

Both commands require Administrator permission.

## Admin Portal

Access at **http://localhost:5000**

Default login: `admin` / `changeme`

### Portal Features

- **Config** - Edit API settings
- **Messages** - Customize welcome messages per channel
- **Channels** - Add/remove channels and categories
- **Roles** - Add/remove roles with custom colors
- **Permissions** - Set role permissions per category
- **Webhooks** - Configure event webhooks
- **Import/Export** - Backup and restore full configuration

## File Structure

```
DiscordServerBuild/
├── bot/
│   ├── main.py           # Discord bot code
│   ├── requirements.txt  # Python dependencies (py-cord)
│   └── Dockerfile
├── portal/
│   ├── app.py            # Flask admin panel
│   ├── requirements.txt  # Python dependencies (Flask)
│   ├── Dockerfile
│   └── templates/
│       ├── index.html    # Admin dashboard
│       └── login.html    # Login page
├── config/
│   ├── cfg.json          # Roles, channels, permissions config
│   ├── messages.json     # Channel welcome messages
│   ├── auth.json         # Portal authentication
│   └── webhooks.json     # Webhook configurations
├── docker-compose.yml
├── .env                  # Discord bot token (create this)
├── .env.example
└── .gitignore
```

## Configuration

### cfg.json

Defines roles, channels, and permissions:

```json
{
  "roles": {
    "Founder": "#FF1744",
    "Core Team": "#2196F3",
    "Moderator": "#FF9800"
  },
  "chans": {
    "「 PUBLIC 」": [
      "📢・announcements",
      "👋・welcome",
      "📜・rules"
    ],
    "「 VOICE 」": [
      "🎙️・general-voice"
    ]
  },
  "perms": {
    "「 PUBLIC 」": {
      "Founder": {"view": true, "send": true},
      "Moderator": {"view": true, "send": true}
    }
  }
}
```

### messages.json

Defines welcome messages for each channel:

```json
{
  "messages": {
    "📢・announcements": "📢 **ANNOUNCEMENTS**\nOfficial updates posted here.",
    "👋・welcome": "👋 **Welcome!**\nRead the rules and have fun!"
  }
}
```

## Bot Permissions

### Required Discord Permissions

- **Manage Roles** - Create and assign roles
- **Manage Channels** - Create categories and channels
- **View Channels** - Access channels
- **Send Messages** - Post welcome messages
- **Manage Messages** - Pin messages and delete pin notifications
- **Read Message History** - Check for existing messages

### Required Intents

Enable these in [Discord Developer Portal](https://discord.com/developers/applications) → Bot:

- ✅ Server Members Intent
- ✅ Message Content Intent

## Troubleshooting

### Bot won't start

- Check `DISCORD_BOT_TOKEN` in `.env` file
- Verify token is valid in Discord Developer Portal
- Check logs: `docker compose logs bot`

### "Could not get server info" error

- Bot needs Administrator permission or the specific permissions listed above
- Re-invite the bot with correct permissions
- Make sure intents are enabled in Developer Portal

### Slash commands not showing

- Wait 1-2 minutes for Discord to sync commands
- Try kicking and re-inviting the bot
- Restart the bot: `docker compose restart bot`

### Portal can't connect

- Check both containers are running: `docker compose ps`
- Verify port 5000 is not in use: `lsof -i :5000`
- Check logs: `docker compose logs portal`

### Channels/roles not created

- Bot role must be higher than roles it's creating
- Check bot has Manage Roles and Manage Channels permissions
- Check logs for specific errors: `docker compose logs bot`

### Pin notification not deleted

- Bot needs Manage Messages permission
- Check message history permission

### Config changes not applying

- Restart the bot after config changes: `docker compose restart bot`
- Or run `/setup` again (it skips existing items)

## Local Development (No Docker)

**Bot:**
```bash
cd bot
pip install -r requirements.txt
export DISCORD_BOT_TOKEN=your_token
python main.py
```

**Portal:**
```bash
cd portal
pip install -r requirements.txt
python app.py
```

## License

MIT
