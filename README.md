# EnableMind - Multi-Agent Research System

A multi-agent system that researches a technical topic and produces a structured analysis report. Built with [CrewAI](https://www.crewai.com/) for agent orchestration, the system coordinates three specialized agents -- Research, Analysis, and Report Generation -- to deliver comprehensive, citation-backed research reports.

## Architecture

```
                        +-----------------+
                        |   User / CLI    |
                        |  (--topic ...)  |
                        +--------+--------+
                                 |
                        +--------v--------+
                        |   CrewAI Crew   |
                        |  (Sequential)   |
                        +--------+--------+
                                 |
              +------------------+------------------+
              |                  |                   |
     +--------v--------+ +------v--------+ +--------v--------+
     |  Research Agent  | | Analysis Agent| |  Report Agent   |
     |  (Specialist)    | |  (Analyst)    | | (Tech Writer)   |
     +--------+--------+ +------+--------+ +--------+--------+
              |                  |                   |
     +--------v--------+ +------v--------+ +--------v--------+
     | - WebSearchTool  | | - Delegation  | | - MarkdownExport|
     | - WebScraperTool | |   (feedback)  | | - PDFExportTool |
     +-----------------+ +---------------+ +-----------------+
```

### Agents

| Agent | Role | Tools | Delegation |
|-------|------|-------|------------|
| **Research Agent** | Technical Research Specialist | WebSearchTool, WebScraperTool | No |
| **Analysis Agent** | Research Analyst | None (uses delegation) | Yes -- can delegate back to Research Agent |
| **Report Agent** | Technical Writer | MarkdownExportTool, PDFExportTool | No |

### Workflow

1. **Research Phase**: The Research Agent searches the web using DuckDuckGo and scrapes relevant pages to gather comprehensive information on the topic.
2. **Analysis Phase**: The Analysis Agent synthesizes findings, identifies gaps, calculates a quality score (0.0--1.0), and can delegate back to the Research Agent for additional information if quality is below threshold.
3. **Report Phase**: The Report Agent structures everything into a polished report with executive summary, key findings, detailed analysis, and sources. Exports to Markdown and PDF.

### Feedback Loop

The Analysis Agent implements a quality-driven feedback loop:
- Evaluates research quality across four dimensions: source diversity, claim verification, coverage depth, and recency.
- If the quality score falls below 0.7, it delegates specific questions back to the Research Agent.
- This loop runs up to a configurable maximum number of iterations (default: 3) to prevent infinite cycles.

## Project Structure

```
enablemind/
├── config/
│   ├── __init__.py
│   └── settings.py              # Pydantic Settings (API keys, model config)
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py    # Technical Research Specialist
│   │   ├── analysis_agent.py    # Research Analyst
│   │   └── report_agent.py      # Technical Writer
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── research_task.py     # Research task definition
│   │   ├── analysis_task.py     # Analysis task with feedback loop
│   │   └── report_task.py       # Report generation task
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tool.py       # DuckDuckGo web search
│   │   ├── scraper_tool.py      # BeautifulSoup web scraper
│   │   └── export_tool.py       # Markdown and PDF export
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py    # Structured logging (structlog)
├── tests/
│   └── __init__.py
├── outputs/                     # Generated reports (gitignored)
├── .env.example                 # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key (for the LLM powering the agents)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd enablemind
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:

   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | -- | Your OpenAI API key |
| `TAVILY_API_KEY` | No | -- | Tavily API key (not used in current implementation) |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_RESEARCH_ITERATIONS` | No | `3` | Max feedback loop iterations |

## Usage

Run a research session on any technical topic:

```bash
python -m src.main --topic "Your technical topic here"
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--topic` | The technical topic to research (required) | -- |
| `--max-iterations` | Maximum analysis-research feedback loop iterations | `3` |

### Example

```bash
python -m src.main --topic "Large Language Model fine-tuning techniques"
```

### Expected Output

The system produces:
- **Console output**: Real-time agent activity logs showing each agent's reasoning and tool usage.
- **Markdown report**: Saved to `outputs/report_<timestamp>.md`
- **PDF report** (if weasyprint is installed): Saved to `outputs/report_<timestamp>.pdf`
- **HTML fallback** (if weasyprint is not available): Saved to `outputs/report_<timestamp>.html`

#### Report Structure

```
# Research Report: <Topic>

## Executive Summary
(Under 200 words)

## Introduction
Background and scope...

## Key Findings
1. Finding with supporting evidence...
2. ...

## Detailed Analysis
In-depth exploration with citations...

## Recommendations
Actionable next steps...

## Conclusion
Summary of significance...

## Sources
- [1] Title - URL
- [2] ...
```

## Troubleshooting

### "Error: duckduckgo-search package is not installed"

```bash
pip install duckduckgo-search
```

### "weasyprint not available; styled HTML report saved"

PDF export requires weasyprint, which depends on system libraries. If you only need Markdown output, this is safe to ignore. To install weasyprint:

```bash
# macOS
brew install pango
pip install weasyprint

# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip install weasyprint
```

### OpenAI API errors

- Verify your API key is set correctly in `.env`.
- Check that your API key has sufficient credits/quota.
- If you hit rate limits, the agents have built-in retry logic (`max_retry_limit` on each agent).

### Import errors

Make sure you run the project from the repository root directory:

```bash
cd enablemind
python -m src.main --topic "..."
```

### No output files generated

- Check that the `outputs/` directory is writable.
- Review console logs for agent errors -- verbose mode is enabled by default.

---

## Technical Decision Document

### Architecture and Framework Decisions

**Framework Selection: CrewAI**

We chose CrewAI as the multi-agent orchestration framework for the following reasons:

- **Purpose-built for multi-agent workflows**: CrewAI provides first-class abstractions for Agents, Tasks, Tools, and Crews, mapping directly to the assignment requirements.
- **Built-in delegation**: The `allow_delegation=True` flag enables the Analysis Agent to delegate back to the Research Agent for gap-filling, implementing the required feedback loop without custom routing logic.
- **Sequential and hierarchical process support**: CrewAI's `Process.sequential` ensures agents execute in the correct order (Research -> Analysis -> Report) with context passing between tasks.
- **Tool integration**: The `BaseTool` class provides a clean interface for building custom tools with Pydantic input schemas and error handling.

*Alternatives considered*:
- **LangGraph**: More flexible for complex state machines but requires more boilerplate for simple sequential workflows. Better suited for dynamic routing patterns.
- **AutoGen**: Strong at multi-agent conversations but less structured for task-based workflows with clear tool boundaries.
- **Custom implementation**: Maximum control but significantly more development time for features CrewAI provides out of the box (delegation, memory, verbose logging).

**LLM Selection: GPT-4o-mini**

- Cost-effective for research tasks while maintaining high quality output.
- Fast inference speeds support the iterative feedback loop without excessive latency.
- Configurable via environment variable (`OPENAI_MODEL`) to easily switch to GPT-4o or other models.
- All three agents share the same model to keep configuration simple; differentiation comes from role-specific prompting and tool access.

**State Management**

- CrewAI manages context passing between tasks via the `context` parameter on Task definitions.
- The Analysis Task receives context from the Research Task; the Report Task receives context from both.
- Agent memory is enabled at the Crew level (`memory=True`), allowing agents to recall information across interactions within a session.
- Configuration state is managed centrally through Pydantic Settings, loaded from environment variables and `.env` file.

**Orchestration Pattern: Sequential with Delegation**

- The primary flow is sequential: Research -> Analysis -> Report.
- Within this flow, the Analysis Agent can delegate back to the Research Agent for additional information, creating a controlled feedback loop.
- This hybrid approach ensures predictable execution order while allowing dynamic interaction when quality thresholds are not met.
- Iteration control (`max_iterations` parameter) prevents infinite delegation loops.

### Implementation Details

**Tool Integration**

Three custom tools built on CrewAI's `BaseTool`:

1. **WebSearchTool**: Uses `duckduckgo-search` for free web search (no API key required). Returns formatted results with titles, URLs, and snippets.
2. **WebScraperTool**: Uses `requests` + `BeautifulSoup` to extract clean text content from web pages. Removes non-content elements (scripts, nav, footer) and identifies main content areas.
3. **MarkdownExportTool / PDFExportTool**: Saves reports to disk. PDF generation uses `weasyprint` with a styled HTML intermediate, with a graceful fallback to HTML if weasyprint is unavailable.

**Agent Differentiation**

| Aspect | Research Agent | Analysis Agent | Report Agent |
|--------|---------------|----------------|--------------|
| **Prompting** | Focused on thorough search and source verification | Focused on synthesis, gap detection, and quality scoring | Focused on structure, clarity, and formatting |
| **Tools** | WebSearchTool, WebScraperTool | None | MarkdownExportTool, PDFExportTool |
| **Delegation** | Disabled | Enabled (can request more research) | Disabled |
| **Max iterations** | 5 | 3 | 5 |
| **Retry limit** | 3 | 2 | 2 |

**Error Handling**

- Each tool returns descriptive error messages rather than raising exceptions, allowing agents to reason about failures and try alternative approaches.
- HTTP errors in the scraper are categorized (timeout, HTTP status, connection error) for clear diagnostics.
- Import errors are caught gracefully with installation instructions in the error message.
- Agent-level retry limits (`max_retry_limit`) handle transient LLM failures.
- The feedback loop has a hard iteration cap to prevent runaway execution.

### Optimization and Production Readiness

**Token/Cost Optimization**

- GPT-4o-mini is used by default for cost efficiency.
- Web scraper truncates content to 5,000 characters by default to avoid sending excessive context to the LLM.
- Search results are capped at 5 per query by default.
- Both limits are configurable per-tool invocation.

**Scalability Considerations**

For production at scale, the following changes would be recommended:
- Switch to async HTTP requests for parallel web scraping.
- Add a caching layer for search results and scraped content to avoid redundant API calls.
- Implement a proper task queue for handling multiple concurrent research sessions.
- Add persistent storage for research results and reports.

**Convergence and Control**

- The feedback loop between Analysis and Research is bounded by `max_iterations` (default: 3).
- Quality score threshold (0.7) determines whether additional research is needed.
- After exhausting iterations, the system proceeds with the best available data rather than failing.
- Each agent has its own `max_iter` limit preventing individual agent loops.

**Trade-offs and Limitations**

- **DuckDuckGo search**: Free but may have rate limits under heavy use. For production, consider Tavily, Serper, or Google Custom Search API.
- **Sequential execution**: Agents run one at a time. Parallel execution of Research and Analysis is not possible since Analysis depends on Research output.
- **PDF export**: Requires weasyprint and its system dependencies (Pango). The HTML fallback ensures the system remains functional without it.
- **No persistent memory**: Agent memory is session-scoped. Previous research sessions are not recalled.
- **Single LLM provider**: Currently OpenAI-only. Adding support for Anthropic, local models, or other providers would require extending the configuration.
- **No authentication for web scraping**: Some sources may block the scraper's requests. A rotating proxy or authenticated access would improve reliability.
