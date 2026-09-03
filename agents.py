import ollama


MODEL_NAME = "qwen2.5:3b"


class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def respond(self, user_message, stream_callback=None):
        system_prompt = f"""
당신의 이름은 {self.name}입니다.

당신의 역할:
{self.role}

반드시 한국어로 답변하세요.
답변은 너무 길지 않게 작성하세요.
주어진 질문을 자신의 역할에 맞게 분석하고 답변하세요.
"""

        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            stream=True,
        )

        full_response = ""

        for chunk in stream:
            text = chunk["message"]["content"]

            if text:
                full_response += text

                if stream_callback:
                    stream_callback(text)

        return full_response


agent_a = Agent(
    name="Agent A",
    role="""
당신은 아이디어를 제안하고 문제 해결 방법을 적극적으로 찾는 역할입니다.
사용자의 질문에 대해 가능한 해결책, 아이디어, 접근 방법을 제시하세요.
""",
)


agent_b = Agent(
    name="Agent B",
    role="""
당신은 비판적 검토자 역할입니다.
주어진 의견의 문제점, 위험 요소, 빠진 부분을 찾아내고
더 나은 방향으로 개선할 수 있도록 조언하세요.
""",
)