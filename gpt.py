from openai import OpenAI

client = OpenAI(api_key="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")

# import EmployeeProfile, CompanyRole
# EmployeeProfile.MyEmployeeProfile.load('data/employee_profiles')
# CompanyRole.MyCompanyRole.load('data/company_roles')


def skills(text):
    response = client.responses.create(
        model="gpt-4o",
        instructions=
        """
        You are building an AI-powered system for Chevron to assess employee capabilities and match them to the most suitable internal roles.

        The system will:
        - Analyze employee data such as performance reviews, project outcomes, self-assessments, and peer feedback.
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
        input=text,
    )

    return response.output_text.split(",")

import ast
import re

def companySkills():
    response = client.responses.create(
        model="gpt-4o",
        instructions=
        """
        You are an AI assistant helping Chevron identify required skills for various job roles.

        For each role listed below:
        - Provide a list of 10 required skills.
        - Assign a weight between 1 and 10 indicating the importance of each skill.
        - Format your response as a **Python list of dictionaries**, where each dictionary represents one role.

        Return your answer like this:

        [
            {
                "role": "Cloud Engineer",
                "skills": {
                    "AWS": 10,
                    "Python": 9,
                    "Terraform": 8,
                    ...
                }
            },
            ...
        ]

        Roles to analyze:
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


from difflib import SequenceMatcher

def partial_match_score(skill_1, skill_2):
    return SequenceMatcher(None, skill_1, skill_2).ratio()  # Returns a value between 0 and 1

def match_employee_to_role(employee_skills, company_roles, top_n=3):
    role_scores = []

    # Normalize employee skills
    normalized_employee_skills = [skill.strip().lower() for skill in employee_skills]

    for role in company_roles:
        score = 0

        # Normalize role skills and apply weights
        normalized_role_skills = {k.strip().lower(): v for k, v in role["skills"].items()}

        for skill in normalized_employee_skills:
            matched_score = 0
            # Exact match
            if skill in normalized_role_skills:
                matched_score = normalized_role_skills[skill]
            # Partial match
            else:
                # Iterate over all skills in the role and find partial matches
                for role_skill, weight in normalized_role_skills.items():
                    similarity = partial_match_score(skill, role_skill)
                    if similarity > 0.6:  # Only consider partial matches that are above a certain threshold
                        matched_score = weight * similarity  # Multiply by the weight for the role

            score += matched_score

        print(f"Total Score for Role: {role['role']} = {score}\n")

        role_scores.append((role["role"], score))

    # Sort roles by score in descending order and return top N
    top_matches = sorted(role_scores, key=lambda x: x[1], reverse=True)[:top_n]

    return [f"{i+1}. {role} (Score: {score})" for i, (role, score) in enumerate(top_matches)]



def read_file(file):
    with open(file, 'r') as f:
        text = f.read()
    return text

text = read_file("text.txt")

employee_skills = skills(text)

print(employee_skills)

company = companySkills()

print(match_employee_to_role(employee_skills, company))








