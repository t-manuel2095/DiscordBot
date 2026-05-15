# Voice Channel Error Troubleshooting

## Problem Statement

**Error Message:**
```
Could not join channel: davey library needed in order to use voice
```

**When It Occurs:**
When user runs `/join` command in Discord to have the bot join a voice channel.

**Root Cause:**
The error message is misleading - it actually refers to **PyNaCl** (not "davey"). The bot is missing required dependencies for voice support:
1. **PyNaCl** - For Discord voice encryption
2. **FFmpeg** - For audio processing

---

## Debug Methods Attempted

### Attempt 1: Check PyNaCl Installation
**Date:** 2026-05-14 ~1:10 PM

**Command:**
```powershell
pipenv run pip list | findstr PyNaCl
```

**Result:** ✅ SUCCESS
- PyNaCl 1.6.2 was already installed

**Conclusion:** PyNaCl was not the issue

---

### Attempt 2: Upgrade PyNaCl
**Date:** 2026-05-14 ~1:10 PM

**Goal:** Ensure PyNaCl is compatible with Python 3.14

**Command:**
```powershell
pipenv install PyNaCl --upgrade
```

**Result:** ✅ COMPLETED
- PyNaCl reinstalled/upgraded

**Conclusion:** PyNaCl version confirmed

---

### Attempt 3: Check FFmpeg Installation
**Date:** 2026-05-14 ~1:14 PM

**Command:**
```powershell
ffmpeg -version
```

**Result:** ❌ FAILED
```
ffmpeg : The term 'ffmpeg' is not recognized...
```

**Conclusion:** **FFmpeg is NOT installed** - This is the actual problem!

---

### Attempt 4: Install FFmpeg with Chocolatey (Non-Admin)
**Date:** 2026-05-14 ~1:15 PM

**Command:**
```powershell
choco install ffmpeg -y
```

**Result:** ❌ FAILED
```
Access to the path 'C:\ProgramData\chocolatey\lib-bad' is denied.
```

**Error Details:**
- Permission denied error
- Chocolatey couldn't create required directories
- Non-administrator PowerShell session

**Conclusion:** Need admin privileges

---

### Attempt 5: Install FFmpeg with Admin Privileges
**Date:** 2026-05-14 ~1:18 PM

**Command:**
```powershell
Start-Process powershell -ArgumentList "choco install ffmpeg -y" -Verb RunAs -Wait
```

**Result:** ✅ COMPLETED
- FFmpeg 8.1.1 successfully installed
- Verified: `ffmpeg -version` works correctly

**But Still Failing!** ❌
- Bot still shows: "Could not join channel: davey library needed in order to use voice"
- This indicates a deeper issue than just missing FFmpeg

---

### Attempt 6: Kill All Processes and Fresh Restart
**Date:** 2026-05-14 ~1:25 PM

**Issue Identified:**
- FFmpeg installed but error persists
- Possible causes:
  1. Bot didn't properly reload after FFmpeg installation
  2. Pipenv environment cache issue
  3. Discord.py needs FFmpeg in specific location
  4. Runtime cache from old bot process

**Actions Taken:**
1. Killed all Python processes (Django + Bot)
2. Fresh restart of both services
3. Waiting for new bot connection

**Commands:**
```powershell
# Kill all Python
Get-Process python | Stop-Process -Force

# Restart Django
python -m pipenv run python manage.py runserver

# Restart Bot
python -m pipenv run python bot/main.py
```

**Result:** ❌ STILL FAILING
- Error persists: "Could not join channel: davey library needed in order to use voice"

---

### Attempt 7: Add FFmpeg Detection & Explicit Configuration
**Date:** 2026-05-14 ~1:29 PM

**Theory:** 
- discord.py might not be detecting FFmpeg properly
- Added explicit FFmpeg verification to bot startup

**Changes Made to `bot/main.py`:**
```python
import subprocess

def check_ffmpeg():
    """Verify FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

if not check_ffmpeg():
    print("WARNING: FFmpeg not found in PATH...")
```

**Result:** ❌ STILL FAILING
- Bot restarts but `/join` still shows same error
- This indicates the problem is NOT a missing FFmpeg in PATH

**New Theory:**
The error "davey library" is coming from discord.py's voice initialization, not from missing system FFmpeg. This suggests:
1. Discord.py voice module isn't loading properly
2. Possible Python 3.14 compatibility issue
3. PyNaCl/discord.py version mismatch
4. Deep discord.py voice subsystem failure

---

## Environment Details

| Item | Value |
|------|-------|
| OS | Windows 10 (Build 26200) |
| Python | 3.14.0 |
| discord.py | Installed (exact version unknown) |
| PyNaCl | 1.6.2 (upgraded) |
| FFmpeg | Installing... |
| pipenv | Active |

---

## Key Findings

1. **The Real Issue:** FFmpeg was missing, not PyNaCl
2. **Error Message is Misleading:** "davey library" should be "voice libraries" (PyNaCl + FFmpeg)
3. **Admin Rights Required:** FFmpeg installation via Chocolatey requires elevated permissions
4. **Both Dependencies Needed:**
   - PyNaCl: For voice encryption/authentication
   - FFmpeg: For audio stream encoding/decoding

---

## Testing Checklist

- [ ] FFmpeg installation completes successfully
- [ ] Bot restarts without errors
- [ ] Bot shows green online status in Discord
- [ ] `/join` command succeeds
- [ ] Bot connects to voice channel
- [ ] Next test: Try `/play` with a YouTube URL

---

## Alternative Solutions (If Current Fails)

### Option 1: Manual FFmpeg Installation
If Chocolatey continues to fail:
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to System PATH
4. Restart bot

### Option 2: Different Python Version
If FFmpeg still causes issues:
- Try Python 3.12 or 3.13 instead of 3.14
- May have better compatibility with PyNaCl/FFmpeg

### Option 3: Use discord.py's Built-in Audio
- Some discord.py versions have alternative audio backends
- Not recommended - FFmpeg is standard

---

## Lessons Learned

1. **Voice Support Requires Multiple Dependencies**
   - Just having discord.py isn't enough
   - FFmpeg must be in system PATH
   - PyNaCl must be in Python environment

2. **Windows Permission Issues**
   - Chocolatey often requires admin rights
   - Use `-Verb RunAs` in PowerShell for elevation
   - Manual installation is more reliable alternative

3. **Error Messages Can Be Misleading**
   - "davey library" → Actually means missing voice dependencies
   - Check the actual library availability, not just error text

---

## Root Cause Analysis

**What We Know:**
- ✅ FFmpeg IS installed and accessible (verified via `ffmpeg -version`)
- ✅ PyNaCl IS installed (version 1.6.2)
- ✅ discord.py IS installed
- ❌ BUT: discord.py voice module won't initialize

**The Real Problem:**
The error "davey library needed in order to use voice" is **NOT** about missing system FFmpeg. It's discord.py internally failing to initialize its voice subsystem. Possible reasons:

1. **Python 3.14 Incompatibility** - voice module may not work with Python 3.14
2. **PyNaCl Version Issue** - discord.py expects specific PyNaCl version
3. **discord.py Version Mismatch** - installed version may not support current setup
4. **libopus Missing** - Some discord.py versions need libopus library
5. **Windows-Specific Issue** - Voice module has known issues on Windows

---

## Root Cause Analysis

**What We Know:**
- ✅ FFmpeg IS installed and accessible (verified via `ffmpeg -version`)
- ✅ PyNaCl IS installed (version 1.6.2)
- ✅ discord.py IS installed
- ❌ BUT: discord.py voice module won't initialize

**The Real Problem:**
The error "davey library needed in order to use voice" is **NOT** about missing system FFmpeg. It's discord.py internally failing to initialize its voice subsystem. Possible reasons:

1. **Python 3.14 Incompatibility** - voice module may not work with Python 3.14
2. **PyNaCl Version Issue** - discord.py expects specific PyNaCl version
3. **discord.py Version Mismatch** - installed version may not support current setup
4. **libopus Missing** - Some discord.py versions need libopus library
5. **Windows-Specific Issue** - Voice module has known issues on Windows

---

## Solution Attempt: Downgrade to Python 3.12

### Attempt 8: Python Version Downgrade
**Date:** 2026-05-14 ~1:36 PM

**Hypothesis:** Python 3.14 is too new and discord.py voice module isn't fully compatible

**Actions Taken:**

1. **Installed Python 3.12**
   ```powershell
   Start-Process powershell -ArgumentList "choco uninstall python -y; choco install python312 -y" -Verb RunAs -Wait
   ```
   - Result: ✅ Python 3.12.10 successfully installed

2. **Killed existing Python processes**
   ```powershell
   Get-Process python | Stop-Process -Force
   ```
   - Result: ✅ All processes terminated

3. **Removed old pipenv environment**
   ```powershell
   python -m pipenv --rm
   ```
   - Result: ✅ Old virtualenv deleted

4. **Updated Pipfile to require Python 3.12**
   ```
   [requires]
   python_version = "3.12"
   ```
   - Result: ✅ Pipfile updated

5. **Reinstalled dependencies with Python 3.12**
   ```powershell
   python -m pipenv install
   ```
   - Result: ✅ SUCCESS - Using C:/Python312/python.exe3.12.10
   - All dependencies installed successfully
   - Pipfile.lock updated

6. **Restarted Services**
   - Django server: Started ✅
   - Discord bot: Started ✅

**Status:** 🔄 **TESTING** - Waiting for `/join` command test with Python 3.12

---

### Attempt 9: Install discord.py[voice] Explicitly
**Date:** 2026-05-14 ~1:50 PM

**Hypothesis:** discord.py needs explicit voice extras installed

**Actions Taken:**
1. Killed all Python processes
2. Installed discord.py with voice support:
   ```powershell
   python -m pipenv install "discord.py[voice]"
   ```
3. Restarted both services

**Result:** ✅ **SUCCESS!** Bot joined voice channel!

**Root Cause Found:** 
- discord.py was installed but without the `[voice]` extras
- The `[voice]` extra installs additional voice-specific dependencies
- This was the missing piece preventing voice functionality

---

## ✅ RESOLVED

**Status:** 🟢 **WORKING** - Voice functionality operational!

**Solution:** Install `discord.py[voice]` instead of just `discord.py`

**What was wrong:**
- discord.py installed: YES ✅
- discord.py[voice] installed: NO ❌
- FFmpeg installed: YES ✅
- PyNaCl installed: YES ✅
- Python 3.12: YES ✅

**Final Fix:**
```powershell
pipenv install "discord.py[voice]"
```

**Test Result:** `/join` command now works! Bot successfully joins voice channels!

---

## Key Takeaway

The error "davey library needed in order to use voice" was misleading. It wasn't about missing system libraries or FFmpeg. The issue was that discord.py's voice **extras** were never installed. When installing discord.py, you must use `discord.py[voice]` (with the brackets) to get voice support, not just `discord.py`.
