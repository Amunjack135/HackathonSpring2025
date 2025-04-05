import json
import ast
import re
import typing

from openai import OpenAI
from difflib import SequenceMatcher

import EmployeeProfile
import CompanyRole
import Resume


class MyGPTAPI:
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)

        api_key = config.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("API key not found in config.json.")

        self.__client__: OpenAI = OpenAI(api_key=api_key)

    def get_skills_from_resume(self, resume: Resume.MyResume) -> tuple[str, ...]:
        response = self.__client__.responses.create(
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

    def company_skills(self, roles_to_check: typing.Iterable[str]):
        response = self.__client__.responses.create(
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

    def partial_match_score(self, skill_1, skill_2):
        return SequenceMatcher(None, skill_1, skill_2).ratio()  # Returns a value between 0 and 1

    def match_employee_to_role(self, employee: EmployeeProfile.MyEmployeeProfile,
                               company_roles: dict[int, CompanyRole.MyCompanyRole]):
        role_scores: dict[int, float] = {}
        active_roles: set[str] = set(role.role_name for role in company_roles.values())
        extra_skills_input: list[dict[str, typing.Any]] = self.company_skills(active_roles)
        extra_skills: dict[int, dict[str, float]] = {}

        for info in extra_skills_input:
            role_name: str = info['role']
            uids: tuple[int, ...] = CompanyRole.MyCompanyRole.get_uuids_from_role_name(role_name.replace(' ', ''))

            if len(uids) == 0:
                continue

            for uid in uids:
                extra_skills[uid] = info['skills']

        normalized_employee_skills = [skill.strip().lower() for skill in employee.skills]

        for uid, role in company_roles.items():
            required_score = 0
            optional_score = 0
            extra_score = 0

            normalized_role_required_skills = {k.strip().lower(): v for k, v in role.required_skills.items()}
            normalized_role_optional_skills = {k.strip().lower(): v for k, v in role.optional_skills.items()}
            normalized_role_extra_skills = {k.strip().lower(): v for k, v in extra_skills.get(uid, {}).items()}

            # Calculate required skills score
            for skill, weight in normalized_role_required_skills.items():
                if skill in normalized_employee_skills:
                    required_score += weight
                else:
                    for emp_skill in normalized_employee_skills:
                        similarity = self.partial_match_score(emp_skill, skill)
                        if similarity > 0.6:
                            required_score += weight * similarity
                            break

            # Calculate optional skills score
            for skill, weight in normalized_role_optional_skills.items():
                if skill in normalized_employee_skills:
                    optional_score += weight
                else:
                    for emp_skill in normalized_employee_skills:
                        similarity = self.partial_match_score(emp_skill, skill)
                        if similarity > 0.6:
                            optional_score += weight * similarity
                            break

            # Calculate extra (AI) skills score
            for skill, weight in normalized_role_extra_skills.items():
                if skill in normalized_employee_skills:
                    extra_score += weight
                else:
                    for emp_skill in normalized_employee_skills:
                        similarity = self.partial_match_score(emp_skill, skill)
                        if similarity > 0.6:
                            extra_score += weight * similarity
                            break

            total_score = required_score + optional_score + extra_score

            print(f"\nRole: {role.role_name}")
            print(f"Required Score: {required_score:.2f}")
            print(f"Optional Score: {optional_score:.2f}")
            print(f"Extra (AI) Score: {extra_score:.2f}")
            print(f"Total Score: {total_score:.2f}")

            role_scores[uid] = total_score

        top_matches: list[tuple[int, float]] = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        return {pair[0]: pair[1] for pair in top_matches}









