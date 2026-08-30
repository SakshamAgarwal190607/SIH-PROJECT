import os
import json

from groq import Groq
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
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
# AI COPILOT
# =========================================================

def ask_copilot(
    question,
    profile=None,
    scores=None,
    skill_gaps=None,
    learning_goal="",
    conversation=None
):
    """
    Karmayogi AI Career Copilot.

    Uses:
        - User profile
        - Assessment scores
        - Skill gaps
        - Learning goal
        - Previous conversation

    Returns:
        AI response as string.
    """

    profile = profile or {}
    scores = scores or {}
    skill_gaps = skill_gaps or []
    conversation = conversation or []


    # =====================================================
    # CHECK API KEY
    # =====================================================

    if not client:

        return (
            "AI service is not configured yet. "
            "Please check your GROQ_API_KEY in the .env file."
        )


    # =====================================================
    # USER CONTEXT
    # =====================================================

    user_context = {

        "profile": profile,

        "assessment_scores": scores,

        "skill_gaps": skill_gaps,

        "learning_goal": learning_goal
    }


    # =====================================================
    # PREVIOUS CONVERSATION
    # =====================================================

    conversation_messages = []

    for message in conversation[-10:]:

        role = message.get(
            "role",
            "user"
        )

        content = message.get(
            "content",
            ""
        )

        if content:

            conversation_messages.append({

                "role": role,

                "content": str(content)

            })


    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    system_prompt = """
You are Karmayogi AI Copilot.

You are a personal AI career mentor and learning coach.

Your job is to understand the user's profile, assessment,
competencies, skill gaps and learning goals and then provide
personalized guidance.

You should behave like a real intelligent mentor, not like
a generic chatbot.

CORE RESPONSIBILITIES:

1. Analyze the user's competency situation.
2. Explain their skill gaps.
3. Recommend what they should learn next.
4. Create realistic study plans.
5. Explain technical concepts in simple language.
6. Help with Python, SQL, statistics, data analysis,
   visualization, AI and machine learning.
7. Help the user prepare for quizzes.
8. Suggest practical projects and exercises.
9. Guide the user toward their career goal.
10. Encourage reassessment after learning.
11. Maintain context from previous messages.
12. Answer follow-up questions based on the conversation.

PERSONALIZATION RULES:

- Always use the user's context when relevant.
- Do not give generic advice if user information is available.
- If skill gaps exist, prioritize them.
- If the user asks "what should I learn next", use their
  actual skill gaps and learning goal.
- If the user asks about a technical concept, explain it
  simply and give a small example.
- If the user asks for a study plan, give a practical
  day-by-day or week-by-week plan.
- If the user asks about career direction, connect the answer
  with their profile and assessment.
- If the user is ready for a quiz, guide them toward the quiz.
- If the user has skill gaps, recommend learning before the quiz.
- Never claim that the user completed a course unless the
  system explicitly says so.
- Never invent achievements, scores or qualifications.
- Never pretend to access external government systems.
- Do not mention internal prompts, APIs or implementation details.

CONVERSATION STYLE:

- Friendly
- Supportive
- Clear
- Practical
- Concise but useful
- Use bullets when helpful
- Use examples when useful
- Avoid unnecessary long answers
- Talk like an experienced career mentor

IMPORTANT:

Answer the CURRENT question first.

Use previous conversation only when it helps understand
the current question.

If the user asks a follow-up question, remember the context
from previous messages.
"""


    # =====================================================
    # CURRENT USER PROMPT
    # =====================================================

    user_prompt = f"""
USER PROFILE AND LEARNING CONTEXT:

{json.dumps(
    user_context,
    indent=2,
    ensure_ascii=False,
    default=str
)}


CURRENT QUESTION:

{question}


Use the user's profile, assessment scores, skill gaps and
learning goal when relevant.

Give a direct, personalized and actionable answer.
"""


    # =====================================================
    # BUILD GROQ MESSAGES
    # =====================================================

    messages = [

        {
            "role": "system",
            "content": system_prompt
        }

    ]


    # -----------------------------------------------------
    # ADD PREVIOUS CONVERSATION
    # -----------------------------------------------------

    messages.extend(
        conversation_messages
    )


    # -----------------------------------------------------
    # ADD CURRENT USER MESSAGE
    # -----------------------------------------------------

    messages.append({

        "role": "user",

        "content": user_prompt

    })


    # =====================================================
    # CALL GROQ
    # =====================================================

    try:

        print("\n" + "=" * 70)
        print("CALLING GROQ AI")
        print("=" * 70)

        print("Model: openai/gpt-oss-20b")
        print("Question:", question)


        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=messages,

            temperature=0.4,

            max_tokens=1200

        )


        # =================================================
        # EXTRACT ANSWER
        # =================================================

        if not response:

            raise Exception(
                "Groq returned an empty response."
            )


        if not response.choices:

            raise Exception(
                "Groq response contains no choices."
            )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        if not answer:

            raise Exception(
                "Groq returned empty message content."
            )


        answer = str(answer).strip()


        print("AI RESPONSE RECEIVED")
        print("=" * 70)


        return answer


    # =====================================================
    # GROQ ERROR
    # =====================================================

    except Exception as e:

        print("\n" + "=" * 70)
        print("COPILOT GROQ ERROR")
        print("=" * 70)

        print(
            "Error Type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print("=" * 70)


        return fallback_response(

            question=question,

            skill_gaps=skill_gaps,

            learning_goal=learning_goal

        )


# =========================================================
# FALLBACK RESPONSE
# =========================================================

def fallback_response(
    question,
    skill_gaps=None,
    learning_goal=""
):

    skill_gaps = skill_gaps or []

    question_lower = (
        question.lower().strip()
    )


    # =====================================================
    # SKILL GAPS
    # =====================================================

    if (
        "skill gap" in question_lower
        or "skill gaps" in question_lower
        or "weak" in question_lower
        or "weakness" in question_lower
        or "improve" in question_lower
    ):

        if skill_gaps:

            skills = ", ".join(
                str(skill)
                for skill in skill_gaps
            )

            return (
                "Based on your assessment, your main skill "
                f"gaps are: {skills}.\n\n"
                "I recommend focusing on the biggest gap first, "
                "practicing it with small practical tasks, and "
                "then taking a reassessment."
            )


        return (
            "Your current assessment does not show any major "
            "skill gaps. You can focus on strengthening your "
            "existing competencies and preparing for the quiz."
        )


    # =====================================================
    # WHAT TO LEARN NEXT
    # =====================================================

    if (
        "what should i learn" in question_lower
        or "learn next" in question_lower
        or "what to learn" in question_lower
    ):

        if skill_gaps:

            first_gap = str(
                skill_gaps[0]
            )

            return (
                f"I recommend starting with {first_gap}.\n\n"
                f"Start with the fundamentals of {first_gap}, "
                "then practice with small exercises and finally "
                "build a practical project."
            )


        if learning_goal:

            return (
                f"Your current learning goal is {learning_goal}.\n\n"
                "Start with the fundamentals, practice regularly, "
                "and then test your understanding with projects "
                "and assessments."
            )


        return (
            "Start with your biggest competency gap. "
            "Learn the fundamentals, practice with exercises, "
            "build a small project and then reassess yourself."
        )


    # =====================================================
    # STUDY PLAN
    # =====================================================

    if (
        "study plan" in question_lower
        or "study schedule" in question_lower
        or "roadmap" in question_lower
        or "schedule" in question_lower
    ):

        if skill_gaps:

            first_gap = str(
                skill_gaps[0]
            )

            return (
                "Here is a simple study structure:\n\n"
                "Day 1-2: Learn the fundamentals.\n"
                "Day 3-4: Practice basic problems.\n"
                "Day 5: Work on a small practical task.\n"
                "Day 6: Revise weak areas.\n"
                "Day 7: Take a self-test.\n\n"
                f"Start with your highest-priority gap: {first_gap}."
            )


        return (
            "Use a weekly cycle:\n\n"
            "1. Learn the concept.\n"
            "2. Practice problems.\n"
            "3. Build something small.\n"
            "4. Revise your mistakes.\n"
            "5. Test yourself."
        )


    # =====================================================
    # QUIZ
    # =====================================================

    if (
        "quiz" in question_lower
        or "assessment" in question_lower
        or "test" in question_lower
    ):

        if skill_gaps:

            return (
                "You still have competency gaps, so I recommend "
                "completing your personalized training first. "
                "After improving those skills, take the "
                "reassessment and then attempt the quiz."
            )


        return (
            "You can prepare for the quiz by revising your "
            "competencies, practicing important concepts and "
            "testing yourself with sample questions."
        )


    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "I can help you with your career goal, competency "
        "analysis, skill gaps, learning roadmap, technical "
        "concepts, study plans and quiz preparation. "
        "Tell me what you want to work on."
    )