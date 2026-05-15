# Discord Music Bot - Setup & Invite Guide

## Prerequisites

Before you start, make sure you have:
- Python 3.12+ installed
- Git installed
- Bot token from Discord Developer Portal (if creating a new bot)
- MSSQL Server running or connection string ready

---

## Part 1: Invite Bot to Discord Server

### Step 1: Get the Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click on your bot application (or create new if needed)
3. Go to **Settings → Bot** section
4. Copy the **TOKEN** (keep this secret!)
5. Save it in your `.env` file:
   ```
   DISCORD_BOT_TOKEN=your_token_here
   ```

### Step 2: Generate OAuth2 Invite Link
1. In Developer Portal, go to **OAuth2 → URL Generator**
2. Select scopes: `bot`
3. Select permissions:
   - Read Messages/View Channels ✓
   - Send Messages ✓
   - Connect ✓
   - Speak ✓
   - Use Voice Activity ✓
4. Copy the generated URL
5. Paste URL in browser and select the server to invite bot to

### Step 3: Enable Required Intents
1. In Developer Portal, go to **Settings → Bot**
2. Enable these **Privileged Gateway Intents:**
   - Message Content Intent ✓
   - Server Members Intent ✓
   - Voice States ✓

### Step 4: Verify Bot is in Server
- Go to your Discord server
- You should see the bot in the member list
- Bot should show as "Offline" until you start it

---

## Part 2: Start the Services

### Prerequisites Check
- [ ] Python 3.12+ installed
- [ ] MSSQL Server running and accessible
- [ ] `.env` file configured with:
  - `DISCORD_BOT_TOKEN`
  - `DJANGO_SECRET_KEY`
  - Database connection string

### Step 1: Start Django API Server

Open **PowerShell** and navigate to the project:

```powershell
cd C:\Users\Manuel\source\repos\DiscordBot\DiscordBot
```

Activate virtual environment:

```powershell
python -m pipenv shell
```

Run Django server:

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**Keep this window open!** The API server must stay running.

### Step 2: Start Discord Bot

Open **another PowerShell window** and navigate to project:

```powershell
cd C:\Users\Manuel\source\repos\DiscordBot\DiscordBot
```

Activate virtual environment:

```powershell
python -m pipenv shell
```

Run the bot with unbuffered output:

```powershell
python -u bot/main.py
```

You should see:
```
[*] Running setup_hook()
[+] Loaded cog: queue_commands
[+] Loaded cog: voice_commands
[+] Synced 10 slash command(s) globally
Our bot#XXXX has connected to Discord!
```

**Keep this window open!** Bot must stay running to respond to commands.

---

## Part 3: Test the Bot

### Step 1: Join a Voice Channel
- In Discord, join any voice channel in your server
- Bot should be available to use

### Step 2: Try a Command
Type in any text channel:

```
/play https://www.youtube.com/watch?v=VIDEO_ID
```

Expected response:
```
▶️ Now playing: [Song Title]
[+ Bot joins your voice channel]
[+ Audio starts playing]
```

### Step 3: Try Other Commands

```
/queue                    # Show queue
/pause                    # Pause music
/resume                   # Resume music
/skip                     # Skip to next song
/repeat                   # Repeat current song
/remove <position>        # Remove song from queue
/clear                    # Clear entire queue
/leave                    # Bot leaves channel
/nowplaying              # Show current song
```

---

## Quick Reference: Daily Startup

### Every time you want to use the bot:

**Terminal 1 - Django Server:**
```powershell
cd C:\Users\Manuel\source\repos\DiscordBot\DiscordBot
python -m pipenv shell
python manage.py runserver
```

**Terminal 2 - Discord Bot:**
```powershell
cd C:\Users\Manuel\source\repos\DiscordBot\DiscordBot
python -m pipenv shell
python -u bot/main.py
```

**In Discord:**
- Join voice channel
- Use `/play <YouTube URL>`
- Enjoy! 🎵

---

## Troubleshooting

### Bot doesn't appear in Discord
- Check that you enabled Privileged Intents in Developer Portal
- Check that bot has permission to "Connect" and "Speak"
- Restart Discord client (close completely, reopen)

### "Could not join channel" error
- Make sure you have FFmpeg installed
- Check you're in a voice channel (bot can only play in voice channels)
- Verify bot has "Connect" and "Speak" permissions

### "Cannot find youtube video" error
- Make sure URL is a valid YouTube link
- Try: `https://www.youtube.com/watch?v=VIDEO_ID`
- Song must be under 10 minutes

### "Failed to add song to queue" error
- Make sure Django server is running (check Terminal 1)
- Check database connection in `.env`
- Restart both Django and bot

### Bot says "Not connected to voice"
- Make sure you're in a voice channel
- Try `/play` command (it auto-joins)
- If still fails, manually have bot `/leave` and try again

### Audio not playing (but bot appears to work)
- Make sure FFmpeg is installed and in PATH
- Restart bot
- Check YouTube video is accessible (not region-blocked)

### Bot doesn't respond to commands
- Bot must be running (check Terminal 2)
- Make sure you typed `/` correctly (slash command)
- Commands might need to sync - wait 30 seconds and try again
- Close Discord completely and reopen

---

## Environment Variables (`.env` file)

Create a `.env` file in `DiscordBot/` directory:

```
DISCORD_BOT_TOKEN=your_bot_token_here
DJANGO_SECRET_KEY=your_secret_key_here
DB_ENGINE=mssql
DB_NAME=DiscordBot
DB_USER=sa
DB_PASSWORD=your_password
DB_HOST=DESKTOP-AB3PKMH\SQLEXPRESS01
DB_PORT=1433
```

---

## Commands Overview

| Command | Purpose | Example |
|---------|---------|---------|
| `/play <url>` | Queue and play song | `/play https://youtu.be/dQw4w9WgXcQ` |
| `/queue` | Show queue | Shows songs waiting to play |
| `/skip` | Skip current song | Goes to next song immediately |
| `/pause` | Pause music | Bot stays in channel |
| `/resume` | Resume paused music | Continues from where paused |
| `/repeat` | Repeat current song | Song plays again after |
| `/remove <pos>` | Remove song from queue | `/remove 2` removes position 2 |
| `/clear` | Clear entire queue | Deletes all queued songs |
| `/nowplaying` | Show current song | Shows what's playing + who added it |
| `/leave` | Bot leaves channel | Clears queue and disconnects |

---

## Important Notes

⚠️ **Keep Terminals Open**
- Both Django server and bot terminals must stay open
- If you close either, bot stops working
- Look for errors in terminal if bot misbehaves

⚠️ **Audio Requirements**
- FFmpeg must be installed on your computer
- YouTube videos must be accessible (not region-blocked)
- Audio streams expire after ~6 hours (re-extract by replaying)

⚠️ **Database**
- MSSQL Server must be running
- Database must exist and migrations must be run
- Check `.env` file for correct connection details

⚠️ **Permissions**
- Bot needs "Connect", "Speak", "Send Messages" permissions
- You need "Manage Server" to add bot to server
- Voice channel permissions must allow bot to connect

---

## Next Steps

1. ✅ Bot running locally? Great!
2. 📦 **Next:** Deploy to cloud (see `DEPLOYMENT_OPTIONS.md`)
3. 🚀 Bot runs 24/7 without your computer being on

---

## Support

If bot stops working:
1. Check Terminal 1 - is Django running?
2. Check Terminal 2 - any error messages?
3. Restart both services
4. Check `AUDIO_PLAYBACK_TROUBLESHOOTING.md` for audio issues
5. Check `SLASH_COMMANDS_TROUBLESHOOTING.md` for command issues

---

**Current Commands Available:** 10 slash commands ✓  
**Bot Status:** Ready to use on any server! 🎵
