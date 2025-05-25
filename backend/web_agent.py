from typing import Literal, Annotated
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver

from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from backend.llm_providers_helpers import get_chat_model
from langchain_core.tools import tool
from backend.llm_agent_credentials import AgentCredentials
from backend.llm_prompts import internet_llm_agent_prompt

@tool
def get_weather(location: str) -> str:
    """
    Dummy function to simulate a weather API call.
    :param location: Location for which to get the weather.
    :return: Weather information as a string.
    """
    return f"The weather in {location} is sunny with a high of 25°C."

tools = [get_weather]
tool_node = ToolNode(tools)


class CustomGraphState(TypedDict):
    """
    The state of this graph, which for now only has the list of messages to enable a history of the conversation
    and also allow the LLM to use the outputs of the tools.
    """
    messages: Annotated[list, add_messages]


def should_continue(state: CustomGraphState) -> Literal["tools", "__end__"]:
    """
    Function to decide whether to finish the graph flow if the LLM gave a text answer, or call the ToolNode if it
    replied with a tool.
    :param state:
    :return:
    """
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"

    return "__end__"


def call_model(state: CustomGraphState, model):
    """
    Call the Agent node to decide what to do next or answer the user's question
    :param state: Current state of the graph
    :param model: The LLM model to use for this agent.
    :return: Next decision of the graph
    """
    messages = state["messages"]
    print(messages)
    if len(messages) == 1:
        messages = [
                       SystemMessage(
                           content=internet_llm_agent_prompt)
                   ] + messages
    try:
        response = model.invoke(messages)
    except Exception as e:
        print("error", e)
        return {"messages": [AIMessage(content="Error occurred because token limit has been reached (Token limit"
                                               "is only 8k tokens for free GitHub LLM API usage). Please switch the"
                                               "LLM provider to avoid this error.")]}

    # Gemini does not support passing multiple system messages.
    if "safety_ratings" in response.response_metadata:
        return {"messages": [HumanMessage(
        content=internet_llm_agent_prompt),
        response]}

    print("no safety ratings")
    return {"messages": [SystemMessage(
        content=internet_llm_agent_prompt),
        response]}


def get_agent(agent_llm_credentials: AgentCredentials):

    if not agent_llm_credentials.has_any_valid_credentials():
        raise Exception("LLM Agent credentials are invalid, please check again.")

    # Get right model based on given configuration
    model = get_chat_model(agent_llm_credentials=agent_llm_credentials).bind_tools(tools)

    # Create flow with messages
    workflow = StateGraph(CustomGraphState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", lambda state: call_model(state, model))
    workflow.add_node("tools", tool_node)

    # Graph starts with the agent
    workflow.add_edge("__start__", "agent")
    # Based on agent output decide next node
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    # Always go back from tools to agent node
    workflow.add_edge("tools", "agent")

    memory = InMemorySaver()

    app = workflow.compile(checkpointer=memory)

    return app
