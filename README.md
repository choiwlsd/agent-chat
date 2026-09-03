### 가상환경 실행 후 패키지 설치

가상환경 활성화

```git bash
source .venv/Scripts/activate
```

`(.venv)` 뜨면 requirements.txt 설치

```git bash
python -m pip install -r requirements.txt
```

### 저장된 대화 기록을 SQLite 프로그램 없이 확인

DB에 정말 저장되었는지 확인
터미널에서 아래 명령어를 입력하고 리스트 형태의 응답으로 확인 가능

```git bash
python -c "import sqlite3; conn=sqlite3.connect('data/conversations.db'); print(conn.execute('SELECT * FROM conversations').fetchall())"
```

Agent 답변 확인

```git bash
python -c "import sqlite3; conn=sqlite3.connect('data/conversations.db'); print(conn.execute('SELECT turn_number, agent_name, message FROM messages').fetchall())"
```

```markdown
[
(1, 'Agent A', '...'),
(2, 'Agent B', '...'),
(3, 'Agent A', '...'),
(4, 'Agent B', '...')
]
```

### 전체 실행 방법 정리

1. 프로젝트 폴더로 이동
2. 가상환경 활성화
3. Ollama 확인
4. Streamlit 실행
5. 브라우저에서 질문 입력

```git bash
cd ai-agent-chat
source .venv/bin/activate
ollama list
python3 -m streamlit run app.py
```

정상이라면 브라우저에서 다음 주소로 접속: `http://localhost:8501`
