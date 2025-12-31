import streamlit as st
from agent import call_text2sql_agent

st.set_page_config(
    page_title="🧠 Text-to-SQL Agent Demo",
    page_icon="🗄️",
    layout="centered"
)

st.title("🧠 Text-to-SQL using Agentic AI")
st.markdown(
    """
    Ask natural language questions and let the **Agentic AI** query the
    **ComicStore SQLite database** for you.
    """
)

# User input
query = st.text_input(
    "Enter your question:",
    placeholder="e.g. What are the top 5 customers with most comics purchased?"
)

col1, col2 = st.columns([1, 3])
with col1:
    run = st.button("Run Query 🚀")

with col2:
    verbose = st.checkbox("Show Agent Reasoning")

# Run agent
if run:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Agent is thinking... 🤖"):
            try:
                response, reasoning = call_text2sql_agent(
                    query=query,
                    verbose=verbose
                )

                st.subheader("📊 Final Answer")
                st.markdown(response)

                if verbose and reasoning:
                    st.subheader("🧠 Agent Reasoning")
                    for step in reasoning:
                        st.markdown(step)
                        st.markdown("---")

            except Exception as e:
                st.error("Something went wrong while running the agent.")
                st.exception(e)
