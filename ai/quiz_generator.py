import os
import json
import re

from groq import Groq
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GROQ CLIENT
# =========================================================

api_key = os.getenv("GROQ_API_KEY")

client = None

if api_key:
    client = Groq(api_key=api_key)
else:
    print("WARNING: GROQ_API_KEY not found.")


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_NAME = "openai/gpt-oss-20b"

# Groq TPM limit is 8000.
# Keep input comfortably below the limit.
MAX_TEXT_CHARS = 4500

DEFAULT_QUESTIONS = 5

# Do not generate 15 questions with this model/limit.
MAX_QUESTIONS = 10

# Keep output compact.
MAX_OUTPUT_TOKENS = 1800


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # Normalize tabs and spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize newlines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


# =========================================================
# NORMALIZE CORRECT ANSWER
# =========================================================

def normalize_correct_answer(correct_answer, options):

    if not correct_answer:
        return None

    if not options:
        return None

    answer = str(correct_answer).strip()

    # -----------------------------------------------------
    # Exact option text
    # -----------------------------------------------------

    for option in options:

        option_text = str(option).strip()

        if answer.lower() == option_text.lower():

            return option_text

    # -----------------------------------------------------
    # Normalize AI answer
    # -----------------------------------------------------

    normalized = answer.upper().strip()

    normalized = re.sub(
        r"^(OPTION|ANSWER)\s+",
        "",
        normalized
    ).strip()

    # -----------------------------------------------------
    # A / B / C / D
    # -----------------------------------------------------

    letters = ["A", "B", "C", "D"]

    if normalized in letters:

        index = letters.index(normalized)

        if index < len(options):

            return str(
                options[index]
            ).strip()

    return None


# =========================================================
# VALIDATE QUESTION
# =========================================================

def validate_question(question):

    if not isinstance(question, dict):
        return None

    question_text = question.get(
        "question",
        ""
    )

    options = question.get(
        "options",
        []
    )

    correct_answer = question.get(
        "correct_answer",
        ""
    )

    explanation = question.get(
        "explanation",
        ""
    )

    difficulty = question.get(
        "difficulty",
        "Medium"
    )

    # -----------------------------------------------------
    # QUESTION
    # -----------------------------------------------------

    question_text = str(
        question_text
    ).strip()

    if not question_text:
        return None

    if len(question_text) < 10:
        return None

    # -----------------------------------------------------
    # OPTIONS
    # -----------------------------------------------------

    if not isinstance(options, list):
        return None

    if len(options) != 4:
        return None

    cleaned_options = []

    for option in options:

        option = str(option).strip()

        if not option:
            return None

        cleaned_options.append(option)

    # -----------------------------------------------------
    # DUPLICATE OPTIONS
    # -----------------------------------------------------

    normalized_options = [
        option.lower()
        for option in cleaned_options
    ]

    if len(set(normalized_options)) != 4:
        return None

    # -----------------------------------------------------
    # CORRECT ANSWER
    # -----------------------------------------------------

    normalized_answer = normalize_correct_answer(
        correct_answer,
        cleaned_options
    )

    if not normalized_answer:
        return None

    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    difficulty = str(
        difficulty
    ).strip().capitalize()

    if difficulty not in [
        "Easy",
        "Medium",
        "Difficult"
    ]:

        difficulty = "Medium"

    # -----------------------------------------------------
    # EXPLANATION
    # -----------------------------------------------------

    explanation = str(
        explanation
    ).strip()

    # Keep output small
    if len(explanation) > 180:

        explanation = (
            explanation[:180]
            .rsplit(" ", 1)[0]
            + "..."
        )

    # -----------------------------------------------------
    # FINAL QUESTION
    # -----------------------------------------------------

    return {

        "question":
            question_text,

        "options":
            cleaned_options,

        "correct_answer":
            normalized_answer,

        "explanation":
            explanation,

        "difficulty":
            difficulty
    }


# =========================================================
# REMOVE DUPLICATE QUESTIONS
# =========================================================

def remove_duplicate_questions(questions):

    unique_questions = []

    seen = set()

    for question in questions:

        key = re.sub(
            r"\s+",
            " ",
            question["question"].lower()
        ).strip()

        if key in seen:
            continue

        seen.add(key)

        unique_questions.append(
            question
        )

    return unique_questions


# =========================================================
# GENERATE QUIZ
# =========================================================

def generate_quiz(
    text,
    topic="",
    number_of_questions=DEFAULT_QUESTIONS
):

    # =====================================================
    # API CHECK
    # =====================================================

    if not client:

        return {
            "topic": topic,
            "questions": [],
            "error": "GROQ_API_KEY is missing."
        }

    # =====================================================
    # TEXT CHECK
    # =====================================================

    if not text or not str(text).strip():

        return {
            "topic": topic,
            "questions": [],
            "error": "Learning material is empty."
        }

    # =====================================================
    # QUESTION COUNT
    # =====================================================

    try:

        number_of_questions = int(
            number_of_questions
        )

    except (
        ValueError,
        TypeError
    ):

        number_of_questions = DEFAULT_QUESTIONS

    # Only 5 or 10
    if number_of_questions <= 5:

        number_of_questions = 5

    else:

        number_of_questions = 10

    # =====================================================
    # CLEAN TEXT
    # =====================================================

    text = clean_text(text)

    # =====================================================
    # LIMIT TEXT
    # =====================================================

    original_length = len(text)

    if len(text) > MAX_TEXT_CHARS:

        print(
            f"PDF text: {original_length} characters"
        )

        print(
            f"Using first {MAX_TEXT_CHARS} characters."
        )

        text = text[:MAX_TEXT_CHARS]

    # =====================================================
    # TOPIC
    # =====================================================

    topic = str(
        topic or ""
    ).strip()

    if topic:

        topic_instruction = (
            f"Focus on topic: {topic}. "
            "Use only information present in the material."
        )

    else:

        topic_instruction = (
            "Cover the important concepts present "
            "in the material."
        )

    # =====================================================
    # COMPACT PROMPT
    # =====================================================

    prompt = f"""
Create a competency-focused MCQ quiz.

{topic_instruction}

Generate EXACTLY {number_of_questions} questions.

STRICT RULES:

1. Use ONLY the supplied learning material.
2. Do not use outside knowledge.
3. Every question must have exactly 4 options.
4. Exactly 1 option must be correct.
5. Options must be distinct.
6. Avoid duplicate or ambiguous questions.
7. Include a short explanation.
8. Difficulty must be Easy, Medium, or Difficult.
9. correct_answer MUST exactly match one option.
10. Do not return A, B, C or D as correct_answer.
11. Keep questions and explanations concise.

RETURN ONLY JSON.

FORMAT:

{{
  "topic": "{topic}",
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4"
      ],
      "correct_answer": "Option 1",
      "explanation": "Short explanation.",
      "difficulty": "Easy"
    }}
  ]
}}

LEARNING MATERIAL:

{text}
"""

    # =====================================================
    # DEBUG
    # =====================================================

    print()
    print("=" * 65)
    print("STARTING QUIZ GENERATION")
    print("=" * 65)

    print(
        "Model:",
        MODEL_NAME
    )

    print(
        "Topic:",
        topic or "General"
    )

    print(
        "Questions:",
        number_of_questions
    )

    print(
        "Input characters:",
        len(text)
    )

    # =====================================================
    # GROQ REQUEST
    # =====================================================

    try:

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You generate concise educational MCQs. "
                        "Use only the supplied material. "
                        "Return JSON only."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,

            max_tokens=MAX_OUTPUT_TOKENS,

            response_format={
                "type": "json_object"
            }
        )

        # =================================================
        # RESPONSE CHECK
        # =================================================

        if not response:

            raise Exception(
                "Empty response from Groq."
            )

        if not response.choices:

            raise Exception(
                "Groq returned no choices."
            )

        result = (
            response
            .choices[0]
            .message
            .content
        )

        if not result:

            raise Exception(
                "Groq returned empty content."
            )

        print(
            "AI response received."
        )

        # =================================================
        # JSON PARSE
        # =================================================

        try:

            quiz_data = json.loads(
                result
            )

        except json.JSONDecodeError as e:

            print(
                "JSON ERROR:",
                str(e)
            )

            print(
                "RAW RESPONSE:",
                result
            )

            return {

                "topic": topic,

                "questions": [],

                "error":
                    "AI returned invalid JSON."
            }

        # =================================================
        # QUESTIONS
        # =================================================

        raw_questions = quiz_data.get(
            "questions",
            []
        )

        if not isinstance(
            raw_questions,
            list
        ):

            return {

                "topic": topic,

                "questions": [],

                "error":
                    "Invalid question format."
            }

        # =================================================
        # VALIDATE
        # =================================================

        valid_questions = []

        for question in raw_questions:

            validated = validate_question(
                question
            )

            if validated:

                valid_questions.append(
                    validated
                )

        # =================================================
        # REMOVE DUPLICATES
        # =================================================

        valid_questions = (
            remove_duplicate_questions(
                valid_questions
            )
        )

        # =================================================
        # LIMIT
        # =================================================

        valid_questions = (
            valid_questions[
                :number_of_questions
            ]
        )

        # =================================================
        # NO QUESTIONS
        # =================================================

        if not valid_questions:

            print(
                "No valid questions generated."
            )

            return {

                "topic": topic,

                "questions": [],

                "error":
                    "AI did not generate valid questions."
            }

        # =================================================
        # WARNING
        # =================================================

        if len(valid_questions) < number_of_questions:

            print(
                f"WARNING: Requested "
                f"{number_of_questions}, "
                f"but received "
                f"{len(valid_questions)} valid questions."
            )

        # =================================================
        # FINAL QUIZ
        # =================================================

        final_quiz = {

            "topic":
                quiz_data.get(
                    "topic",
                    topic
                ),

            "questions":
                valid_questions
        }

        # =================================================
        # DEBUG
        # =================================================

        print(
            "Valid questions:",
            len(valid_questions)
        )

        for index, question in enumerate(
            valid_questions,
            start=1
        ):

            print(
                f"{index}.",
                question["question"]
            )

            print(
                "Correct:",
                question["correct_answer"]
            )

        print("=" * 65)
        print("QUIZ GENERATION SUCCESS")
        print("=" * 65)
        print()

        return final_quiz

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print()
        print("=" * 65)
        print("QUIZ GENERATION ERROR")
        print("=" * 65)

        print(
            "Error Type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print("=" * 65)
        print()

        return {

            "topic":
                topic,

            "questions":
                [],

            "error":
                str(e)
        }