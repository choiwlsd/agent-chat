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
