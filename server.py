#!/usr/bin/env python3
"""Generate quizzes from text content. — MEOK AI Labs."""
import json, os, re, hashlib, uuid as _uuid, random
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit/day"})
    _usage[c].append(now); return None

mcp = FastMCP("quiz-generator", instructions="MEOK AI Labs — Generate quizzes from text content.")


@mcp.tool()
def generate_quiz(text: str, num_questions: int = 5) -> str:
    """Generate quiz questions from text content."""
    if err := _rl(): return err
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
    questions = []
    for s in sentences[:num_questions]:
        words = s.split()
        if len(words) > 5:
            blank_idx = random.randint(2, len(words)-2)
            answer = words[blank_idx]
            words[blank_idx] = "____"
            questions.append({"question": " ".join(words), "answer": answer, "type": "fill_blank"})
    return json.dumps({"questions": questions, "total": len(questions)}, indent=2)

if __name__ == "__main__":
    mcp.run()
