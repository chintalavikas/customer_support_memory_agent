# 🧠 Customer Support Memory Agent

### AI-powered customer support that remembers the customer.

A personalized customer-support agent for **CloudDesk** that uses **Hindsight long-term memory** to recall previous issues, successful fixes, customer preferences, and confirmed outcomes.

Instead of starting every conversation from zero, the agent can use relevant customer history to provide more personalized and context-aware support.

> **Recall → Answer → Retain**

---

## 🚀 Why This Project?

Traditional AI customer-support agents often treat every conversation as a new interaction.

Customers may have to repeatedly explain:

* Who they are
* What problem they are facing
* What they already tried
* Which solution worked previously
* How they prefer to receive support

Our goal is to make the support experience more personalized by giving the AI **persistent, customer-specific memory**.

---

# 💡 Our Solution

The **Customer Support Memory Agent** retrieves relevant memories about the active customer before generating a response.

For example, Priya previously experienced an export timeout in January. A chunked-export solution fixed the issue.

Months later, she says:

> **"My export is failing again with a timeout error."**

Instead of giving completely generic troubleshooting, the agent can recall her previous issue and the successful solution.

The system follows three main steps:

```text
                 ┌──────────────────┐
                 │  Customer Message│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │      RECALL      │
                 │                  │
                 │ Retrieve relevant│
                 │ customer memories│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │      ANSWER      │
                 │                  │
                 │ LLM + current    │
                 │ message + memory │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     RETAIN       │
                 │                  │
                 │ Save new useful  │
                 │ interaction      │
                 └──────────────────┘
```

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      CUSTOMER       │
                         │                     │
                         │ Priya / Rahul /     │
                         │       Ananya        │
                         └──────────┬──────────┘
                                    │
                                    │ Message
                                    ▼
                         ┌─────────────────────┐
                         │    STREAMLIT APP    │
                         │      app.py         │
                         │                     │
                         │ Customer selection  │
                         │ Chat interface      │
                         │ Memory controls     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     AGENT LOGIC     │
                         │      agent.py       │
                         └──────────┬──────────┘
                                    │
                          ┌─────────┴─────────┐
                          │                   │
                          ▼                   ▼
                 ┌─────────────────┐  ┌─────────────────┐
                 │    HINDSIGHT    │  │ CURRENT MESSAGE │
                 │  MEMORY SYSTEM  │  │                 │
                 │                 │  │ User's question │
                 │    recall()     │  │                 │
                 └────────┬────────┘  └────────┬────────┘
                          │                    │
                          │ Relevant memories │
                          └─────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │      GROQ LLM       │
                         │                     │
                         │ Current message +   │
                         │ relevant memories  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  PERSONALIZED AI    │
                         │      RESPONSE       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     HINDSIGHT       │
                         │      retain()       │
                         │                     │
                         │ Store new useful    │
                         │ interaction/memory  │
                         └─────────────────────┘
```

---

# 🧠 How Hindsight Memory Works

Hindsight acts as the **long-term memory layer** for the support agent.

At the application level, the system primarily uses two memory operations:

### `recall`

The agent asks:

> "What do I already know about this customer that is relevant to their current message?"

Hindsight retrieves relevant memories.

### `retain`

After the interaction, useful information can be stored so that it can be available in future conversations.

Therefore:

```text
New message
     ↓
   recall
     ↓
Relevant memories
     ↓
Groq LLM
     ↓
Personalized response
     ↓
  retain
     ↓
Updated memory
```

---

# 👥 Customer-Specific Memory

Each customer has their own history and preferences.

## 👩 Priya Nair

Example memories:

* Previous export timeout
* Chunked export solution
* Duplicate billing charge
* Billing confirmation preference
* Nightly synchronization issue
* 429 error troubleshooting

When Priya reports a similar issue, the agent can retrieve relevant information from her history.

---

## 👨 Rahul Mehta

Example memories:

* Mobile login problem
* Keychain-related fix
* Preference for step-by-step instructions

The agent can use this information to make its response more suitable for Rahul.

---

## 👩 Ananya Rao

Example memories:

* Okta → CloudDesk SCIM synchronization delay
* SSO certificate issue
* Preference for regular status updates

The same AI agent can therefore behave differently depending on the customer and their history.

---

# 🔥 Memory OFF vs Memory ON

One of the main demonstrations of this project is comparing the agent with and without memory.

## Without Memory

Customer:

**Priya Nair**

Message:

```text
My export is failing again with a timeout error.
```

Without customer memory, the agent does not have access to Priya's previous export issue.

The response can therefore be generic troubleshooting.

---

## With Memory

Now enable memory and send the **exact same message**:

```text
My export is failing again with a timeout error.
```

The agent can recall Priya's previous export issue and the successful chunked-export solution.

The response can therefore be more personalized and relevant.

### The key idea:

> **Same agent. Same model. Same question. The difference is memory.**

---

# 🔍 Recalled Memories

The application provides a **Recalled Memories** section so the user can inspect the information retrieved for a response.

This provides transparency into why the agent was able to personalize its answer.

Example flow:

```text
Customer message
       ↓
Relevant memories retrieved
       ↓
Memories provided as context
       ↓
LLM generates response
```

---

# 📈 Learning Through Confirmed Outcomes

The system does not retrain the language model.

Instead, it improves future support interactions by retaining useful information from previous conversations.

For example:

```text
Customer:
"Export is timing out again."

        ↓

Agent:
"Try the chunked export solution."

        ↓

Customer:
"The fix worked."

        ↓

Mark as resolved

        ↓

Confirmed outcome becomes useful
for future conversations
```

Later, the customer can ask:

```text
What have we already tried for my export issue?
```

The agent can retrieve the previous interaction and confirmed outcome from memory.

---

# ✨ Key Features

* 🧠 **Long-term customer memory**
* 🔍 **Relevant memory retrieval**
* 👤 **Customer-specific memory**
* 🎯 **Personalized responses**
* 🛠️ **Previous solution recall**
* 💬 **Context-aware conversations**
* ✅ **Confirmed outcome tracking**
* 🔄 **Memory retention after interactions**
* 👥 **Customer-specific preferences**
* 🔎 **Recalled Memories transparency**
* ⚡ **Interactive Streamlit interface**

---

# 🎬 Demo Walkthrough

The recommended demonstration follows this flow.

### 1. Select Priya Nair

Turn **Hindsight memory OFF**.

Send:

```text
My export is failing again with a timeout error.
```

Observe the generic response.

---

### 2. Enable Hindsight Memory

Turn memory **ON**.

Send the exact same message:

```text
My export is failing again with a timeout error.
```

The agent can now retrieve Priya's previous export-related memory.

Open the **Recalled Memories** section to show the retrieved context.

---

### 3. Show another memory

Ask Priya:

```text
I also see a duplicate charge on this month's invoice.
```

The agent can recall the previous duplicate-charge issue and relevant billing preference.

---

### 4. Show customer personalization

Switch to Rahul and ask:

```text
I can't log in on my phone again, it just keeps looping.
```

The agent can use Rahul's previous mobile-login history and communication preference.

---

### 5. Show confirmed learning

With Priya:

```text
Export is timing out again.
```

Confirm that the solution worked and use **Mark Resolved**.

Later ask:

```text
What have we already tried for my export issue?
```

The agent can retrieve the previous interaction and confirmed outcome.

---

# 🛠️ Technology Stack

| Technology                 | Purpose                                    |
| -------------------------- | ------------------------------------------ |
| **Python**                 | Application and agent logic                |
| **Streamlit**              | Interactive user interface                 |
| **Groq**                   | Large language model / response generation |
| **Hindsight by Vectorize** | Long-term memory, recall and retention     |
| **Git / GitHub**           | Version control and source code            |

---

# 📂 Project Structure

```text
customer_support_memory_agent/
│
├── app.py
│       └── Streamlit application and user interface
│
├── agent.py
│       └── Customer-support agent and memory orchestration
│
├── seed_data.py
│       └── Synthetic customer profiles and historical data
│
├── seed.py
│       └── Loads initial customer information into memory
│
├── requirements.txt
│       └── Python dependencies
│
├── .gitignore
│       └── Files and secrets excluded from Git
│
└── README.md
        └── Project documentation
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/chintalavikas/customer_support_memory_agent.git
```

## 2. Enter the project directory

```bash
cd customer_support_memory_agent
```

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If your system uses the `py` launcher:

```bash
py -m pip install -r requirements.txt
```

---

# 🔐 Environment Variables

API keys and other secrets should **never be committed to GitHub**.

Store required credentials in environment variables or a local `.env` file according to the application's configuration.

Example:

```text
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_API_KEY=your_hindsight_api_key
```

> Never replace the placeholder values with real API keys inside this README.

Make sure `.env` is included in `.gitignore`.

---

# ▶️ Run the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Then open the local URL provided by Streamlit in your browser.

---

# 🌱 Initial Customer Data

The project includes synthetic customer data for demonstration.

The seed process prepares customer profiles and previous support interactions so that the memory system has useful history before the demo begins.

Example customers include:

* Priya Nair
* Rahul Mehta
* Ananya Rao

> **The customer data is fictional and does not represent real users.**

---

# 🔒 Privacy & Data

This project uses **synthetic customer data** created specifically for demonstration and hackathon purposes.

No real customer information is required for the demo.

In a production deployment, additional controls would be required for:

* Authentication
* Authorization
* Data encryption
* Memory isolation
* Data retention
* Memory deletion
* Audit logging
* Sensitive information handling

---

# ⚠️ Current Limitations

The current prototype has several limitations:

* Customer data is synthetic.
* Generated responses may occasionally be incorrect.
* The quality of future responses depends on the quality of retained memories.
* Outdated memories may require cleanup or expiration.
* Production deployments would require stronger security and data-governance controls.
* Human review would be useful for sensitive or unresolved support cases.

---

# 🚀 Future Scope

## 🌐 Shared Support Knowledge

Create a separate organization-wide support memory/playbook.

For example:

```text
Customer A
    │
    └── Export timeout
             │
             └── Chunked export worked
                         │
                         ▼
                 Shared Support Playbook
                         │
                         ▼
Customer B → Same problem → Proven solution
```

This would allow successful troubleshooting knowledge to help new customers while keeping personal customer memories isolated.

---

## 🔮 Customer Insights

Use memory reflection capabilities to identify:

* Recurring customer issues
* Frequently successful solutions
* Communication preferences
* Repeated unresolved problems
* Potential escalation cases

---

## 🎫 Ticketing System Integration

Future versions could connect with real customer-support platforms such as:

* Zendesk
* Freshdesk
* Jira Service Management

This would allow the agent to retrieve and update real support tickets.

---

## 👨‍💼 Human Escalation

Repeated unresolved problems could trigger human-support escalation.

```text
Repeated issue
      +
Previous fixes unsuccessful
      ↓
Escalation recommendation
      ↓
Human support agent
```

---

# 🎯 Design Philosophy

The goal is not to replace human support agents.

The goal is to give an AI support agent **useful long-term memory** so that customers do not have to repeatedly explain the same problems.

> **Don't make the customer repeat what the AI should remember.**

---

# 🏆 HackWithHyderabad 3.0

This project was developed for **HackWithHyderabad 3.0** to demonstrate how persistent AI memory can improve customer-support experiences.

### Core Concept

```text
Traditional Support AI

Customer → Question → AI → Answer
                         ↓
                    Starts over


Memory-Enabled Support AI

Customer → Question
              ↓
        Recall History
              ↓
        Relevant Context
              ↓
             LLM
              ↓
     Personalized Answer
              ↓
        Retain Interaction
```

---

# 👨‍💻 Author

**Vikas Chinthala**

GitHub: [@chintalavikas](https://github.com/chintalavikas)

---

## ⭐ Project Highlights

**Persistent Memory**
The agent can recall relevant customer history instead of starting every interaction from zero.

**Personalization**
Different customers can receive responses based on their individual history and preferences.

**Transparent Retrieval**
The Recalled Memories section makes the retrieved context visible during the demonstration.

**Continuous Memory**
New interactions and confirmed outcomes can become part of future customer context.

---

## 📜 License

This project is intended for educational and hackathon demonstration purposes.
