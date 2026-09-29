# Customer Support Memory Agent

A support agent for a fictional SaaS product (CloudDesk) that remembers each customer between conversations. It uses [Hindsight](https://github.com/vectorize-io/hindsight) for long-term memory, Groq for generation, and Streamlit for the console.

> **Same agent. Same model. Same message. The difference is memory.**

## The idea

Most support bots start every chat from zero, so customers re-explain their setup, their history, and what already failed. This agent keeps one memory bank per customer and does three things on every message:

```text
customer message → RECALL relevant memories → ANSWER with them in context → RETAIN the exchange
```

Example: in January, Priya's 50,000-row CSV export timed out and switching to chunked export fixed it. Months later she writes:

> My export is failing again with a timeout error.

| Memory OFF | Memory ON |
| --- | --- |
| Generic checklist: retry, check your connection, shrink the date range. | Leads with the chunked-export fix that worked before, says it looks like the same issue, and keeps the reply short and technical, as her profile asks. |

The console has a sidebar toggle so you can send the same message both ways.

## How it works

All of the memory logic lives in `agent.py`.

- **One bank per customer.** Every read and write goes through `bank_for(customer_id)` (`cust-<id>`). There is no code path that recalls without naming a bank, so customer A's history can't appear in customer B's prompt.
- **Recall.** `hs.recall(...)` is queried with the customer's raw message (`budget="mid"`, `max_tokens=2048`). Results are added to the system prompt with rules: never re-ask known information, lead with a past fix that applies, match the customer's communication style.
- **Retain.** Each exchange is stored with `context="support conversation"`.
- **Confirmed outcomes.** "Mark resolved" stores what actually worked with `context="ticket resolution"`. This is a separate write path on purpose: the agent's own replies are guesses, while a resolution is something a human confirmed.
- **Transparency.** Every reply has a "Recalled N memories" expander showing exactly what was retrieved.

## Quick start

**Prerequisites:** Python 3.10+, a [Groq](https://console.groq.com) API key, and a [Hindsight](https://hindsight.vectorize.io/) API key.

```bash
git clone https://github.com/chintalavikas/customer_support_memory_agent.git
cd customer_support_memory_agent
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_API_KEY=your_hindsight_api_key
# Optional: defaults to https://api.hindsight.vectorize.io
# HINDSIGHT_URL=
```

Seed the sample customers, then start the app. **Seeding is required**: without it the banks are empty and memory ON will look identical to memory OFF.

```bash
python seed.py
streamlit run app.py
```

Run `seed.py` once per fresh setup rather than repeatedly.

## Try it

Pick a customer in the sidebar. The sidebar also shows a suggested first message for each.

| Customer | Profile | Suggested message | What memory adds |
| --- | --- | --- | --- |
| Priya Nair | Ops lead, Pro plan, REST API user; prefers short, technical answers | "My export is failing again with a timeout error." | Past chunked-export fix, rate-limit history, and her request for email confirmation on billing fixes |
| Rahul Mehta | Starter plan, iOS app; new to the product | "I can't log in on my phone again, it just keeps looping." | Past Keychain fix and step-by-step instructions with exact menu names |
| Ananya Rao | IT admin, Enterprise with 4-hour SLA, Okta SSO | "New hires aren't showing up in CloudDesk after we add them in Okta." | Past SCIM delay and SSO certificate issue, and her request for proactive status updates |

<img width="958" height="530" alt="Screenshot 2026-09-28 204916" src="https://github.com/user-attachments/assets/691c69f2-64d1-405f-b332-e08d391254ee" />
<img width="959" height="527" alt="Screenshot 2026-09-28 205323" src="https://github.com/user-attachments/assets/58ba9794-f575-41d8-8ef0-fb657c8d150d" />
<img width="958" height="522" alt="Screenshot 2026-09-28 205346" src="https://github.com/user-attachments/assets/3ec1a89d-1e35-4309-bf38-f0c86960c144" />
<img width="209" height="187" alt="Screenshot 2026-09-28 205358" src="https://github.com/user-attachments/assets/c3f81e57-515f-4804-9f4d-b3dfa516195e" />
<img width="957" height="533" alt="Screenshot 2026-09-28 205540" src="https://github.com/user-attachments/assets/e6c6ae7a-acd3-463c-93f3-c878283202f2" />






A good walkthrough:

1. Choose Priya, turn **Use Hindsight memory** off, and send her message. Note the generic answer.
2. Turn memory on, send the same message, and open **Recalled memories** to see what was retrieved.
3. Ask, "I also see a duplicate charge on this month's invoice." The billing history and her confirmation preference should surface.
4. Click **Mark resolved** after a fix works, then later ask, "What have we already tried for my export issue?"

All customer data is synthetic (`seed_data.py`).

## Project layout

```text
agent.py       Recall → answer → retain loop, bank setup, LLM call with retries
app.py         Streamlit console: customer picker, memory toggle, Mark resolved
seed.py        Loads each customer's profile and dated ticket history into memory
seed_data.py   Synthetic customers, tickets, and suggested messages
```

## Limitations

- **Single-turn prompts.** Each LLM call sees the current message plus recalled memories, not the earlier turns of the current chat.
- **Unverified agent replies.** Retained exchanges include the model's own answers. Only "Mark resolved" records a confirmed fix, and the two are not yet weighted differently in the prompt.
- **Broad error handling.** `ensure_bank` swallows all exceptions so setup can be re-run, which can also hide a bad key or unreachable server.
- **No memory maintenance.** There is no expiry or cleanup for outdated memories.
- **No production controls.** Authentication, authorization, audit logging, retention policy, and deletion workflows are out of scope for this repo.
- **No evaluation harness.** The memory toggle allows manual side-by-side comparison only.

## Roadmap

- Shared, organization-level playbook of proven fixes, kept separate from personal customer banks
- Reflection over a customer's history to surface recurring issues and escalation candidates
- Ticketing integrations (Zendesk, Freshdesk, Jira Service Management)
- Human escalation when the same issue repeats after previous fixes failed

## Built with

Python, [Streamlit](https://streamlit.io), [Groq](https://groq.com) (`openai/gpt-oss-120b`), and [Hindsight](https://hindsight.vectorize.io/) by Vectorize. See also [what agent memory is](https://vectorize.io/what-is-agent-memory).

Built for HackWithHyderabad 3.0 by [Vikas Chinthala](https://github.com/chintalavikas).

## License

No license file has been added yet. Add one (MIT is a common choice) before inviting outside use.
