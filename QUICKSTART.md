# Quick Start Guide

Get up and running with the Multi-Agent CLI in 5 minutes!

## 1. Install Dependencies

```bash
# Automated setup (recommended)
./setup.sh

# OR manual setup
pip install -r requirements.txt
```

## 2. Get API Keys

### Gemini API Key (FREE)
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Sign in with Google
4. Create a new API key
5. Copy the key

### YouTube API Key (FREE)
1. Visit https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy the key

## 3. Set Environment Variables

```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
export YOUTUBE_API_KEY='your-youtube-api-key-here'
```

**Or** edit `.env` file and source it:
```bash
cp .env.example .env
# Edit .env with your keys
set -a; source .env; set +a
```

## 4. Run the CLI

```bash
python main.py
```

## 5. Try the YouTube Agent

1. Select `1. YouTube Channel Analyzer`
2. Select `1. Download channel data`
3. Enter a YouTube channel URL, for example:
   - `https://www.youtube.com/@mkbhd`
   - `https://www.youtube.com/@veritasium`
4. Wait for download (this may take a few minutes)
5. When prompted, choose **YES** to upload to File Search
6. Back at the menu, select `2. Chat with channel content`
7. Start asking questions!

## Example Queries

```
What topics does this channel cover?

Which video is the most popular?

What are viewers saying about AI?

Summarize the last 5 videos

Show me trending topics in the comments
```

## That's it!

You're now chatting with YouTube channel content using AI with automatic citations.

## Next Steps

- Try different channels
- Check out the full README.md for more features
- Add your own agents (see "Adding New Agents" in README.md)

## Troubleshooting

**"Missing API keys" error:**
- Make sure you exported the environment variables
- Try running: `set -a; source .env; set +a`

**Import errors:**
- Run: `pip install -r requirements.txt`

**YouTube quota exceeded:**
- YouTube API has daily limits
- Wait 24 hours or create a new API key

For more help, see README.md or check the code in `agents/`.
