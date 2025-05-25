import reflex as rx
from frontend.state import State
from frontend.components.hint import hint


def reset() -> rx.Component:
    return hint(
        text="New Chat",
        content=rx.box(
            rx.icon(
                tag="square-pen",
                size=22,
                stroke_width="1.5",
                class_name="!text-slate-10",
            ),
            class_name="hover:bg-slate-3 p-2 rounded-xl transition-colors cursor-pointer",
            on_click=State.clear_chat,
        ),
        side="bottom",
    )

def reset_cache() -> rx.Component:
    return hint(
        text="Reset Cache",
        content=rx.box(
            rx.icon(
                tag="trash",
                size=22,
                stroke_width="1.5",
                class_name="!text-slate-10",
            ),
            class_name="hover:bg-slate-3 p-2 rounded-xl transition-colors cursor-pointer",
            on_click=State.reset_chats,
        ),
        side="bottom",
    )
