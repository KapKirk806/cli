# Multi-Agent CLI - Architecture

This document explains the architecture and design decisions of the Multi-Agent CLI system.

## Overview

The Multi-Agent CLI is designed to be:
- **Extensible**: Easy to add new agents
- **Modular**: Each component has a single responsibility
- **User-friendly**: Menu-driven UI with clear feedback
- **Configurable**: Agents can be customized via configuration files

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   (CLI Entry Point)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  UI Module   │    │   Registry   │
│  (utils/ui)  │    │ (agents/base)│
└──────────────┘    └───────┬──────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌───────────────┐      ┌───────────────┐
        │ YouTube Agent │      │ Future Agents │
        │   (agents/)   │      │   (agents/)   │
        └───────┬───────┘      └───────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────────┐
│  YouTube API │  │ Gemini File      │
│              │  │ Search           │
└──────────────┘  └──────────────────┘
```

## Core Components

### 1. Main Entry Point (`main.py`)

**Responsibilities:**
- Initialize UI
- Create and populate agent registry
- Display main menu
- Handle user input and navigation
- Manage application lifecycle

**Key Functions:**
- `main()`: Application entry point
- Main loop for menu navigation
- Exception handling and user interrupts

### 2. Base Agent System (`agents/base.py`)

#### `AgentConfig`
Data class holding agent configuration:
- `id`: Unique identifier
- `name`: Display name
- `description`: User-facing description
- `personality`: Agent's conversational style
- `system_prompt`: Instructions for the AI model
- `model`: Gemini model to use
- `temperature`: Response creativity (0-1)
- `knowledge_base_path`: Where to store agent data
- `mcp_servers`: MCP servers to use (future)
- `tools`: Tools available to agent (future)

Methods:
- `from_file()`: Load config from JSON
- `to_file()`: Save config to JSON

#### `BaseAgent`
Abstract base class for all agents:

**Properties:**
- `config`: Agent configuration
- `knowledge_base_path`: Storage location
- `id`, `name`, `description`: Config accessors

**Methods:**
- `run(ui)`: Main entry point (must implement)
- `get_system_prompt()`: Build full system prompt
- `save_to_knowledge_base()`: Store data
- `load_from_knowledge_base()`: Retrieve data

#### `AgentRegistry`
Manages agent lifecycle:

**Methods:**
- `register(agent)`: Add agent to registry
- `get_agent(id)`: Retrieve agent by ID
- `list_agents()`: Get all agents info
- `unregister(id)`: Remove agent

### 3. UI System (`utils/ui.py`)

#### `Color`
ANSI color codes for terminal styling:
- Regular colors (red, green, blue, etc.)
- Bright variants
- Special formatting (bold, dim)

#### `UI`
Terminal interface helper:

**Methods:**
- `clear_screen()`: Clear terminal
- `print_banner()`: Show app logo
- `print_header()`: Section headers
- `print_success/error/warning/info()`: Styled messages
- `get_input()`: Get user input with prompt
- `confirm()`: Yes/no questions
- `pause()`: Wait for duration
- `show_spinner()`: Loading indicator

### 4. YouTube Agent (`agents/youtube_agent.py`)

Specialized agent for YouTube channel analysis.

#### Data Collection

**Channel Data:**
- `_get_channel_info()`: Basic channel metadata
- `_get_channel_videos()`: All video IDs from channel

**Video Data:**
- `_get_video_details()`: Title, description, stats
- `_get_video_comments()`: Comments and replies
- Transcript via `youtube-transcript-api`

**Storage Structure:**
```
data/youtube_analyzer/
└── {channel_name}/
    ├── channel_info.json          # Channel metadata
    ├── complete_data.json          # All data combined
    ├── video_{id}.json             # Individual videos
    └── .file_search_store          # File Search store ID
```

#### File Search Integration

1. **Upload Phase:**
   - Create File Search store
   - Upload JSON files
   - Save store ID locally

2. **Chat Phase:**
   - Check for store ID
   - If exists: Use File Search (with citations)
   - If not: Use local context (no citations)

### 5. Gemini File Search (`utils/gemini_file_search.py`)

Wrapper around Google's File Search API.

#### `FileSearchManager`

**Store Management:**
- `create_store()`: Create new File Search store
- `delete_store()`: Remove store
- `list_stores()`: Get all stores

**File Operations:**
- `upload_file()`: Upload single file
- `upload_directory()`: Batch upload with glob patterns
- Handles file processing status

**Querying:**
- `query()`: One-off question
- `create_chat_session()`: Interactive chat
- Automatic context injection

#### `FileSearchChat`

Interactive chat interface:
- `send_message()`: Send user message
- `get_history()`: Retrieve conversation
- Maintains session state

## Data Flow

### YouTube Agent - Download Flow

```
User Input (Channel URL)
    ↓
Extract Channel ID
    ↓
Fetch Channel Info → Save channel_info.json
    ↓
Get All Video IDs
    ↓
For Each Video:
    ├─→ Get Video Details
    ├─→ Get Transcript
    ├─→ Get Comments & Replies
    └─→ Save video_{id}.json
    ↓
Combine All Data → Save complete_data.json
    ↓
(Optional) Upload to File Search
    ├─→ Create Store
    ├─→ Upload All JSON Files
    └─→ Save Store ID
```

### Chat Flow

```
User Selects Channel
    ↓
Load complete_data.json
    ↓
Check for .file_search_store
    ↓
┌──────────────┴──────────────┐
│                             │
File Search Available    No File Search
│                             │
Create FileSearchChat    Create Local Context
│                             │
User Query                User Query
│                             │
→ File Search RAG       → Embed Context in Prompt
│                             │
Response + Citations     Response (No Citations)
```

## Adding New Agents

### Step-by-Step Guide

1. **Create Agent Class**
   ```python
   # agents/my_agent.py
   from agents.base import BaseAgent, AgentConfig

   class MyAgent(BaseAgent):
       def __init__(self):
           config = AgentConfig(...)
           super().__init__(config)

       def run(self, ui):
           # Agent logic here
           pass
   ```

2. **Implement Agent Logic**
   - Use `ui` for user interaction
   - Save data to `self.knowledge_base_path`
   - Use `self.file_search_manager` for RAG

3. **Register Agent**
   ```python
   # main.py
   from agents.my_agent import MyAgent

   registry.register(MyAgent())
   ```

### Agent Design Patterns

**Pattern 1: Data Collection + Chat**
1. Collect external data
2. Save to knowledge base
3. Upload to File Search
4. Provide chat interface

**Pattern 2: Interactive Tools**
1. Present tool interface
2. Process user inputs
3. Generate outputs
4. Save results

**Pattern 3: Analysis Pipeline**
1. Load existing data
2. Run analysis
3. Present results
4. Allow Q&A

## Configuration System

### Agent Configuration Files

Located in `config/`, agents can be configured via JSON:

```json
{
  "id": "unique_id",
  "name": "Display Name",
  "description": "What the agent does",
  "personality": "How the agent behaves",
  "system_prompt": "Instructions for AI",
  "model": "gemini-1.5-pro",
  "temperature": 0.7,
  "knowledge_base_path": "data/agent_id",
  "mcp_servers": ["server1", "server2"],
  "tools": ["tool1", "tool2"]
}
```

Load with:
```python
config = AgentConfig.from_file(Path("config/agent.json"))
```

## Future Extensions

### Planned Features

1. **MCP Server Integration**
   - Connect agents to MCP servers
   - Access external tools and APIs
   - Defined in agent config

2. **Custom Tool System**
   - Define tools per agent
   - Tool registration system
   - Automatic prompt injection

3. **Multi-Agent Collaboration**
   - Agents can call other agents
   - Shared knowledge bases
   - Workflow orchestration

4. **Enhanced File Search**
   - Multiple stores per agent
   - Custom embedding models
   - Advanced filtering

5. **Export/Import**
   - Export chat histories
   - Import external data
   - Share agent configurations

## Best Practices

### For Agent Development

1. **Use the UI Helper**
   - Clear, consistent user feedback
   - Error handling with helpful messages
   - Loading indicators for long operations

2. **Structure Data Properly**
   - Use JSON for structured data
   - Separate files for different data types
   - Include metadata (timestamps, versions)

3. **Handle Errors Gracefully**
   - Try/except around API calls
   - Inform user of issues
   - Provide fallback options

4. **Optimize for File Search**
   - Break large files into smaller chunks
   - Use descriptive filenames
   - Include context in each file

5. **Document Your Agent**
   - Clear description
   - Example use cases
   - Required API keys/dependencies

### For Users

1. **API Key Management**
   - Never commit API keys to git
   - Use environment variables
   - Rotate keys periodically

2. **Data Storage**
   - Data is stored in `data/` by default
   - Can grow large - monitor disk usage
   - Consider cleanup for old channels

3. **API Quotas**
   - YouTube API has daily limits
   - File Search has storage limits
   - Plan downloads accordingly

## Security Considerations

1. **API Keys**
   - Stored in environment variables
   - Never logged or displayed
   - `.gitignore` prevents accidental commits

2. **Data Privacy**
   - Downloaded data stored locally
   - File Search data in Google's infrastructure
   - No data shared between agents without user action

3. **Input Validation**
   - User inputs are sanitized for filenames
   - URL validation before API calls
   - Error handling prevents crashes

## Performance

### Optimization Strategies

1. **Batch Operations**
   - Upload multiple files at once
   - Parallel API calls where possible

2. **Caching**
   - Store API responses locally
   - Reuse data when available
   - Timestamp checks for freshness

3. **Lazy Loading**
   - Load data only when needed
   - Stream large responses
   - Pagination for large datasets

4. **Context Management**
   - Limit context size for prompts
   - Summarize when necessary
   - Use File Search for large datasets

## Testing

### Manual Testing Checklist

For each agent:
- [ ] Loads without errors
- [ ] Menu displays correctly
- [ ] Happy path works end-to-end
- [ ] Error handling works
- [ ] Data persists correctly
- [ ] File Search integration works
- [ ] Chat interface functional

### Integration Testing

- [ ] Multiple agents can coexist
- [ ] Registry works correctly
- [ ] UI is consistent across agents
- [ ] File paths don't conflict

## Troubleshooting

### Common Issues

**Import Errors**
- Check `requirements.txt` installed
- Verify Python version (3.9+)

**API Errors**
- Verify API keys are set
- Check quota limits
- Validate network connection

**File Search Issues**
- Ensure files uploaded successfully
- Check store ID saved correctly
- Verify API key has permissions

**Data Issues**
- Check write permissions on `data/`
- Verify JSON formatting
- Look for path issues

## Resources

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [File Search Guide](https://ai.google.dev/gemini-api/docs/file-search)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
