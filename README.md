# 🧠 Google Cloud Natural Language API — MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that connects **Claude** to the **Google Cloud Natural Language API**, enabling sentiment analysis, entity extraction, content classification, and syntax analysis as native Claude tools.

> 🔐 **No `.env` file needed.** Your API key is stored securely in your local Claude Desktop config — it never touches this repo.

---

## ✨ Features

| Tool | Description |
|---|---|
| `analyze_sentiment` | Detects overall and per-sentence emotional tone (-1.0 to +1.0) |
| `extract_entities` | Identifies people, places, orgs, dates, and more with salience scores |
| `classify_content` | Categorizes text using Google's content taxonomy with confidence scores |
| `analyze_syntax` | Tokenizes text and labels parts-of-speech and dependency roles |

---

## 📋 Prerequisites

- Python 3.10+
- A [Google Cloud](https://console.cloud.google.com/) account
- The **Cloud Natural Language API** enabled in your GCP project
- A valid **Google API Key**
- [Claude Desktop](https://claude.ai/download) installed

---

## 🚀 Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/google-nl-mcp-server.git
cd google-nl-mcp-server
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key to Claude Desktop config

Your API key is configured **locally in Claude Desktop only** — not in this repo. This means it is never exposed on GitHub.

Open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following block, replacing the path and key with your own:

```json
{
  "mcpServers": {
    "google-nl": {
      "command": "python",
      "args": ["/absolute/path/to/google-nl-mcp-server/server.py"],
      "env": {
        "GOOGLE_API_KEY": "AIza..."
      }
    }
  }
}
```

> 💡 Use the **absolute path** to `server.py` on your machine (e.g. `/Users/yourname/projects/google-nl-mcp-server/server.py` on macOS).

Then **restart Claude Desktop**. The tools will appear automatically in Claude's tool picker.

---

## 🧪 Example Usage with Claude

Once connected, you can ask Claude things like:

> *"Analyze the sentiment of this customer review: 'The product arrived late and was damaged. Very disappointing.'"*

> *"Extract all the entities mentioned in this news article..."*

> *"What category does this blog post belong to?"*

> *"Break down the syntax of this sentence for me."*

Claude will automatically call the appropriate tool and reason over the structured results.

---

## 📁 Project Structure

```
google-nl-mcp-server/
├── server.py             # Main MCP server
├── requirements.txt      # Python dependencies
├── .gitignore            # Keeps secrets out of git
└── README.md             # You are here
```

---

## 🔐 Security Notes

- Your API key lives **only** in `claude_desktop_config.json` on your local machine — never in this repo
- Restrict your Google API key to the Natural Language API only via [GCP Console](https://console.cloud.google.com/apis/credentials)
- Consider adding API key IP restrictions for extra security

---

## 📚 Resources

- [Google Cloud Natural Language API Docs](https://cloud.google.com/natural-language/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude MCP Documentation](https://docs.anthropic.com/en/docs/mcp)
- [Google Cloud Free Tier](https://cloud.google.com/free)

---

## 📄 License

MIT License — feel free to fork, modify, and use this in your own projects.
