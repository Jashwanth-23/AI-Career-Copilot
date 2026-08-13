"""
AI Mock Interview Engine Module

Provides AI personalized question generation, real-time answer evaluation,
adaptive difficulty calibration, and comprehensive final performance report generation
powered by Google Gemini GenAI SDK (`google.genai`).
"""

import json
import logging
from typing import Any, Dict, List, Optional

from google.genai import types

from app.core.gemini_client import (
    GeminiAuthError,
    GeminiQuotaExhaustedError,
    GeminiServiceError,
    get_gemini_client,
    get_gemini_model,
    handle_gemini_api_error,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class MockInterviewEngineError(Exception):
    """Base exception class for Mock Interview Engine errors."""

    pass


class InterviewQuestionGenerationError(MockInterviewEngineError):
    """Raised when Gemini fails to generate a valid interview question."""

    pass


class InterviewEvaluationError(MockInterviewEngineError):
    """Raised when Gemini fails to evaluate candidate's answer."""

    pass


# ============================================================================
# Helpers
# ============================================================================


def _clean_json_text(raw_text: str) -> str:
    """Extract raw JSON substring from markdown backticks or text wrapping."""
    if not raw_text:
        return "{}"
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ============================================================================
# Core Gemini AI Engine Functions
# ============================================================================


def generate_interview_question(
    target_role: str,
    interview_type: str,
    difficulty: str,
    question_number: int,
    total_questions: int,
    structured_resume: Dict[str, Any],
    previous_questions: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Generate ONE personalized interview question using structured JSON output.

    Args:
        target_role: Target job position (e.g., Backend Developer).
        interview_type: Category (technical, behavioral, hr, system_design, mixed, resume_based).
        difficulty: Level (easy, medium, hard).
        question_number: 1-based index of current question.
        total_questions: Total questions in session.
        structured_resume: Candidate's structured resume JSON (skills, experience, projects, education).
        previous_questions: History of past questions & candidate answers in this session.

    Returns:
        Structured dictionary matching question format:
        {
            "question": "...",
            "question_type": "...",
            "difficulty": "...",
            "topic": "...",
            "focus_area": "...",
            "resume_reference": "..."
        }
    """
    logger.info(
        "Generating Question %d/%d for target_role='%s', type='%s', difficulty='%s'",
        question_number,
        total_questions,
        target_role,
        interview_type,
        difficulty,
    )

    model_name = get_gemini_model()
    try:
        client = get_gemini_client()
    except Exception as exc:
        handle_gemini_api_error(exc, "get_gemini_client in question generation")

    # Compact context extraction from structured resume
    skills = structured_resume.get("skills", [])
    projects = [
        f"{p.get('name', '')}: {p.get('description', '')}"
        for p in structured_resume.get("projects", [])
        if isinstance(p, dict) and p.get("name")
    ][:3]
    experiences = [
        f"{e.get('position', '')} at {e.get('company', '')}"
        for e in structured_resume.get("experience", [])
        if isinstance(e, dict) and e.get("company")
    ][:3]

    history_summary = []
    if previous_questions:
        for item in previous_questions:
            q_num = item.get("question_number", 0)
            q_text = item.get("question_text", "")
            ans = item.get("user_answer", "No answer submitted.")
            score = item.get("score", "N/A")
            history_summary.append(
                f"Q{q_num}: '{q_text}' -> Answer Score: {score}/100"
            )

    history_str = "\n".join(history_summary) if history_summary else "None (This is Question 1)."

    prompt = f"""You are a top-tier Senior Technical Interviewer conducting a personalized mock interview.

INTERVIEW CONFIGURATION:
- Target Job Role: {target_role}
- Interview Type: {interview_type}
- Difficulty Level: {difficulty}
- Question Progress: Question {question_number} of {total_questions}

CANDIDATE RESUME SUMMARY:
- Top Skills: {', '.join(skills[:15]) if skills else 'Not specified'}
- Key Projects: {'; '.join(projects) if projects else 'Not specified'}
- Key Experience: {'; '.join(experiences) if experiences else 'Not specified'}

SESSION HISTORY & PREVIOUS PERFORMANCE:
{history_str}

REQUIREMENTS FOR THIS QUESTION:
1. Generate EXACTLY ONE relevant, professional, concise, role-specific question.
2. If type is 'resume_based' or 'technical', reference actual projects or skills from candidate's resume summary above.
3. NEVER invent facts about candidate experience that are not in the resume summary.
4. Adapt difficulty: 'easy' focuses on fundamental concepts; 'medium' on practical implementation and scenarios; 'hard' on architecture tradeoffs, edge cases, and deep technical reasoning.
5. Ensure the question is distinct and non-repetitive from previous session history.

RETURN ONLY VALID JSON WITH EXACTLY THIS SCHEMA:
{{
  "question": "Clear and detailed question text string",
  "question_type": "{interview_type}",
  "difficulty": "{difficulty}",
  "topic": "Primary topic/skill being tested",
  "focus_area": "Sub-concept or focus area",
  "resume_reference": "Specific resume project or skill referenced, or null"
}}
"""

    generation_config = types.GenerateContentConfig(
        temperature=0.3,
        response_mime_type="application/json",
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generation_config,
        )
        if not response or not response.text:
            raise InterviewQuestionGenerationError("Gemini returned empty text response.")

        cleaned_json = _clean_json_text(response.text)
        data = json.loads(cleaned_json)

        return {
            "question": data.get("question", f"Describe your approach to building robust backend systems for a {target_role}."),
            "question_type": data.get("question_type", interview_type),
            "difficulty": data.get("difficulty", difficulty),
            "topic": data.get("topic", "General Software Engineering"),
            "focus_area": data.get("focus_area", "Problem Solving"),
            "resume_reference": data.get("resume_reference"),
        }
    except GeminiQuotaExhaustedError:
        raise
    except Exception as exc:
        logger.error("Error generating question with Gemini: %s", exc, exc_info=True)
        handle_gemini_api_error(exc, "generate_interview_question")
        # Fallback question if handle_gemini_api_error doesn't raise
        return {
            "question": f"Can you explain a challenging technical problem you solved while working as a {target_role}?",
            "question_type": interview_type,
            "difficulty": difficulty,
            "topic": "Software Engineering",
            "focus_area": "Problem Solving",
            "resume_reference": None,
        }


def evaluate_interview_answer(
    question_text: str,
    user_answer: str,
    target_role: str,
    interview_type: str,
    difficulty: str,
    topic: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate candidate's answer for a single interview question.

    Args:
        question_text: The interview question presented.
        user_answer: The candidate's text response.
        target_role: Target job position.
        interview_type: Category of interview.
        difficulty: Level of question.
        topic: Specific topic being evaluated.

    Returns:
        Structured evaluation payload:
        {
            "overall_score": 82,
            "technical_accuracy": 80,
            "relevance": 90,
            "completeness": 75,
            "clarity": 85,
            "communication": 85,
            "problem_solving": 80,
            "strengths": [...],
            "weaknesses": [...],
            "missing_points": [...],
            "improvement": "...",
            "ideal_answer": "...",
            "follow_up_needed": false
        }
    """
    logger.info("Evaluating answer for question topic='%s', role='%s'", topic, target_role)

    model_name = get_gemini_model()
    try:
        client = get_gemini_client()
    except Exception as exc:
        handle_gemini_api_error(exc, "get_gemini_client in answer evaluation")

    prompt = f"""You are an expert AI Technical Interviewer evaluating a candidate's answer.

QUESTION INFORMATION:
- Target Role: {target_role}
- Interview Type: {interview_type}
- Difficulty: {difficulty}
- Topic: {topic or 'General'}
- Question Text: "{question_text}"

CANDIDATE SUBMITTED ANSWER:
"{user_answer}"

EVALUATION INSTRUCTIONS:
1. Score strictly and fairly on a 0 to 100 scale across key dimensions.
2. Provide concise, professional, non-harsh feedback.
3. Identify top strengths demonstrated in the answer.
4. Highlight missing concepts or key technical points candidate should have mentioned.
5. Provide actionable improvement advice and a clear ideal answer summary.
6. Do NOT expose internal chain-of-thought; return strictly structured JSON.

RETURN ONLY VALID JSON WITH EXACTLY THIS SCHEMA:
{{
  "overall_score": 85,
  "technical_accuracy": 85,
  "relevance": 90,
  "completeness": 80,
  "clarity": 85,
  "communication": 85,
  "problem_solving": 80,
  "strengths": ["List item 1", "List item 2"],
  "weaknesses": ["List item 1"],
  "missing_points": ["List item 1"],
  "improvement": "Concise advice on how to improve this answer.",
  "ideal_answer": "Brief summary of what a complete ideal response would cover.",
  "follow_up_needed": false
}}
"""

    generation_config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generation_config,
        )
        if not response or not response.text:
            raise InterviewEvaluationError("Gemini returned empty evaluation response.")

        cleaned_json = _clean_json_text(response.text)
        data = json.loads(cleaned_json)

        overall = int(data.get("overall_score", 75))
        overall = min(100, max(0, overall))

        return {
            "overall_score": overall,
            "technical_accuracy": int(data.get("technical_accuracy", overall)),
            "relevance": int(data.get("relevance", overall)),
            "completeness": int(data.get("completeness", overall)),
            "clarity": int(data.get("clarity", overall)),
            "communication": int(data.get("communication", overall)),
            "problem_solving": int(data.get("problem_solving", overall)),
            "strengths": data.get("strengths", ["Answer addressed the main question."]),
            "weaknesses": data.get("weaknesses", []),
            "missing_points": data.get("missing_points", []),
            "improvement": data.get("improvement", "Elaborate further with specific practical examples."),
            "ideal_answer": data.get("ideal_answer", "A comprehensive answer details relevant architecture, edge cases, and practical trade-offs."),
            "follow_up_needed": bool(data.get("follow_up_needed", False)),
        }
    except GeminiQuotaExhaustedError:
        raise
    except Exception as exc:
        logger.error("Error evaluating answer with Gemini: %s", exc, exc_info=True)
        handle_gemini_api_error(exc, "evaluate_interview_answer")
        return {
            "overall_score": 75,
            "technical_accuracy": 75,
            "relevance": 80,
            "completeness": 70,
            "clarity": 75,
            "communication": 75,
            "problem_solving": 75,
            "strengths": ["Answer successfully submitted."],
            "weaknesses": ["Feedback system degraded."],
            "missing_points": [],
            "improvement": "Please elaborate further on practical examples.",
            "ideal_answer": "Cover key architectural and technical principles clearly.",
            "follow_up_needed": False,
        }


def generate_final_interview_report(
    target_role: str,
    interview_type: str,
    difficulty: str,
    questions_evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate comprehensive final performance report after interview completion.

    Args:
        target_role: Target job role.
        interview_type: Type of interview session.
        difficulty: Difficulty level.
        questions_evaluations: Full record of questions, user answers, scores, and evaluations.

    Returns:
        Structured report payload:
        {
            "overall_score": 82,
            "technical_score": 84,
            "problem_solving_score": 80,
            "communication_score": 79,
            "role_readiness_score": 85,
            "performance_rating": "Strong",
            "strengths": [...],
            "weaknesses": [...],
            "recommended_topics": [...],
            "final_feedback": "...",
            "action_plan": [...]
        }
    """
    logger.info("Generating final report for role='%s', questions_count=%d", target_role, len(questions_evaluations))

    # Fallback score calculations if Gemini fails
    scores = [q.get("score", 70) for q in questions_evaluations if q.get("score") is not None]
    avg_score = int(sum(scores) / len(scores)) if scores else 75

    eval_summary = []
    for q in questions_evaluations:
        eval_summary.append(
            f"Q{q.get('question_number')}: '{q.get('question_text')}'\n"
            f"Candidate Answer: '{q.get('user_answer')}'\n"
            f"Score: {q.get('score')}/100 | Topic: {q.get('topic')}\n"
        )
    eval_text = "\n".join(eval_summary)

    model_name = get_gemini_model()
    try:
        client = get_gemini_client()
    except Exception as exc:
        handle_gemini_api_error(exc, "get_gemini_client in final report")

    prompt = f"""You are a Lead Hiring Manager synthesizing a final candidate interview evaluation report.

INTERVIEW OVERVIEW:
- Target Position: {target_role}
- Session Category: {interview_type}
- Difficulty Level: {difficulty}

QUESTION-BY-QUESTION EVALUATION RECORDS:
{eval_text}

REPORT REQUIREMENTS:
1. Synthesize overall performance across technical depth, problem solving, communication, and overall role readiness.
2. Determine qualitative performance rating from: 'Excellent' (90-100), 'Strong' (80-89), 'Satisfactory' (70-79), 'Needs Improvement' (<70).
3. Identify top 3 key candidate strengths and top 3 growth areas.
4. List recommended technical topics to study before real interviews.
5. Create a step-by-step 3-item action plan.

RETURN ONLY VALID JSON WITH EXACTLY THIS SCHEMA:
{{
  "overall_score": {avg_score},
  "technical_score": 85,
  "problem_solving_score": 80,
  "communication_score": 80,
  "role_readiness_score": 82,
  "performance_rating": "Strong",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "recommended_topics": ["Topic 1", "Topic 2", "Topic 3"],
  "final_feedback": "Comprehensive summary of performance and candidate potential.",
  "action_plan": ["Action step 1", "Action step 2", "Action step 3"]
}}
"""

    generation_config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generation_config,
        )
        if not response or not response.text:
            raise MockInterviewEngineError("Gemini returned empty report text.")

        cleaned_json = _clean_json_text(response.text)
        data = json.loads(cleaned_json)

        ov_score = int(data.get("overall_score", avg_score))
        rating = data.get("performance_rating")
        if not rating:
            if ov_score >= 90:
                rating = "Excellent"
            elif ov_score >= 80:
                rating = "Strong"
            elif ov_score >= 70:
                rating = "Satisfactory"
            else:
                rating = "Needs Improvement"

        return {
            "overall_score": ov_score,
            "technical_score": int(data.get("technical_score", ov_score)),
            "problem_solving_score": int(data.get("problem_solving_score", ov_score)),
            "communication_score": int(data.get("communication_score", ov_score)),
            "role_readiness_score": int(data.get("role_readiness_score", ov_score)),
            "performance_rating": rating,
            "strengths": data.get("strengths", ["Solid foundational knowledge."]),
            "weaknesses": data.get("weaknesses", ["Review advanced implementation details."]),
            "recommended_topics": data.get("recommended_topics", [f"{target_role} core principles"]),
            "final_feedback": data.get("final_feedback", f"Candidate demonstrated good readiness for {target_role}."),
            "action_plan": data.get("action_plan", ["Practice mock interview questions under time constraints."]),
        }
    except GeminiQuotaExhaustedError:
        raise
    except Exception as exc:
        logger.error("Error generating final report with Gemini: %s", exc, exc_info=True)
        handle_gemini_api_error(exc, "generate_final_interview_report")

        if avg_score >= 90:
            rating = "Excellent"
        elif avg_score >= 80:
            rating = "Strong"
        elif avg_score >= 70:
            rating = "Satisfactory"
        else:
            rating = "Needs Improvement"

        return {
            "overall_score": avg_score,
            "technical_score": avg_score,
            "problem_solving_score": avg_score,
            "communication_score": avg_score,
            "role_readiness_score": avg_score,
            "performance_rating": rating,
            "strengths": ["Completed mock interview session."],
            "weaknesses": ["Review missing technical points from questions."],
            "recommended_topics": [f"{target_role} concepts"],
            "final_feedback": f"Session completed with average score of {avg_score}%.",
            "action_plan": ["Review question feedback and practice again."],
        }
