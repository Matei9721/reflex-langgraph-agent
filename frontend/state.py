import asyncio
import uuid
import reflex as rx


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

    user_id: str = str(uuid.uuid4())

    def set_question(self, question: str):
        if question != "Enter":
            self.question = question

    async def answer(self):
        # Set the processing state to True.
        self.processing = True
        yield

        # convert chat history to a list of dictionaries
        chat_history_dicts = []
        for chat_history_tuple in self.chat_history:
            chat_history_dicts.append(
                {"role": "user", "content": chat_history_tuple[0]}
            )
            chat_history_dicts.append(
                {"role": "assistant", "content": chat_history_tuple[1]}
            )

        self.chat_history.append((self.question, ""))

        # Clear the question input.
        question = self.question
        self.question = ""

        # Yield here to clear the frontend input before continuing.
        yield

        answer = "Default hardcoded response.Default hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded responseDefault hardcoded response"

        for i in range(len(answer)):
            # Pause to show the streaming effect.
            await asyncio.sleep(0.0155)
            # Add one letter at a time to the output.
            self.chat_history[-1] = (
                self.chat_history[-1][0],
                answer[: i + 1],
            )
            yield


        # Add to the answer as the chatbot responds.
        answer = ""
        yield

        # # Ensure the final answer is added to chat history
        # if answer:
        #     self.chat_history[-1] = (self.chat_history[-1][0], answer)
        #     yield

        # Set the processing state to False.
        self.processing = False

    async def handle_key_down(self, key: str):
        if key == "Enter":
            async for t in self.answer():
                yield t

    def clear_chat(self):
        # Reset the chat history and processing state
        self.chat_history = []
        self.processing = False
