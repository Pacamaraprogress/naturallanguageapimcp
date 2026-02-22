"""
Google Cloud Natural Language API - MCP Server
Exposes sentiment analysis, entity extraction, content classification,
and syntax analysis as MCP tools for use with Claude.
"""

import os
import json
import asyncio
import requests
from typing import Any
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://language.googleapis.com/v1/documents"

if not API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY is not set. Please check your .env file.")

app = Server("google-nl-mcp-server")


# ──────────────────────────────────────────────
# Helper: call Google NL API
# ──────────────────────────────────────────────

def call_google_nl(endpoint: str, payload: dict) -> dict:
    """Send a request to the Google Natural Language API."""
    url = f"{BASE_URL}:{endpoint}?key={API_KEY}"
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def build_document(text: str) -> dict:
    """Build a standard document payload."""
    return {"type": "PLAIN_TEXT", "content": text}


# ──────────────────────────────────────────────
# Tool Definitions
# ──────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_sentiment",
            description=(
                "Analyzes the overall emotional tone (sentiment) of the provided text. "
                "Returns a score (-1.0 = very negative, +1.0 = very positive) and a "
                "magnitude (0.0+ = strength of emotion). Also returns per-sentence breakdown."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze for sentiment."
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="extract_entities",
            description=(
                "Extracts named entities from text such as people, organizations, locations, "
                "events, dates, consumer goods, and more. Returns entity names, types, "
                "salience scores, and Wikipedia metadata when available."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to extract entities from."
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="classify_content",
            description=(
                "Classifies text into one or more content categories using Google's taxonomy "
                "(e.g., /News/Politics, /Sports/Soccer, /Technology/AI). "
                "Returns categories with confidence scores. Text should be at least 20 tokens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to classify. Should be at least a few sentences."
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="analyze_syntax",
            description=(
                "Performs morphological analysis on text: tokenizes it into sentences and tokens, "
                "and tags each token with its part-of-speech (noun, verb, adjective, etc.) "
                "and dependency parse role. Useful for grammar analysis and linguistic research."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze syntactically."
                    }
                },
                "required": ["text"]
            }
        ),
    ]


# ──────────────────────────────────────────────
# Tool Handlers
# ──────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    text = arguments.get("text", "").strip()

    if not text:
        return [types.TextContent(type="text", text="Error: 'text' argument is required and cannot be empty.")]

    try:
        if name == "analyze_sentiment":
            result = call_google_nl("analyzeSentiment", {
                "document": build_document(text),
                "encodingType": "UTF8"
            })

            doc_sentiment = result.get("documentSentiment", {})
            sentences = result.get("sentences", [])

            summary = {
                "overall_sentiment": {
                    "score": doc_sentiment.get("score"),
                    "magnitude": doc_sentiment.get("magnitude"),
                    "label": _sentiment_label(doc_sentiment.get("score", 0))
                },
                "sentence_breakdown": [
                    {
                        "text": s["text"]["content"],
                        "score": s["sentiment"]["score"],
                        "magnitude": s["sentiment"]["magnitude"]
                    }
                    for s in sentences
                ]
            }
            return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]

        elif name == "extract_entities":
            result = call_google_nl("analyzeEntities", {
                "document": build_document(text),
                "encodingType": "UTF8"
            })

            entities = [
                {
                    "name": e.get("name"),
                    "type": e.get("type"),
                    "salience": round(e.get("salience", 0), 4),
                    "wikipedia_url": e.get("metadata", {}).get("wikipedia_url"),
                    "mid": e.get("metadata", {}).get("mid")
                }
                for e in result.get("entities", [])
            ]
            entities.sort(key=lambda x: x["salience"], reverse=True)
            return [types.TextContent(type="text", text=json.dumps({"entities": entities}, indent=2))]

        elif name == "classify_content":
            result = call_google_nl("classifyText", {
                "document": build_document(text)
            })

            categories = [
                {
                    "name": c.get("name"),
                    "confidence": round(c.get("confidence", 0), 4)
                }
                for c in result.get("categories", [])
            ]
            return [types.TextContent(type="text", text=json.dumps({"categories": categories}, indent=2))]

        elif name == "analyze_syntax":
            result = call_google_nl("analyzeSyntax", {
                "document": build_document(text),
                "encodingType": "UTF8"
            })

            tokens = [
                {
                    "text": t["text"]["content"],
                    "pos": t.get("partOfSpeech", {}).get("tag"),
                    "dependency_label": t.get("dependencyEdge", {}).get("label"),
                    "lemma": t.get("lemma")
                }
                for t in result.get("tokens", [])
            ]
            sentences = [s["text"]["content"] for s in result.get("sentences", [])]

            summary = {
                "sentence_count": len(sentences),
                "token_count": len(tokens),
                "sentences": sentences,
                "tokens": tokens
            }
            return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]

        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool '{name}'.")]

    except requests.exceptions.HTTPError as e:
        error_body = e.response.text if e.response else str(e)
        return [types.TextContent(type="text", text=f"Google API Error: {e}\nDetails: {error_body}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]


# ──────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────

def _sentiment_label(score: float) -> str:
    if score >= 0.25:
        return "positive"
    elif score <= -0.25:
        return "negative"
    else:
        return "neutral"


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
