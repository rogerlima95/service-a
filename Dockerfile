FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV FLASK_RUN_PORT 80
EXPOSE 80
CMD ["python", "app.py"]