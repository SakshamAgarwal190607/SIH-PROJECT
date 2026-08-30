import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# MAIN AI ANALYSIS
# =========================================================

def analyze_user(profile, scores):

    """
    Analyze user's profile and assessment scores.

    Returns:
        career goal
        required competencies
        user competencies
        skill gaps
        competency score
        personalized roadmap
        quiz eligibility
    """

    user_data = {
        "profile": profile,
        "assessment_scores": scores
    }

    prompt = f"""
You are an AI competency advisor for an
AI-enabled learning platform for India's
Official Statistical System.

Analyze the following user.

USER DATA:
{json.dumps(user_data, indent=2)}

Your task:

1. Suggest ONE suitable career/job role.

2. Explain why this career is suitable.

3. Identify the important competencies required
   for this career.

4. Compare required competency with user's
   assessment score.

Assessment scores are from 0 to 5.

Scoring:
0 = No knowledge
1 = Very weak
2 = Beginner
3 = Intermediate
4 = Good
5 = Advanced

5. For every required competency provide:

name
required_score
user_score
gap
status

Status:
"fulfilled" if user_score >= required_score
"gap" if user_score < required_score

6. Calculate overall competency score.

The score should represent how many required
competencies have been fulfilled.

7. Identify only the competencies having gaps.

8. Create a personalized roadmap ONLY for
competencies having gaps.

For every gap provide:

competency
current_level
target_level
why_needed
what_to_learn
action

9. Decide quiz eligibility.

The user is ready for quiz ONLY when
ALL required competencies are fulfilled.

Do NOT create URLs.
Do NOT invent training links.
Do NOT mention URLs.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "career_goal": "",
    "career_reason": "",

    "competencies": [
        {{
            "name": "",
            "required_score": 0,
            "user_score": 0,
            "gap": 0,
            "status": "gap"
        }}
    ],

    "overall_competency_score": 0,

    "skill_gaps": [],

    "personalized_roadmap": [
        {{
            "competency": "",
            "current_level": 0,
            "target_level": 0,
            "why_needed": "",
            "what_to_learn": "",
            "action": ""
        }}
    ],

    "ready_for_quiz": false,

    "overall_feedback": ""
}}
"""

    try:

        response = client.chat.completions.create(

            # Use a model available in your Groq account
            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are an expert competency "
                        "and learning advisor. "
                        "Return valid JSON only."
                    )
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

        result = response.choices[0].message.content

        analysis = json.loads(result)

        # Validate / normalize AI response
        analysis = validate_analysis(
            analysis,
            scores
        )

        return analysis

    except Exception as e:

        print("=" * 50)
        print("GROQ AI ERROR")
        print(e)
        print("=" * 50)

        return fallback_analysis(
            profile,
            scores
        )


# =========================================================
# VALIDATE AI RESPONSE
# =========================================================

def validate_analysis(analysis, scores):

    """
    Makes sure AI response has all required fields.
    """

    if not isinstance(analysis, dict):
        return fallback_analysis({}, scores)

    analysis.setdefault(
        "career_goal",
        "Statistical Data Analyst"
    )

    analysis.setdefault(
        "career_reason",
        "This career aligns with the user's "
        "data and analytical competencies."
    )

    analysis.setdefault(
        "competencies",
        []
    )

    analysis.setdefault(
        "skill_gaps",
        []
    )

    analysis.setdefault(
        "personalized_roadmap",
        []
    )

    analysis.setdefault(
        "overall_competency_score",
        0
    )

    analysis.setdefault(
        "ready_for_quiz",
        False
    )

    analysis.setdefault(
        "overall_feedback",
        ""
    )

    # -------------------------------------------------
    # Make sure every competency has valid fields
    # -------------------------------------------------

    for competency in analysis["competencies"]:

        competency.setdefault(
            "name",
            "Unknown"
        )

        competency.setdefault(
            "required_score",
            4
        )

        competency.setdefault(
            "user_score",
            0
        )

        competency.setdefault(
            "gap",
            max(
                competency["required_score"]
                - competency["user_score"],
                0
            )
        )

        competency.setdefault(
            "status",
            (
                "fulfilled"
                if competency["user_score"]
                >= competency["required_score"]
                else "gap"
            )
        )

    # -------------------------------------------------
    # Calculate quiz eligibility ourselves
    # -------------------------------------------------

    all_fulfilled = True

    for competency in analysis["competencies"]:

        if competency["user_score"] < competency["required_score"]:

            all_fulfilled = False

            break

    analysis["ready_for_quiz"] = all_fulfilled

    # -------------------------------------------------
    # Calculate competency percentage
    # -------------------------------------------------

    total = len(
        analysis["competencies"]
    )

    fulfilled = sum(
        1
        for c in analysis["competencies"]
        if c["user_score"] >= c["required_score"]
    )

    if total > 0:

        analysis["overall_competency_score"] = round(
            (fulfilled / total) * 100
        )

    else:

        analysis["overall_competency_score"] = 0

    # -------------------------------------------------
    # Generate skill gaps ourselves
    # -------------------------------------------------

    analysis["skill_gaps"] = [

        c["name"]

        for c in analysis["competencies"]

        if c["user_score"] < c["required_score"]

    ]

    return analysis


# =========================================================
# FALLBACK ANALYSIS
# =========================================================

def fallback_analysis(profile, scores):

    """
    Backup system if Groq is unavailable.
    """

    competencies = []

    gaps = []

    # For MVP we use 4 as target level.
    REQUIRED_LEVEL = 4

    for skill, score in scores.items():

        gap = max(
            REQUIRED_LEVEL - score,
            0
        )

        status = (
            "fulfilled"
            if score >= REQUIRED_LEVEL
            else "gap"
        )

        competency = {

            "name": skill,

            "required_score":
                REQUIRED_LEVEL,

            "user_score":
                score,

            "gap":
                gap,

            "status":
                status
        }

        competencies.append(
            competency
        )

        if status == "gap":

            gaps.append(skill)

    # -------------------------------------------------
    # Competency percentage
    # -------------------------------------------------

    total = len(competencies)

    fulfilled = sum(

        1

        for c in competencies

        if c["status"] == "fulfilled"

    )

    percentage = (

        round(
            (fulfilled / total) * 100
        )

        if total > 0

        else 0
    )

    # -------------------------------------------------
    # Roadmap
    # -------------------------------------------------

    roadmap = []

    for skill in gaps:

        current = scores.get(
            skill,
            0
        )

        roadmap.append({

            "competency":
                skill,

            "current_level":
                current,

            "target_level":
                REQUIRED_LEVEL,

            "why_needed":
                f"{skill} is important "
                "for the selected career path.",

            "what_to_learn":
                f"Improve your {skill} "
                "fundamentals and practical skills.",

            "action":
                f"Complete training and "
                f"practice activities for {skill}."
        })

    ready = len(gaps) == 0

    # -------------------------------------------------
    # Return fallback
    # -------------------------------------------------

    return {

        "career_goal":
            "Statistical Data Analyst",

        "career_reason":
            "This role aligns with "
            "data analysis and "
            "statistical competencies.",

        "competencies":
            competencies,

        "overall_competency_score":
            percentage,

        "skill_gaps":
            gaps,

        "personalized_roadmap":
            roadmap,

        "ready_for_quiz":
            ready,

        "overall_feedback":

            (
                "All required competencies "
                "have been fulfilled. "
                "You can proceed to the quiz."

                if ready

                else

                "You have competency gaps. "
                "Complete the recommended "
                "training before attempting "
                "the quiz."
            )
    }