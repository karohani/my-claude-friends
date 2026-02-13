---
name: youtube-digest
description: This skill should be used when the user asks to "summarize youtube", "youtube 요약", "analyze video", "영상 분석", "extract transcript", "자막 추출", "youtube digest", or provides a YouTube URL. Extracts subtitles, corrects proper nouns, generates summary and optional quiz.
version: 1.0.0
user-invocable: true
arguments:
  - name: url
    description: YouTube video URL
    required: true
  - name: quiz
    description: Generate learning quiz (--quiz flag)
    required: false
---

# YouTube Digest Skill

A workflow for analyzing YouTube videos and organizing them into markdown documents.

## Prerequisites

yt-dlp must be installed:
```bash
brew install yt-dlp
# or
pip install yt-dlp
```

## Workflow

### Phase 1: Metadata and Subtitle Extraction

1. **URL Validation**: Verify YouTube URL format (youtube.com/watch, youtu.be)

2. **Metadata Extraction** (using yt-dlp):
   ```bash
   yt-dlp --print "%(title)s|||%(channel)s|||%(upload_date)s|||%(duration_string)s" --no-download "URL"
   ```

3. **Subtitle Extraction** — Priority order:
   - 1st: Manual Korean subtitles (`ko`)
   - 2nd: Manual English subtitles (`en`)
   - 3rd: Auto-generated Korean subtitles (`ko-auto`)
   - 4th: Auto-generated English subtitles (`en-auto`)

   ```bash
   # Check available subtitles
   yt-dlp --list-subs --no-download "URL"

   # Download subtitles (e.g., Korean)
   yt-dlp --write-sub --sub-lang ko --skip-download --output "%(id)s" "URL"
   # Or auto-generated subtitles
   yt-dlp --write-auto-sub --sub-lang ko --skip-download --output "%(id)s" "URL"
   ```

4. **Subtitle File Parsing**: Parse VTT using Python script
   ```bash
   # Default (deduplication + merging)
   python3 ${pluginDir}/scripts/parse_vtt.py <video_id>.ko.vtt

   # With timestamps
   python3 ${pluginDir}/scripts/parse_vtt.py <video_id>.ko.vtt --timestamps

   # JSON format output
   python3 ${pluginDir}/scripts/parse_vtt.py <video_id>.ko.vtt --json
   ```

### Phase 2: Proper Noun Correction

Run the `proper-noun-corrector` agent via the Task tool:
- Extract proper nouns, technical terms, and brand names from subtitles
- Verify correct spelling via WebSearch
- Apply corrections consistently

### Phase 3: Summary and Insight Generation

Run the `summary-generator` agent via the Task tool:
- 3-5 sentence summary
- 3-5 key insights
- Section-by-section breakdown (when possible)

### Phase 4: Quiz Generation (Optional)

If the `--quiz` flag is provided, run the `quiz-generator` agent via the Task tool:
- 3 basic questions
- 3 intermediate questions
- 3 advanced questions

### Phase 5: Save as Markdown

Save path: `./youtube/{channel-name}/{YYYY-MM-DD}-{sanitized-title}.md`

## Output Format

```markdown
---
title: "[Title]"
source: "[Channel Name]"
url: "[URL]"
duration: "[Video Duration]"
date_processed: "[Processing Date]"
original_language: "[Original Subtitle Language]"
---

# [Title]

> Source: [Channel Name](Channel URL) | Duration: [Video Duration] | [Upload Date]

## Summary

[3-5 sentence summary of the video content]

## Key Insights

- **[Insight 1 Title]**: [Description]
- **[Insight 2 Title]**: [Description]
- **[Insight 3 Title]**: [Description]

## Full Script

[Corrected full script with timestamps]

## Learning Quiz

### Basic
1. [Question]
   - A) [Choice]
   - B) [Choice]
   - C) [Choice]
   - D) [Choice]
   <details><summary>Answer</summary>B) [Answer and explanation]</details>

### Intermediate
[...]

### Advanced
[...]
```

## Error Handling

- **No subtitles**: "No subtitles are available for this video. Please use a speech recognition tool or manually input the script."
- **URL error**: "Please enter a valid YouTube URL. Example: https://youtube.com/watch?v=xxxxx"
- **yt-dlp not installed**: "yt-dlp is not installed. Install it with `brew install yt-dlp` or `pip install yt-dlp`."

## Temporary File Cleanup

Delete downloaded .vtt files after completion:
```bash
rm -f *.vtt
```
