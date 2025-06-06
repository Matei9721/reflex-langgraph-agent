import reflex as rx

from frontend import style
from frontend.state import SettingsState, State
from frontend.components.settings import settings_icon
from frontend.components.reset import reset, reset_cache
from frontend.views.templates import templates
from frontend.views.chat import chat, action_bar


def index() -> rx.Component:
    return rx.theme(
        rx.el.style(
            f"""
            :root {{
                --font-family: "{SettingsState.font_family}", sans-serif;
            }}
        """
        ),
        # Top bar with the reset and settings buttons
        rx.box(
            reset(),
            reset_cache(),
            settings_icon(),

            class_name="top-4 right-4 absolute flex flex-row items-center gap-3.5",
        ),
        # Main content
        rx.box(
            # Prompt examples
            templates(),
            # Chat history
            chat(),
            # Action bar
            action_bar(),
            class_name="relative flex flex-col justify-between gap-20 mx-auto px-6 pt-16 lg:pt-6 pb-6 max-w-4xl h-screen",
            on_mount=State.on_load,
        ),
        accent_color=SettingsState.color,
    )


app = rx.App(stylesheets=style.STYLESHEETS, style={"font_family": "var(--font-family)"}, theme=rx.theme(appearance="dark"))
app.add_page(
    index, title="Chatbot", description="A chatbot powered by Reflex and LlamaIndex!"
)
