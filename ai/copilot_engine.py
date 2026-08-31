import os
import json

from groq import Groq
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = None

if api_key:
    client = Groq(api_key=api_key)
else:
    print("WARNING: GROQ_API_KEY not found.")


# =========================================================
# MAIN COPILOT FUNCTION
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
    Karmayogi AI conversational career and learning copilot.

    The Copilot:
    - understands the user's context
    - remembers recent conversation
    - answers the current question first
    - gives personalized guidance
    - does NOT generate a roadmap unless requested
    """

    # -----------------------------------------------------
    # NORMALIZE INPUT
    # -----------------------------------------------------

    question = str(question or "").strip()

    profile = profile or {}
    scores = scores or {}
    skill_gaps = skill_gaps or []
    learning_goal = learning_goal or ""
    conversation = conversation or []


    # -----------------------------------------------------
    # EMPTY QUESTION
    # -----------------------------------------------------

    if not question:

        return (
            "Sure — what would you like help with?"
        )


    # -----------------------------------------------------
    # API KEY CHECK
    # -----------------------------------------------------

    if not client:

        print("ERROR: GROQ_API_KEY is missing.")

        return fallback_response(
            question=question,
            profile=profile,
            scores=scores,
            skill_gaps=skill_gaps,
            learning_goal=learning_goal
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
    # CONVERSATION HISTORY
    # =====================================================

    conversation_messages = []


    for message in conversation[-12:]:

        if not isinstance(message, dict):
            continue

        role = message.get("role")

        content = message.get("content", "")


        if role not in ["user", "assistant"]:
            continue


        if not content:
            continue


        conversation_messages.append({

            "role": role,

            "content": str(content)

        })


    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    system_prompt = """
You are Karmayogi AI Copilot.

You are a conversational AI career and learning mentor inside
a competency-based learning platform.

Your MOST IMPORTANT job is to have a natural conversation with
the user and answer the CURRENT question correctly.

You are NOT a report generator.

=========================================================
1. CORE CONVERSATIONAL BEHAVIOUR
=========================================================

Always answer the user's CURRENT question first.

Do not automatically turn every question into:

- a roadmap
- a study plan
- a 6-phase program
- a table
- a list of courses
- a resource catalog
- a long career report

Only create those things when the user explicitly asks for them.

For a simple question, give a simple answer.

For example:

User:
"What is SQL?"

Good:
"SQL is a language used to communicate with relational
databases. You can use it to retrieve, filter, update and
analyze data."

Bad:
A six-phase SQL mastery roadmap.

=========================================================
2. PERSONALIZATION
=========================================================

Use the user's context when it is relevant.

Available context may include:

- name
- department
- designation
- education
- experience
- assessment scores
- skill gaps
- learning goal
- learning format
- previous conversation

Do not mention the entire profile unnecessarily.

Use only the information needed for the current answer.

=========================================================
3. SKILL PRIORITIZATION
=========================================================

When recommending what to learn next:

Consider:

1. size of competency gap
2. career relevance
3. learning-goal relevance
4. dependency between skills
5. practical importance

Do not blindly choose the lowest score.

If the assessment data does not contain enough information,
say that instead of inventing scores.

=========================================================
4. NORMAL QUESTIONS
=========================================================

For ordinary questions:

Answer directly.

Prefer:

2-6 sentences.

Use bullets only when they improve clarity.

Do not unnecessarily create sections.

=========================================================
5. TECHNICAL QUESTIONS
=========================================================

When explaining a technical concept:

1. Explain it simply.
2. Give a small example.
3. Give code only when useful.
4. Explain the code briefly.

Example:

If the user asks:
"What is a Python list?"

Explain the concept and give a tiny example.

Do NOT create a complete Python roadmap unless requested.

=========================================================
6. "WHAT SHOULD I LEARN NEXT?"
=========================================================

If the user asks:

"What should I learn next?"
"What should I study next?"
"Where should I start?"

Give a short personalized recommendation.

Prefer 1-3 priorities.

Explain WHY they are priorities.

Do NOT generate a huge roadmap.

=========================================================
7. ROADMAP REQUESTS
=========================================================

Only generate a detailed roadmap if the user explicitly asks:

- roadmap
- learning roadmap
- career roadmap
- complete path
- path to become X

Then provide a structured sequence.

Keep it realistic.

Do not invent specific courses or URLs unless they are provided
by the application or user.

=========================================================
8. STUDY PLAN REQUESTS
=========================================================

Only generate a study plan when explicitly requested.

Examples:

"Make me a 30 day study plan."

"Create a weekly schedule."

"How should I study Python for 4 weeks?"

Then provide a structured schedule.

If available time is essential and unknown, ask a short
clarifying question.

=========================================================
9. SKILL GAP QUESTIONS
=========================================================

If the user asks about skill gaps:

Explain:

- current level if available
- required level if available
- gap
- why it matters
- what to do next

Do not invent missing values.

=========================================================
10. CAREER QUESTIONS
=========================================================

For career questions:

Consider:

- user's profile
- assessment
- skill gaps
- learning goal

Explain why a recommendation fits.

Do not guarantee:

- jobs
- salary
- promotions
- exam results
- career success

=========================================================
11. QUIZ QUESTIONS
=========================================================

If the user asks about quiz preparation:

Focus on their relevant competency gaps.

If the application indicates they are ready for the quiz,
encourage them to take it.

If they still have gaps, recommend improving those areas first.

Do not claim that the user passed or completed something
unless the application explicitly provides that information.

=========================================================
12. CONVERSATION MEMORY
=========================================================

Use recent conversation history.

If the user says:

"Explain that again."

Use the previous message to understand what "that" means.

If the user says:

"What about Python?"

Understand what was discussed previously.

Do not restart the conversation unnecessarily.

=========================================================
13. FOLLOW-UP QUESTIONS
=========================================================

Do not ask unnecessary questions.

If you have enough information, answer directly.

Ask a clarification question only when the missing information
is genuinely necessary.

=========================================================
14. RECOMMENDATIONS
=========================================================

Recommendations must be practical.

Instead of:

"Improve Python."

Say:

"Focus first on functions, lists, dictionaries and file handling,
then practice with small data-analysis problems."

Instead of:

"Improve SQL."

Say:

"Start with SELECT, WHERE, GROUP BY and JOIN, then practice
queries on a small dataset."

=========================================================
15. HONESTY
=========================================================

Never invent:

- user scores
- user achievements
- completed courses
- certifications
- work experience
- course URLs
- iGOT data
- government data
- assessment results

Never pretend to have accessed an external system.

If information is unavailable, say so.

=========================================================
16. RESPONSE LENGTH
=========================================================

Match the answer length to the question.

Simple question:
Short answer.

Concept explanation:
Short explanation + example.

Recommendation:
3-5 useful points maximum.

Roadmap explicitly requested:
Detailed structured response.

Study plan explicitly requested:
Structured schedule.

Complex question:
Use headings and bullets.

=========================================================
17. VERY IMPORTANT
=========================================================

Do NOT interpret every learning-related question as a request
for a roadmap.

For example:

"What is Pandas?"
→ Explain Pandas.

"Why should I learn SQL?"
→ Explain why SQL is useful.

"My SQL score is 2/5, what should I do?"
→ Give targeted SQL advice.

"Make me an SQL roadmap."
→ Generate a roadmap.

"Make me a 30-day SQL study plan."
→ Generate a study plan.

=========================================================
18. NATURAL PERSONALITY
=========================================================

Be:

- friendly
- intelligent
- supportive
- practical
- professional
- conversational

Do not repeatedly say:

"According to your profile..."

Do not sound robotic.

Talk like a knowledgeable mentor.

=========================================================
FINAL RULE
=========================================================

Answer the CURRENT USER QUESTION.

Then, only if useful, give a short personalized next step.

Never unnecessarily expand a simple question into a huge response.
"""


    # =====================================================
    # CURRENT USER MESSAGE
    # =====================================================

    user_prompt = f"""
USER CONTEXT:

{json.dumps(
    user_context,
    indent=2,
    ensure_ascii=False,
    default=str
)}


CURRENT USER QUESTION:

{question}


IMPORTANT:

Answer the CURRENT question directly.

Use the user's context only when relevant.

Do NOT create a roadmap, study plan, table, phases or resource
list unless the user explicitly asks for it.

If the question is simple, keep the answer simple.
"""


    # =====================================================
    # BUILD MESSAGES
    # =====================================================

    messages = [

        {
            "role": "system",
            "content": system_prompt
        }

    ]


    # -----------------------------------------------------
    # ADD HISTORY
    # -----------------------------------------------------

    messages.extend(
        conversation_messages
    )


    # -----------------------------------------------------
    # CURRENT MESSAGE
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
        print("KARMAYOGI AI COPILOT")
        print("=" * 70)

        print("Model: openai/gpt-oss-20b")
        print("Question:", question)
        print("Conversation messages:", len(conversation_messages))


        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=messages,

            temperature=0.35,

            max_tokens=1000

        )


        # =================================================
        # VALIDATE RESPONSE
        # =================================================

        if not response:

            raise Exception(
                "Empty response from Groq."
            )


        if not response.choices:

            raise Exception(
                "Groq returned no choices."
            )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        if not answer:

            raise Exception(
                "Groq returned empty content."
            )


        answer = str(
            answer
        ).strip()


        if not answer:

            raise Exception(
                "AI response became empty after processing."
            )


        print("AI RESPONSE SUCCESS")
        print("=" * 70)


        return answer


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

            profile=profile,

            scores=scores,

            skill_gaps=skill_gaps,

            learning_goal=learning_goal
        )


# =========================================================
# FALLBACK
# =========================================================

def fallback_response(
    question,
    profile=None,
    scores=None,
    skill_gaps=None,
    learning_goal=""
):

    profile = profile or {}
    scores = scores or {}
    skill_gaps = skill_gaps or []

    q = str(
        question or ""
    ).lower().strip()


    # =====================================================
    # GREETING
    # =====================================================

    greetings = [
        "hi",
        "hello",
        "hey",
        "hii",
        "helo"
    ]

    if q in greetings:

        name = profile.get(
            "name",
            ""
        )

        if name:

            return (
                f"Hi {name}! 👋 "
                "How can I help you with your learning or career today?"
            )

        return (
            "Hi! 👋 How can I help you with your learning or career today?"
        )


    # =====================================================
    # SKILL GAPS
    # =====================================================

    if (
        "skill gap" in q
        or "skill gaps" in q
        or "my weakness" in q
        or "weakness" in q
    ):

        if skill_gaps:

            skills = ", ".join(
                str(skill)
                for skill in skill_gaps
            )

            return (
                f"Your current assessment shows these areas "
                f"for improvement: {skills}.\n\n"
                "I'd recommend focusing on the most relevant gap "
                "first, practicing it with small tasks, and then "
                "taking a reassessment."
            )

        return (
            "I don't currently have any recorded skill gaps "
            "from your assessment."
        )


    # =====================================================
    # WHAT TO LEARN NEXT
    # =====================================================

    if (
        "what should i learn" in q
        or "what should i study" in q
        or "learn next" in q
        or "study next" in q
        or "what to learn" in q
    ):

        if skill_gaps:

            first_gap = str(
                skill_gaps[0]
            )

            return (
                f"I'd start with **{first_gap}** because it's one "
                "of your identified improvement areas.\n\n"
                f"Start with the fundamentals of {first_gap}, "
                "practice a few small problems, and then reassess "
                "your understanding."
            )


        if learning_goal:

            return (
                f"Since your current learning goal is "
                f"**{learning_goal}**, I'd start by strengthening "
                "the fundamentals and then move into practical "
                "practice."
            )


        return (
            "Start with the competency that is most relevant to "
            "your current career or learning goal, then practice "
            "it with small practical tasks."
        )


    # =====================================================
    # ROADMAP
    # =====================================================

    if (
        "roadmap" in q
        or "complete path" in q
        or "learning path" in q
    ):

        if skill_gaps:

            first_gap = str(
                skill_gaps[0]
            )

            return (
                f"A good starting point is **{first_gap}**.\n\n"
                "1. Learn the fundamentals.\n"
                "2. Practice basic problems.\n"
                "3. Build a small practical project.\n"
                "4. Test your understanding.\n"
                "5. Reassess your competency."
            )

        return (
            "A simple learning path is:\n\n"
            "1. Learn fundamentals.\n"
            "2. Practice.\n"
            "3. Build a small project.\n"
            "4. Test yourself.\n"
            "5. Reassess."
        )


    # =====================================================
    # STUDY PLAN
    # =====================================================

    if (
        "study plan" in q
        or "study schedule" in q
        or "weekly plan" in q
        or "30 day plan" in q
        or "30-day plan" in q
    ):

        if skill_gaps:

            first_gap = str(
                skill_gaps[0]
            )

            return (
                f"For your current gap in **{first_gap}**, "
                "use this basic weekly structure:\n\n"
                "Day 1-2 → Learn fundamentals\n"
                "Day 3-4 → Practice problems\n"
                "Day 5 → Practical task\n"
                "Day 6 → Revise mistakes\n"
                "Day 7 → Self-test\n\n"
                "Then repeat with progressively harder tasks."
            )

        return (
            "Use a simple weekly cycle:\n\n"
            "Learn → Practice → Build → Revise → Test."
        )


    # =====================================================
    # QUIZ
    # =====================================================

    if (
        "quiz" in q
        or "test" in q
        or "assessment" in q
    ):

        if skill_gaps:

            return (
                "You still have identified competency gaps, so "
                "I'd recommend working on those areas first. "
                "After improving them, take the reassessment "
                "before attempting the final quiz."
            )

        return (
            "You can prepare by revising the important concepts, "
            "practicing questions, and testing yourself before "
            "the quiz."
        )


    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "I'm here to help with your learning, competency gaps, "
        "career direction, technical concepts, study planning "
        "and quiz preparation. What would you like to work on?"
    )