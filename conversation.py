from agents import agent_a, agent_b


def format_history(history):
    if not history:
        return "아직 대화가 없습니다."

    lines = []

    for item in history:
        lines.append(f"{item['agent']}: {item['message']}")

    return "\n\n".join(lines)


def print_stream(text):
    print(text, end="", flush=True)


def run_conversation(user_question, rounds=4):
    history = []

    current_message = user_question

    for turn in range(rounds):
        if turn % 2 == 0:
            current_agent = agent_a
        else:
            current_agent = agent_b

        prompt = f"""
사용자의 원래 질문:
{user_question}

지금까지의 대화:
{format_history(history)}

상대 Agent의 마지막 메시지 또는 시작 질문:
{current_message}

당신의 역할에 맞게 다음 대화를 이어가세요.
이전 내용을 단순 반복하지 말고, 상대 Agent의 의견에 반응하세요.
"""

        print(f"\n--- {turn + 1}번째 대화 / {current_agent.name} ---")
        print("생각 중...\n")

        response = current_agent.respond(
            prompt,
            stream_callback=print_stream,
        )

        print("\n")

        history.append(
            {
                "agent": current_agent.name,
                "message": response,
            }
        )

        current_message = response

    return history


if __name__ == "__main__":
    question = input("사용자 질문을 입력하세요: ")

    print("\n대화를 시작합니다...\n")

    run_conversation(
        user_question=question,
        rounds=4,
    )