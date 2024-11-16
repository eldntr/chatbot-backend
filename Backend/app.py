from flask import Flask, request, jsonify
from pymongo import MongoClient
from auth import auth_bp
from journal import journal_bp
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from chatbot import chatbot_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(journal_bp, url_prefix='/journal')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')


client = MongoClient('mongo', 27017)  # 'mongo' adalah nama layanan di docker-compose.yml
db = client['chat_db']
messages_collection = db['messages']

model_path = "Model"
tokenizer_path = "Model"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/sentiment', methods=['POST'])
def sentiment_analysis():
    data = request.json
    input_text = data.get('text', '')
    preds = classifier(input_text)
    return jsonify(preds), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')