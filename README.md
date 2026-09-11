# [PLACEHOLDER] Discord Bot

A feature-rich Discord bot with moderation, auto-roles, and VoiceMaster functionality.

## Features

### 🎯 Auto-Role System
- Automatically assign roles to new members
- Admin-only command to set the auto-role
- `!autorole @role` - Set the auto-role

### 🛡️ Moderation System
- **Ban** - `!ban @user [reason]`
- **Kick** - `!kick @user [reason]`
- **Timeout** - `!timeout @user <minutes> [reason]`
- **Purge** - `!purge <amount>` (max 100 messages)

### 🎤 VoiceMaster
- Create custom voice channels: `!createvc [name]`
- Interactive voice channel controls:
  - ✏️ Rename
  - 🔒 Lock/🔓 Unlock
  - 🗑️ Delete
- View voice channel info: `!vcinfo`

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. **Clone/Download the bot**
```bash
cd [PLACEHOLDER]-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
```
Edit `.env` and add:
- `DISCORD_TOKEN` - Your bot token from Discord Developer Portal
- `OWNER_ID` - Your Discord user ID
- `COMMAND_PREFIX` - Prefix for commands (default: `!`)

4. **Create Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create New Application
   - Go to "Bot" tab → "Add Bot"
   - Copy the token to `.env`
   - Enable these intents:
     - Message Content Intent
     - Server Members Intent
     - Voice States Intent

5. **Invite Bot to Server**
   - OAuth2 → URL Generator
   - Scopes: `bot`
   - Permissions:
     - Send Messages
     - Manage Messages
     - Manage Roles
     - Manage Channels
     - Manage Voice Channels
     - Kick Members
     - Ban Members
     - Moderate Members
     - Read Message History
   - Copy generated URL and open in browser

## Running the Bot

### Local Development
```bash
python main.py
```

### Quaxly Deployment

#### Option 1: Direct Python (Recommended)

1. **SSH into your Quaxly server**
```bash
ssh user@your-quaxly-server.com
```

2. **Clone the bot**
```bash
git clone <your-repo-url>
cd [PLACEHOLDER]-bot
```

3. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp .env.example .env
nano .env  # Edit with your token and config
```

5. **Run with systemd (auto-restart on reboot)**

Create `/etc/systemd/system/placeholder-bot.service`:
```ini
[Unit]
Description=[PLACEHOLDER] Discord Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/[PLACEHOLDER]-bot
Environment="PATH=/home/your-username/[PLACEHOLDER]-bot/venv/bin"
ExecStart=/home/your-username/[PLACEHOLDER]-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable placeholder-bot
sudo systemctl start placeholder-bot
sudo systemctl status placeholder-bot
```

View logs:
```bash
sudo journalctl -u placeholder-bot -f
```

#### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t placeholder-bot .
docker run -d --name placeholder-bot --env-file .env placeholder-bot
```

## Commands

### Moderation
| Command | Usage | Permission |
|---------|-------|-----------|
| `!ban` | `!ban @user reason` | Admin |
| `!kick` | `!kick @user reason` | Admin |
| `!timeout` | `!timeout @user <minutes> reason` | Admin |
| `!purge` | `!purge <amount>` | Admin |

### Auto-Role
| Command | Usage | Permission |
|---------|-------|-----------|
| `!autorole` | `!autorole @role` | Admin |

### VoiceMaster
| Command | Usage | Permission |
|---------|-------|-----------|
| `!createvc` | `!createvc [name]` | Everyone |
| `!vcinfo` | `!vcinfo` | Everyone |

## Database

The bot uses SQLite for persistent storage:
- Guild settings (auto-role configuration)
- Voice channel ownership tracking
- Automatic cleanup when channels are deleted

Database file: `bot.db` (auto-created)

## Troubleshooting

### Bot Won't Start
- Check `.env` file exists and has valid `DISCORD_TOKEN`
- Verify Python 3.11+ is installed: `python --version`
- Check dependencies: `pip list | grep -E 'discord|python-dotenv'`

### Commands Not Working
- Ensure bot has required permissions in the server
- Check command prefix matches your configuration
- Verify the user running the command has appropriate permissions

### Voice Channel Issues
- Bot needs "Manage Channels" and "Move Members" permissions
- Ensure bot has voice access in the category

### Database Issues
- Delete `bot.db` to reset (warning: loses all data)
- Check file permissions on the server

## Support

For issues or feature requests, contact your bot administrator.

## License

MIT

---

**Note**: Replace `[PLACEHOLDER]` with your final bot name when ready.
