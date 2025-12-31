# ================================
# Agentic Text-to-SQL Implementation
# ================================

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("GROK_API_KEY")

# ================================
# Database Setup
# ================================

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///ComicStore.db")

# ================================
# LLM Configuration (Groq + LLaMA)
# ================================

from langchain_openai import ChatOpenAI

chatgpt = ChatOpenAI(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0,
    openai_api_key=OPENAI_KEY,
    openai_api_base="https://api.groq.com/openai/v1"
)

# ================================
# SQL Toolkit
# ================================

from langchain_community.agent_toolkits import SQLDatabaseToolkit

sql_toolkit = SQLDatabaseToolkit(db=db, llm=chatgpt)
sql_tools = sql_toolkit.get_tools()

# ================================
# System Prompt
# ================================

from langchain_core.messages import SystemMessage, HumanMessage

SQL_PREFIX = r"""
You are an agent designed to interact with a SQL database in SQLite.
Given an input question, create a syntactically correct SQLite query to run,
then look at the results of the query and return the answer.

Unless the user specifies a specific number of examples they wish to obtain,
always limit your query to at most 10 results.

You can order the results by a relevant column to return the most interesting examples.

Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

Make sure you generate a correct SQLite query as plain text without any formatting
or code blocks. Do not include sql or similar markers.
Do not try to explain the query, just provide the query as-is, like this:
SELECT ...

You have access to tools for interacting with the database.
Only use the below tools.
Only use the information returned by the below tools to construct your final answer.

You MUST double check your query before executing it.
If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
to the database even if the user asks.

To start you should ALWAYS look at the tables in the database
to see what you can query.
Then you should query the schema of the most relevant tables.

Do NOT skip this step.

When generating the final answer in markdown from the results,
if there are special characters in the text, such as the dollar symbol,
ensure they are escaped properly for correct rendering
e.g $25.5 should become \\$25.5
"""

SYS_PROMPT = SystemMessage(content=SQL_PREFIX)

# ================================
# Agent Creation (ReAct)
# ================================

from langgraph.prebuilt import create_react_agent

text2sql_agent = create_react_agent(
    model=chatgpt,
    tools=sql_tools
)

# ================================
# Agent Invocation Function
# ================================

def call_text2sql_agent(query: str, verbose: bool = False):
    """
    Executes the Text-to-SQL agent.

    Returns:
        final_response (str)
        reasoning (list[str])
    """

    final_response = None
    reasoning = []

    for event in text2sql_agent.stream(
        {
            "messages": [
                SYS_PROMPT,
                HumanMessage(content=query)
            ]
        },
        stream_mode="values"
    ):
        msg = event["messages"][-1]

        # Capture reasoning
        if verbose:
            reasoning.append(f"**{msg.type.upper()}**:\n{msg.content}")

        final_response = msg.content

    return final_response, reasoning

# ================================
# Local Test
# ================================

if __name__ == "__main__":
    res = call_text2sql_agent(
        "What are the top 5 customers with most comics purchased?",
        verbose=True
    )
    print("\nFinal Response:\n")
    print(res)
