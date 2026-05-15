# Slash Commands Troubleshooting

**Date Started:** Thursday, May 14, 2026 - 3:13 PM
**Status:** ✅ FULLY RESOLVED AND WORKING (Verified & Enhanced Friday, May 15, 2026 - 10:59 AM)

## Problem Statement

Slash commands were not appearing in Discord when the user typed `/`. The bot was connected but:
- No autocomplete dropdown when typing `/`
- No slash commands visible in Discord
- `on_ready()` and `setup_hook()` events appeared to not be firing

## Root Causes & Solutions

### Root Cause 1: OUTPUT BUFFERING (RESOLVED ✅)
Python was buffering output, making it appear nothing was happening.

**Solution:** Use unbuffered output flag:
```bash
python -u -m pipenv run python -u bot/main.py
```

### Root Cause 2: GUILD-SPECIFIC SYNC CAUSED CommandNotFound (RESOLVED ✅)
After fixing buffering, discovered another issue:
- Commands synced to guild but Discord couldn't invoke them
- Error: `discord.app_commands.errors.CommandNotFound: Application command 'join' not found`
- Using `@app_commands.guilds()` decorator scoped commands to guild, but the bot's command tree didn't have them registered locally

**Solution:** Remove `@app_commands.guilds()` decorator and sync globally instead

### Root Cause 3: COMMANDS NOT REGISTERED IN BOT TREE (RESOLVED ✅)
When using guild-specific sync, commands weren't appearing in `bot.tree._get_all_commands()`.

**Solution:** Use global sync - commands now appear in tree as "Commands in tree: 9"

## Final Working Solution

### Step 1: Remove Guild Decorators from Commands

**bot/commands/queue_commands.py** - Remove GUILD_ID and `@app_commands.guilds()`:
```python
class QueueCommands(commands.Cog):
    @app_commands.command(name='play', description='Queue a song from YouTube')
    async def play(self, interaction: discord.Interaction, url: str):
        # No @app_commands.guilds() decorator
```

**bot/commands/voice_commands.py** - Same approach:
```python
class VoiceCommands(commands.Cog):
    @app_commands.command(name='join', description='Bot joins the voice channel')
    async def join(self, interaction: discord.Interaction):
        # No @app_commands.guilds() decorator
```

### Step 2: Sync Commands Globally in Bot

**bot/main.py:**
```python
async def setup_hook():
    """Load cogs and sync commands when bot is setting up"""
    print('[*] Running setup_hook()')
    await load_cogs()
    print('[*] About to sync slash commands...')
    try:
        synced = await bot.tree.sync()  # Global sync, no guild parameter
        print(f'[+] Synced {len(synced)} slash command(s) globally')
        for cmd in synced:
            print(f'    - {cmd.name}')
    except Exception as e:
        print(f'[-] Failed to sync commands: {e}')

bot.setup_hook = setup_hook
```

### Step 3: Add Debug Logging to Commands

All commands now have try/except with detailed logging:
```python
@app_commands.command(name='join', description='Bot joins the voice channel')
async def join(self, interaction: discord.Interaction):
    """Bot joins the voice channel"""
    try:
        await interaction.response.defer()
        print('[*] /join command invoked')
        
        if not interaction.user.voice:
            print('[-] User not in voice channel')
            await interaction.followup.send('You must be in a voice channel')
            return
        
        channel = interaction.user.voice.channel
        print(f'[*] User is in channel: {channel.name}')
        await channel.connect()
        print(f'[+] Connected to {channel.name}')
        await interaction.followup.send(f'Joined {channel.name}')
    except Exception as e:
        print(f'[-] Error in /join command: {e}')
        import traceback
        traceback.print_exc()
        try:
            await interaction.followup.send(f'Could not join channel: {str(e)}')
        except:
            print(f'[-] Failed to send error message')
```

### Step 4: Run Bot with Unbuffered Output

```bash
python -u -m pipenv run python -u bot/main.py
```

## Successful Terminal Output

```
[*] Running setup_hook()
[*] Loading cogs from: c:\Users\Manuel\source\repos\DiscordBot\DiscordBot\bot\commands
[+] Loaded cog: queue_commands
[+] Loaded cog: voice_commands
[*] About to sync slash commands...
[+] Synced 9 slash command(s) globally
    - play
    - queue
    - skip
    - remove
    - clear
    - nowplaying
    - join
    - leave
    - stop
[2026-05-15 10:35:21] [INFO    ] discord.gateway: Shard ID None has connected to Gateway
Our bot#2943 has connected to Discord!
------
Commands in tree: 9
```

## All Working Slash Commands (9 Total)

1. **`/play <url>`** - Queue a song from YouTube and play if nothing is playing
2. **`/queue`** - Display current queue
3. **`/skip`** - Skip to next song
4. **`/remove <position>`** - Remove song at position
5. **`/clear`** - Clear entire queue
6. **`/nowplaying`** - Show currently playing song
7. **`/join`** - Bot joins the voice channel
8. **`/leave`** - Bot leaves the voice channel
9. **`/stop`** - Stop audio playback

## How to Use Commands in Discord

1. Type `/` in any text channel in your server
2. You'll see autocomplete dropdown with all 9 commands
3. Click on the command or continue typing the name
4. Fill in any required parameters
5. Press Enter to execute

## Key Learnings

1. **Unbuffered Output is Critical** - Always use `-u` flag when debugging Python bots
2. **Global Sync is More Reliable** - Avoids CommandNotFound errors
3. **Commands Must Be in bot.tree** - Discord needs to find commands in the bot's local tree to invoke them
4. **Guild-Specific Sync Issues** - `@app_commands.guilds()` scopes commands away from bot.tree, causing invocation failures
5. **Debug Logging is Essential** - Try/except blocks with detailed logging help identify runtime issues
6. **Immediate Feedback** - Unbuffered output allows real-time monitoring of bot behavior
7. **Shared API Client** - Store APIClient instance on bot object for access across cogs
8. **Cleanup on Exit** - Always clear state (queue) when bot leaves to prevent orphaned data

## Error We Fixed

**Error:** `discord.app_commands.errors.CommandNotFound: Application command 'join' not found`

**Root Cause:** Using `@app_commands.guilds(discord.Object(id=GUILD_ID))` decorator removed commands from global tree

**Fix:** Removed guild scoping and used global sync instead

---

## Additional Fixes (May 15, 2026 - Continued)

### Fix 4: Skip/Remove/Clear Commands Delayed or Don't Update Playback
**Problem:** 
- `/skip` would show "Skipped" but audio kept playing current song for 20 seconds
- `/remove` on current song - audio kept playing
- `/clear` - audio kept playing even though queue was empty

**Root Cause:** Commands only updated the queue/index but didn't stop current playback, so FFmpeg kept playing until song naturally finished (then after-callback would fire)

**Solution:** Updated all three commands to call `voice_client.stop()`:
- `/skip` - Calls `next_song()` then stops playback (triggers after-callback → plays next immediately)
- `/remove` - If removing currently playing song, stops playback
- `/clear` - Stops playback before clearing queue
- All use the same pattern: `voice_client.stop()` → triggers after-callback → audio transitions smoothly

### Fix 5: No "Now Playing" Announcement When Song Starts
**Problem:** Songs would start playing silently with no indication in chat

**Solution:** Added automatic embed message to `play_audio()`:
- Finds guild's text channel (prefers "general")
- Sends embed with title, added by, and duration
- Triggered on: initial play, skip, remove, auto-advance
- Shows users what's currently playing without needing `/nowplaying`

### Fix 6: Manual Disconnect Doesn't Clear Queue (FIXED ✅)
**Problem:** Right-clicking bot → "Disconnect" leaves queue intact in database

**Root Cause:** Event listener was added as a Cog method but Cog event listeners don't work reliably for voice state updates. Only bot-level event listeners are reliable.

**Solution:** Moved `on_voice_state_update()` from VoiceCommands cog to bot/main.py:
```python
@bot.listen()
async def on_voice_state_update(member, before, after):
    """Detect when bot is manually disconnected from voice"""
    if member == bot.user:
        if before.channel and not after.channel:
            print(f'[*] Bot manually disconnected')
            guild_id = str(before.channel.guild.id)
            await bot.api.delete_queue(guild_id)  # Clears queue
```

Now when bot is manually disconnected:
- Event fires immediately
- Queue is automatically deleted from database
- Keep-alive tasks are cancelled
- All state is cleaned up

### Fix 7: Stop Command is Redundant (Removed)
**Problem:** `/stop` stopped audio but left queue - similar to `/leave` but different behavior

**Solution:** Removed `/stop` and replaced with `/pause` and `/resume`:
- `/pause` - Pauses current song, keeps queue intact
- `/resume` - Resumes paused song
- Both required new `paused_state` tracking dictionary
- Better UX than stop

### Fix 8: Pause Command Causes Auto-Disconnect
**Problem:** Pausing music - after ~15 minutes Discord auto-disconnects idle bot

**Solution:** Added keep-alive background task:
- When `/pause` called, starts `_keep_alive()` async task
- Task runs every 30 seconds while paused
- Maintains connection state to prevent Discord idle timeout
- Task cancelled when `/resume` or `/leave` called
- Stores tasks in `keep_alive_tasks` dictionary per guild

---

## Current Working Commands (9 Total - Updated)

1. **`/play <url>`** - Queue a song from YouTube and play if nothing is playing
2. **`/queue`** - Display current queue with ▶️ indicator
3. **`/skip`** - Skip to next song (immediate playback transition)
4. **`/remove <position>`** - Remove song, auto-play next if removed current song
5. **`/clear`** - Clear entire queue and stop playback
6. **`/nowplaying`** - Show currently playing song details
7. **`/leave`** - Bot leaves voice and clears queue
8. **`/pause`** - ⏸️ Pause audio (keeps queue, bot stays connected)
9. **`/resume`** - ▶️ Resume paused audio

## Command Sync Status

```
[+] Synced 9 slash command(s) globally
    - play
    - queue
    - skip
    - remove
    - clear
    - nowplaying
    - leave
    - pause
    - resume
```

## Disconnect Handling

| Scenario | Behavior | Queue Cleared? |
|----------|----------|---|
| `/leave` | Bot disconnects | ✅ Yes |
| Manual right-click disconnect | Bot disconnects | ✅ Yes (now) |
| `/pause` then idle 15 min | Bot stays connected (keep-alive) | ❌ No |
| `/stop` (removed) | N/A | N/A |

## Files Modified (Final)

- `bot/main.py` - Added `on_voice_state_update()` bot-level event listener for manual disconnect detection
- `bot/commands/queue_commands.py` - Updated `/skip`, `/remove`, `/clear` to stop playback
- `bot/commands/voice_commands.py` - Added `/pause`, `/resume`, `_keep_alive()` task
- Both command files - Removed `/stop` and replaced with pause/resume functionality

## Status Summary (Final)

| Aspect | Status | Notes |
|--------|--------|-------|
| Slash Commands | ✅ Working | 9 commands globally synced |
| Pause/Resume | ✅ WORKING | Both commands fully functional |
| Manual Disconnect | ✅ FIXED | Queue clears immediately on right-click disconnect |
| Pause Idle Timeout | ✅ FIXED | Keep-alive task prevents auto-disconnect |
| Now Playing Announce | ✅ WORKING | Auto-sends embed when song starts |
| Playback Transitions | ✅ SMOOTH | No audio gaps when skipping/removing |
| Bot Event Listeners | ✅ WORKING | Voice state updates handled at bot level |

---

**Last Updated:** Friday, May 15, 2026 - 12:24 PM
**Status:** ✅ ALL SLASH COMMANDS AND DISCONNECT HANDLING FULLY WORKING

### Fix 1: `/skip` Command Not Working
**Problem:** Skip command appeared to work but queue showed same song playing

**Root Cause:** `next_song` endpoint in API didn't validate if `current_song_index` was within bounds - it just kept incrementing blindly

**Solution:** Updated `queue_api/views.py` `next_song()` endpoint to:
- Check if queue has songs
- Validate `current_song_index < song_count - 1` before incrementing  
- Return error if already at last song
- Only increment if there's a valid next song

### Fix 2: `/remove` and `/clear` Commands Not Implemented
**Problem:** Commands showed placeholder messages but didn't actually modify the queue

**Solution:** Fully implemented both commands:
- `/remove <position>` - Deletes specific song, validates position, reorders queue
- `/clear` - Calls `delete_queue()` API method to completely clear queue
- Added error handling and logging to both

### Fix 3: `/queue` Display Doesn't Show Current Song
**Problem:** `/queue` displayed all songs but didn't indicate which one is currently playing

**Solution:** Enhanced `/queue` command to:
- Display `▶️ (NOW PLAYING)` indicator on current song
- Compare each song's index with `current_song_index` from queue
- Shows which song is actually playing while skipping works

## Files Modified

- `bot/main.py` - Global sync in setup_hook, unbuffered output, APIClient instance
- `bot/commands/queue_commands.py` - Removed GUILD_ID, removed `@app_commands.guilds()`, added debug logging to all commands, enhanced `/queue` to show current song
- `bot/commands/voice_commands.py` - Removed GUILD_ID, removed `@app_commands.guilds()`, added debug logging, queue clear on leave
- `bot/api_client.py` - Added `delete_queue()` method
- `queue_api/views.py` - Fixed `next_song()` endpoint to properly validate bounds before incrementing

## Status Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| Slash Commands | ✅ Working | 9 commands globally synced |
| Command Registration | ✅ Working | Commands in tree: 9 |
| Autocomplete Dropdown | ✅ Working | Appears when typing `/` |
| Command Invocation | ✅ Working | CommandNotFound error resolved |
| Bot Connection | ✅ Working | Connected to Discord gateway |
| Queue Management | ✅ Working | All CRUD operations functional |
| Voice Commands | ✅ Working | Join/leave/stop commands working |
| Debug Logging | ✅ Enhanced | Detailed output for all commands |
| Queue Clear on Leave | ✅ Working | Bot clears queue when leaving voice |
| Skip Command | ✅ FIXED | Now properly validates bounds before skipping |
| Remove Command | ✅ FIXED | Fully implemented with position validation |
| Clear Command | ✅ FIXED | Fully implemented to delete entire queue |
| Queue Display | ✅ ENHANCED | Shows ▶️ indicator on currently playing song |
| Audio Playback | ⏳ TODO | Needs implementation (Day 6) |

---

**RESOLUTION:** All 9 slash commands fully functional and tested. Queue management commands enhanced with proper playback transitions. Manual disconnect handling added. Pause/Resume implemented with idle-timeout protection.

**Last Updated:** Friday, May 15, 2026 - 12:07 PM
**Total Time to Resolve:** ~8+ hours of debugging, testing, and enhancement
