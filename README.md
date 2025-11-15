# Multi-Agent CLI System

A terminal-based CLI system for running various specialized AI agents powered by Google Gemini and File Search.

## Features

- **Menu-Driven Interface**: Beautiful terminal UI with color-coded output
- **Multiple Specialized Agents**: Extensible architecture for different task-specific agents
- **Gemini File Search Integration**: Full RAG capabilities with automatic citations
- **Agent Configuration**: Each agent has unique personality, prompts, and knowledge bases

## Current Agents

### 1. YouTube Channel Analyzer

Downloads and analyzes YouTube channel content:
- Complete video transcripts
- Video metadata (titles, descriptions, views, likes)
- Comments and replies with engagement metrics
- Upload dates and statistics

Then chat with the content using natural language:
- "What topics does this creator focus on?"
- "Show me the most popular videos"
- "What are viewers saying about [topic]?"
- Get answers with automatic citations from File Search!

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- YouTube Data API v3 key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cli
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**

   **Gemini API Key:**
   - Visit https://ai.google.dev/
   - Create an account or sign in
   - Go to "Get API Key"
   - Create a new API key

   **YouTube API Key:**
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable "YouTube Data API v3"
   - Create credentials (API Key)

   **Set environment variables:**
   ```bash
   export GEMINI_API_KEY='your-gemini-api-key'
   export YOUTUBE_API_KEY='your-youtube-api-key'
   ```

   To make them permanent, add to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   echo "export GEMINI_API_KEY='your-gemini-api-key'" >> ~/.bashrc
   echo "export YOUTUBE_API_KEY='your-youtube-api-key'" >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

### Running the CLI

```bash
python main.py
```

### YouTube Agent Workflow

1. **Download Channel Data**
   - Select "YouTube Channel Analyzer" from main menu
   - Choose "Download channel data"
   - Enter YouTube channel URL or ID
   - Wait for download to complete
   - Choose whether to upload to File Search

2. **Chat with Content**
   - Select "Chat with channel content"
   - Choose a downloaded channel
   - Start asking questions!

### Example Queries

```
You: What are the main topics this creator covers?

You: Which video has the most engagement?

You: What do viewers think about [specific topic]?

You: Summarize the content from the last 5 videos

You: Are there any common complaints in the comments?
```

## Project Structure

```
cli/
├── main.py                         # Main CLI entry point
├── agents/
│   ├── __init__.py
│   ├── base.py                     # Base agent classes
│   └── youtube_agent.py            # YouTube analyzer agent
├── utils/
│   ├── __init__.py
│   ├── ui.py                       # Terminal UI utilities
│   └── gemini_file_search.py      # Gemini File Search wrapper
├── config/                          # Agent configurations
├── data/                            # Agent knowledge bases
│   └── youtube_analyzer/           # YouTube agent data
│       └── {channel_name}/         # Per-channel directories
│           ├── channel_info.json
│           ├── complete_data.json
│           ├── video_*.json
│           └── .file_search_store  # File Search store ID
├── logs/                            # Application logs
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                        # Claude instructions
└── README.md                        # This file
```

## Adding New Agents

To add a new agent:

1. **Create agent class** in `agents/your_agent.py`:
   ```python
   from agents.base import BaseAgent, AgentConfig
   from utils.ui import UI

   class YourAgent(BaseAgent):
       def __init__(self):
           config = AgentConfig(
               id="your_agent",
               name="Your Agent Name",
               description="What your agent does",
               personality="Agent's personality/style",
               system_prompt="Agent's system instructions",
               model="gemini-1.5-pro"
           )
           super().__init__(config)

       def run(self, ui: UI):
           # Implement your agent logic
           pass
   ```

2. **Register in main.py**:
   ```python
   from agents.your_agent import YourAgent

   # In main():
   registry.register(YourAgent())
   ```

## Gemini File Search

This system uses Google's **File Search** feature, which provides:

- **Automatic RAG**: Handles chunking, embeddings, and retrieval
- **Vector Search**: Semantic understanding of queries
- **Built-in Citations**: Responses cite sources automatically
- **Multi-format Support**: PDF, DOCX, TXT, JSON, code files

### Pricing

- **Indexing**: $0.15 per 1M tokens (one-time per file)
- **Storage**: Free (1GB on free tier)
- **Query-time Search**: FREE

## Testing

The project includes a comprehensive test suite to validate all components:

```bash
python3 test_suite.py
```

### What Gets Tested

- **Module Imports**: All components import correctly
- **UI Components**: Terminal UI and color system
- **Agent System**: Base classes, registry, configuration
- **YouTube Agent**: Initialization, methods, data handling
- **File Search**: Manager initialization
- **Data Storage**: Save/load operations
- **Error Handling**: Edge cases and missing data

All tests run **without requiring API keys** - they validate code structure and logic.

### Test Results

```
✅ All 18 tests passed!
```

## Troubleshooting

### API Key Issues

```
Error: Missing API keys: GEMINI_API_KEY
```
→ Make sure you've exported the environment variables

### YouTube API Quota

YouTube API has daily quota limits. If you hit the limit:
- Wait 24 hours for reset
- Or create additional API keys in Google Cloud Console

### Import Errors

```
ModuleNotFoundError: No module named 'google.generativeai'
```
→ Run `pip install -r requirements.txt`

### Permission Errors

```
PermissionError: [Errno 13] Permission denied: 'data/'
```
→ Make sure the CLI has write permissions in the directory

## Future Enhancements

- [ ] Web Scraper Agent
- [ ] UI Builder Agent
- [ ] Code Analysis Agent
- [ ] MCP Server Integration
- [ ] Custom tool support per agent
- [ ] Export chat histories
- [ ] Multi-language support

## Contributing

Feel free to add new agents or improve existing ones!

## License

MIT License

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the agent code in `agents/`
3. Check Gemini API docs: https://ai.google.dev/gemini-api/docs
4. Check YouTube API docs: https://developers.google.com/youtube/v3
