FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Chạy init và seed (không cần xác nhận)
RUN python database/init_db.py
RUN python database/seed.py

EXPOSE 5000
CMD ["python", "app.py"]