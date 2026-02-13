# Karohani Claude Code Plugin

A plugin development lab for Claude Code. A marketplace covering Skills, Hooks, Agents, and Commands.

## Writing Guidelines

- All markdown documents (`.md` files) must be written in English.
- **SKILL.md localization rule**:
  - `SKILL.md` is the primary file and must always be written in English.
  - A Korean translation must be provided as `SKILL-ko.md` in the same directory.
  - When `SKILL.md` is created or updated, `SKILL-ko.md` must also be created or updated to stay in sync.
  - Both files must have identical structure; only the language differs.

## Installation

```bash
# Add marketplace
/plugin marketplace add jay/my-karohani-claude-code-plugin

# Install plugins
/plugin install hello-skill
/plugin install session-wrap
/plugin install youtube-digest
/plugin install voice
/plugin install tdd

# Session wrap usage
/wrap              # Interactive session analysis
/wrap [message]    # Quick commit

# YouTube video analysis (requires yt-dlp)
/youtube [URL]         # Extract subtitles + summarize
/youtube [URL] --quiz  # Include quiz

# Voice input/output (requires sox, whisper-cpp)
/voice                 # Check status
/voice ask             # Ask via voice
/voice on|off          # Toggle TTS on/off

# TDD meta plugin
/tdd init              # Detect stack → generate .claude/skills/tdd/
/tdd init --with-hooks # Also generate hooks.json (auto-test)
```

## Project Structure (Marketplace)

```
.
├── .claude-plugin/
│   ├── plugin.json           # Root metadata
│   └── marketplace.json      # Plugin list definition
├── plugins/
│   ├── hello-skill/          # Skills example
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/hello/SKILL.md
│   ├── session-wrap/         # Multi-agent workflow
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/           # 5 specialized agents
│   │   │   ├── doc-updater.md
│   │   │   ├── automation-scout.md
│   │   │   ├── learning-extractor.md
│   │   │   ├── followup-suggester.md
│   │   │   └── duplicate-checker.md
│   │   ├── commands/wrap.md
│   │   └── skills/
│   │       ├── session-wrap/SKILL.md
│   │       ├── history-insight/SKILL.md
│   │       └── session-analyzer/SKILL.md
│   ├── youtube-digest/       # YouTube video summarizer
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/           # 4 specialized agents
│   │   │   ├── transcript-extractor.md
│   │   │   ├── proper-noun-corrector.md
│   │   │   ├── summary-generator.md
│   │   │   └── quiz-generator.md
│   │   ├── commands/youtube.md
│   │   └── skills/
│   │       └── youtube-digest/SKILL.md
│   ├── voice/                # Voice input/output
│   │   ├── .claude-plugin/plugin.json
│   │   ├── pyproject.toml    # uv run dependencies
│   │   ├── config.json       # STT/TTS configuration
│   │   ├── hooks/hooks.json  # Stop, Notification, PostToolUse → auto TTS
│   │   ├── scripts/          # Python scripts
│   │   │   ├── speak.py      # TTS (Haiku summary + say)
│   │   │   ├── record.py     # Recording (sox)
│   │   │   ├── transcribe.py # STT (whisper/OpenAI)
│   │   │   └── config_loader.py
│   │   ├── commands/voice.md
│   │   └── skills/
│   │       └── voice/SKILL.md
│   └── tdd/                  # TDD meta plugin
│       ├── .claude-plugin/plugin.json
│       ├── templates/        # Stack-specific TDD skill templates
│       │   ├── nodejs.md
│       │   ├── python.md
│       │   └── generic.md
│       ├── commands/tdd.md
│       └── skills/
│           └── tdd/SKILL.md  # Per-project skill generation workflow
├── scripts/
│   ├── install.py            # Install script
│   ├── uninstall.py          # Uninstall script
│   └── dev.py                # Dev mode setup
├── CLAUDE.md                 # This file
├── README.md
└── pyproject.toml
```

## Plugin List

| Plugin | Type | Description |
|--------|------|-------------|
| hello-skill | Skills | Simple greeting skill - `/hello` trigger |
| session-wrap | Skills + Agents | Multi-agent session analysis - `/wrap` trigger |
| youtube-digest | Skills + Agents | YouTube video summarizer - `/youtube` trigger |
| voice | Skills + Hooks | Voice input/output (STT/TTS) - `/voice` trigger |
| tdd | Skills (Meta) | TDD meta plugin - generates per-project `.claude/skills/tdd/` |
| functional-code | Skills | FP guidance (Grokking Simplicity) - `/functional-code` trigger |

## Five Plugin Components

### 1. Skills (SKILL.md)
- **Location**: `plugins/<name>/skills/<skill-name>/SKILL.md`
- **Purpose**: Define prompts/workflows, works without code
- **Trigger**: `/skillname` slash command
- **Example**: `plugins/hello-skill/`, `plugins/session-wrap/skills/`

### 2. Hooks (hooks.json)
- **Location**: `plugins/<name>/hooks/hooks.json`
- **Purpose**: Event-driven auto-execution (Stop, PreToolUse, etc.)
- **Trigger**: Claude Code events
- **Example**: `plugins/voice/hooks/` (TTS execution on Stop, Notification, PostToolUse events)

### 3. MCP Servers (Python)
- **Location**: `plugins/<name>/src/server.py`
- **Purpose**: Custom tools, API calls, external service integration
- **Config**: `mcpServers` field in plugin.json

### 4. Agents (agents/*.md)
- **Location**: `plugins/<name>/agents/<agent-name>.md`
- **Purpose**: Define specialized analysis/processing agents
- **Feature**: Can be executed in parallel via the Task tool
- **Example**: `plugins/session-wrap/agents/` (5 agents)

### 5. Commands (commands/*.md)
- **Location**: `plugins/<name>/commands/<command>.md`
- **Purpose**: Define slash commands, entry points for Skills
- **Example**: `plugins/session-wrap/commands/wrap.md`

## Adding a New Plugin

### 1. Create directories
```bash
mkdir -p plugins/<name>/.claude-plugin
mkdir -p plugins/<name>/skills/<name>  # For Skills
mkdir -p plugins/<name>/src            # For MCP
mkdir -p plugins/<name>/agents         # For Agents
mkdir -p plugins/<name>/commands       # For Commands
```

### 2. Create plugin.json
```json
{
  "name": "<name>",
  "version": "0.1.0",
  "description": "Description",
  "mcpServers": { ... }  // If MCP server
}
```

### 3. Register in marketplace.json
```json
{
  "owner": { "name": "Author", "email": "email@example.com" },
  "plugins": [
    {
      "name": "<name>",
      "source": "./plugins/<name>",
      "version": "1.0.0",
      "author": { "name": "Author", "email": "email@example.com" },
      "category": "productivity"
    }
  ]
}
```
**Note**: Use `source` field instead of `path`, `owner` is required.

## Development Insights

### Lessons Learned
- MCP servers are configured via `.mcp.json` or the `mcpServers` field in plugin.json
- Skills can define a slash command with just a single SKILL.md file
- `uv` is convenient for Python dependency management
- Agents are defined in markdown and executed via the Task tool
- hooks.json structure: `{"hooks": {"EventName": [{"hooks": [{type, command}]}]}}` (nested structure)
- venv is required in externally-managed environments like macOS Homebrew Python
- dev.py loads plugins using the `--plugin-dir` flag (alias or wrapper mode)
- Marketplace cache (~/.claude/plugins/cache/) sometimes needs manual updates
- Stop event hooks extract the last response from transcript files (~/.claude/projects/) (more stable)
- Background TTS: use `subprocess.Popen(start_new_session=True)` pattern
- Korean language detection: checking Unicode range (0xAC00-0xD7A3) is efficient
- **.venv is not copied during marketplace installation** (.gitignore excluded) → use pyproject.toml + `uv run` pattern
- `uv run --directory ${pluginDir}` pattern: auto-install/run dependencies without venv (hooks use `${CLAUDE_PLUGIN_ROOT}`)
- **Hook cwd is the cache directory, not the project** (`~/.claude/plugins/cache/`) → `os.getcwd()` is unreliable
- **CLAUDE_PROJECT_ROOT env var does not exist** - accessing project path requires searching all of `~/.claude/projects/`

### Claude Code Plugin System File Structure
```
~/.claude/
├── plugins/
│   ├── known_marketplaces.json    # Registered marketplace list
│   ├── installed_plugins.json     # Installed plugin list
│   └── marketplaces/
│       └── {marketplace-name}/    # Plugins stored per marketplace
└── settings.json                  # Managed via enabledPlugins
```

### Failed Attempts
- Placing mcpServers in settings.local.json causes schema errors
- Must use `source` field instead of `path` in marketplace.json
- hooks.json "hooks" cannot be a simple array/object (nesting required: EventName → [{hooks: [...]}])
- Installing packages without venv in the current Python environment causes externally-managed errors (Homebrew)
- Cache inconsistency requires explicit cache deletion or Claude Code restart
- `${pluginDir}` is not available in hooks.json → use `${CLAUDE_PLUGIN_ROOT}` (venv requires absolute paths)
- `os.getcwd()` based project directory detection fails in hooks → runs from cache directory, must search all of `~/.claude/projects/`
- Registering marketplaces via `extraKnownMarketplaces` field in `settings.json` causes infinite loading
- Manipulating `known_marketplaces.json` directly causes marketplace conflicts → switched to `--plugin-dir` approach

### Useful Patterns
- `${pluginDir}` variable is used in commands/skills; hooks use `${CLAUDE_PLUGIN_ROOT}`
- Multi-agent pipeline: Phase 1 parallel execution → Phase 2 verification pattern (see session-wrap)
- Agents can be executed in parallel via the Task tool
- SKILL.md description pattern: `"This skill should be used when the user asks to..."` format improves Claude skill matching accuracy
- Multilingual trigger keywords: listing both Korean/English increases matching coverage (e.g., `"wrap up"`, `"세션 마무리"`, `"마무리해줘"`)
- `/skill` shortcut: setting plugin.json name to `voice` allows `voice:voice` skill to be accessed via `/voice`
- Using claude-agent-sdk for Haiku summary calls is more concise than direct anthropic calls
- **Use `--plugin-dir` flag during development**: `claude --plugin-dir ./plugins/my-plugin` format recommended

### Dev Mode (dev.py)
Loads plugins using the official `--plugin-dir` flag.

```bash
python scripts/dev.py              # Alias mode (default) - adds alias to ~/.zshrc
python scripts/dev.py --alias      # Alias mode
python scripts/dev.py --wrapper    # Wrapper mode - creates ~/.local/bin/claude-dev
python scripts/dev.py --off        # Deactivate (removes both alias + wrapper)
python scripts/dev.py --status     # Check current status
```

**Alias mode** (`claude` command runs with plugins):
- Run `claude` in a new terminal to load plugins
- Run original claude: `\claude` or `command claude`

**Wrapper mode** (separate `claude-dev` command):
- `claude-dev`: Run in dev mode (with plugins loaded)
- `claude`: Run in normal mode

File changes are reflected immediately (only session restart needed).

## References

- [team-attention/plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives)
- [MCP Python SDK](https://github.com/anthropics/mcp-python-sdk)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)
