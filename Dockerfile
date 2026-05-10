FROM python:3.14
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN chown -R appuser:appuser /app
USER appuser