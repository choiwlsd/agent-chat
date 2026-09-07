from agents import agent_a, agent_b
from database import init_db, create_conversation, save_message


def format_history(history):
    if not history:
        return "아직 대화가 없습니다."

    return "\n\n".join(
        f"{item['agent']}: {item['message']}" for item in history
    )


def build_turn_prompt(user_question, history, current_message):
    return f"""
[사용자의 원래 질문]
{user_question}

[지금까지의 대화]
{format_history(history)}

[상대 Agent의 마지막 메시지 또는 시작 질문]
{current_message}

[이번 답변의 우선순위]
1. 원래 질문에 명시된 핵심 분야와 사용자의 목표를 반드시 유지합니다.
2. 난이도, 기간, 비용 같은 조건은 핵심 분야 안에서 범위를 조정하는 데 사용합니다.
3. 상대 Agent의 의견을 검토하고 대화를 한 단계 발전시킵니다.
4. 앞선 내용을 그대로 반복하지 않습니다.
5. 최종 답변은 자연스러운 한국어로만 작성합니다.

예를 들어 사용자가 'CV를 경험할 간단한 프로젝트'를 요청하면,
'CV 프로젝트'가 필수 조건이고 '간단한'은 구현 규모를 줄이는 조건입니다.
"""


def print_stream(text):
    print(text, end="", flush=True)


def run_conversation(user_question, rounds=4):
    init_db()
    conversation_id = create_conversation(user_question)
    history = []
    current_message = user_question

    for turn in range(rounds):
        current_agent = agent_a if turn % 2 == 0 else agent_b
        prompt = build_turn_prompt(user_question, history, current_message)

        print(f"\n--- {turn + 1}번째 대화 / {current_agent.name} ---")
        print("생각 중...\n")

        response = current_agent.respond(prompt, stream_callback=print_stream)
        print("\n")

        history.append({"agent": current_agent.name, "message": response})
        save_message(
            conversation_id=conversation_id,
            turn_number=turn + 1,
            agent_name=current_agent.name,
            message=response,
        )
        current_message = response

    return history


if __name__ == "__main__":
    question = input("사용자 질문을 입력하세요: ")
    print("\n대화를 시작합니다...\n")
    run_conversation(user_question=question, rounds=4)
