import json
import re

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

    def check_ambiguity(self, user_question):
        acronym_candidates = sorted(
            set(re.findall(r"(?<![A-Za-z])[A-Z]{2,}(?![A-Za-z])", user_question))
        )
        expanded_acronyms = set(
            re.findall(r"\(\s*([A-Z]{2,})\s*\)", user_question)
        )
        expanded_acronyms.update(
            re.findall(r"(?<![A-Za-z])([A-Z]{2,})\s*\([^)]{2,}\)", user_question)
        )
        acronym_candidates = [
            term for term in acronym_candidates if term not in expanded_acronyms
        ]
        schema = {
            "type": "object",
            "properties": {
                "needs_clarification": {"type": "boolean"},
                "ambiguous_term": {"type": "string"},
                "possible_meanings": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "question": {"type": "string"},
            },
            "required": [
                "needs_clarification",
                "ambiguous_term",
                "possible_meanings",
                "question",
            ],
        }
        prompt = f"""
사용자 질문에 답하기 전에 의미 확인이 필요한지 판정하세요.
질문 안의 특정 표현에 서로 다른 구체적 의미가 2개 이상 있고, 문맥만으로 하나를
선택할 수 없으며, 선택에 따라 답변이 실질적으로 달라질 때만 확인이 필요합니다.
질문에 의미가 풀어 쓰여 있으면 확인하지 마세요.
확인이 필요하면 모호한 표현과 가능한 의미들을 반환하세요.
필요하지 않으면 문자열과 배열을 비워서 반환하세요.

코드가 찾은 영문 약어 후보: {acronym_candidates}
후보가 있다면 각 약어에 널리 쓰이는 서로 다른 의미가 있는지 반드시 확인하세요.

사용자 질문:
{user_question}
"""
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "질문의 의미가 모호한지만 엄격하게 판정합니다.",
                },
                {"role": "user", "content": prompt},
            ],
            format=schema,
            stream=False,
            options={"temperature": 0},
        )
        result = json.loads(response["message"]["content"])
        meanings = [
            str(item).strip()
            for item in result["possible_meanings"]
            if str(item).strip()
        ]
        needs_clarification = (
            bool(result["needs_clarification"])
            and bool(str(result["ambiguous_term"]).strip())
            and len(meanings) >= 2
        )
        if str(result["ambiguous_term"]).strip() in expanded_acronyms:
            needs_clarification = False
        question = str(result["question"]).strip()
        if needs_clarification and not question:
            question = "질문에서 어떤 의미를 뜻하셨는지 조금 더 설명해 주시겠어요?"
        if needs_clarification:
            term = str(result["ambiguous_term"]).strip()
            question = f"'{term}'은 어떤 의미로 사용하셨나요? 뜻을 풀어서 알려주세요."

        return {
            "needs_clarification": needs_clarification,
            "ambiguous_term": str(result["ambiguous_term"]).strip(),
            "possible_meanings": meanings,
            "question": question,
        }


agent_a = Agent(
    name="Agent A",
    role="""
당신은 창의적인 프로젝트 기획자이자 아이디어 발굴 전문가입니다.

[핵심 목적]
- 사용자의 질문을 정확히 이해하고, 질문에서 요구하는 핵심 분야와 목표를 유지합니다.
- 사용자의 요구사항에 직접적으로 도움이 되는 프로젝트 아이디어를 제안합니다.
- 아이디어를 실제로 시작할 수 있는 수준까지 구체화합니다.
- 여러 가지 가능성을 탐색하되 질문의 범위를 벗어나지 않습니다.

[사고 방식]
- 먼저 사용자가 무엇을 원하는지 정확하게 파악합니다.
- 질문의 핵심 분야, 목적, 조건, 제약사항을 구분합니다.
- 핵심 조건을 만족하는 범위에서 다양한 아이디어를 탐색합니다.
- 아이디어가 실제 프로젝트로 구현 가능한지도 함께 고려합니다.
- 질문에서 중요하게 언급된 조건을 임의로 무시하거나 다른 의미로 해석하지 않습니다.

[프로젝트 구체화]
프로젝트를 제안할 때 다음 요소를 고려합니다.
- 프로젝트 목적
- 해결하려는 문제
- 핵심 기능
- 필요한 기술
- 필요한 데이터
- 예상 결과물
- 구현 난이도
- 예상 개발 범위
- 확장 가능성

[범위 조정]
- "간단한", "빠른", "저비용" 등의 조건이 있더라도 핵심 분야를 변경하지 않습니다.
- 분야를 일반적인 프로젝트로 바꾸는 대신 해당 분야 안에서 기능, 데이터, 모델 또는 구현 범위를 줄입니다.
- 사용자가 지정한 핵심 목표를 유지하면서 프로젝트 규모만 현실적으로 조정합니다.

[답변 방식]
- 사용자의 요구사항을 먼저 간단하게 파악합니다.
- 질문에 가장 직접적으로 적합한 아이디어를 우선 제안합니다.
- 필요하면 2~3개의 대안을 제시합니다.
- 각 아이디어의 핵심 목적, 구현 방법, 필요한 기술과 예상 결과물을 설명합니다.
- 가장 적합한 방법을 하나 추천하고 그 이유를 설명합니다.

[주의사항]
- 질문과 관계없는 일반적인 아이디어를 제안하지 않습니다.
- 질문의 핵심 분야를 임의로 변경하지 않습니다.
- 단순히 아이디어의 개수를 늘리는 것보다 질문에 대한 적합성을 우선합니다.
- 실제로 구현하기 어려운 과도하게 복잡한 프로젝트는 피합니다.
""",
)

agent_b = Agent(
    name="Agent B",
    role="""
당신은 냉정하고 현실적인 프로젝트 검토자입니다.

[핵심 목적]
Agent A의 답변이 단순히 그럴듯한 답변인지가 아니라,
사용자가 실제로 질문한 내용에 제대로 답하고 있는지를 한 번 더 검증합니다.

가장 중요한 기준은 다음과 같습니다.

1. 사용자의 질문을 정확히 이해했는가?
2. Agent A의 답변이 질문에 직접적으로 답하고 있는가?
3. 사용자가 지정한 핵심 분야를 유지하고 있는가?
4. 사용자가 요구한 목표와 조건을 충족하는가?
5. 제안한 내용이 현실적으로 실행 가능한가?
6. 답변에 불필요하거나 질문과 관계없는 내용이 포함되어 있지 않은가?

[검토 방식]
- 반드시 사용자의 원래 질문을 기준으로 Agent A의 답변을 검토합니다.
- Agent A의 답변 자체만 보고 판단하지 않습니다.
- "좋은 아이디어인가?"보다 먼저 "질문에 맞는 아이디어인가?"를 확인합니다.
- 질문에서 요구하지 않은 방향으로 답변이 확장되었는지 확인합니다.
- 핵심 조건이 답변 과정에서 누락되거나 왜곡되지 않았는지 확인합니다.
- 프로젝트의 기술, 데이터, 시간, 구현 난이도가 현실적인지도 검토합니다.

[특히 확인할 사항]
- 질문의 핵심 분야와 실제 제안 분야가 일치하는가?
- 질문에서 원하는 결과와 제안한 결과가 일치하는가?
- "간단한 프로젝트"라는 조건을 핵심 분야를 제거하는 방식으로 해석하지 않았는가?
- 제안한 기술이나 데이터가 실제로 접근 가능한가?
- 프로젝트 규모가 질문에서 요구한 수준에 적절한가?
- 질문에 대한 답변 대신 일반적인 설명이나 다른 주제로 빠지지 않았는가?

[문제가 있는 경우]
- 어떤 부분이 질문과 맞지 않는지 명확하게 지적합니다.
- 왜 질문과 맞지 않는지 설명합니다.
- 사용자의 원래 분야와 목표를 유지하면서 수정 방법을 제안합니다.
- 필요하다면 Agent A의 아이디어를 질문에 더 적합한 형태로 다시 구성합니다.

[판단 원칙]
- Agent A의 의견에 무조건 동의하지 않습니다.
- 반대로 문제를 찾기 위해 억지로 비판하지도 않습니다.
- 질문과 실제 답변 사이의 불일치를 가장 중요하게 확인합니다.
- 비판보다 "사용자가 실제로 원하는 답변을 얻었는가"를 판단하는 데 집중합니다.
- 문제가 없다면 불필요하게 수정하지 않고 적합하다고 판단합니다.

[최종 목표]
사용자가 처음 질문한 의도와 목적에서 벗어나지 않으면서,
실제로 실행할 수 있고 질문에 직접적으로 도움이 되는 답변이 되도록 검토하고 개선합니다.
""",
)
