import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
from datetime import datetime


class QuizServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game Server")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        
        # servr state vars
        self.server_socket = None
        self.is_listening = False
        self.is_game_active = False
        self.clients = {}  # {name: {'socket': socket, 'address': addr, 'score': 0}}
        self.disconnected_during_game = set()  # ppl who dced mid gme
        self.questions = []
        self.current_question_index = 0
        self.num_questions = 0
        self.answers_received = {}  # {player_name: answer}
        self.first_correct_player = None
        self.lock = threading.Lock()
        
        self.setup_gui()
        
    def setup_gui(self):
        # titl
        title_label = tk.Label(
            self.root, 
            text="QUIZ GAME SERVER", 
            font=("Helvetica Neue", 28, "bold"),
            bg="#1a1a2e", 
            fg="#e94560"
        )
        title_label.pack(pady=15)
        
        # main containr
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # lft panl confg
        left_panel = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        config_label = tk.Label(
            left_panel, 
            text="Server Configuration", 
            font=("Helvetica Neue", 16, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        config_label.pack(pady=10)
        
        # prt input
        port_frame = tk.Frame(left_panel, bg="#16213e")
        port_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(port_frame, text="Port:", font=("Helvetica Neue", 12), bg="#16213e", fg="#ffffff").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(port_frame, font=("Helvetica Neue", 12), width=10, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.port_entry.pack(side=tk.LEFT, padx=10)
        self.port_entry.insert(0, "5647")
        
        # questins file
        file_frame = tk.Frame(left_panel, bg="#16213e")
        file_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(file_frame, text="Questions File:", font=("Helvetica Neue", 12), bg="#16213e", fg="#ffffff").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, font=("Helvetica Neue", 12), width=20, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.file_entry.pack(side=tk.LEFT, padx=10)
        self.file_entry.insert(0, "quiz_qa.txt")
        browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#e94560", fg="#ffffff", font=("Helvetica Neue", 10))
        browse_btn.pack(side=tk.LEFT)
        
        # num questns
        num_frame = tk.Frame(left_panel, bg="#16213e")
        num_frame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(num_frame, text="Number of Questions:", font=("Helvetica Neue", 12), bg="#16213e", fg="#ffffff").pack(side=tk.LEFT)
        self.num_questions_entry = tk.Entry(num_frame, font=("Helvetica Neue", 12), width=5, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.num_questions_entry.pack(side=tk.LEFT, padx=10)
        self.num_questions_entry.insert(0, "5")
        
        # cntrl btns
        btn_frame = tk.Frame(left_panel, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.listen_btn = tk.Button(
            btn_frame, 
            text="Start Listening", 
            command=self.toggle_listening,
            font=("Helvetica Neue", 12, "bold"),
            bg="#00d9ff",
            fg="#1a1a2e",
            width=15
        )
        self.listen_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_game_btn = tk.Button(
            btn_frame, 
            text="Start Game", 
            command=self.start_game,
            font=("Helvetica Neue", 12, "bold"),
            bg="#4caf50",
            fg="#ffffff",
            width=15,
            state=tk.DISABLED
        )
        self.start_game_btn.pack(side=tk.LEFT, padx=5)
        
        # conected playrs
        players_label = tk.Label(
            left_panel, 
            text="Connected Players", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        players_label.pack(pady=(15, 5))
        
        self.players_listbox = tk.Listbox(
            left_panel, 
            font=("Consolas", 11),
            bg="#0f3460",
            fg="#00ff88",
            selectbackground="#e94560",
            height=6
        )
        self.players_listbox.pack(fill=tk.X, padx=15, pady=5)
        
        # scorebrd
        score_label = tk.Label(
            left_panel, 
            text="Scoreboard", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        score_label.pack(pady=(15, 5))
        
        self.scoreboard_listbox = tk.Listbox(
            left_panel, 
            font=("Consolas", 11),
            bg="#0f3460",
            fg="#ffd700",
            selectbackground="#e94560",
            height=6
        )
        self.scoreboard_listbox.pack(fill=tk.X, padx=15, pady=5)
        
        # rigt panel logg
        right_panel = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(
            right_panel, 
            text="Activity Log", 
            font=("Helvetica Neue", 16, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        log_label.pack(pady=10)
        
        # logg w scrolbar
        log_frame = tk.Frame(right_panel, bg="#16213e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_listbox = tk.Listbox(
            log_frame, 
            font=("Consolas", 10),
            bg="#0f3460",
            fg="#ffffff",
            selectbackground="#e94560",
            yscrollcommand=scrollbar.set
        )
        self.log_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_listbox.yview)
        
        # staus bar
        self.status_var = tk.StringVar(value="Status: Not listening")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var,
            font=("Helvetica Neue", 11),
            bg="#0f3460",
            fg="#00d9ff",
            anchor=tk.W,
            padx=10
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # whn windw closd
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_listbox.insert(tk.END, f"[{timestamp}] {message}")
        self.log_listbox.see(tk.END)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Questions File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            
    def update_players_list(self):
        self.players_listbox.delete(0, tk.END)
        for name in self.clients.keys():
            self.players_listbox.insert(tk.END, f"  {name}")
            
    def update_scoreboard(self):
        self.scoreboard_listbox.delete(0, tk.END)
        if not self.clients:
            return
            
        # srt by scre desc
        sorted_players = sorted(
            self.clients.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        # calc rankngs w ties
        rankings = []
        current_rank = 1
        for i, (name, data) in enumerate(sorted_players):
            if i > 0 and data['score'] < sorted_players[i-1][1]['score']:
                current_rank = i + 1
            rankings.append((current_rank, name, data['score']))
            
        for rank, name, score in rankings:
            self.scoreboard_listbox.insert(tk.END, f"#{rank} {name}: {score} pts")
            
    def get_scoreboard_data(self):
        # scorebrd data for clents
        if not self.clients:
            return []
            
        sorted_players = sorted(
            self.clients.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        rankings = []
        current_rank = 1
        for i, (name, data) in enumerate(sorted_players):
            if i > 0 and data['score'] < sorted_players[i-1][1]['score']:
                current_rank = i + 1
            rankings.append({
                'rank': current_rank,
                'name': name,
                'score': data['score']
            })
        return rankings
        
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
            return
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", port))
            self.server_socket.listen(10)
            self.is_listening = True
            
            self.listen_btn.config(text="Stop Listening", bg="#e94560")
            self.port_entry.config(state=tk.DISABLED)
            self.status_var.set(f"Status: Listening on port {port}")
            self.log(f"Server started listening on port {port}")
            
            # strt accpting thred
            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.log(f"ERROR: Failed to start server - {str(e)}")
            
    def stop_listening(self):
        self.is_listening = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.listen_btn.config(text="Start Listening", bg="#00d9ff")
        self.port_entry.config(state=tk.NORMAL)
        self.status_var.set("Status: Not listening")
        self.log("Server stopped listening")
        
        # end gme if running
        if self.is_game_active:
            self.end_game("Server stopped listening")
        
    def accept_connections(self):
        while self.is_listening:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    conn, addr = self.server_socket.accept()
                except socket.timeout:
                    continue
                    
                # handl in new thred
                client_thread = threading.Thread(
                    target=self.handle_new_connection, 
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.is_listening:
                    self.root.after(0, lambda: self.log(f"ERROR: Accept connection - {str(e)}"))
                break
                
    def handle_new_connection(self, conn, addr):
        try:
            # rcv clent name
            data = conn.recv(1024).decode()
            if not data:
                conn.close()
                return
                
            message = json.loads(data)
            client_name = message.get('name', '')
            
            with self.lock:
                # chek if gme activ
                if self.is_game_active:
                    response = {'type': 'error', 'message': 'Game is in progress. Cannot join now.'}
                    conn.send(json.dumps(response).encode())
                    self.root.after(0, lambda: self.log(f"Rejected '{client_name}' from {addr} - Game in progress"))
                    conn.close()
                    return
                    
                # chek if nme takn
                if client_name in self.clients:
                    response = {'type': 'error', 'message': f'Name "{client_name}" is already in use.'}
                    conn.send(json.dumps(response).encode())
                    self.root.after(0, lambda: self.log(f"Rejected '{client_name}' from {addr} - Name already in use"))
                    conn.close()
                    return
                    
                # chek if playr dced durng gme
                if client_name in self.disconnected_during_game:
                    response = {'type': 'error', 'message': f'Cannot rejoin during the same game.'}
                    conn.send(json.dumps(response).encode())
                    self.root.after(0, lambda: self.log(f"Rejected '{client_name}' from {addr} - Disconnected during game"))
                    conn.close()
                    return
                    
                # accpt clent
                self.clients[client_name] = {
                    'socket': conn,
                    'address': addr,
                    'score': 0
                }
                
            response = {'type': 'connected', 'message': f'Welcome to the quiz, {client_name}!'}
            conn.send(json.dumps(response).encode())
            
            num_clients = len(self.clients)
            self.root.after(0, lambda: self.log(f"Client '{client_name}' connected from {addr}"))
            self.root.after(0, lambda: self.log(f"Total connected players: {num_clients}"))
            self.root.after(0, self.update_players_list)
            self.root.after(0, self.check_game_ready)
            
            # handl clent msgs
            self.handle_client(client_name, conn)
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"ERROR: Connection handling - {str(e)}"))
            try:
                conn.close()
            except:
                pass
                
    def handle_client(self, client_name, conn):
        while True:
            try:
                conn.settimeout(1.0)
                try:
                    data = conn.recv(4096)
                except socket.timeout:
                    continue
                    
                if not data:
                    raise ConnectionError("Client disconnected")
                    
                message = json.loads(data.decode())
                
                if message.get('type') == 'answer':
                    self.process_answer(client_name, message.get('answer'))
                elif message.get('type') == 'disconnect':
                    raise ConnectionError("Client requested disconnect")
                    
            except (ConnectionError, ConnectionResetError, BrokenPipeError):
                self.handle_client_disconnect(client_name)
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if client_name in self.clients:
                    self.handle_client_disconnect(client_name)
                break
                
    def handle_client_disconnect(self, client_name):
        with self.lock:
            if client_name not in self.clients:
                return
                
            try:
                self.clients[client_name]['socket'].close()
            except:
                pass
                
            del self.clients[client_name]
            remaining_players = len(self.clients)
            
            if self.is_game_active:
                self.disconnected_during_game.add(client_name)
                # rmv frm answrs if not anserd
                if client_name in self.answers_received:
                    del self.answers_received[client_name]
            
        self.root.after(0, lambda: self.log(f"Client '{client_name}' disconnected"))
        self.root.after(0, lambda: self.log(f"Remaining players: {remaining_players}"))
        self.root.after(0, self.update_players_list)
        self.root.after(0, self.update_scoreboard)
        self.root.after(0, self.check_game_ready)
        
        if self.is_game_active:
            # notfy othrs
            self.broadcast_message({
                'type': 'player_disconnected',
                'player': client_name,
                'message': f"Player '{client_name}' has disconnected from the game."
            })
            
            # chek if shud procss ans now
            self.root.after(100, self.check_all_answers_received)
            
    def check_game_ready(self):
        if len(self.clients) >= 2 and not self.is_game_active:
            self.start_game_btn.config(state=tk.NORMAL)
        else:
            if not self.is_game_active:
                self.start_game_btn.config(state=tk.DISABLED)
                
    def load_questions(self):
        filename = self.file_entry.get()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
                
            questions = []
            i = 0
            while i + 4 <= len(lines) - 1:
                # pars ans - handls both frmats
                answer_line = lines[i + 4]
                if answer_line.startswith("Answer:"):
                    answer = answer_line.replace("Answer:", "").strip()
                else:
                    answer = answer_line.strip()
                    
                question = {
                    'question': lines[i],
                    'A': lines[i + 1],
                    'B': lines[i + 2],
                    'C': lines[i + 3],
                    'answer': answer
                }
                questions.append(question)
                i += 5
                
            if not questions:
                messagebox.showerror("Error", f"No valid questions found in '{filename}'")
                self.log(f"ERROR: No valid questions found in '{filename}'")
                return None
                
            self.log(f"Loaded {len(questions)} questions from '{filename}'")
            return questions
        except FileNotFoundError:
            messagebox.showerror("Error", f"Questions file '{filename}' not found")
            self.log(f"ERROR: Questions file '{filename}' not found")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read questions file: {str(e)}")
            self.log(f"ERROR: Failed to read questions file - {str(e)}")
            return None
            
    def start_game(self):
        if len(self.clients) < 2:
            messagebox.showerror("Error", "Need at least 2 players to start the game")
            return
            
        try:
            self.num_questions = int(self.num_questions_entry.get())
            if self.num_questions <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of questions")
            return
            
        questions = self.load_questions()
        if not questions:
            return
            
        self.questions = questions
        self.current_question_index = 0
        self.is_game_active = True
        self.disconnected_during_game.clear()
        
        # rst scores
        for name in self.clients:
            self.clients[name]['score'] = 0
            
        self.start_game_btn.config(state=tk.DISABLED)
        self.file_entry.config(state=tk.DISABLED)
        self.num_questions_entry.config(state=tk.DISABLED)
        
        self.log(f"=== GAME STARTED with {len(self.clients)} players ===")
        self.log(f"Questions to ask: {self.num_questions}")
        self.update_scoreboard()
        
        # snd gme start w scorebrd
        self.broadcast_message({
            'type': 'game_start',
            'message': 'The game has started!',
            'num_questions': self.num_questions,
            'players': list(self.clients.keys()),
            'scoreboard': self.get_scoreboard_data()
        })
        
        # snd 1st q aftr dlay
        self.root.after(1000, self.send_next_question)
        
    def send_next_question(self):
        if not self.is_game_active:
            return
            
        if len(self.clients) < 2:
            self.end_game("Not enough players remaining")
            return
            
        if self.current_question_index >= self.num_questions:
            self.end_game("All questions answered")
            return
            
        # gt q (wrp if needd)
        q_index = self.current_question_index % len(self.questions)
        question = self.questions[q_index]
        
        self.answers_received = {}
        self.first_correct_player = None
        
        question_num = self.current_question_index + 1
        self.log(f"--- Question {question_num}/{self.num_questions} ---")
        self.log(f"Q: {question['question']}")
        self.log(f"   {question['A']}")
        self.log(f"   {question['B']}")
        self.log(f"   {question['C']}")
        self.log(f"   Correct: {question['answer']}")
        
        self.broadcast_message({
            'type': 'question',
            'question_num': question_num,
            'total_questions': self.num_questions,
            'question': question['question'],
            'A': question['A'],
            'B': question['B'],
            'C': question['C']
        })
        
    def process_answer(self, player_name, answer):
        with self.lock:
            if not self.is_game_active:
                return
                
            if player_name in self.answers_received:
                return  # alredy anserd
                
            q_index = self.current_question_index % len(self.questions)
            correct_answer = self.questions[q_index]['answer']
            
            is_correct = answer.upper() == correct_answer.upper()
            
            self.answers_received[player_name] = {
                'answer': answer,
                'correct': is_correct,
                'time': time.time()
            }
            
            # trck 1st corect
            if is_correct and self.first_correct_player is None:
                self.first_correct_player = player_name
                
            self.root.after(0, lambda: self.log(f"Answer from '{player_name}': {answer} ({'CORRECT' if is_correct else 'WRONG'})"))
            
        self.root.after(100, self.check_all_answers_received)
        
    def check_all_answers_received(self):
        with self.lock:
            if not self.is_game_active:
                return
                
            # chek if all conectd playrs anserd
            connected_players = set(self.clients.keys())
            answered_players = set(self.answers_received.keys())
            
            if connected_players == answered_players:
                self.root.after(0, self.process_question_results)
                
    def process_question_results(self):
        if not self.is_game_active:
            return
            
        q_index = self.current_question_index % len(self.questions)
        correct_answer = self.questions[q_index]['answer']
        num_players = len(self.clients)
        bonus_points = num_players - 1
        
        self.log(f"--- Results for Question {self.current_question_index + 1} ---")
        
        # calc scors n snd msgs
        for player_name, answer_data in self.answers_received.items():
            if player_name not in self.clients:
                continue
                
            points = 0
            if answer_data['correct']:
                points = 1
                if player_name == self.first_correct_player:
                    points += bonus_points
                    msg = f"Correct! You answered first and earned {points} points ({bonus_points} bonus)!"
                else:
                    msg = f"Correct! You earned {points} point."
            else:
                msg = f"Incorrect. The correct answer was {correct_answer}. You earned 0 points."
                
            self.clients[player_name]['score'] += points
            self.log(f"  {player_name}: {points} points (Total: {self.clients[player_name]['score']})")
            
            # snd prsonlzd msg
            try:
                self.clients[player_name]['socket'].send(json.dumps({
                    'type': 'result',
                    'your_answer': answer_data['answer'],
                    'correct_answer': correct_answer,
                    'correct': answer_data['correct'],
                    'first': player_name == self.first_correct_player,
                    'points_earned': points,
                    'total_score': self.clients[player_name]['score'],
                    'message': msg,
                    'scoreboard': self.get_scoreboard_data()
                }).encode())
            except:
                pass
                
        self.update_scoreboard()
        self.current_question_index += 1
        
        # chek end conditns
        if len(self.clients) < 2:
            self.root.after(2000, lambda: self.end_game("Not enough players remaining"))
        elif self.current_question_index >= self.num_questions:
            self.root.after(2000, lambda: self.end_game("All questions answered"))
        else:
            self.root.after(2000, self.send_next_question)
            
    def end_game(self, reason):
        self.is_game_active = False
        self.log(f"=== GAME ENDED: {reason} ===")
        
        # figre out winnr(s)
        scoreboard = self.get_scoreboard_data()
        winners = []
        if scoreboard:
            max_score = scoreboard[0]['score']
            winners = [p['name'] for p in scoreboard if p['score'] == max_score]
            
        if len(winners) == 1:
            winner_msg = f"Winner: {winners[0]}!"
        elif len(winners) > 1:
            winner_msg = f"Tie! Winners: {', '.join(winners)}!"
        else:
            winner_msg = "No winner determined."
            
        self.log(winner_msg)
        self.log("Final Scoreboard:")
        for p in scoreboard:
            self.log(f"  #{p['rank']} {p['name']}: {p['score']} points")
            
        # snd finl reslts
        self.broadcast_message({
            'type': 'game_end',
            'reason': reason,
            'winners': winners,
            'winner_message': winner_msg,
            'final_scoreboard': scoreboard
        })
        
        # cls all conns
        for name, data in list(self.clients.items()):
            try:
                data['socket'].close()
            except:
                pass
                
        self.clients.clear()
        self.disconnected_during_game.clear()
        self.update_players_list()
        self.update_scoreboard()
        
        # re enble contrls
        self.file_entry.config(state=tk.NORMAL)
        self.num_questions_entry.config(state=tk.NORMAL)
        self.start_game_btn.config(state=tk.DISABLED)
        
        self.log("Server is ready for new game")
        
    def broadcast_message(self, message):
        msg_json = json.dumps(message).encode()
        for name, data in list(self.clients.items()):
            try:
                data['socket'].send(msg_json)
            except:
                pass
                
    def on_closing(self):
        self.is_listening = False
        self.is_game_active = False
        
        # cls all clent conns
        for name, data in list(self.clients.items()):
            try:
                data['socket'].close()
            except:
                pass
                
        # cls servr sock
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizServer(root)
    root.mainloop()
