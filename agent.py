import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

hs = Hindsight(
    base_url=os.getenv("HINDSIGHT_URL", "https://api.hindsight.vectorize.io"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)
llm = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-120b"

BASE_SYSTEM = (
    "You are a support agent for CloudDesk, a SaaS product. "
    "Reply in under 120 words. Be specific and actionable. "
    "If you do not know something about the customer, ask one short question."
)

MEMORY_RULES = (
    "\n\nWhat you know about this customer from past interactions:\n{memories}\n"
    "Use this. Never re-ask for information you already have. "
    "If a past fix applies, lead with it and mention it is the same issue as before. "
    "Match the customer's preferred communication style."
)


def bank_for(customer_id):
    return f"cust-{customer_id}"


def ensure_bank(customer_id, name):
    try:
        hs.create_bank(
            bank_id=bank_for(customer_id),
            name=name,
            mission="Remember this customer's history, environment, past issues, fixes that worked, and communication preferences.",
            disposition={"skepticism": 2, "literalism": 3, "empathy": 4},
        )
    except Exception:
        pass


def recall_history(customer_id, message):
    res = hs.recall(
        bank_id=bank_for(customer_id),
        query=message,
        budget="mid",
        max_tokens=2048,
    )
    return [r.text for r in res.results]


def call_llm(system, message):
    for attempt in range(3):
        try:
            resp = llm.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1.5)


def answer(customer_id, message, use_memory=True):
    memories = recall_history(customer_id, message) if use_memory else []
    system = BASE_SYSTEM
    if memories:
        system += MEMORY_RULES.format(memories="\n".join(f"- {m}" for m in memories))
    reply = call_llm(system, message)
    if use_memory:
        hs.retain(
            bank_id=bank_for(customer_id),
            content=f"Customer said: {message}\nSupport agent replied: {reply}",
            context="support conversation",
            timestamp=datetime.now(timezone.utc),
        )
    return reply, memories


def resolve(customer_id, issue, fix):
    hs.retain(
        bank_id=bank_for(customer_id),
        content=f"Outcome: customer confirmed the fix worked. Issue: {issue}\nFix that worked: {fix}",
        context="ticket resolution",
        timestamp=datetime.now(timezone.utc),
    )