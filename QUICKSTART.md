# [PLACEHOLDER] Bot - Quick Start Guide

## 5-Minute Setup

### 1. Get Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → name it "[PLACEHOLDER]"
3. Go to "Bot" tab → "Add Bot"
4. Copy the token (click "Copy" button)
5. Enable these intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Voice States Intent

### 2. Clone & Configure
```bash
cd [PLACEHOLDER]-bot
cp .env.example .env
```

Edit `.env`:
```
DISCORD_TOKEN=your_token_here
OWNER_ID=your_discord_id_here
COMMAND_PREFIX=!
```

### 3. Get Your Discord ID
- Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
- Right-click yourself → Copy User ID
- Paste into `.env` as `OWNER_ID`

### 4. Install & Run
```bash
pip install -r requirements.txt
python main.py
```

✅ Bot should be online!

### 5. Invite to Server
1. In Developer Portal → OAuth2 → URL Generator
2. Scopes: `bot`
3. Permissions:
   - ✅ Send Messages
   - ✅ Manage Messages
   - ✅ Manage Roles
   - ✅ Manage Channels
   - ✅ Manage Voice Channels
   - ✅ Kick Members
   - ✅ Ban Members
   - ✅ Moderate Members
4. Copy URL → open in browser → select server → authorize

✅ Done! Bot is in your server.

## Testing Commands

```bash
# Set auto-role
!autorole @NewMembers

# Test moderation
!kick @testuser test reason
!ban @testuser test reason
!timeout @testuser 5 test reason

# Test VoiceMaster
!createvc My Channel
# Then use buttons in the embed to manage it

# Purge messages
!purge 10
```

## Quaxly Deployment (After Testing Locally)

### Using systemd (Recommended)
```bash
# SSH into server
ssh user@quaxly-server.com

# Clone bot
git clone <repo-url>
cd [PLACEHOLDER]-bot

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
nano .env  # Add your token and config
```

Create `/etc/systemd/system/placeholder-bot.service`:
```ini
[Unit]
Description=[PLACEHOLDER] Discord Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/[PLACEHOLDER]-bot
Environment="PATH=/home/botuser/[PLACEHOLDER]-bot/venv/bin"
ExecStart=/home/botuser/[PLACEHOLDER]-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable placeholder-bot
sudo systemctl start placeholder-bot
sudo systemctl status placeholder-bot
```

### Using Docker
```bash
docker-compose up -d
docker-compose logs -f
```

## Quick Command Reference

| Command | What It Does | Example |
|---------|-------------|---------|
| `!autorole` | Set auto-role for new members | `!autorole @NewMember` |
| `!ban` | Ban a user | `!ban @user spam` |
| `!kick` | Kick a user | `!kick @user spam` |
| `!timeout` | Timeout a user (minutes) | `!timeout @user 5 spam` |
| `!purge` | Delete last X messages | `!purge 10` |
| `!createvc` | Create voice channel | `!createvc Gaming Room` |
| `!vcinfo` | Get voice channel info | `!vcinfo` |

## Troubleshooting

**Bot won't start?**
- Check `.env` has valid `DISCORD_TOKEN`
- Try: `python -c "import discord; print(discord.__version__)"`

**Commands not working?**
- Verify bot has permissions in the server
- Check bot role is high enough (manage-able roles for ban/kick/timeout)

**Voice channels not deleting?**
- Check bot has "Manage Channels" permission

## Need Help?

Check `README.md` for full documentation.
