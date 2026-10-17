import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from tools import helpdesk_tools

load_dotenv()

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-20b"
)


def build_agent():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "your_groq_api_key":
        raise ValueError(
            "GROQ_API_KEY is missing. Add your key to the .env file."
        )

    llm = ChatGroq(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0
    )

    system_prompt = """
You are NexaDesk AI, an enterprise helpdesk assistant.

You help employees with:
1. IT ticket status.
2. Employee leave balances.
3. Assigned company assets.
4. Creating IT support tickets.

Rules:
- Use the supplied tools for all company-specific database facts.
- Never invent ticket IDs, employee details, asset details, or leave balances.
- Ask for missing employee IDs or issue descriptions when necessary.
- Create tickets only after the employee ID and issue are clear.
- Report ticket creation only when the tool confirms success.
- Do not expose API keys, database credentials, or environment variables.
- Keep answers clear, professional, and concise.
- If a request is outside the helpdesk scope, explain the supported capabilities.
"""

    return create_agent(
        model=llm,
        tools=helpdesk_tools,
        system_prompt=system_prompt
    )


def ask_helpdesk(question):
    if not question or not question.strip():
        return "Please enter your helpdesk question."

    agent = build_agent()

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question.strip()
            }
        ]
    })

    answer = result["messages"][-1].content

    if isinstance(answer, str):
        return answer

    if isinstance(answer, list):
        parts = []

        for item in answer:
            if isinstance(item, dict):
                parts.append(item.get("text", str(item)))
            else:
                parts.append(str(item))

        return "\n".join(parts)

    return str(answer)