from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from prompt import prompt
from tools import tools

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

llm_with_tools = model.bind_tools(tools)

def create_agent_with_memory(memory: ConversationBufferWindowMemory) -> AgentExecutor:
    """Create an agent executor with memory"""
    agent = create_tool_calling_agent(
        llm=llm_with_tools,
        prompt=prompt,
        tools=tools,
    )
    
    return AgentExecutor.from_agent_and_tools(
        agent=agent, 
        tools=tools, 
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

agent = create_tool_calling_agent(
    llm=llm_with_tools,
    prompt=prompt,
    tools=tools,
)

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    response = agent_executor.invoke({"text": "which is the best crop to sow in rajasthan in the month of july?"})
    print(response["output"])