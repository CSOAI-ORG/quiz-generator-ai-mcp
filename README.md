# Quiz Generator Ai

> By [MEOK AI Labs](https://meok.ai) — Quiz generation and assessment by MEOK AI Labs.

Quiz generation, validation, and flashcard creation — MEOK AI Labs.

## Installation

```bash
pip install quiz-generator-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install quiz-generator-ai-mcp
```

## Tools

### `generate_quiz`
Generate a quiz from provided content text.

**Parameters:**
- `content` (str)
- `num_questions` (int)
- `question_type` (str)

### `validate_answers`
Validate submitted answers against correct answers and return scoring.

**Parameters:**
- `questions` (str)
- `answers` (str)

### `generate_flashcards`
Generate flashcards (front/back pairs) from content for study purposes.

**Parameters:**
- `content` (str)
- `num_cards` (int)

### `assess_difficulty`
Assess the difficulty level of content for quiz/study purposes.

**Parameters:**
- `content` (str)
- `target_audience` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/quiz-generator-ai-mcp](https://github.com/CSOAI-ORG/quiz-generator-ai-mcp)
- **PyPI**: [pypi.org/project/quiz-generator-ai-mcp](https://pypi.org/project/quiz-generator-ai-mcp/)

## License

MIT — MEOK AI Labs
