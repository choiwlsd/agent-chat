import streamlit as st

from agents import agent_a, agent_b
from database import (
    init_db,
    create_conversation,
    save_message,
)


st.set_page_config(
    page_title="Local AI Agent Chat",
    page_icon="🤖",
    layout="centered",
)


def format_history(history):
    if not history:
        return "아직 대화가 없습니다."

    lines = []

    for item in history:
        lines.append(
            f"{item['agent']}: {item['message']}"
        )

    return "\n\n".join(lines)


def run_agent_conversation(user_question, rounds=4):
    init_db()

    conversation_id = create_conversation(
        user_question
    )

    history = []
    current_message = user_question

    for turn in range(rounds):
        if turn % 2 == 0:
            current_agent = agent_a
            avatar = "🧠"
        else:
            current_agent = agent_b
            avatar = "🔍"

        prompt = f"""
사용자의 원래 질문:
{user_question}

지금까지의 대화:
{format_history(history)}

상대 Agent의 마지막 메시지 또는 시작 질문:
{current_message}

당신의 역할에 맞게 다음 대화를 이어가세요.
이전 내용을 단순 반복하지 말고,
상대 Agent의 의견에 반응하세요.
"""

        with st.chat_message(
            "assistant",
            avatar=avatar,
        ):
            st.markdown(
                f"**{current_agent.name}**"
            )

            status_placeholder = st.empty()
            response_placeholder = st.empty()

            status_placeholder.markdown(
                "⏳ 생각 중..."
            )

            full_response = ""

            def stream_to_ui(text):
                nonlocal full_response

                full_response += text

                response_placeholder.markdown(
                    full_response + "▌"
                )

            response = current_agent.respond(
                prompt,
                stream_callback=stream_to_ui,
            )

            status_placeholder.empty()

            response_placeholder.markdown(
                response
            )

        history.append(
            {
                "agent": current_agent.name,
                "message": response,
            }
        )

        save_message(
            conversation_id=conversation_id,
            turn_number=turn + 1,
            agent_name=current_agent.name,
            message=response,
        )

        current_message = response

    return history


def main():
    st.title("🤖 Local AI Agent Chat")

    st.caption(
        "Ollama + Python + SQLite 기반 로컬 AI Agent MVP"
    )

    st.divider()

    user_question = st.chat_input(
        "질문을 입력하세요"
    )

    if user_question:
        with st.chat_message(
            "user",
            avatar="👤",
        ):
            st.markdown(user_question)

        run_agent_conversation(
            user_question=user_question,
            rounds=4,
        )


if __name__ == "__main__":
    main()