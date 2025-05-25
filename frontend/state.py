import asyncio
import reflex as rx
import os

from dotenv import load_dotenv

from backend.web_agent import get_agent
from backend.llm_agent_credentials import AgentCredentials
from langchain_core.messages import HumanMessage

# Ideally should move this to a helper class or something but for now we can keep it simple here
load_dotenv("frontend/.env")

agent_credentials = AgentCredentials()
agent_credentials.openai_key = os.getenv("OPENAI_KEY")
agent_credentials.openai_model = "gpt-4o"

agent_pool = {}

class SettingsState(rx.State):
    # The accent color for the app
    color: str = "violet"

    # The font family for the app
    font_family: str = "Poppins"


class State(rx.State):
    # The current question being asked.
    question: str

    # Whether the app is processing a question.
    processing: bool = False

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    agent_id: str = ""


    def on_load(self):
        # Get unique tab identifier
        tab_id = self.router.session.client_token

        self.agent_id = tab_id

        print(f"New tab connected: {tab_id}")

    def set_question(self, question: str):
        if question != "Enter":
            self.question = question

    async def answer(self):

        self.chat_history.append((self.question, ""))
        yield

        # Set the processing state to True.
        self.processing = True
        yield

        # Clear the question input.
        question = self.question
        self.question = ""

        # Yield here to clear the frontend input before continuing.
        yield

        print(agent_pool)
        print(self.agent_id, "agent id")

        agent = agent_pool.get(self.agent_id, None)
        print(agent)
        if not agent:
            print("in agent not found")
            # Create a new agent if it doesn't exist in the pool.
            agent = get_agent(agent_llm_credentials=agent_credentials)
            print("in agent not found, created new agent",agent)
            agent_pool[self.agent_id] = agent

        # self.stream(agent = agent, inputs = {"messages": [HumanMessage(content=question)]}, config = {"configurable": {"thread_id": "1"}}, stream_mode=["messages", "updates"] )
        yield

        async for _ in self.stream(
                agent=agent,
                inputs={"messages": [HumanMessage(content=question)]},
                config={"configurable": {"thread_id": "1"}},
                stream_mode=["messages", "updates"]
        ):
            yield

        # agent_respose = agent.astream(input = {"messages": [HumanMessage(content=question)]}, config = {"configurable": {"thread_id": "1"}}, stream_mode=["messages", "updates"])
        #
        # answer = agent_respose["messages"][-1].content
        #
        # for i in range(len(answer)):
        #     # Pause to show the streaming effect.
        #     await asyncio.sleep(0.0155)
        #     # Add one letter at a time to the output.
        #     self.chat_history[-1] = (
        #         self.chat_history[-1][0],
        #         answer[: i + 1],
        #     )
        #     yield

        yield

        # Set the processing state to False.
        self.processing = False

    async def stream(self, agent, inputs, stream_mode, config=None):
        async for agent_update in agent.astream(
                inputs, stream_mode=stream_mode, config=config
        ):
            # If we only stream updates, then LangGraph doesn't return a tuple so we force it to be one
            if stream_mode == "updates":
                update_type, update_info = "updates", agent_update
            # If we stream both updates and messages, then LangGraph returns a tuple so we unpack it
            else:
                update_type, update_info = agent_update

            if update_type == "updates":
                for node, values in update_info.items():
                    # If we are only streaming updates, then we only care about the last message
                    if stream_mode == "updates":
                        final_response = values["messages"][-1].content

                    if node == "agent":

                        for agent_message in values["messages"]:
                            if (
                                    agent_message.additional_kwargs
                                    and "tool_calls" in agent_message.additional_kwargs
                                    and agent_message.additional_kwargs["tool_calls"]
                            ):
                                print("Agent decided to call tools 🛠️")
                                # st.markdown(
                                #     "Agent decided to call the following tools 🛠️"
                                # )
                                # for tool_call in agent_message.additional_kwargs[
                                #     "tool_calls"
                                # ]:
                                #     st.markdown(
                                #         f"🛠️*{tool_call['function']['name']}*:"
                                #         f" Arguments: {tool_call['function']['arguments']}"
                                #     )
                            else:
                                # st.markdown("Agent finalized running 🤖")
                                print("Agent finalized running 🤖")
                    else:
                        for tool_message in values["messages"]:
                            if tool_message.content.startswith("Error"):
                                # st.markdown(
                                #     f"""Error running '{tool_message.name}' 🛠️"""
                                # )
                                print(f"Error running '{tool_message.name}' 🛠️")
                        # st.markdown("Tools finalized running 🛠️")
                        # updates.append((node, values))
            elif update_type == "messages" and update_info[1]["langgraph_node"] == "agent":
                print(update_info[0].content)
                # Stream the agent message chunks if it's a final answer and not a tool call
                if update_info[0].content != "" and "You are an useful AI assistant" not in update_info[0].content:

                    self.chat_history[-1] = (
                        self.chat_history[-1][0],
                        self.chat_history[-1][1] + update_info[0].content,
                    )
                    yield


    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False

    def reset_chats(self):
        self.clear_chat()
        global agent_pool
        agent_pool = {}

        yield




