import os
import json

from groq import Groq
from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# GROQ CLIENT
# ==========================================

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing from .env file"
    )

client = Groq(
    api_key=api_key
)


# ==========================================
# AI QUIZ GENERATOR
# ==========================================

def generate_quiz(
    text,
    topic="",
    number_of_questions=10
):

    # --------------------------------------
    # Limit extremely large PDF text
    # --------------------------------------

    MAX_CHARS = 10000

    if len(text) > MAX_CHARS:

        print(
            f"PDF text too large: {len(text)} characters"
        )

        text = text[:MAX_CHARS]

        print(
            f"Using first {MAX_CHARS} characters"
        )


    # --------------------------------------
    # Create AI prompt
    # --------------------------------------

    prompt = f"""
You are an AI quiz generator for an
AI-enabled learning platform for
India's Official Statistical System.

Generate a high-quality multiple-choice quiz
from the learning material provided below.

Topic:
{topic}

Learning Material:
{text}

Requirements:

1. Generate exactly {number_of_questions} questions.

2. Each question must have exactly 4 options.

3. Only ONE option must be correct.

4. Questions must be based ONLY on the
   supplied learning material.

5. Do NOT invent facts.

6. Include a mixture of:
   - Easy
   - Medium
   - Difficult

7. Questions should test understanding,
   not only memorization.

8. Include a short explanation for
   every correct answer.

9. Make incorrect options plausible.

10. Return ONLY valid JSON.

Use exactly this structure:

{{
    "topic": "{topic}",

    "questions": [

        {{
            "question": "Question text",

            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],

            "correct_answer": "Option A",

            "explanation": "Short explanation",

            "difficulty": "Easy"
        }}

    ]
}}
"""


    # ======================================
    # CALL GROQ
    # ======================================

    try:

        print("\n==============================")
        print("STARTING QUIZ GENERATION")
        print("==============================")

        print(
            "Topic:",
            topic
        )

        print(
            "Questions:",
            number_of_questions
        )

        print(
            "Text length:",
            len(text)
        )


        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",

                    "content":
                    """
You are a reliable educational
quiz generation AI.

Always return valid JSON.
Never return markdown.
Never add explanations outside JSON.
"""
                },

                {
                    "role": "user",

                    "content": prompt
                }

            ],

            temperature=0.2,

            response_format={
                "type": "json_object"
            }

        )


        # ==================================
        # GET AI RESPONSE
        # ==================================

        result = response.choices[0].message.content


        print("\nAI RESPONSE RECEIVED")


        # ==================================
        # CONVERT JSON
        # ==================================

        quiz_data = json.loads(result)


        # ==================================
        # VALIDATE RESPONSE
        # ==================================

        questions = quiz_data.get(
            "questions",
            []
        )


        if not questions:

            print(
                "AI returned zero questions."
            )

            return {
                "topic": topic,
                "questions": [],
                "error":
                "AI did not generate any questions."
            }


        # ==================================
        # CHECK QUESTION STRUCTURE
        # ==================================

        valid_questions = []


        for question in questions:

            if not isinstance(
                question,
                dict
            ):
                continue


            question_text = question.get(
                "question"
            )

            options = question.get(
                "options"
            )

            correct_answer = question.get(
                "correct_answer"
            )


            if not question_text:
                continue


            if not options:
                continue


            if len(options) != 4:
                continue


            if not correct_answer:
                continue


            valid_questions.append(
                question
            )


        # ==================================
        # FINAL RESULT
        # ==================================

        quiz_data["questions"] = (
            valid_questions[
                :number_of_questions
            ]
        )


        print(
            "Valid questions:",
            len(quiz_data["questions"])
        )


        print("==============================")
        print("QUIZ GENERATION SUCCESS")
        print("==============================\n")


        return quiz_data


    # ======================================
    # ERROR HANDLING
    # ======================================

    except Exception as e:

        print("\n==============================")
        print("QUIZ GENERATION ERROR")
        print("==============================")

        print(
            "Error Type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print("==============================\n")


        return {

            "topic": topic,

            "questions": [],

            "error": str(e)

        }