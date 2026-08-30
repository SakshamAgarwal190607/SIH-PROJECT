import json
import os


# =====================================================
# LOAD COURSE CATALOG
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

COURSES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "courses.json"
)


# =====================================================
# LOAD COURSES
# =====================================================

def load_courses():
    """
    Load all training courses from courses.json.
    """

    try:

        with open(
            COURSES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            courses = json.load(file)

            # Make sure JSON contains a list
            if not isinstance(courses, list):

                print(
                    "Course catalog must contain a list."
                )

                return []

            return courses

    except FileNotFoundError:

        print(
            f"courses.json not found at: {COURSES_FILE}"
        )

        return []

    except json.JSONDecodeError:

        print(
            "courses.json contains invalid JSON."
        )

        return []

    except Exception as e:

        print(
            "Course catalog error:",
            e
        )

        return []


# =====================================================
# FIND PERSONALIZED TRAINING
# =====================================================

def get_training_recommendations(
    profile=None,
    skill_gaps=None
):
    """
    Generate personalized training recommendations.

    profile:
        User profile containing:
        name
        department
        designation
        experience
        education

    skill_gaps:
        List of competencies where the user
        needs improvement.

    Example:

        profile = {
            "name": "Saksham",
            "department": "Statistics",
            "designation": "Analyst",
            "experience": "2 years",
            "education": "B.Tech"
        }

        skill_gaps = [
            "Python",
            "SQL"
        ]
    """

    # =================================================
    # BACKWARD COMPATIBILITY
    # =================================================
    #
    # If dashboard.py calls:
    #
    # get_training_recommendations(skill_gaps)
    #
    # then the first argument will actually contain
    # the skill gap list.
    #
    # This block handles that situation automatically.
    # =================================================

    if skill_gaps is None and isinstance(
        profile,
        list
    ):

        skill_gaps = profile

        profile = {}


    # =================================================
    # DEFAULT VALUES
    # =================================================

    if profile is None:

        profile = {}


    if skill_gaps is None:

        skill_gaps = []


    # =================================================
    # LOAD COURSE CATALOG
    # =================================================

    courses = load_courses()


    recommendations = []


    # =================================================
    # NO SKILL GAP
    # =================================================

    if not skill_gaps:

        return recommendations


    # =================================================
    # NORMALIZE SKILL GAPS
    # =================================================

    normalized_gaps = []

    for skill in skill_gaps:

        if not skill:
            continue

        normalized_gaps.append(
            str(skill).strip().lower()
        )


    # =================================================
    # MATCH COURSES
    # =================================================

    for course in courses:

        if not isinstance(course, dict):

            continue


        course_competency = str(
            course.get(
                "competency",
                ""
            )
        ).strip().lower()


        # Skip invalid course
        if not course_competency:

            continue


        # =================================================
        # CHECK MATCH
        # =================================================

        if course_competency in normalized_gaps:

            recommendations.append({

                "competency":
                    course.get(
                        "competency",
                        ""
                    ),

                "title":
                    course.get(
                        "title",
                        "Recommended Training"
                    ),

                "description":
                    course.get(
                        "description",
                        "Improve this competency through "
                        "recommended learning."
                    ),

                "url":
                    course.get(
                        "url",
                        "#"
                    ),

                # User profile information is retained
                # for future personalization.
                "department":
                    profile.get(
                        "department",
                        ""
                    ),

                "designation":
                    profile.get(
                        "designation",
                        ""
                    )

            })


    # =================================================
    # REMOVE DUPLICATES
    # =================================================

    unique_recommendations = []

    seen = set()

    for recommendation in recommendations:

        key = (
            recommendation["competency"].lower(),
            recommendation["title"].lower()
        )

        if key not in seen:

            seen.add(key)

            unique_recommendations.append(
                recommendation
            )


    return unique_recommendations