import requests
import html
import json
import os
import random
import time
from config import WINDOW_WIDTH, FONT_SIZE, FONT_PATH

class GameLogic:
    def __init__(self, session_length=61000, question_time=9000, answer_time=2000):
        print("Initializing GameLogic...")
        start_time = time.time()
        
        self.session_length = session_length
        self.question_time = question_time
        self.answer_time = answer_time
        self.USED_QUESTIONS_FILE = "used_questions.json"
        self.used_questions = set()
        
        print("Loading used questions from file...")
        if os.path.exists(self.USED_QUESTIONS_FILE):
            with open(self.USED_QUESTIONS_FILE, 'r') as f:
                try:
                    self.used_questions = set(json.load(f))
                    print(f"Loaded {len(self.used_questions)} used questions")
                except Exception as e:
                    print(f"Error loading used questions: {e}")
                    self.used_questions = set()
        
        print("Fetching new questions from API...")
        self.questions = self.fetch_questions()
        if not self.questions:
            raise Exception("No new questions available. Please clear used_questions.json if you want to repeat questions.")
        
        print(f"Successfully loaded {len(self.questions)} questions")
        self.current_index = 0
        self.show_answer = False
        self.last_switch_time = 0
        self.session_start_time = 0
        self.show_time = 0
        self.session_should_end = False
        
        end_time = time.time()
        print(f"GameLogic initialized in {end_time - start_time:.2f} seconds")

    def fetch_questions(self):
        print("Making API request to Open Trivia Database...")
        start_time = time.time()
        
        API_URL = "https://opentdb.com/api.php?amount=6"
        try:
            response = requests.get(API_URL)
            data = response.json()
            print(f"API response received in {time.time() - start_time:.2f} seconds")
            
            questions = []
            print("Processing questions...")
            for item in data["results"]:
                qid = item["question"] + "|" + item["correct_answer"]
                if qid in self.used_questions:
                    continue
                qtype = item["type"]
                question = html.unescape(item["question"])
                difficulty = item["difficulty"].capitalize()
                if qtype == "boolean":
                    choices = ["True", "False"]
                    answer = 0 if item["correct_answer"] == "True" else 1
                else:
                    choices = [html.unescape(ans) for ans in item["incorrect_answers"]]
                    idx = random.randint(0, len(choices))
                    choices.insert(idx, html.unescape(item["correct_answer"]))
                    answer = idx
                questions.append({
                    "question": question,
                    "choices": choices,
                    "answer": answer,
                    "type": qtype,
                    "difficulty": difficulty,
                    "qid": qid
                })
            
            print(f"Processed {len(questions)} new questions")
            return questions
            
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return []

    def start(self, now):
        self.last_switch_time = now
        self.session_start_time = now
        self.show_answer = False
        self.current_index = 0
        self.session_should_end = False

    def update(self, now):
        elapsed = now - self.last_switch_time
        session_elapsed = now - self.session_start_time
        session_end = False
        question_end = False
        if not self.session_should_end and session_elapsed >= self.session_length:
            self.session_should_end = True
        if not self.show_answer and elapsed >= self.question_time:
            self.show_answer = True
            self.show_time = now
        if self.show_answer and now - self.show_time >= self.answer_time:
            # Save used question
            self.used_questions.add(self.questions[self.current_index]["qid"])
            self.current_index += 1
            if self.current_index >= len(self.questions):
                session_end = True
            elif self.session_should_end:
                session_end = True
            else:
                self.last_switch_time = now
                self.show_answer = False
            question_end = True
        return session_end, question_end

    def get_current(self):
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index], self.show_answer, self.last_switch_time

    def save_used(self):
        with open(self.USED_QUESTIONS_FILE, 'w') as f:
            json.dump(list(self.used_questions), f) 