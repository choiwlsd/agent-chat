import streamlit as st

from agents import agent_a, agent_b
from conversation import build_turn_prompt
from database import init_db, create_conversation, save_message


st.set_page_config(
    page_title="Local AI Agent Chat",
    page_icon="🤖",
    layout="centered",
)


def run_agent_conversation(user_question, rounds=4):
    init_db()
    conversation_id = create_conversation(user_question)
    history = []
    current_message = user_question

    for turn in range(rounds):
        current_agent = agent_a if turn % 2 == 0 else agent_b
        avatar = "💡" if turn % 2 == 0 else "🔎"
        prompt = build_turn_prompt(user_question, history, current_message)

        with st.chat_message("assistant", avatar=avatar):
            st.markdown(f"**{current_agent.name}**")
            status_placeholder = st.empty()
            response_placeholder = st.empty()
            status_placeholder.markdown("생각 중...")
            full_response = ""

            def stream_to_ui(text):
                nonlocal full_response
                full_response += text
                response_placeholder.markdown(full_response + "▌")

            response = current_agent.respond(prompt, stream_callback=stream_to_ui)
            status_placeholder.empty()
            response_placeholder.markdown(response)

        history.append({"agent": current_agent.name, "message": response})
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
    st.caption("Ollama + Python + SQLite 기반 로컬 AI Agent MVP")
    st.divider()

    user_question = st.chat_input("질문을 입력하세요")

    if user_question:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)

        run_agent_conversation(user_question=user_question, rounds=4)


if __name__ == "__main__":
    main()
