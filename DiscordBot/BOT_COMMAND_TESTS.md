# Discord Bot Command Tests

**Date:** Friday, May 15, 2026
**Status:** Test Plan Created for Manual Testing

## Test Overview

All 9 slash commands need to be tested in Discord to verify functionality. These tests should be performed in the Discord server where the bot is active.

---

## Test 1: `/join` Command

**Prerequisites:**
- Be in a voice channel in Discord
- Bot must not already be connected to a voice channel

**Steps:**
1. Join any voice channel (e.g., "General Voice")
2. Type `/join` in any text channel
3. Select the command from autocomplete

**Expected Result:**
- ✅ Bot joins your voice channel
- ✅ Bot displays message: `"Joined [Channel Name]"`
- ✅ You should see the bot's avatar in your voice channel

**Actual Result:** 
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 2: `/leave` Command

**Prerequisites:**
- Bot must be connected to a voice channel (run `/join` first)

**Steps:**
1. Type `/leave` in any text channel
2. Select the command from autocomplete

**Expected Result:**
- ✅ Bot leaves the voice channel
- ✅ Bot displays message: `"Left voice channel"`
- ✅ Bot's avatar disappears from voice channel

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 3: `/play` Command

**Prerequisites:**
- Have a valid YouTube URL ready
- Bot should be in a voice channel (run `/join` first)

**Steps:**
1. Type `/play` and enter a YouTube URL, e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. Select the command

**Expected Result:**
- ✅ Command responds (may not play audio yet, that's implemented in Day 6)
- ✅ Bot displays message: `"▶️ Now playing from queue: \`[URL]\`"` or `"✅ Added to queue: \`[URL]\`"`
- ✅ Queue is created in database for your server
- ✅ Song is added to the queue

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

**Example URLs:**
- https://www.youtube.com/watch?v=dQw4w9WgXcQ (Rick Roll)
- https://www.youtube.com/watch?v=jNQXAC9IVRw (Me at the zoo - First YouTube video)

---

## Test 4: `/queue` Command

**Prerequisites:**
- At least one song should be in the queue (run `/play` first)

**Steps:**
1. Type `/queue` in any text channel
2. Select the command

**Expected Result:**
- ✅ Bot displays queue as embed with blue color
- ✅ Shows "🎵 Current Queue" title
- ✅ Lists songs with numbers (1., 2., 3., etc.)
- ✅ Shows "Added by: [username]" for each song
- ✅ If more than 10 songs, shows "+X more songs"

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 5: `/nowplaying` Command

**Prerequisites:**
- At least one song should be in the queue (run `/play` first)

**Steps:**
1. Type `/nowplaying` in any text channel
2. Select the command

**Expected Result:**
- ✅ Bot displays currently playing song (first song in queue)
- ✅ Shows green embed with "🎵 Now Playing" title
- ✅ Shows song title in description
- ✅ Shows "Added by: [username]"

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 6: `/skip` Command

**Prerequisites:**
- At least two songs should be in the queue (run `/play` twice)

**Steps:**
1. Type `/skip` in any text channel
2. Select the command

**Expected Result:**
- ✅ Bot displays message: `"⏭️ Skipped to next song"`
- ✅ Queue index advances to next song
- ✅ Running `/nowplaying` should show the new song

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 7: `/remove` Command

**Prerequisites:**
- At least two songs should be in the queue

**Steps:**
1. Type `/remove 2` in any text channel (remove the 2nd song)
2. Select the command

**Expected Result:**
- ✅ Bot displays message: `"Removed song at position 2"`
- ✅ Running `/queue` should not show the removed song
- ✅ Queue has one fewer song

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 8: `/clear` Command

**Prerequisites:**
- At least one song should be in the queue

**Steps:**
1. Type `/clear` in any text channel
2. Select the command

**Expected Result:**
- ✅ Bot displays message: `"Queue cleared"`
- ✅ Running `/queue` should show "Queue is empty"

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Test 9: `/stop` Command

**Prerequisites:**
- Bot is in voice channel
- Audio is currently playing (will be after Day 6 implementation)

**Steps:**
1. Type `/stop` in any text channel
2. Select the command

**Expected Result:**
- ✅ Bot displays message: `"⏹️ Playback stopped"` or `"Nothing is playing"`
- ✅ Audio stops (after Day 6 implementation)

**Actual Result:**
- [ ] Pass
- [ ] Fail

**Notes:** _Record any errors or unexpected behavior_

---

## Edge Case Tests

### Test 10: `/play` with Already Playing Song

**Prerequisites:**
- Bot is in voice channel with one song queued
- Song is currently playing (Day 6+)

**Steps:**
1. While song is playing, run `/play [URL]`

**Expected Result:**
- ✅ Bot displays message: `"✅ Added to queue: \`[URL]\`"`
- ✅ Song is added but not played immediately

**Notes:** _This tests the queue logic_

---

### Test 11: `/join` When Already Connected

**Prerequisites:**
- Bot is already in a voice channel

**Steps:**
1. Type `/join` while bot is already in voice

**Expected Result:**
- ✅ Bot either joins again or displays message that it's already connected
- ✅ No errors or crashes

**Notes:** _This tests error handling_

---

### Test 12: `/queue` When Empty

**Prerequisites:**
- Queue is empty (run `/clear` first)

**Steps:**
1. Type `/queue` when queue is empty

**Expected Result:**
- ✅ Bot displays message: `"Queue is empty"`

**Notes:** _This tests empty state handling_

---

## Test Checklist

Command Tests:
- [ ] Test 1: `/join`
- [ ] Test 2: `/leave`
- [ ] Test 3: `/play`
- [ ] Test 4: `/queue`
- [ ] Test 5: `/nowplaying`
- [ ] Test 6: `/skip`
- [ ] Test 7: `/remove`
- [ ] Test 8: `/clear`
- [ ] Test 9: `/stop`

Edge Case Tests:
- [ ] Test 10: `/play` with already playing
- [ ] Test 11: `/join` already connected
- [ ] Test 12: `/queue` when empty

---

## Recommended Test Order

1. Start with `/join` (prerequisite for other tests)
2. Test `/play` (add songs)
3. Test `/queue` (view songs)
4. Test `/nowplaying` (show current song)
5. Test `/skip` (change current song)
6. Test `/remove` (remove from queue)
7. Test `/clear` (empty queue)
8. Test `/leave` (disconnect bot)
9. Test `/stop` (after Day 6 audio implementation)
10. Run edge case tests

---

## Reporting

When tests fail, note:
- Exact command used
- Error message displayed (if any)
- Bot terminal output
- Any unexpected behavior

---

**Created:** Friday, May 15, 2026 - 10:38 AM
**Last Updated:** Friday, May 15, 2026 - 10:38 AM
