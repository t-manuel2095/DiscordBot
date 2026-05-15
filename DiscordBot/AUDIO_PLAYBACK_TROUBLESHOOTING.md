# Audio Playback Troubleshooting - Day 6

## Overview
Documentation of the audio playback implementation process and troubleshooting for the Discord music bot. This covers the implementation of actual audio streaming in voice channels and auto-advance functionality.

---

## Issue #1: No Audio Playing - FFmpeg Invalid Data Error

### Description
When using `/play <YouTube URL>`, the bot would:
- Auto-join the voice channel successfully
- Appear to start playback
- But NO audio would actually play
- FFmpeg would error: `Error opening input: Invalid data found when processing input`

### Root Cause Analysis
The issue had **two layers**:

1. **Wrong URL being stored in database**: 
   - The `/play` command extracted the audio stream URL from yt-dlp correctly
   - BUT then sent the original raw YouTube URL (`https://www.youtube.com/watch?v=...`) to the API
   - The API normalized it back to YouTube URL format
   - When `play_audio()` tried to use this URL with FFmpeg, FFmpeg couldn't play it

2. **FFmpeg needs direct audio stream URLs**:
   - FFmpeg can only play direct HTTP(S) audio URLs or media files
   - YouTube URLs require special handling (yt-dlp does this)
   - We were trying to pass YouTube URLs directly to FFmpeg

### Solution Steps Taken

**Step 1: Extract audio stream URL in bot before API call**
```python
# Before (wrong):
song_data = await self.api.add_song(
    guild_id,
    title=title,
    url=url,  # Raw YouTube URL - WRONG
    added_by=username
)

# After (correct):
audio_url = song_info.get('url')  # Audio stream URL from yt-dlp
song_data = await self.api.add_song(
    guild_id,
    title=title,
    url=audio_url,  # Direct audio stream URL - CORRECT
    added_by=username
)
```

**Step 2: Modified serializer to accept audio stream URLs**
```python
# Before: Always normalized to YouTube URL
def to_internal_value(self, data):
    if 'url' in data:
        data['url'] = normalize_youtube_url(data['url'])  # Converts to YouTube URL
    return super().to_internal_value(data)

# After: Only normalize YouTube URLs, accept audio URLs as-is
def to_internal_value(self, data):
    if 'url' in data:
        url = data['url']
        if 'youtube.com' in url or 'youtu.be' in url:
            data['url'] = normalize_youtube_url(url)
        # Otherwise keep as-is (audio stream URL)
    return super().to_internal_value(data)
```

**Step 3: Simplified play_audio() to use URL directly**
```python
# Before: Tried to extract audio again (failed because YouTube URL)
audio_url, extracted_title = self.extract_audio_url(url)  # Failed
if not audio_url:
    return

# After: Use URL directly from queue (already audio stream URL)
audio_url = current_song['url']  # This is already audio stream URL
if not audio_url:
    return
```

---

## Issue #3: API Rejects Audio Stream URL with 400 Error

### Description
After fixing the FFmpeg error, the bot would still fail when trying to add a song:
- `/play` command would extract audio stream URL correctly
- Bot would try to POST to `/api/v1/queues/.../add_song/`
- API would return `400 Bad Request`
- Error message: "Failed to add song to queue"

The audio stream URL looked like:
```
https://rr9---sn-bvvbaxivnuxqjvhj5nu-vgqd.googlevideo.com/videoplayback?expire=123456&ei=abc...
```

### Root Cause
The `Song` model used `URLField()` which:
- Has strict URL validation (RFC 3986 compliant)
- Has a max_length of 200 by default
- Cannot parse URLs with complex query parameters like Google's audio stream URLs
- These URLs are often 500+ characters long

### Solution
Changed the `Song` model's `url` field from `URLField()` to `TextField()`:

```python
# Before (wrong):
class Song(models.Model):
    url = models.URLField()  # Strict validation, 200 char limit

# After (correct):
class Song(models.Model):
    url = models.TextField()  # No validation, unlimited length
```

Steps taken:
1. Modified `queue_api/models.py` - Changed `url` field to `TextField`
2. Removed URL validation from `SongSerializer` (since TextField doesn't validate URLs)
3. Created migration: `makemigrations`
4. Applied migration: `migrate`
5. Restarted bot and server

This allows storing:
- Raw YouTube URLs (for future reference)
- Google audio stream URLs (for immediate playback)
- Any other media URLs without validation errors

---

## Issue #2: RuntimeError in After-Playback Callback

### Description
When a song finished playing, FFmpeg would exit but the bot would crash with:
```
RuntimeError: no running event loop
```

And the after-callback coroutine would never execute:
```
RuntimeWarning: coroutine 'VoiceCommands.play_next_in_queue' was never awaited
```

### Root Cause
The `after_callback` function is called by discord.py's player in a **non-async context** (separate thread). Inside this callback, we were trying to use `asyncio.create_task()` which requires a running event loop. However, in a non-async context, there's no loop available.

### Solution
Use `asyncio.run_coroutine_threadsafe()` which is designed for scheduling coroutines from **non-async contexts**:

```python
# Before (wrong):
def after_callback(error):
    if error:
        print(f'[-] Playback error: {error}')
    else:
        asyncio.create_task(self.play_next_in_queue(guild_id, voice_client))  # FAILS

# After (correct):
def after_callback(error):
    if error:
        print(f'[-] Playback error: {error}')
    else:
        try:
            asyncio.run_coroutine_threadsafe(
                self.play_next_in_queue(guild_id, voice_client),
                self.bot.loop  # Use bot's event loop
            )
        except Exception as e:
            print(f'[-] Error scheduling next song: {e}')
```

---

## Audio Playback Flow (Current Implementation)

```
User: /play <YouTube URL>
    ↓
Bot: Extract audio stream URL using yt-dlp
    ↓
Bot: Send audio stream URL to API
    ↓
API: Store audio stream URL in database
    ↓
Bot: Get audio URL from queue
    ↓
Bot: Create FFmpeg audio source with audio stream URL
    ↓
Bot: Play audio via voice_client.play()
    ↓
Song Finishes
    ↓
after_callback triggers
    ↓
Bot: Schedule play_next_in_queue() via run_coroutine_threadsafe()
    ↓
Bot: Increment current_song_index via API
    ↓
Bot: Get next song and play
    ↓
Loop continues...
```

---

## Key Files Modified

### 1. `bot/commands/queue_commands.py` - /play command
- **Change**: Extract audio stream URL from `song_info` before sending to API
- **Lines**: 50-51 (get audio_url from song_info)
- **Line**: 69 (send audio_url instead of raw url)

### 2. `bot/commands/voice_commands.py` - Audio playback
- **Change 1**: Modified `extract_song_info()` to return audio stream URL (not YouTube URL)
  - Line 98: Returns `info.get('url')` which is the audio stream URL
  
- **Change 2**: Removed `extract_audio_url()` method (no longer needed)
  
- **Change 3**: Simplified `play_audio()` to use URL directly from queue
  - Line 121: `audio_url = current_song['url']` (already audio stream URL)
  - Removed re-extraction logic
  
- **Change 4**: Fixed after-callback to use `run_coroutine_threadsafe()`
  - Lines 140-147: Proper async scheduling from callback

### 3. `queue_api/serializers.py` - URL validation
- **Change**: Modified `to_internal_value()` to conditionally normalize URLs
- **Logic**: Only normalize YouTube URLs, accept audio stream URLs as-is

---

## Testing Checklist

- [x] Bot extracts audio stream URL from YouTube
- [x] Audio stream URL is sent to API (not YouTube URL)
- [x] API accepts and stores audio stream URL (TextField)
- [x] FFmpeg can play the audio stream URL
- [x] Audio is audible in Discord voice channel
- [x] Song finishes without crashing
- [x] After-callback schedules next song properly
- [x] Auto-play continues to next song in queue
- [x] Green ring appears in Discord (voice active indicator)

---

## Possible Future Issues & Solutions

---

## Issue #4: Skip Command Delayed Playback

### Description
When using `/skip`, the bot would:
- Show "Skipped to next song" response
- But audio would keep playing the current song for ~20 seconds
- Then finally cut off and play the next song
- This created an awkward delay

### Root Cause
The `/skip` command only called `next_song()` (API) to increment the queue index, but it never:
- Stopped the currently playing audio
- Triggered playback of the next song

The after-callback from the current song would eventually fire (when the song ended), which would then play the next song. This caused the 20-second delay.

### Solution
Updated `/skip` to:
1. Call `next_song()` to increment index (already done)
2. **Stop the current playback** with `voice_client.stop()`
3. This triggers the after-callback immediately
4. The after-callback calls `play_next_in_queue()` which plays the new song right away

```python
# Before (wrong):
if result:
    await interaction.followup.send('⏭️ Skipped to next song')

# After (correct):
if result:
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Triggers after_callback → plays next song immediately
    await interaction.followup.send('⏭️ Skipped to next song')
```

---

## Issue #5: Remove/Clear Commands Don't Update Playback

### Description
- `/remove <position>` - If you removed the currently playing song, audio kept playing
- `/clear` - If you cleared the queue, audio kept playing the current song

### Solution
Updated both commands to check if the removed/cleared song is currently playing:

**For `/remove`:**
```python
if position - 1 == current_index:
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Plays next song or stops if queue empty
```

**For `/clear`:**
```python
voice_client = interaction.guild.voice_client
if voice_client and voice_client.is_playing():
    voice_client.stop()  # Stops playback when queue is cleared
```

---

## Issue #6: No "Now Playing" Notifications

### Description
Songs would start playing silently without any message to users indicating what's playing.

### Solution
Added automatic "Now Playing" embed message to `play_audio()`:
- Finds the guild's text channel (prefers "general", falls back to first channel)
- Sends embed with:
  - Song title
  - Who added the song
  - Duration (if available)
- Sends automatically whenever a song starts (initial play, skip, remove, etc.)

---

## Testing Checklist (Updated)

- [x] Bot extracts audio stream URL from YouTube
- [x] Audio stream URL is sent to API (not YouTube URL)
- [x] API accepts and stores audio stream URL (TextField)
- [x] FFmpeg can play the audio stream URL
- [x] Audio is audible in Discord voice channel
- [x] Song finishes without crashing
- [x] After-callback schedules next song properly
- [x] Auto-play continues to next song in queue
- [x] Green ring appears in Discord (voice active indicator)
- [x] `/skip` stops current song and plays next immediately
- [x] `/remove` current song stops playback and plays next
- [x] `/clear` stops playback
- [x] "Now Playing" embed appears when song starts
- [x] Duration displays correctly in embed
- [x] Song added by username displays in embed

---

## Possible Future Issues & Solutions

### Issue: Audio stutters or drops
**Solution**: Adjust FFmpeg reconnection options in `play_audio()`:
```python
before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
```
Try different values if needed.

### Issue: Audio stream URLs expire
**Solution**: YouTube audio URLs expire after ~6 hours. If user queues many songs and waits, URLs might expire:
- Option 1: Re-extract URL when playing (uses more API calls)
- Option 2: Implement URL refresh logic when URL is close to expiry
- Option 3: Store YouTube ID instead of audio URL, extract when playing

### Issue: Some YouTube videos fail to extract
**Solution**: Already has try-catch blocks in `extract_song_info()`. May need to:
- Log which videos fail
- Test with video-specific yt-dlp options
- Consider fallback sources

### Issue: Callback not firing for some songs
**Solution**: Discord.py player might not call after() if:
- Voice connection disconnects (already handled)
- FFmpeg process crashes (logs error)
- Source is invalid (would error during play)

### Issue: "Now Playing" message posts to wrong channel
**Solution**: Current logic searches for "general" channel first, then uses first available. Could be improved to:
- Store preferred channel ID in database
- Use guild's default channel if available
- Check channel permissions before posting

---

## Notes

- Audio stream URLs are time-limited (usually 4-6 hours from extraction)
- yt-dlp handles all YouTube URL format variations automatically
- FFmpeg must be installed on system (already handled in earlier troubleshooting)
- Discord.py requires proper error handling in after-callbacks
- Using bot's event loop (`self.bot.loop`) is critical for thread-safe async operations
- All playback commands (skip, remove, clear) now use `voice_client.stop()` for consistency
