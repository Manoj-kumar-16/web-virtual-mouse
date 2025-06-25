from flask import Flask, render_template, request, redirect
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/virtual_mouse', methods=['POST'])
def virtual_mouse():
    subprocess.Popen(["python", "virtual_mouse.py"])
    return render_template('index.html', output_text="Virtual Mouse Activated")

@app.route('/personal_assistant', methods=['POST'])
def personal_assistant():
    subprocess.Popen(["python", "personal_assistant.py"])
    return render_template('index.html', output_text="Personal Assistant Launched")

if __name__ == '__main__':
    app.run(debug=True)
