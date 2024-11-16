from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
model_path = "Model"
tokenizer_path = "Model"

tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

model = AutoModelForSequenceClassification.from_pretrained(model_path)

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

input = "saya merasa cemas hari ini karena tugas saya nilainya jelek"

preds = classifier(input)

for pred in preds:
    print(f"Label: {pred['label']}, Score: {pred['score']:.4f}")

highest_score_prediction = max(preds, key=lambda x: x['score'])
print("Predicted label:", highest_score_prediction['label'])
print("Confidence score:", highest_score_prediction['score'])