# Building Customer Support memory agent AI That Remembers With Hindsight

The most expensive sentence in customer support is "Can you tell me what you've already tried?" I built a support agent whose job is to never say it to someone who has already told us.

## What the system does

The agent answers support questions for a SaaS product (I'll call it CloudDesk). It's a small Python service: a Streamlit console for support staff, a Groq-hosted LLM for generation, and [Hindsight](https://github.com/vectorize-io/hindsight), an open-source agent memory system, for everything the agent needs to remember between conversations.

The whole request path is three verbs: **recall, answer, retain**.

1. A customer message arrives.
2. I recall memories from that customer's history that are relevant to the message.
3. Those memories go into the system prompt, and the model answers.
4. The exchange is written back to memory.

There is a fourth step, which turned out to matter more than the other three: when a ticket is marked resolved, I write down what *actually* fixed it. More on that below.

The codebase is deliberately small. `agent.py` is under 100 lines and holds the entire memory loop. `app.py` is the console. `seed.py` loads a customer's profile and ticket history into memory when we onboard them. Almost all of the interesting decisions are in how memory is scoped and what gets written to it.

## The through-line: memory is a data-modeling problem

When I started, I assumed the hard part would be retrieval quality. It wasn't. The hard part was deciding what a "memory" is and who it belongs to. Two decisions shaped everything.

### Decision 1: one bank per customer

Support data is full of things that must not leak across customers: environments, plan tiers, ticket contents, and complaints about our own product. A single shared vector index with a `customer_id` metadata filter would work, but it makes isolation a query-time discipline. One forgotten filter and customer A's context appears in customer B's prompt.

Hindsight has a first-class concept of a memory *bank*, so I made isolation structural instead:

```python
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
```

Every read and write goes through `bank_for`. There is no code path that recalls without naming a bank, so there is no filter to forget. This is the property I care about most, and it costs one line.

The `mission` string is worth a comment. It tells the memory layer what to pay attention to when it extracts facts from raw text: environment, past fixes, communication preferences. That is a very different mission from, say, a coding assistant's. I found that writing the mission down forced me to decide what "useful to remember" means for this domain, which I had been hand-waving.

The `disposition` values are a softer knob. I set empathy high and skepticism low, because a support memory that second-guesses a customer's account of their own problem is worse than useless. I'd treat those numbers as tuning parameters, not settings I've proven optimal.

### Decision 2: retain outcomes, not just conversations

The naive version of this agent retains every exchange. Mine does that too:

```python
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
```

The problem is in the retained text: `Support agent replied: {reply}`. That is a claim by a language model, not a fact. If the agent suggests a wrong fix and I store it, the next recall may surface that wrong fix as "history," and the agent will cheerfully lead with it. I've watched a memory system launder its own guesses into ground truth, and it's a quiet, compounding failure.

So there is a second write path, gated on a human action:

```python
def resolve(customer_id, issue, fix):
    hs.retain(
        bank_id=bank_for(customer_id),
        content=f"Outcome: customer confirmed the fix worked. Issue: {issue}\nFix that worked: {fix}",
        context="ticket resolution",
        timestamp=datetime.now(timezone.utc),
    )
```

The wording is intentional. "Outcome: customer confirmed the fix worked" is a distinct kind of statement from "agent replied." When both are in the bank, recall can tell a suggestion from a verified resolution, and the prompt can weight them accordingly. In the console this is a single "Mark resolved" button that only appears when there's a conversation to resolve. In production it's driven by the ticket closing with a confirmation from the customer.

The `context` field (`"support conversation"` versus `"ticket resolution"`) gives me a cheap provenance label on every memory. I did not appreciate how useful that would be until I was debugging a bad answer and could immediately see which class of memory had produced it.

## How recall gets used

Retrieval is one call:

```python
def recall_history(customer_id, message):
    res = hs.recall(
        bank_id=bank_for(customer_id),
        query=message,
        budget="mid",
        max_tokens=2048,
    )
    return [r.text for r in res.results]
```

I query with the customer's raw message. I considered rewriting it into a search query with an LLM first and decided against it: an extra model call on the critical path for a support reply is latency I'd rather spend elsewhere, and the raw message has been good enough. The `budget="mid"` and `max_tokens=2048` are what keep recalled context from crowding out the actual conversation. Support replies are capped at 120 words in the system prompt, so a 2,000-token wall of history would be out of proportion to the answer.

The recalled memories become bullets in the system prompt, wrapped in rules that tell the model how to behave:

```python
MEMORY_RULES = (
    "\n\nWhat you know about this customer from past interactions:\n{memories}\n"
    "Use this. Never re-ask for information you already have. "
    "If a past fix applies, lead with it and mention it is the same issue as before. "
    "Match the customer's preferred communication style."
)
```

"Lead with it and mention it is the same issue as before" is the line that changes the feel of a reply. It gives the customer evidence that we have a record, and it gives the support engineer reviewing the transcript something to check.

The console shows the recalled memories in an expander under every reply. That was originally a debugging aid. It became the feature I'd defend hardest, because it turns "why did the agent say that?" from a guess into a lookup.

## What it looks like in practice

The clearest case is a customer I'll call Priya, an operations lead who uses our REST API and, per her profile, dislikes generic troubleshooting. Months earlier a CSV export of roughly 50,000 rows had timed out, and switching the export mode to chunked fixed it. She had also noted, with some irritation, that it was the second time that quarter.

She writes: *"My export is failing again with a timeout error."*

Without memory, the agent has a timeout and nothing else. The best it can do is the standard checklist: retry, check your connection, try a smaller date range. That is exactly the advice she has said she doesn't want.

With memory, recall returns the earlier ticket and the profile, and the reply can open with the fix that worked last time (Settings > Data > Export mode > chunked), say it looks like the same issue, and keep to the short, technical register her profile asks for. If she confirms it works again, "Mark resolved" reinforces the record.

The same mechanism handles very different customers. A new user on a phone who prefers step-by-step instructions with exact menu names gets a different reply shape for a similar-sounding problem. An enterprise admin whose past outage came close to an SLA gets a reply that offers proactive status updates. The model is the same and the prompt is the same. The difference is what's in the bank.

The console has a sidebar toggle that turns memory off for a conversation, and I lean on it constantly. Sending the same customer message with memory on and off is the fastest way I know to see what the memory layer is contributing. I haven't built a formal evaluation harness on top of it; what I have is a side-by-side comparison, and I'd rather say that than dress it up.

## What was painful

**Swallowed exceptions.** `ensure_bank` catches everything because bank creation is idempotent in spirit and I wanted onboarding to be re-runnable. But a bare `except Exception: pass` will also hide a bad API key or an unreachable server. I've been narrowing it to the "already exists" case so that real failures surface.

**The LLM call needs retries.** `call_llm` retries three times with a short sleep. That's crude, but the provider does fail transiently, and a support reply that errors out is worse than one that takes an extra second and a half.

**Seeding history is easy to get subtly wrong.** When importing past tickets I pass the original ticket date as the `timestamp`. If you forget and let it default to "now," every historical ticket looks like it happened today, and any reasoning about recency is quietly broken.

## Lessons learned

1. **Make isolation structural, not procedural.** One memory bank per customer means a cross-customer leak requires writing new code, not forgetting a filter.

2. **Never let the model write its own ground truth.** Store what the agent said and what a human confirmed as different kinds of memory, and label them so retrieval can tell them apart.

3. **Write the memory mission down.** Deciding what the system should remember about a customer forced clearer thinking than any amount of tuning retrieval parameters.

4. **Show the recalled context to humans.** An expander listing recalled memories costs almost nothing and makes the system auditable, which is what lets support staff trust it.

5. **Keep a memory on/off switch.** Not as a product feature, but as a debugging tool. The comparison tells you what memory is buying you, and whether it's buying anything.

## Where to go next

If you want to try this pattern yourself, the [Hindsight docs](https://hindsight.vectorize.io/) cover banks, `retain`, and `recall` in more detail than I have here, and Vectorize has a useful overview of [what agent memory is and how it differs from plain RAG](https://vectorize.io/what-is-agent-memory). The [Hindsight repository on GitHub](https://github.com/vectorize-io/hindsight) is open source, so you can read how retention and recall actually work before committing to it.

The core of my implementation fits on one screen. I think that's the real argument for treating agent memory as a dedicated layer: the interesting work moves out of glue code and into deciding what deserves to be remembered.
