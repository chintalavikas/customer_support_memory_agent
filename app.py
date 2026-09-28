import streamlit as st
from agent import answer, resolve
from seed_data import CUSTOMERS

st.set_page_config(page_title="CloudDesk Support Agent")
st.title("CloudDesk support agent")
st.caption("Memory by Hindsight. One memory bank per customer.")

cid = st.sidebar.selectbox(
    "Customer", list(CUSTOMERS), format_func=lambda k: CUSTOMERS[k]["name"]
)
use_memory = st.sidebar.toggle("Use Hindsight memory", value=True)
st.sidebar.write("Try: " + CUSTOMERS[cid]["demo_message"])

key = f"chat-{cid}"
if key not in st.session_state:
    st.session_state[key] = []
hist = st.session_state[key]

for m in hist:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("memories"):
            with st.expander(f"Recalled {len(m['memories'])} memories"):
                for x in m["memories"]:
                    st.write("- " + x)

msg = st.chat_input("Type as the customer...")
if msg:
    hist.append({"role": "user", "content": msg})
    with st.spinner("Thinking..."):
        reply, mems = answer(cid, msg, use_memory)
    hist.append({"role": "assistant", "content": reply, "memories": mems})
    st.rerun()

if hist and use_memory and st.sidebar.button("Mark resolved"):
    users = [m["content"] for m in hist if m["role"] == "user"]
    bots = [m["content"] for m in hist if m["role"] == "assistant"]
    if users and bots:
        resolve(cid, users[-1], bots[-1])
        st.sidebar.success("Outcome saved to memory")