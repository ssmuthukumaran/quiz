from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM Categories').fetchall()
    conn.close()
    return render_template('index.html', categories=categories)

@app.route('/quiz/<int:subject_id>')
def quiz(subject_id):
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM Questions WHERE category_id = ?', (subject_id,)).fetchall()
    conn.close()
    
    if not questions:
        return "No questions available for this category."

    # Start with the first question
    session['current_question_index'] = 0
    session['questions'] = [dict(q) for q in questions]  # Convert rows to dictionaries
    return redirect(url_for('question'))

@app.route('/question')
def question():
    current_question_index = session.get('current_question_index', 0)
    questions = session.get('questions', [])
    
    if current_question_index >= len(questions):
        return redirect(url_for('result'))
    
    question = questions[current_question_index]
    conn = get_db_connection()
    print("current question index", current_question_index)
    print ("question ", questions[current_question_index])
    print("question id ", question['id'])
    options = conn.execute('SELECT * FROM ans_options WHERE question_id = ?', (question['id'],)).fetchall()
    conn.close()
    for i in options:
        print("options are ", i)
    # Convert options to a list of dictionaries
    option_texts = [dict(option) for option in options]
    option_texts.append({'wr_question': question['cor_answer']})  # Add the correct answer to the options

    for i in option_texts:
        print ("options: ", i)
    return render_template('question.html', question=question, options=option_texts)

@app.route('/answer', methods=['POST'])
def answer():
    question_id = request.form['question_id']
    selected_option = request.form['selected_option']
    
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM Questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()
    
    correct = selected_option == question['cor_answer']
    session['current_question_index'] += 1
    return render_template('answer.html', correct=correct, question=question)

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
