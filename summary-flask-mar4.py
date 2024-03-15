from flask import Flask, request, render_template
import docx2txt
import re
from transformers import pipeline

app = Flask(__name__)

# Load the summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

@app.route('/', methods=['GET'])
def index():
    # Serve the index page
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No selected file')
    if file:
        text = docx2txt.process(file)
        # Extract specific section using regex
        pattern = r'(?<=Project Description:).*?(?=Reporting to:)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted_text = match.group(0).strip()
            # Summarize the extracted text
            summary = summarizer(extracted_text, max_length=130, min_length=30, do_sample=False)
            summary_text = summary[0]['summary_text']
            # Render the result page with the summary
            return render_template('result.html', summary=summary_text)
        else:
            return render_template('index.html', error='No relevant section found.')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
