import json
import ast
import re
import typing

from openai import OpenAI
from difflib import SequenceMatcher

import EmployeeProfile
import CompanyRole
import Resume


with open('config.json') as f:
    config = json.load(f)

api_key = config.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found in config.json.")


EmployeeProfile.MyEmployeeProfile.load('data/employee_profiles')
CompanyRole.MyCompanyRole.load('data/company_roles')

client = OpenAI(api_key=api_key)


def get_skills_from_resume(resume: Resume.MyResume) -> tuple[str, ...]:
    response = client.responses.create(
        model="gpt-4o",
        instructions=
        """
        You are building an AI-powered system for Chevron to assess employee capabilities and match them to the most suitable internal roles.

        The system will:
        - Analyzåe employee data such as performance reviews, project outcomes, self-assessments, and peer feedback.
        - Extract relevant technical and soft skills.
        - Compare these skills with Chevron's available roles to determine the best match.

        Given the following resume or employee data, do the following:

        1. Extract **exactly 8** key skills (technical , certifications, or tools).

        Chevron Roles:
        - Cloud Engineer
        - Network Engineer
        - Infrastructure Engineer
        - Data Engineer
        - Data Analyst
        - Data Scientist
        - Machine Learning Engineer
        - Business Intelligence Analyst
        - Cyber Engineer - Information Technology (IT)
        - Cyber Engineer - Operational Technology (OT)
        - Software Engineer
        - Application Engineer

        **Return your answer in this format:**

        Comma-separated list of 8 relevant skills

        Employee Data:
        {text}
        """
        ,
        input=resume.contents,
    )

    return tuple(response.output_text.split(","))

def company_skills(roles_to_check: typing.Iterable[str]):
    response = client.responses.create(
        model="gpt-4o",
        instructions=
        f"""
        You are an AI assistant helping Chevron identify required skills for various job roles.

        For each role listed below:
        - Provide a list of 10 required skills.
        - Assign a weight between 1 and 10 indicating the importance of each skill.
        - Format your response as a **Python list of dictionaries**, where each dictionary represents one role.

        Return your answer like this:

        [
            {{
                "role": "Cloud Engineer",
                "skills": {{
                    "AWS": 10,
                    "Python": 9,
                    "Terraform": 8,
                    ...
                }}
            }},
            ...
        ]

        Roles to analyze:
        {"\n".join(f" - {role}" for role in roles_to_check)}
        """,
        input="Provide required skills and importance weights for each Chevron role.",
    )

    # Extract just the list part using a regular expression
    match = re.search(r"\[\s*{.*?}\s*\]", response.output_text, re.DOTALL)
    if match:
        try:
            # Convert the matched string into actual Python list
            parsed_output = ast.literal_eval(match.group(0))
            return parsed_output
        except Exception as e:
            print("Parsing failed:", e)
            print("Raw output:", response.output_text)
            return []
    else:
        print("No valid list found in output.")
        print("Raw output:", response.output_text)
        return []


def partial_match_score(skill_1, skill_2):
    return SequenceMatcher(None, skill_1, skill_2).ratio()  # Returns a value between 0 and 1


def match_employee_to_role(employee: EmployeeProfile.MyEmployeeProfile, company_roles: dict[int, CompanyRole.MyCompanyRole]):
    role_scores = {}
    active_roles: set[str] = set(role.role_name for role in company_roles.values())     # Get all active roles as loaded from file
    extra_skills: dict[str, dict[str, float]] = company_skills(active_roles)            # Get ChatGPT estimated AI skills

    # Normalize employee skills
    normalized_employee_skills = [skill.strip().lower() for skill in employee.skills]

    for uid, role in company_roles.items():
        score = 0

        # Normalize role skills and apply weights
        normalized_role_required_skills = {k.strip().lower(): v for k, v in role.required_skills.items()}       # Get required skills as listed in company role files
        normalized_role_optional_skills = {k.strip().lower(): v for k, v in role.optional_skills.items()}       # Get optional skills as listed in company role files
        normalized_role_extra_skills = {k.strip().lower(): v for k, v in extra_skills[role.role_name].items()}  # Get extra skills as listed from AI

        for skill in normalized_role_required_skills:
            matched_score = 0
            # Exact match
            if skill in normalized_role_required_skills:
                matched_score = normalized_role_required_skills[skill]
            # Partial match
            else:
                # Iterate over all skills in the role and find partial matches
                for role_skill, weight in normalized_role_required_skills.items():
                    similarity = partial_match_score(skill, role_skill)
                    if similarity > 0.6:  # Only consider partial matches that are above a certain threshold
                        matched_score = weight * similarity  # Multiply by the weight for the role

            score += matched_score

        print(f"Total Score for Role: {role.role_name} = {score}\n")

        role_scores[uid] = score

    # Sort roles by score in descending order
    top_matches = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    return top_matches


profile: EmployeeProfile.MyEmployeeProfile = EmployeeProfile.MyEmployeeProfile.get_employees_by_name('Amun Jackson')[0]     # Load profile
resume: Resume.MyResume = profile.resume                                                                                    # Get profile attached resume
employee_skills = get_skills_from_resume(resume)                                                                            # Get profile skills from resume
print(employee_skills)

print(match_employee_to_role(profile, CompanyRole.MyCompanyRole.COMPANY_ROLES))
#hello








