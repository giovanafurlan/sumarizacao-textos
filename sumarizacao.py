from flask import Flask, request, jsonify
from docx import Document
from transformers import pipeline
import os
import tempfile

app = Flask(__name__)

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

def read_docx(docx_path):
    """
    Reads the text from a .docx document.
    :param docx_path: Path to the .docx document
    :return: Full text of the document
    """
    document = Document(docx_path)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return "".join(full_text)

def summarize_text(text, max_length=130, min_length=30, do_sample=False):
    """
    Summarizes a text.
    :param text: Text to be summarized
    :param max_length: Maximum length of the summary
    :param min_length: Minimum length of the summary
    :param do_sample: If True, use sampling; if False, use truncation
    :return: Summary of the text
    """
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=do_sample)
    return summary[0]['summary_text']

@app.route('/summarize', methods=['POST'])
def summarize_document():
    # Check if the request has a file part
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    # Save the uploaded .docx file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
        file.save(temp_docx.name)
        temp_docx_path = temp_docx.name
    
    # Read and summarize the document
    try:
        full_text = read_docx(temp_docx_path)
        summary = summarize_text(full_text, max_length=200, min_length=50)
    finally:
        # Clean up the temporary file
        os.remove(temp_docx_path)
    
    # Return the summary as JSON
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
