import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime


class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game Client")
        self.root.geometry("800x700")
        self.root.configure(bg="#1a1a2e")
        
        # clinet vars
        self.client_socket = None
        self.is_connected = False
        self.username = ""
        self.receive_thread = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # tittle lbl
        title_label = tk.Label(
            self.root, 
            text="QUIZ GAME CLIENT", 
            font=("Helvetica Neue", 28, "bold"),
            bg="#1a1a2e", 
            fg="#e94560"
        )
        title_label.pack(pady=15)
        
        # main containr
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # conn section
        conn_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        conn_label = tk.Label(
            conn_frame, 
            text="Connection", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        conn_label.pack(pady=10)
        
        # inpuuts
        inputs_frame = tk.Frame(conn_frame, bg="#16213e")
        inputs_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # ip addr
        tk.Label(inputs_frame, text="Server IP:", font=("Helvetica Neue", 11), bg="#16213e", fg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = tk.Entry(inputs_frame, font=("Helvetica Neue", 11), width=15, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.ip_entry.insert(0, "127.0.0.1")
        
        # prt
        tk.Label(inputs_frame, text="Port:", font=("Helvetica Neue", 11), bg="#16213e", fg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_entry = tk.Entry(inputs_frame, font=("Helvetica Neue", 11), width=8, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.port_entry.insert(0, "5647")
        
        # usrname
        tk.Label(inputs_frame, text="Username:", font=("Helvetica Neue", 11), bg="#16213e", fg="#ffffff").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.username_entry = tk.Entry(inputs_frame, font=("Helvetica Neue", 11), width=15, bg="#0f3460", fg="#ffffff", insertbackground="#ffffff")
        self.username_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # butns
        btn_frame = tk.Frame(conn_frame, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.connect_btn = tk.Button(
            btn_frame, 
            text="Connect", 
            command=self.connect_to_server,
            font=("Helvetica Neue", 11, "bold"),
            bg="#4caf50",
            fg="#ffffff",
            width=12
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = tk.Button(
            btn_frame, 
            text="Disconnect", 
            command=self.disconnect_from_server,
            font=("Helvetica Neue", 11, "bold"),
            bg="#e94560",
            fg="#ffffff",
            width=12,
            state=tk.DISABLED
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # gme area
        game_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        game_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # lft side questoin
        left_game = tk.Frame(game_frame, bg="#16213e")
        left_game.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # questn disply
        q_label = tk.Label(
            left_game, 
            text="Current Question", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        q_label.pack(pady=(0, 10))
        
        self.question_text = tk.Text(
            left_game,
            font=("Helvetica Neue", 12),
            bg="#0f3460",
            fg="#ffffff",
            wrap=tk.WORD,
            height=6,
            state=tk.DISABLED
        )
        self.question_text.pack(fill=tk.X, pady=5)
        
        # answrs
        answer_frame = tk.Frame(left_game, bg="#16213e")
        answer_frame.pack(fill=tk.X, pady=15)
        
        self.answer_var = tk.StringVar(value="")
        
        self.radio_a = tk.Radiobutton(
            answer_frame,
            text="A",
            variable=self.answer_var,
            value="A",
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e",
            fg="#00d9ff",
            selectcolor="#0f3460",
            activebackground="#16213e",
            activeforeground="#00d9ff",
            state=tk.DISABLED
        )
        self.radio_a.pack(side=tk.LEFT, padx=20)
        
        self.radio_b = tk.Radiobutton(
            answer_frame,
            text="B",
            variable=self.answer_var,
            value="B",
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e",
            fg="#00d9ff",
            selectcolor="#0f3460",
            activebackground="#16213e",
            activeforeground="#00d9ff",
            state=tk.DISABLED
        )
        self.radio_b.pack(side=tk.LEFT, padx=20)
        
        self.radio_c = tk.Radiobutton(
            answer_frame,
            text="C",
            variable=self.answer_var,
            value="C",
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e",
            fg="#00d9ff",
            selectcolor="#0f3460",
            activebackground="#16213e",
            activeforeground="#00d9ff",
            state=tk.DISABLED
        )
        self.radio_c.pack(side=tk.LEFT, padx=20)
        
        self.submit_btn = tk.Button(
            answer_frame, 
            text="Submit Answer", 
            command=self.submit_answer,
            font=("Helvetica Neue", 12, "bold"),
            bg="#ffd700",
            fg="#1a1a2e",
            width=15,
            state=tk.DISABLED
        )
        self.submit_btn.pack(side=tk.RIGHT, padx=20)
        
        # reslt lbl
        self.result_label = tk.Label(
            left_game,
            text="",
            font=("Helvetica Neue", 12),
            bg="#16213e",
            fg="#00ff88",
            wraplength=400
        )
        self.result_label.pack(pady=10)
        
        # rght side scores
        right_game = tk.Frame(game_frame, bg="#16213e", width=200)
        right_game.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right_game.pack_propagate(False)
        
        score_label = tk.Label(
            right_game, 
            text="Scoreboard", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        score_label.pack(pady=10)
        
        self.scoreboard_listbox = tk.Listbox(
            right_game, 
            font=("Consolas", 10),
            bg="#0f3460",
            fg="#ffd700",
            selectbackground="#e94560",
            height=10
        )
        self.scoreboard_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # botom log
        log_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(
            log_frame, 
            text="Activity Log", 
            font=("Helvetica Neue", 14, "bold"),
            bg="#16213e", 
            fg="#0f3460"
        )
        log_label.pack(pady=10)
        
        # logg w scrolbar
        log_container = tk.Frame(log_frame, bg="#16213e")
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_listbox = tk.Listbox(
            log_container, 
            font=("Consolas", 10),
            bg="#0f3460",
            fg="#ffffff",
            selectbackground="#e94560",
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.log_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_listbox.yview)
        
        # stats bar
        self.status_var = tk.StringVar(value="Status: Not connected")
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
        
        # whn window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_listbox.insert(tk.END, f"[{timestamp}] {message}")
        self.log_listbox.see(tk.END)
        
    def update_scoreboard(self, scoreboard_data):
        self.scoreboard_listbox.delete(0, tk.END)
        for p in scoreboard_data:
            marker = " <--" if p['name'] == self.username else ""
            self.scoreboard_listbox.insert(tk.END, f"#{p['rank']} {p['name']}: {p['score']} pts{marker}")
            
    def set_question(self, question_data):
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        
        q_num = question_data.get('question_num', '?')
        total = question_data.get('total_questions', '?')
        
        text = f"Question {q_num}/{total}\n\n"
        text += f"{question_data['question']}\n\n"
        text += f"{question_data['A']}\n"
        text += f"{question_data['B']}\n"
        text += f"{question_data['C']}"
        
        self.question_text.insert(tk.END, text)
        self.question_text.config(state=tk.DISABLED)
        
        # enabl ans btns
        self.answer_var.set("")
        self.radio_a.config(state=tk.NORMAL)
        self.radio_b.config(state=tk.NORMAL)
        self.radio_c.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.result_label.config(text="")
        
    def disable_answer_controls(self):
        self.radio_a.config(state=tk.DISABLED)
        self.radio_b.config(state=tk.DISABLED)
        self.radio_c.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        
    def clear_question(self):
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.config(state=tk.DISABLED)
        self.answer_var.set("")
        self.disable_answer_controls()
        self.result_label.config(text="")
        
    def connect_to_server(self):
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter server IP address")
            return
            
        if not port_str:
            messagebox.showerror("Error", "Please enter port number")
            return
            
        if not username:
            messagebox.showerror("Error", "Please enter your username")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
            
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            
            # snd usrname
            self.client_socket.send(json.dumps({'type': 'connect', 'name': username}).encode())
            
            # wiat for respons
            response = self.client_socket.recv(4096).decode()
            message = json.loads(response)
            
            if message.get('type') == 'error':
                error_msg = message.get('message', 'Connection refused')
                messagebox.showerror("Connection Error", error_msg)
                self.log(f"ERROR: {error_msg}")
                self.client_socket.close()
                self.client_socket = None
                return
                
            # conected ok
            self.is_connected = True
            self.username = username
            
            self.log(f"Connected to server at {ip}:{port}")
            self.log(message.get('message', 'Connected successfully'))
            
            self.status_var.set(f"Status: Connected as '{username}'")
            
            # updaet ui
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.ip_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)
            self.username_entry.config(state=tk.DISABLED)
            
            # strt recieve thred
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Connection refused. Is the server running?")
            self.log("ERROR: Connection refused")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            self.log(f"ERROR: {str(e)}")
            
    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.send(json.dumps({'type': 'disconnect'}).encode())
            except:
                pass
            self.cleanup_connection()
            self.log("Disconnected from server")
            
    def cleanup_connection(self):
        self.is_connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
            
        self.status_var.set("Status: Not connected")
        
        # updte ui
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.ip_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)
        self.username_entry.config(state=tk.NORMAL)
        
        self.clear_question()
        self.scoreboard_listbox.delete(0, tk.END)
        
    def receive_messages(self):
        while self.is_connected:
            try:
                self.client_socket.settimeout(1.0)
                try:
                    data = self.client_socket.recv(4096)
                except socket.timeout:
                    continue
                    
                if not data:
                    raise ConnectionError("Server disconnected")
                    
                message = json.loads(data.decode())
                self.root.after(0, lambda m=message: self.handle_message(m))
                
            except (ConnectionError, ConnectionResetError, BrokenPipeError):
                self.root.after(0, lambda: self.handle_disconnect("Server disconnected"))
                break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if self.is_connected:
                    self.root.after(0, lambda: self.handle_disconnect(f"Connection error: {str(e)}"))
                break
                
    def handle_message(self, message):
        msg_type = message.get('type', '')
        
        if msg_type == 'game_start':
            self.log("=== GAME STARTED ===")
            self.log(f"Players: {', '.join(message.get('players', []))}")
            self.log(f"Number of questions: {message.get('num_questions', '?')}")
            if 'scoreboard' in message:
                self.update_scoreboard(message['scoreboard'])
                
        elif msg_type == 'question':
            q_num = message.get('question_num', '?')
            self.log(f"--- Question {q_num} received ---")
            self.log(f"Q: {message.get('question', '')}")
            self.set_question(message)
            
        elif msg_type == 'result':
            self.log(f"--- Your Result ---")
            self.log(f"Your answer: {message.get('your_answer', '?')}")
            self.log(f"Correct answer: {message.get('correct_answer', '?')}")
            self.log(message.get('message', ''))
            self.log(f"Points earned: {message.get('points_earned', 0)}")
            self.log(f"Your total score: {message.get('total_score', 0)}")
            
            # shw reslt
            result_msg = message.get('message', '')
            if message.get('correct'):
                self.result_label.config(text=result_msg, fg="#00ff88")
            else:
                self.result_label.config(text=result_msg, fg="#e94560")
                
            if 'scoreboard' in message:
                self.update_scoreboard(message['scoreboard'])
                
            self.disable_answer_controls()
            
        elif msg_type == 'player_disconnected':
            player = message.get('player', 'Unknown')
            self.log(f"WARNING: Player '{player}' has disconnected")
            
        elif msg_type == 'game_end':
            self.log("=== GAME ENDED ===")
            self.log(f"Reason: {message.get('reason', 'Unknown')}")
            self.log(message.get('winner_message', ''))
            
            self.log("Final Scoreboard:")
            for p in message.get('final_scoreboard', []):
                self.log(f"  #{p['rank']} {p['name']}: {p['score']} points")
                
            if 'final_scoreboard' in message:
                self.update_scoreboard(message['final_scoreboard'])
                
            self.clear_question()
            
            # winnr popup
            winner_msg = message.get('winner_message', 'Game Over!')
            messagebox.showinfo("Game Over", winner_msg)
            
            # cleaup
            self.cleanup_connection()
            
        elif msg_type == 'error':
            self.log(f"ERROR: {message.get('message', 'Unknown error')}")
            
    def handle_disconnect(self, reason):
        self.log(f"Disconnected: {reason}")
        self.cleanup_connection()
        messagebox.showwarning("Disconnected", reason)
        
    def submit_answer(self):
        answer = self.answer_var.get()
        
        if not answer:
            messagebox.showwarning("Warning", "Please select an answer (A, B, or C)")
            return
            
        if not self.is_connected or not self.client_socket:
            messagebox.showerror("Error", "Not connected to server")
            return
            
        try:
            self.client_socket.send(json.dumps({
                'type': 'answer',
                'answer': answer
            }).encode())
            
            self.log(f"Submitted answer: {answer}")
            self.disable_answer_controls()
            self.result_label.config(text="Waiting for other players...", fg="#ffd700")
            
        except Exception as e:
            self.log(f"ERROR: Failed to submit answer - {str(e)}")
            messagebox.showerror("Error", f"Failed to submit answer: {str(e)}")
            
    def on_closing(self):
        if self.is_connected:
            try:
                self.client_socket.send(json.dumps({'type': 'disconnect'}).encode())
            except:
                pass
                
        self.is_connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizClient(root)
    root.mainloop()
