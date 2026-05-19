# AWS Deployment Guide - Discord Music Bot

**Last Updated:** May 19, 2026  
**Status:** Complete beginner guide for AWS free tier

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [AWS Setup (Step-by-Step)](#aws-setup-step-by-step)
4. [Deploying Your Bot](#deploying-your-bot)
5. [Keeping the Bot Running 24/7](#keeping-the-bot-running-247)
6. [Updating Your Code](#updating-your-code)
7. [Cost Breakdown](#cost-breakdown)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## Overview

**What You're Doing:**
- Moving your Django server + Discord bot from your local PC to **AWS EC2** (Amazon's virtual computer service)
- Your bot will run 24/7 on AWS, even when your PC is off
- Your database stays on your local PC (we'll connect to it remotely)
- This uses the **AWS free tier** (no cost for 12 months, with limits)

**Benefits:**
- ✅ Bot runs 24/7 without your PC
- ✅ Your home internet not tied up
- ✅ Professional deployment
- ✅ Free tier covers your usage

**What Stays Local:**
- Your MSSQL database (keeps it simple)
- Your development environment

---

## Prerequisites

**Before Starting, You Need:**

1. ✅ AWS account (you already have this)
2. ✅ Your Discord bot token (you already have this)
3. ✅ Your GitHub repository link (recommended - makes updates easy)
4. ✅ MSSQL database still running on your local PC
5. ✅ Your `.env` file ready (with tokens and secrets)
6. ✅ Basic command line knowledge (we'll use PowerShell/Terminal)

**If you DON'T have GitHub set up yet:**
- Create a repo on GitHub with your DiscordBot code
- This makes deploying updates super easy

---

## AWS Setup (Step-by-Step)

### Step 1: Log Into AWS Console

1. Go to `https://aws.amazon.com`
2. Click "Sign In to the Console"
3. Use your AWS account credentials
4. You're in the **AWS Management Console** (this is the dashboard)

### Step 2: Create an EC2 Instance

An "instance" is just a virtual computer running in AWS.

**Navigate to EC2:**
1. In the search bar at top, type "EC2"
2. Click "EC2" (Elastic Compute Cloud)
3. Click the orange **"Launch Instance"** button

**Configure Your Instance:**

#### Name Your Instance
- **Name:** `discord-bot` (or whatever you want)

#### Choose an Operating System
- Look for **"Ubuntu"** in the list
- Select the **latest Ubuntu LTS version** available (24.04 or 26.04 are both fine)
- Make sure it says "Free tier eligible" next to it
- Click the checkbox next to it

#### Choose Instance Type
- Look for **"t3.micro"** in the list (this is free tier)
- It should say "Eligible for free tier" next to it

#### Key Pair (Important!)
- Click **"Create new key pair"**
- **Key pair name:** `discord-bot-key` (remember this)
- **Key pair type:** RSA
- **Private key file format:** .pem (for Mac/Linux) OR .ppk (for Windows) - Use the OS you chose above, not you're personal machine
- Click **"Create key pair"**
- **SAVE THIS FILE SOMEWHERE SAFE** - you'll need it to connect

#### Security Group
- This controls what can connect to your server
- Click **"Create security group"**
- Click on the edit button to edit name and description
- **Name:** `discord-bot-sg`
- **Description:** "Security group for Discord bot"

**Add Security Group Rules:**
- Click **"Add security group rule"**
- Rule 1:
  - **Type:** SSH
  - **Source:** Anywhere (0.0.0.0/0)
  - (This lets you connect from your PC)
- Rule 2:
  - **Type:** Custom TCP
  - **Port Range:** 8000
  - **Source:** Anywhere (0.0.0.0/0)
  - (This lets your database connect)

#### Storage
- Leave default: **8 GiB** (more than enough for your bot, logs, and dependencies)

#### Review & Launch
- Scroll down and click **"Launch Instance"**
- You'll see a confirmation page
- Click **"View Instance"** or go to the Instances dashboard

### Step 3: Get Your Instance Details

After launching:
1. Your instance will be starting (orange dot = starting, green dot = running)
2. Wait for the green circle (takes ~1 minute)
3. Click on your instance
4. Copy the **"Public IPv4 address"** (looks like: `54.123.45.67`)
5. Save this - you'll need it to connect

---

## Deploying Your Bot

### Step 1: Connect to Your EC2 Instance

You'll use SSH (Secure Shell) to connect from your PC to the AWS server.

**On Windows (PowerShell):**

1. Open PowerShell
2. Navigate to where you saved your key pair:
   ```powershell
   cd C:\path\to\your\key
   ```

3. Connect to your instance:
   ```powershell
   ssh -i discord-bot-key.pem ubuntu@YOUR_PUBLIC_IP_ADDRESS
   ```
   Replace `YOUR_PUBLIC_IP_ADDRESS` with the IP you saved earlier

4. When prompted about "authenticity," type `yes` and press Enter

**You're now connected to your AWS server!** (You'll see `ubuntu@...` in the terminal)

### Step 2: Install Dependencies

Now you're inside your AWS server. Install what you need:

```bash
# Update package manager
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Git (to clone your repository)
sudo apt install -y git

# Install requirements for your bot
sudo apt install -y ffmpeg
```

### Step 3: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your GitHub repo
git clone https://github.com/YOUR_USERNAME/DiscordBot.git
cd DiscordBot
```

### Step 4: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at the start of your terminal line
```

### Step 5: Install Python Dependencies

```bash
# Make sure you're in the DiscordBot directory
pip install -r requirements.txt

# If you don't have requirements.txt, install manually:
pip install discord.py yt-dlp aiohttp python-dotenv django djangorestframework django-cors-headers
```

### Step 6: Set Up Environment Variables

Create a `.env` file on the AWS server:

```bash
# Create .env file
nano .env
```

Paste your variables:
```
DISCORD_TOKEN=your_bot_token_here
DATABASE_HOST=your_local_pc_ip_address
DATABASE_PORT=1433
DATABASE_NAME=DiscordBotDB
DATABASE_USER=sa
DATABASE_PASSWORD=your_password
```

**To find your local PC's IP address:**
- On Windows: Open Command Prompt, type `ipconfig`, look for "IPv4 Address" (usually starts with 192.168...)

Press `Ctrl+X`, then `Y`, then `Enter` to save

### Step 7: Configure Django Settings

Edit your Django settings to use the remote database:

```bash
nano DiscordBot/settings.py
```

Find the DATABASES section and update:
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        }
    }
}
```

Install MSSQL driver:
```bash
sudo apt install -y msodbcsql17 mssql-tools
pip install django-mssql-backend pyodbc
```

### Step 8: Run Your Bot

```bash
# Make sure you're in the DiscordBot directory
# Make sure virtual environment is activated (you see (venv) in terminal)

# Start Django server (in background)
nohup python manage.py runserver 0.0.0.0:8000 &

# Start Discord bot (in background)
nohup python -u bot/main.py &

# Check if processes are running
ps aux | grep python
```

You should see both `manage.py runserver` and `bot/main.py` in the list

---

## Keeping the Bot Running 24/7

### Option 1: Using Screen (Recommended for Beginners)

```bash
# Install screen
sudo apt install -y screen

# Create a new screen session for Django
screen -S django
python manage.py runserver 0.0.0.0:8000

# Press Ctrl+A then D to detach (leaves it running)

# Create a new screen session for bot
screen -S bot
python -u bot/main.py

# Press Ctrl+A then D to detach
```

**Later, to check if they're running:**
```bash
screen -ls
```

**To reconnect to a session:**
```bash
screen -r django
# or
screen -r bot
```

### Option 2: Using Systemd (More Professional)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/discord-bot.service
```

Paste this:
```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/DiscordBot
ExecStart=/home/ubuntu/DiscordBot/venv/bin/python -u bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# Check status
sudo systemctl status discord-bot
```

---

## Updating Your Code

When you make changes locally:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Your message"
   git push
   ```

2. **On your AWS server, pull the updates:**
   ```bash
   # Connect via SSH
   ssh -i discord-bot-key.pem ubuntu@YOUR_PUBLIC_IP

   # Navigate to repo
   cd ~/DiscordBot

   # Pull latest code
   git pull origin main

   # Restart the bot
   # If using screen:
   screen -r bot
   # Press Ctrl+C to stop
   # Run again: python -u bot/main.py
   
   # If using systemd:
   sudo systemctl restart discord-bot
   ```

---

## Cost Breakdown

**AWS Free Tier Includes (for 12 months):**
- ✅ t2.micro EC2 instance: **750 hours/month** (24/7 is ~730 hours, so you're covered!)
- ✅ 30 GB storage: **FREE**
- ✅ 1 GB outbound data transfer: **FREE**
- ✅ Data transfers between AWS and your PC: Minimal cost (~$0.01/GB)

**Realistic Monthly Cost After Free Tier:**
- EC2 (t2.micro): ~$9.50/month
- Data transfer: ~$0.50/month
- **Total: ~$10/month**

**If you want to save money later:**
- Move database to AWS RDS for MSSQL: ~$10-15/month (but more reliable)
- Use a smaller instance: t2.nano (~$5/month)

---

## Troubleshooting

### "Connection refused" error

**Problem:** Bot can't connect to your local database

**Solution:**
1. Make sure MSSQL is running on your local PC
2. Verify the IP address in `.env` is correct
3. Check Windows Firewall allows port 1433
4. Restart MSSQL service on your PC

### Bot crashes immediately

**Solution:**
```bash
# Check logs
tail -f nohup.out

# Or with screen:
screen -r bot  # See the error messages
```

### EC2 instance stopped/terminated

**Solution:**
1. Go to AWS Console > EC2 > Instances
2. Select your instance
3. Click "Start Instance" (if stopped)
4. If terminated, you'll need to launch a new one

### Can't connect to instance via SSH

**Common causes:**
- Security group doesn't allow SSH (port 22)
- Wrong IP address
- Key pair file permissions wrong

**Fix permissions (on your PC):**
```bash
chmod 400 discord-bot-key.pem
```

---

## Next Steps

### Phase 1 (Current)
- ✅ Get bot running on AWS
- ✅ Bot runs 24/7
- ✅ Test that it works

### Phase 2 (Later)
- Move database to AWS RDS (more reliable)
- Set up monitoring/alerts
- Add SSL certificate for Django
- Set up automatic backups

### Phase 3 (Advanced)
- Use Docker containers
- Set up auto-scaling
- Add load balancing

---

## Quick Reference Commands

```bash
# Connect to AWS instance
ssh -i discord-bot-key.pem ubuntu@YOUR_PUBLIC_IP

# Check what's running
ps aux | grep python

# View logs
tail -f nohup.out

# Stop running processes
pkill -f "manage.py runserver"
pkill -f "bot/main.py"

# Start fresh
python manage.py runserver 0.0.0.0:8000 &
python -u bot/main.py &

# View running screen sessions
screen -ls

# Attach to screen session
screen -r [session-name]

# Detach from screen session
# Ctrl+A then D
```

---

## Support & Questions

If you run into issues:

1. **Check AWS console** - Verify instance is running and has public IP
2. **Check security groups** - Make sure ports 22, 8000 are open
3. **Check logs** - Look at terminal output or log files
4. **Verify database connection** - Can your AWS instance reach your local PC?

---

**You're deployed!** Your bot is now running 24/7 on AWS. 🎉
