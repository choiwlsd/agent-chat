import OpenAI from "openai";
import { NextResponse } from "next/server";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const AGENT_A = `
너는 낙관적인 창업가 Agent다.

역할:
- 아이디어의 가능성을 찾는다.
- 새로운 아이디어를 적극적으로 제안한다.
- 상대방의 의견을 발전시킨다.
- 너무 쉽게 포기하지 않는다.

대화 스타일:
- 짧고 자연스럽게 말한다.
- 한 번에 하나의 핵심 주장만 한다.
- 상대방의 말에 반드시 반응한다.
`;

const AGENT_B = `
너는 비판적인 창업가 Agent다.

역할:
- 아이디어의 약점을 찾는다.
- 새로운 아이디어를 적극적으로 제안한다.
- 근거가 부족하면 질문한다.
- 시장성, 실행 가능성, 비용을 의심한다.
- 단순한 반대가 아니라 더 나은 방향을 제안한다.
- 너무 쉽게 포기하지 않는다.

대화 스타일:
- 짧고 날카롭게 말한다.
- 한 번에 하나의 핵심 질문 또는 반박만 한다.
- 상대방의 주장에 구체적으로 반응한다.
`;

export async function POST(request: Request) {
  try {
    const { topic } = await request.json();

    if (!topic || typeof topic !== "string") {
      return NextResponse.json(
        { error: "주제를 입력해주세요." },
        { status: 400 }
      );
    }

    const messages: {
      agent: "A" | "B";
      text: string;
    }[] = [];

    let previousResponse = "";

    for (let i = 0; i < 8; i++) {
      const isAgentA = i % 2 === 0;
      const agent: "A" | "B" = isAgentA ? "A" : "B";
      const systemPrompt = isAgentA ? AGENT_A : AGENT_B;

      const conversationHistory =
        messages.length > 0
          ? messages
              .map((message) => `Agent ${message.agent}: ${message.text}`)
              .join("\n")
          : "(아직 대화가 시작되지 않았음)";

      const prompt = `
토론 주제:
"${topic}"

지금까지의 대화:
${conversationHistory}

${
  previousResponse
    ? `직전 상대방의 발언:
"${previousResponse}"`
    : ""
}

지금 네 차례다.

위 대화에 자연스럽게 이어지는 발언을 해라.
2~4문장 정도로 답해라.

너는 ${isAgentA ? "낙관적인 창업가" : "비판적인 창업가"} Agent다.
상대방의 직전 발언에 반드시 구체적으로 반응해라.
`;

      const response = await openai.responses.create({
        model: "gpt-5.6-luna",
        instructions: systemPrompt,
        input: prompt,
      });

      const text = response.output_text.trim();

      messages.push({
        agent,
        text,
      });

      previousResponse = text;
    }

    return NextResponse.json({ messages });
  } catch (error) {
    console.error("Error in conversation route:", error);

    return NextResponse.json(
      { error: "대화 생성 중 오류가 발생했습니다." },
      { status: 500 }
    );
  }
}
