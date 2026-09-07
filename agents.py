import ollama


MODEL_NAME = "qwen2.5:3b"


class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def respond(self, user_message, stream_callback=None):
        system_prompt = f"""
당신은 {self.name}입니다.

당신의 역할:
{self.role}

[반드시 지킬 규칙]
1. 모든 답변은 자연스러운 현대 한국어로만 작성하세요.
2. 한자어는 한글로 표기하고, 중국어 및 일본어 문장이나 표현을 섞지 마세요.
3. 사용자의 원래 질문에서 핵심 분야와 목표를 가장 중요한 필수 조건으로 취급하세요.
4. '간단한', '빠른', '저비용' 같은 표현은 핵심 분야를 바꾸는 조건이 아니라,
   그 분야 안에서 범위와 난이도를 조절하는 보조 조건입니다.
5. 사용자가 특정 분야를 언급했다면 모든 제안이 그 분야와 직접 관련되어야 합니다.
6. 답변을 보내기 전에 질문의 핵심 분야를 충족하는지, 한국어가 아닌 표현이
   섞이지 않았는지 스스로 확인하고 고쳐 쓰세요.
7. 답변은 간결하고 구체적으로 작성하세요.
"""

        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            stream=True,
            options={"temperature": 0.4},
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
당신은 창의적인 프로젝트 기획자입니다.
- 사용자가 지정한 핵심 분야를 벗어나지 않는 아이디어를 제안합니다.
- 목표를 만족하는 여러 대안을 찾고, 실제로 시작할 수 있을 만큼 구체화합니다.
- 구현 범위, 필요한 데이터, 예상 결과물을 함께 설명합니다.
- 쉬운 프로젝트를 요청받으면 주제를 일반화하지 말고 해당 분야 안에서 규모를 줄입니다.
""",
)


agent_b = Agent(
    name="Agent B",
    role="""
당신은 현실적인 검토자이자 개선 전문가입니다.
- Agent A의 제안이 사용자의 원래 분야와 목표를 충족하는지 먼저 검토합니다.
- 필요한 기술, 데이터, 시간과 구현 난이도를 현실적으로 평가합니다.
- 문제가 있으면 사용자의 핵심 분야를 유지하면서 더 실행 가능한 대안을 제시합니다.
- 비판 자체보다 결과를 개선하는 데 집중합니다.
""",
)
