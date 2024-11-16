from llama_cpp import Llama
import datetime

# Inisialisasi model Llama 2
MODEL_PATH = "../asset/llama-2-7b.Q8_0.gguf"
llm = Llama(model_path=MODEL_PATH)

# State management untuk menyimpan riwayat percakapan
conversation_history = []

# Daftar pertanyaan yang akan diajukan
questions = [
    "Bagaimana aktivitas Anda hari ini?",
    "Bagaimana perasaan Anda saat ini?",
    "Apakah ada masalah atau kekhawatiran yang Anda rasakan?",
    "Seberapa puas Anda dengan aktivitas harian Anda dari skala 1-10?",
    "Bagaimana kondisi fisik Anda hari ini? Ada keluhan kesehatan?",
    "Lingkungan sekitar Anda nyaman atau ada hal yang mengganggu?",
    "Adakah kegiatan yang sangat Anda sukai atau hindari hari ini?"
]

# State management untuk mengingat posisi percakapan
conversation_state = {"current_question_index": 0}

# Fungsi untuk mengajukan pertanyaan berdasarkan state
def ask_question(state):
    index = state["current_question_index"]
    if index < len(questions):
        return questions[index]
    else:
        return "Terima kasih atas waktu Anda. Apakah ada hal lain yang ingin Anda bicarakan?"

# Fungsi untuk mendapatkan respons dari Llama 2
def get_llama_response(user_input, history):
    # Gabungkan riwayat percakapan dengan input user saat ini
    context = "\n".join(history) + f"\nUser: {user_input}\nChatbot:"
    
    # Menggunakan model Llama untuk menghasilkan respons
    response = llm(
        prompt=context,
        max_tokens=150,
        stop=["User:", "Chatbot:"],
        temperature=0.7
    )
    return response["choices"][0]["text"].strip()

# Fungsi chatbot flow
def chatbot_flow():
    print("Halo! Saya chatbot terapis Anda yang superkepo dan siap mendengarkan.")
    
    while conversation_state["current_question_index"] < len(questions):
        # Ajukan pertanyaan berdasarkan state
        question = ask_question(conversation_state)
        print(f"Chatbot: {question}")
        
        # Mendapatkan input dari user
        user_input = input("User: ")
        
        # Menghentikan percakapan jika user ingin berhenti
        if user_input.lower() in ["selesai", "stop", "tidak mau jawab"]:
            print("Chatbot: Terima kasih telah berbagi. Semoga hari Anda menyenangkan!")
            break
        
        # Validasi respons user
        if not user_input.strip():
            print("Chatbot: Saya tidak mendengar jawaban Anda, bisa ulangi?")
            continue
        
        # Tambahkan input user ke riwayat percakapan
        conversation_history.append(f"User: {user_input}")
        
        # Dapatkan respons dari model Llama 2
        chatbot_response = get_llama_response(user_input, conversation_history)
        print(f"Chatbot: {chatbot_response}")
        
        # Tambahkan respons chatbot ke riwayat percakapan
        conversation_history.append(f"Chatbot: {chatbot_response}")
        
        # Update state ke pertanyaan berikutnya
        conversation_state["current_question_index"] += 1

    print("Chatbot: Semua pertanyaan sudah selesai. Terima kasih atas waktu Anda!")

# Jalankan chatbot
chatbot_flow()