FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --uid 1000 --create-home app && mkdir /data && chown app:app /data
COPY backend/app ./app
COPY backend/db ./db
COPY backend/pipeline ./pipeline
COPY deploy/start.py ./start.py
USER app
EXPOSE 8000
CMD ["python", "start.py"]
