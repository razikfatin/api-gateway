FROM python:3.10-slim
WORKDIR /app
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY app.py ./
EXPOSE 5001
CMD ["python", "app.py"]