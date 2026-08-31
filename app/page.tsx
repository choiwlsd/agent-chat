"use client";

import { useState } from "react";

type Message = {
  agent: "A" | "B";
  text: string;
};

export default function Home() {
  const [topic, setTopic] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function startConversation() {
    if (!topic.trim()) {
      alert("주제를 입력해주세요.");
      return;
    }

    setLoading(true);
    setMessages([]);

    try {
      const response = await fetch("/api/conversation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "대화 생성에 실패했습니다.");
      }

      setMessages(data.messages);
    } catch (error) {
      console.error(error);
      alert("대화 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8"> 
      <div className="mx-auto max-w-3xl"> 
        <h1 className="mb-2 text-3xl font-bold"> 
          🤖 AI Agent Conversation 
        </h1> 

        <p className="mb-8 text-gray-500"> 
          서로 다른 성격의 AI Agent를 대화시켜보세요. 
        </p> 
        
        <div className="rounded-2xl bg-white p-6 shadow-sm"> 
          <label className="mb-2 block text-sm font-medium"> 
            토론 주제 
          </label> 

          <textarea 
            value={topic} 
            onChange={(e) => setTopic(e.target.value)} 
            className="mb-4 w-full rounded-xl border p-4 outline-none focus:ring-2 focus:ring-black" 
            rows={3} 
            placeholder="예: 대학생을 위한 AI 여행 플래너" 
          /> 

          <button 
            onClick={startConversation} 
            disabled={loading} 
            className="rounded-xl bg-black px-5 py-3 font-medium text-white disabled:opacity-50"
          > 
            {loading ? "Agent들이 대화 중..." : "▶ 대화 시작"} 
          </button> 
        </div>

        <div className="mt-8 space-y-4"> 
          {messages.map((message, index) => { 
            const isA = message.agent === "A"; 
            
            return ( 
              <div 
                key={index} 
                className={`flex ${ 
                  isA ? "justify-start" : "justify-end" 
                }`} 
              > 
                <div className={`max-w-[80%] rounded-2xl p-5 ${ 
                  isA ? "bg-white" : "bg-black text-white" 
                }`}> 
                  <div className="mb-2 text-sm font-bold"> 
                    {isA ? "🤖 Agent A · 창업가" : "🤖 Agent B · 투자자"} 
                  </div> <p className="leading-7"> {message.text} </p> 
                </div> 
              </div> ); 
          })} 
        </div> 
        
        {loading && ( 
          <div className="mt-6 text-center text-gray-400"> 
            🤖 Agent들이 생각하고 있습니다... 
          </div> 
        )} 
      </div> 
    </main> 
  ); 
}