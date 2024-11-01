import uuid
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import chardet


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rag_data.db'
db = SQLAlchemy(app)

class RagData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag1 = db.Column(db.Text)
    tag2 = db.Column(db.Text)
    tag3 = db.Column(db.Text)
    tag4 = db.Column(db.Text)
    tag5 = db.Column(db.Text)
    key = db.Column(db.Text)
    information = db.Column(db.Text)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET','POST'])
def index():
    return ''

@app.route('/rags', methods=['GET'])
def get_all_rags():
    rags = RagData.query.all()
    return jsonify([{
        "id": rag.id,
        "tag1": rag.tag1,
        "tag2": rag.tag2,
        "tag3": rag.tag3,
        "tag4": rag.tag4,
        "tag5": rag.tag5,
        "key": rag.key,
        "information": rag.information,
        "last_update": rag.last_update
    } for rag in rags])

@app.route('/rag', methods=['POST'])
def create_rag():
    data = request.json
    new_rag = RagData(
        tag1=data['tag1'],
        tag2=data['tag2'],
        tag3=data['tag3'],
        tag4=data['tag4'],
        tag5=data['tag5'],
        key=data['key'],
        information=data['information']
    )
    db.session.add(new_rag)
    db.session.commit()
    return jsonify({"message": "RAG data created successfully", "id": new_rag.id}), 201

@app.route('/rag/<int:rag_id>', methods=['GET'])
def read_rag(rag_id):
    rag = RagData.query.get_or_404(rag_id)
    return jsonify({
        "id": rag.id,
        "tag1": rag.tag1,
        "tag2": rag.tag2,
        "tag3": rag.tag3,
        "tag4": rag.tag4,
        "tag5": rag.tag5,
        "key": rag.key,
        "information": rag.information,
        "last_update": rag.last_update
    })

@app.route('/rag/<int:rag_id>', methods=['PUT'])
def update_rag(rag_id):
    rag = RagData.query.get_or_404(rag_id)
    data = request.json
    rag.tag1 = data.get('tag1', rag.tag1)
    rag.tag2 = data.get('tag2', rag.tag2)
    rag.tag3 = data.get('tag3', rag.tag3)
    rag.tag4 = data.get('tag4', rag.tag4)
    rag.tag5 = data.get('tag5', rag.tag5)
    rag.key = data.get('key', rag.key)
    rag.information = data.get('information', rag.information)
    rag.last_update = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "RAG data updated successfully"})

@app.route('/rag/<int:rag_id>', methods=['DELETE'])
def delete_rag(rag_id):
    rag = RagData.query.get_or_404(rag_id)
    db.session.delete(rag)
    db.session.commit()
    return jsonify({"message": "RAG data deleted successfully"})

############################
# chat
############################
def read_file_with_auto_detect_encoding(file_path):
  # Detect the file's encoding
  with open(file_path, 'rb') as file:
      raw_data = file.read()
  detected = chardet.detect(raw_data)
  encoding = detected['encoding']

  # Try to read the file with the detected encoding
  try:
      with open(file_path, 'r', encoding=encoding) as file:
          return file.read()
  except UnicodeDecodeError:
      # If that fails, try UTF-8
      try:
          with open(file_path, 'r', encoding='utf-8') as file:
              return file.read()
      except UnicodeDecodeError:
          # If UTF-8 also fails, try with errors='ignore'
          with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
              return file.read()

def combine_txt_files():
  combined_content = ""
  file_list = []
  for filename in os.listdir('.'):
      if filename.endswith('.txt'):
          file_list.append(filename)
          content = read_file_with_auto_detect_encoding(filename)
          combined_content += f"\n\n--- Content of {filename} ---\n\n"
          combined_content += content
  return combined_content, file_list

def count_words_and_chars(text):
  words = text.split()
  word_count = len(words)
  char_count = len(text)
  return f"Jumlah kata: {word_count} dan jumlah karakter: {char_count}"

# Initialize these variables globally
combined_content, file_list = combine_txt_files()
llm = Ollama(model="llama3.2:1b-instruct-q8_0",base_url="http://192.168.5.6:11434")
prompt_template = PromptTemplate(
  input_variables=["document", "question"],
  template="""
  Kamu adalah seorang Asisten AI yang ditugaskan untuk menjawab berdasarkan dokumen berikut:

  {document}

  Jawablah pertanyaan hanya berdasarkan konteks yang diberikan:

  Pertanyaan: {question}

  Jawaban:
  """
)
llm_chain = LLMChain(llm=llm, prompt=prompt_template)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
  if request.method == 'POST':
      data = request.json
      query = data.get('query', '')
      all_rag_data = RagData.query.all()
      combined_content = ' '.join([entry.information for entry in all_rag_data])
      response = llm_chain.run(document=combined_content, question=query)
      return jsonify({'response': response})
  
  stats = count_words_and_chars(combined_content)
  return render_template('chat.html', file_list=file_list, stats=stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        def add_sample_data():
            sample_data = [
                {
                    "tag1": "AI", "tag2": "Machine Learning", "tag3": "Neural Networks",
                    "tag4": "Deep Learning", "tag5": "Computer Vision",
                    "key": "ai_basics", "information": "Introduction to AI and its subfields"
                },
                {
                    "tag1": "Programming", "tag2": "Python", "tag3": "Data Structures",
                    "tag4": "Algorithms", "tag5": "Software Engineering",
                    "key": "python_fundamentals", "information": "Core concepts of Python programming"
                },
                {
                    "tag1": "Database", "tag2": "SQL", "tag3": "NoSQL",
                    "tag4": "Data Modeling", "tag5": "Query Optimization",
                    "key": "database_systems", "information": "Overview of database management systems"
                },
                {
                    "tag1": "Web Development", "tag2": "HTML", "tag3": "CSS",
                    "tag4": "JavaScript", "tag5": "React",
                    "key": "web_dev_basics", "information": "Fundamentals of web development"
                },
                {
                    "tag1": "Cloud Computing", "tag2": "AWS", "tag3": "Azure",
                    "tag4": "Google Cloud", "tag5": "Serverless",
                    "key": "cloud_platforms", "information": "Introduction to major cloud platforms"
                },
                {
                    "tag1": "Data Science", "tag2": "Statistics", "tag3": "Data Analysis",
                    "tag4": "Visualization", "tag5": "Big Data",
                    "key": "data_science_intro", "information": "Key concepts in data science"
                },
                {
                    "tag1": "Cybersecurity", "tag2": "Network Security", "tag3": "Encryption",
                    "tag4": "Ethical Hacking", "tag5": "Incident Response",
                    "key": "security_fundamentals", "information": "Basic principles of cybersecurity"
                },
                {
                    "tag1": "Mobile Development", "tag2": "Android", "tag3": "iOS",
                    "tag4": "React Native", "tag5": "Flutter",
                    "key": "mobile_dev_platforms", "information": "Overview of mobile app development"
                },
                {
                    "tag1": "DevOps", "tag2": "CI/CD", "tag3": "Docker",
                    "tag4": "Kubernetes", "tag5": "Infrastructure as Code",
                    "key": "devops_practices", "information": "Introduction to DevOps methodologies"
                },
                {
                    "tag1": "Blockchain", "tag2": "Cryptocurrency", "tag3": "Smart Contracts",
                    "tag4": "Decentralized Apps", "tag5": "Consensus Algorithms",
                    "key": "blockchain_basics", "information": "Fundamentals of blockchain technology"
                }
            ]

            for data in sample_data:
                new_rag = RagData(
                    tag1=data["tag1"],
                    tag2=data["tag2"],
                    tag3=data["tag3"],
                    tag4=data["tag4"],
                    tag5=data["tag5"],
                    key=data["key"],
                    information=data["information"],
                    last_update=datetime.utcnow()
                )
                db.session.add(new_rag)
                db.session.commit()
        # add_sample_data()
        print("Sample data added successfully!")

    app.run(debug=True)


