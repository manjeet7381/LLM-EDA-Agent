from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_react_agent, AgentExecutor
from dotenv import load_dotenv
from .tools import load_and_profile_csv, clean_data, generate_eda_summary

load_dotenv()

llm = ChatOllama(model="llama3.2", temperature=0.0, num_ctx=8192)

tools = [load_and_profile_csv, clean_data, generate_eda_summary]

prompt_template = """You are an expert Data Analyst and Cleaning Agent.

You have access to the following tools:

{tools}

Use the following format exactly:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat if needed)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""

prompt = ChatPromptTemplate.from_template(prompt_template)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True, 
    max_iterations=25
)

def run_eda_pipeline(csv_path: str):
    agent_result = agent_executor.invoke({
        "input": f"""Process the file: {csv_path}. 
        Step 1: Profile the data using load_and_profile_csv.
        Step 2: Clean the data using clean_data.
        Step 3: Return a factual summary based ONLY on the actual columns and values in this cafe sales dataset.
        Do NOT invent information about customer age, time of day patterns, promotions, or anything not present in the data."""
    })
    
    # Generate factual summary
    rich_summary_prompt = f"""
    You are a senior data analyst. Write a **factual** professional EDA summary using ONLY the information below.

    Agent Output:
    {agent_result['output']}

    Write in this exact structure:
    1. Executive Summary
    2. Key Data Quality Issues Found & Fixed
    3. Important Insights (use real column names and numbers only)
    4. Recommendations

    Be concise and strictly factual. Do not hallucinate new information.
    """

    rich_summary = llm.invoke(rich_summary_prompt)
    
    return f"{agent_result['output']}\n\n📋 PROFESSIONAL EDA SUMMARY:\n{rich_summary.content}"