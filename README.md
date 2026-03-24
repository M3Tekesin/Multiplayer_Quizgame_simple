# Multiplayer Quiz Game — CS408 Computer Networks Project

A real-time multiplayer quiz game built with Python, using TCP sockets and multithreading. One machine runs the server and hosts the game; any number of clients connect over a network to compete.

---

## How It Works

The server loads questions from a `.txt` file, waits for at least 2 players to connect, then runs the quiz round by round. Every player receives the same question simultaneously and submits an answer (A, B, or C). The first player to answer correctly earns bonus points. Results and the live scoreboard are broadcast to everyone after each question.

**Scoring:**
- Wrong answer → 0 points
- Correct answer → 1 point
- First correct answer → 1 + (number of players − 1) bonus points

---

## Project Structure

```
quiz_server.py   # Server application — hosts the game
quiz_client.py   # Client application — player interface
quiz_qa.txt      # Question bank (one question per 5 lines)
```

---

## Requirements

- Python 3.x (no external libraries needed — uses only the standard library)
- `tkinter` — comes pre-installed with Python on Windows and macOS

---

## Running the Game

**1. Start the server**
```bash
python quiz_server.py
```
- Set the port (default: `5647`)
- Select your questions file
- Set the number of questions
- Click **Start Listening**
- Click **Start Game** once at least 2 players have connected

**2. Start each client** (on the same or different machines)
```bash
python quiz_client.py
```
- Enter the server's IP address and port
- Choose a username
- Click **Connect**
- Wait for the game to start, then answer each question

---

## Question File Format

Questions are stored in a plain `.txt` file. Each question uses exactly 5 lines:

```
What is the capital of France?
A - Berlin
B - Madrid
C - Paris
Answer: C
```

Or the answer line can be just the letter:
```
C
```

Questions are read sequentially. If more questions are requested than exist in the file, it cycles back to the beginning.

---

## Key Technical Details

| Feature | Implementation |
|---|---|
| Network protocol | TCP (`socket.SOCK_STREAM`) |
| Concurrency | One thread per connected client + one accept thread |
| Thread safety | `threading.Lock()` protecting shared state |
| Message format | JSON over raw TCP sockets |
| GUI | Python `tkinter` |
| GUI thread safety | `root.after()` for all GUI updates from background threads |

---

## Features

- GUI for both server and client built with `tkinter`
- Real-time scoreboard updated after every question
- Supports mid-game disconnections — remaining players continue
- Players who disconnect cannot rejoin the same game
- Tie-aware ranking (players with equal scores share the same rank)
- Server admin controls: port, question file, number of questions
- Activity log with timestamps on both server and client

---

## Network Architecture

```
                    SERVER
                 (Quiz Host)
                /     |     \
           CLIENT1  CLIENT2  CLIENT3
           (Player) (Player) (Player)
```

- Server binds to `0.0.0.0` — accepts connections from any network interface
- Each client gets a dedicated handler thread on the server side
- All communication uses JSON-encoded messages over TCP

---

## Example Message Flow

```
Client → Server:   {"type": "connect", "name": "Alice"}
Server → Client:   {"type": "connected", "message": "Welcome to the quiz, Alice!"}

Server → All:      {"type": "question", "question_num": 1, "question": "...", "A": "...", "B": "...", "C": "..."}
Client → Server:   {"type": "answer", "answer": "B"}

Server → Client:   {"type": "result", "correct": true, "points_earned": 3, "total_score": 3, ...}
Server → All:      {"type": "game_end", "winner_message": "Winner: Alice!", ...}
```
