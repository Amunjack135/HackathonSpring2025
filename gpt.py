from openai import OpenAI

client = OpenAI(api_key="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")


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

        1. Extract **exactly 8** key skills (both technical and soft skills, certifications, or tools).
        2. Identify the **most suitable Chevron role** for this individual from the list below:

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

        Skills: [Comma-separated list of 8 relevant skills]  
        Best Role Match: [One role from the list above]

        Employee Data:
        {text}
        """
        ,
        input=text,
    )
    return response.output_text

def read_file(file):
    with open(file, 'r') as f:
        text = f.read()
    return text

text = read_file("text.txt")
print(skills(text))

