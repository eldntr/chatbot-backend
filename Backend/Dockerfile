# Gunakan image dasar Python
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# Salin requirements.txt dan instal dependensi
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Salin seluruh kode aplikasi
COPY . .

# Jalankan aplikasi
CMD ["python", "app.py"]