#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("quiz-generator-ai-mcp")
@mcp.tool(name="generate_quiz")
async def generate_quiz(topic: str, num_questions: int = 3, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    questions = [{"question": f"Q{i+1} about {topic}?", "options": ["A", "B", "C", "D"], "answer": "A"} for i in range(num_questions)]
    return {"topic": topic, "questions": questions}
@mcp.tool(name="score_quiz")
async def score_quiz(answers: list, correct_answers: list, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    score = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    return {"score": score, "total": len(correct_answers), "percentage": round(score / len(correct_answers) * 100, 1)}
if __name__ == "__main__":
    mcp.run()
