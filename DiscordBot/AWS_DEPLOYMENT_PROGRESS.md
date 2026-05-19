# AWS Deployment Progress & Troubleshooting

**Date Started:** May 19, 2026  
**Current Status:** In Progress - Running bot and Django server

---

## Completed Steps

### ✅ Instance Setup
- Created EC2 t2.micro instance (free tier)
- Ubuntu 24.04 LTS
- Security group configured with SSH (port 22) and custom TCP (port 8000)
- Key pair created: `discord-bot-key.pem` (.pem format)
- Instance launched successfully
- **Issue:** Initially used wrong IP (private IP 172.31.37.142 instead of public IP 18.218.128.141)
- **Fix:** Used public IPv4 address `18.218.128.141` for SSH connection

### ✅ Virtual Environment & Dependencies
- Created Python virtual environment: `venv`
- Activated virtual environment
- Installed Python packages:
  - discord.py
  - yt-dlp
  - aiohttp
  - python-dotenv
  - django
  - djangorestframework
  - django-cors-headers
  - pyodbc
  - django-mssql-backend

### ✅ Repository Clone
- Cloned GitHub repo: `git clone https://github.com/t-manuel2095/DiscordBot.git`
- All latest code available on AWS instance

### ✅ Environment Variables
- Created `.env` file in `~/DiscordBot`
- Configured variables:
  - DISCORD_BOT_TOKEN
  - DJANGO_SECRET_KEY
  - DATABASE_HOST: `10.0.0.29` (local PC IP)
  - DATABASE_PORT: `1433`
  - DATABASE_NAME: `discordbot`
  - DATABASE_USER: `mt`
  - DATABASE_PASSWORD: `nfltop100`

### ✅ Django Settings
- Updated `~/DiscordBot/DiscordBot/DiscordBot/settings.py`
- Added `from dotenv import load_dotenv` and `load_dotenv()`
- Configured DATABASES to use `os.getenv()` for all connection parameters
- MSSQL engine configured with ODBC Driver 17

---

## Issues Encountered & Solutions

### Issue 1: Key Pair Mismatch
**Problem:** Created instance with .ppk key, then deleted and created .pem key separately  
**Solution:** Terminated old instance, created new one with .pem key selected during launch  
**Status:** ✅ Resolved

### Issue 2: SSH Connection Timeout
**Problem:** Used private IP instead of public IP for SSH connection  
**Solution:** Used public IPv4 address from AWS console  
**Status:** ✅ Resolved

### Issue 3: Missing requirements.txt
**Problem:** Repository doesn't have requirements.txt  
**Solution:** Installed packages manually via pip  
**Status:** ✅ Resolved

### Issue 4: ODBC Driver Installation
**Problem:** `apt-key` deprecated, GPG key verification failed for Microsoft repository  
**Attempted Solutions:**
1. `sudo apt-key add` - Failed (command not found)
2. `sudo tee /etc/apt/trusted.gpg.d/microsoft.asc` - Failed (GPG verification)
3. `sudo wget` to install GPG key - Failed (filetype unsupported)

**Current Status:** ⏳ Skipping ODBC driver install for now (pyodbc already installed)  
**Note:** May need to revisit if database connection fails

---

## Current Location on AWS
```
(venv) ubuntu@ip-172-31-47-76:~/DiscordBot$
```

---

## Next Steps

### Step 1: Start Django Server & Bot
```bash
# Start Django server (in background)
nohup python manage.py runserver 0.0.0.0:8000 &

# Start Discord bot (in background)
nohup python -u bot/main.py &

# Check if processes are running
ps aux | grep python
```

### Step 2: Test Database Connection
- Check if bot connects to local MSSQL database
- Monitor bot logs for connection errors
- If connection fails, investigate ODBC driver issue

### Step 3: Test Bot Functionality
- Verify bot appears online in Discord
- Test `/pplay` command
- Test queue management commands
- Verify audio playback

### Step 4: Keep Bot Running 24/7
- Use Screen or Systemd (see AWS_DEPLOYMENT_GUIDE.md)
- Set up monitoring

---

## Key Information

**AWS Instance:**
- Instance ID: `i-0299ac4c09df7d1e9`
- Public IP: `18.218.128.141`
- Instance Type: t2.micro (free tier)
- Region: us-east-2c
- Status: Running ✅

**Local PC Database:**
- Host: `10.0.0.29`
- Port: `1433`
- Database: `discordbot`
- User: `mt`
- Driver: ODBC Driver 17 for SQL Server

**SSH Connection:**
```bash
ssh -i discord-bot-key.pem ubuntu@18.218.128.141
```

---

## Troubleshooting Reference

If you need to revisit ODBC driver installation:
- See AWS_DEPLOYMENT_GUIDE.md Step 7
- Consider alternative: Install SQL Server native client tools
- Or: Use pymssql instead of pyodbc (if needed)

---

**Last Updated:** May 19, 2026 - 2:17 PM UTC-5  
**Next Checkpoint:** Start Django server and Discord bot
