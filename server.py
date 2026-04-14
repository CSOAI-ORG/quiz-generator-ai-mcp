#!/usr/bin/env python3
import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("quiz-generator-ai-mcp")
@mcp.tool(name="generate_quiz")
async def generate_quiz(topic: str, num_questions: int = 3) -> str:
    questions = [{"question": f"Q{i+1} about {topic}?", "options": ["A", "B", "C", "D"], "answer": "A"} for i in range(num_questions)]
    return json.dumps({"topic": topic, "questions": questions})
@mcp.tool(name="score_quiz")
async def score_quiz(answers: list, correct_answers: list) -> str:
    score = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    return json.dumps({"score": score, "total": len(correct_answers), "percentage": round(score / len(correct_answers) * 100, 1)})
if __name__ == "__main__":
    mcp.run()
