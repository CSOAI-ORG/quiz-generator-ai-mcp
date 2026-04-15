#!/usr/bin/env python3
"""Quiz generation, validation, and flashcard creation — MEOK AI Labs."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
import hashlib
import re
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)


def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now)
    return None


def _extract_terms(text: str) -> list:
    """Extract key terms from text for question generation."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "have",
        "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "and", "but", "or", "not", "so", "yet", "if", "when", "where", "how",
        "what", "which", "who", "this", "that", "it", "its", "they", "them",
        "we", "our", "you", "your", "i", "me", "my", "he", "she", "him", "her",
    }
    words = re.findall(r'\b[A-Za-z][a-z]{2,}\b', text)
    seen = set()
    terms = []
    for w in words:
        wl = w.lower()
        if wl not in stop_words and wl not in seen:
            seen.add(wl)
            terms.append(w)
    return terms


def _generate_distractors(correct: str, all_terms: list, count: int = 3) -> list:
    """Generate plausible wrong answers from the term pool."""
    distractors = [t for t in all_terms if t.lower() != correct.lower()]
    result = []
    for i in range(min(count, len(distractors))):
        result.append(distractors[i % len(distractors)])
    while len(result) < count:
        result.append(f"Option {len(result) + 1}")
    return result[:count]


_QUESTION_TEMPLATES = [
    "What is the definition of {term}?",
    "Which of the following best describes {term}?",
    "In the context provided, what role does {term} play?",
    "{term} is most closely associated with which concept?",
    "Which statement about {term} is correct?",
]


mcp = FastMCP("quiz-generator-ai", instructions="Quiz generation and assessment by MEOK AI Labs.")


@mcp.tool()
def generate_quiz(content: str, num_questions: int = 5, question_type: str = "multiple_choice", api_key: str = "") -> dict:
    """Generate a quiz from provided content text."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    terms = _extract_terms(content)
    if len(terms) < 2:
        return {"error": "Not enough content to generate quiz. Provide more text."}

    num_questions = min(num_questions, 20, len(terms))
    questions = []

    for i in range(num_questions):
        term = terms[i % len(terms)]
        template = _QUESTION_TEMPLATES[i % len(_QUESTION_TEMPLATES)]
        question_text = template.format(term=term)
        qid = hashlib.md5(f"{term}_{i}".encode()).hexdigest()[:8]

        if question_type == "multiple_choice":
            distractors = _generate_distractors(term, terms, 3)
            options = [term] + distractors
            # Deterministic shuffle based on hash
            seed = int(hashlib.md5(qid.encode()).hexdigest()[:8], 16)
            indices = list(range(len(options)))
            for j in range(len(indices) - 1, 0, -1):
                k = (seed + j) % (j + 1)
                indices[j], indices[k] = indices[k], indices[j]
            shuffled = [options[idx] for idx in indices]
            correct_idx = shuffled.index(term)

            questions.append({
                "id": f"Q-{qid}",
                "question": question_text,
                "type": "multiple_choice",
                "options": {chr(65 + j): opt for j, opt in enumerate(shuffled)},
                "correct_answer": chr(65 + correct_idx),
                "points": 1,
            })
        elif question_type == "true_false":
            questions.append({
                "id": f"Q-{qid}",
                "question": f"{term} is a key concept in the provided content.",
                "type": "true_false",
                "correct_answer": True,
                "points": 1,
            })
        else:
            questions.append({
                "id": f"Q-{qid}",
                "question": f"Explain the significance of {term} in your own words.",
                "type": "open_ended",
                "key_terms": [term],
                "points": 2,
            })

    return {
        "quiz_id": hashlib.md5(content[:100].encode()).hexdigest()[:12],
        "questions": questions,
        "total_questions": len(questions),
        "total_points": sum(q["points"] for q in questions),
        "question_type": question_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def validate_answers(questions: list, answers: dict, api_key: str = "") -> dict:
    """Validate submitted answers against correct answers and return scoring."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    if not questions:
        return {"error": "No questions provided."}

    results = []
    total_points = 0
    earned_points = 0

    for q in questions:
        qid = q.get("id", "unknown")
        correct = q.get("correct_answer")
        points = q.get("points", 1)
        total_points += points

        submitted = answers.get(qid)
        if submitted is None:
            results.append({"id": qid, "status": "unanswered", "points_earned": 0, "points_possible": points})
            continue

        is_correct = False
        if q.get("type") == "open_ended":
            key_terms = q.get("key_terms", [])
            submitted_lower = str(submitted).lower()
            matched = sum(1 for t in key_terms if t.lower() in submitted_lower)
            is_correct = matched >= len(key_terms) * 0.5
            earned = round(points * matched / max(len(key_terms), 1), 1)
        else:
            is_correct = str(submitted).strip() == str(correct).strip()
            earned = points if is_correct else 0

        earned_points += earned
        results.append({
            "id": qid,
            "status": "correct" if is_correct else "incorrect",
            "submitted": submitted,
            "correct_answer": correct,
            "points_earned": earned,
            "points_possible": points,
        })

    percentage = round(earned_points / max(total_points, 1) * 100, 1)
    grade = "A" if percentage >= 90 else "B" if percentage >= 80 else "C" if percentage >= 70 else "D" if percentage >= 60 else "F"

    return {
        "score": earned_points,
        "total_points": total_points,
        "percentage": percentage,
        "grade": grade,
        "results": results,
        "answered": sum(1 for r in results if r["status"] != "unanswered"),
        "correct": sum(1 for r in results if r["status"] == "correct"),
        "incorrect": sum(1 for r in results if r["status"] == "incorrect"),
        "unanswered": sum(1 for r in results if r["status"] == "unanswered"),
    }


@mcp.tool()
def generate_flashcards(content: str, num_cards: int = 10, api_key: str = "") -> dict:
    """Generate flashcards (front/back pairs) from content for study purposes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content.strip()) if s.strip()]
    terms = _extract_terms(content)

    if not terms or not sentences:
        return {"error": "Not enough content to generate flashcards."}

    num_cards = min(num_cards, 30, max(len(terms), len(sentences)))
    cards = []

    for i in range(num_cards):
        term = terms[i % len(terms)]
        relevant_sents = [s for s in sentences if term.lower() in s.lower()]
        context = relevant_sents[0] if relevant_sents else sentences[i % len(sentences)]

        card_id = hashlib.md5(f"fc_{term}_{i}".encode()).hexdigest()[:8]
        cards.append({
            "id": f"FC-{card_id}",
            "front": f"What is {term}?",
            "back": context,
            "tags": [term.lower()],
            "difficulty": "medium",
        })

    return {
        "flashcards": cards,
        "total": len(cards),
        "source_length": len(content),
        "unique_terms": len(terms),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def assess_difficulty(content: str, target_audience: str = "general", api_key: str = "") -> dict:
    """Assess the difficulty level of content for quiz/study purposes."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(api_key or "anon"):
        return err

    words = content.split()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content.strip()) if s.strip()]
    word_count = len(words)
    sent_count = max(len(sentences), 1)

    avg_word_len = sum(len(w.strip(".,!?;:")) for w in words) / max(word_count, 1)
    avg_sent_len = word_count / sent_count

    long_words = sum(1 for w in words if len(w.strip(".,!?;:")) > 8)
    long_word_pct = round(long_words / max(word_count, 1) * 100, 1)

    # Simplified readability approximation (Flesch-like)
    syllable_est = sum(max(1, len(re.findall(r'[aeiouy]+', w.lower()))) for w in words)
    avg_syllables = syllable_est / max(word_count, 1)
    readability = round(206.835 - 1.015 * avg_sent_len - 84.6 * avg_syllables, 1)

    if readability >= 80:
        level = "easy"
    elif readability >= 60:
        level = "medium"
    elif readability >= 40:
        level = "hard"
    else:
        level = "expert"

    audience_adjust = {"beginner": 1, "general": 0, "advanced": -1, "expert": -2}
    adj = audience_adjust.get(target_audience.lower(), 0)
    levels = ["easy", "medium", "hard", "expert"]
    adjusted_idx = max(0, min(3, levels.index(level) - adj))

    terms = _extract_terms(content)
    technical_terms = [t for t in terms if len(t) > 7]

    return {
        "difficulty_level": level,
        "adjusted_for_audience": levels[adjusted_idx],
        "target_audience": target_audience,
        "readability_score": readability,
        "metrics": {
            "word_count": word_count,
            "sentence_count": sent_count,
            "avg_word_length": round(avg_word_len, 1),
            "avg_sentence_length": round(avg_sent_len, 1),
            "long_word_percentage": long_word_pct,
            "avg_syllables_per_word": round(avg_syllables, 1),
        },
        "technical_terms": technical_terms[:15],
        "recommended_question_types": {
            "easy": ["true_false", "multiple_choice"],
            "medium": ["multiple_choice"],
            "hard": ["multiple_choice", "open_ended"],
            "expert": ["open_ended"],
        }.get(levels[adjusted_idx], ["multiple_choice"]),
    }


if __name__ == "__main__":
    mcp.run()
