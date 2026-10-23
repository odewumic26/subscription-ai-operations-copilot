
import requests

MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_support_recommendation(alert_type):

    instructions = {
        "Pending Review": (
            "A subscription is marked Pending. "
            "Suggest how a support team should verify "
            "its status and decide on follow-up."
        ),
        "Upcoming Billing": (
            "An active subscription has a billing date "
            "within the next seven days. "
            "Suggest a proactive billing reminder."
        ),
        "Past Billing Date": (
            "An active subscription has a billing date "
            "in the past. This does NOT prove payment "
            "failure. Suggest appropriate verification."
        )
    }

    if alert_type not in instructions:
        raise ValueError("Unsupported alert type.")

    prompt = f"""
You are a customer support operations assistant
working with a fictional subscription business.

Situation:
{instructions[alert_type]}

Provide:
1. Recommended support action
2. A short draft customer message
3. An internal follow-up step

Rules:
- Do not invent payment failures.
- Do not invent customer details.
- Do not claim actions have been completed.
- Do not include personal information.
- Keep the response concise and professional.
- Clearly label the customer message as a draft.
- Treat alert categories as indicators for review, not confirmed problems.
- Never assume a payment failed or that verification is required.
- Do not claim a customer has been contacted.
- Do not promise follow-up unless a human has approved it.
- Recommend checking internal records before changing account status.
- All customer messages are drafts requiring human approval.

"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()["response"].strip()
