import reflex as rx
from frontend.components.badge import made_with_reflex
from frontend.state import State


def qa(question: str, tools: list, answer: str) -> rx.Component:
    return rx.box(
        # Question
        rx.box(
            rx.markdown(
                question,
                class_name="[&>p]:!my-2.5",
            ),
            class_name="relative bg-slate-3 px-5 rounded-3xl max-w-[70%] text-slate-12 self-end",
        ),
        # Tools used
        rx.box(
            rx.foreach(
                tools,
                lambda tool: rx.box(
                    rx.box(
                        rx.icon(
                            tag="wrench",
                            size=22,
                            stroke_width="1.5",
                            class_name="!text-slate-10",
                        ),
                        rx.text(f"Running: {tool}", class_name="text-slate-12 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-2 border border-slate-4 shadow-sm"),
                        class_name="flex items-center gap-2"
                    ),
                    class_name="flex items-center gap-2 bg-white/80 hover:bg-slate-2 border border-slate-3 shadow px-3 py-1 rounded-full h-9 transition-colors m-1",
                ),
            ),
        ),
        # Answer
        rx.box(
            rx.box(
                rx.image(
                    src="llama.svg",
                    class_name="h-6" + rx.cond(State.processing, " animate-pulse", ""),
                ),
            ),
            rx.box(
                rx.cond(
                    answer.strip() == "",
                    # Show 3 pulsating dots if answer is empty
                    rx.box(
                        rx.box(".", class_name="animate-bounce [animation-delay:-.32s] text-2xl"),
                        rx.box(".", class_name="animate-bounce [animation-delay:-.16s] text-2xl"),
                        rx.box(".", class_name="animate-bounce text-2xl"),
                        class_name="flex flex-row gap-1 h-7 items-center px-2",
                    ),
                    # Otherwise show the answer markdown and copy button
                    rx.fragment(
                        rx.markdown(
                            answer,
                            class_name="[&>p]:!my-2.5 fade-in",
                            unsafe_allow_html=False
                        ),
                        rx.box(
                            rx.el.button(
                                rx.icon(tag="copy", size=18),
                                class_name="p-1 text-slate-10 hover:text-slate-11 transform transition-colors cursor-pointer",
                                on_click=[rx.set_clipboard(answer), rx.toast("Copied!")],
                                title="Copy",
                            ),
                            class_name="-bottom-9 left-5 absolute opacity-0 group-hover:opacity-100 transition-opacity",
                        ),
                    ),
                ),
                class_name="relative bg-accent-4 px-5 rounded-3xl max-w-[70%] text-slate-12 self-start",
            ),
            class_name="flex flex-row gap-6",
        ),
        class_name="flex flex-col gap-8 pb-10 group",
    )


def chat() -> rx.Component:
    # Changed from scroll_area to auto_scroll for better UX
    return  rx.auto_scroll(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1], messages[2]),
        ),
    type="hover",
        # Make the scrollbar invisible
        style={
            "scrollbarWidth": "none",  # Firefox
            "msOverflowStyle": "none",  # IE 10+
            "overflow": "auto",  # needed if content overflows
        }
    )


def action_bar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.el.input(
                placeholder="Ask anything",
                on_change=State.set_question,
                value=rx.cond(State.question != "", State.question, ""),
                on_key_down=[State.handle_key_down],
                on_blur=State.set_question,
                id="input1",
                class_name="box-border bg-slate-3 px-4 py-2 pr-14 rounded-full w-full outline-none focus:outline-accent-10 h-[48px] text-slate-12 placeholder:text-slate-9",
            ),
            rx.el.button(
                rx.cond(
                    State.processing,
                    rx.icon(
                        tag="loader-circle",
                        size=19,
                        color="white",
                        class_name="animate-spin",
                    ),
                    rx.icon(tag="arrow-up", size=19, color="white"),
                ),
                on_click=[State.answer, rx.set_value("input1", "")],
                class_name="top-1/2 right-4 absolute bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default",
                disabled=rx.cond(
                    State.processing | (State.question == ""), True, False
                ),
            ),
            class_name="relative w-full",
        ),
        # Made with Reflex link
        # made_with_reflex(),
        class_name="flex flex-col justify-center items-center gap-6 w-full",
    )
