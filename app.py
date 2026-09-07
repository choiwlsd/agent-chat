import streamlit as st

from agents import agent_a, agent_b
from conversation import build_turn_prompt
from database import init_db, create_conversation, save_message


st.set_page_config(
    page_title="Local AI Agent Chat",
    page_icon="🤖",
    layout="centered",
)

def run_agent_conversation(
    user_question,
    rounds=4,
    history=None,
    conversation_id=None,
    current_message=None,
):
    init_db()
    if conversation_id is None:
        conversation_id = create_conversation(user_question)
    if history is None:
        history = []
    if current_message is None:
        current_message = user_question

    for turn in range(len(history), rounds):
        current_agent = agent_a if turn % 2 == 0 else agent_b
        avatar = "💡" if turn % 2 == 0 else "🔎"
        prompt = build_turn_prompt(user_question, history, current_message)

        with st.chat_message("assistant", avatar=avatar):
            st.markdown(f"**{current_agent.name}**")
            response_placeholder = st.empty()
            full_response = ""

            def stream_to_ui(text):
                nonlocal full_response
                full_response += text
                response_placeholder.markdown(full_response + "▌")

            needs_clarification = False
            with st.spinner("답변을 생성하고 있습니다..."):
                if current_agent is agent_b:
                    ambiguity = agent_b.check_ambiguity(user_question)
                    needs_clarification = ambiguity["needs_clarification"]

                if needs_clarification:
                    response = ambiguity["question"]
                else:
                    callback = stream_to_ui if current_agent is agent_a else None
                    response = current_agent.respond(
                        prompt,
                        stream_callback=callback,
                    )

            visible_response = response.strip()
            response_placeholder.markdown(visible_response)

        history.append({"agent": current_agent.name, "message": visible_response})
        st.session_state.display_messages.append(
            {
                "role": "assistant",
                "agent": current_agent.name,
                "avatar": avatar,
                "message": visible_response,
            }
        )
        save_message(
            conversation_id=conversation_id,
            turn_number=turn + 1,
            agent_name=current_agent.name,
            message=visible_response,
        )
        current_message = visible_response

        if needs_clarification:
            st.session_state.pending_clarification = True
            st.session_state.conversation_state = {
                "user_question": user_question,
                "history": history,
                "conversation_id": conversation_id,
                "rounds": rounds,
            }
            return history

    st.session_state.pending_clarification = False
    st.session_state.conversation_state = None
    return history


def main():
    st.title("🤖 Local AI Agent Chat")
    st.caption("Ollama + Python + SQLite 기반 로컬 AI Agent MVP")
    st.divider()

    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "pending_clarification" not in st.session_state:
        st.session_state.pending_clarification = False
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = None

    for item in st.session_state.display_messages:
        with st.chat_message(item["role"], avatar=item["avatar"]):
            if item.get("agent"):
                st.markdown(f"**{item['agent']}**")
            st.markdown(item["message"])

    placeholder = (
        "확인 질문에 답해주세요"
        if st.session_state.pending_clarification
        else "질문을 입력하세요"
    )
    user_question = st.chat_input(placeholder)

    if user_question:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_question)

        st.session_state.display_messages.append(
            {
                "role": "user",
                "agent": None,
                "avatar": "👤",
                "message": user_question,
            }
        )

        if st.session_state.pending_clarification:
            state = st.session_state.conversation_state
            clarified_question = (
                f"{state['user_question']}\n\n"
                f"사용자의 추가 설명: {user_question}"
            )
            st.session_state.pending_clarification = False
            run_agent_conversation(
                user_question=clarified_question,
                rounds=state["rounds"],
                history=state["history"],
                conversation_id=state["conversation_id"],
                current_message=f"사용자의 추가 설명: {user_question}",
            )
        else:
            run_agent_conversation(user_question=user_question, rounds=4)


if __name__ == "__main__":
    main()
