FROM python:3.10

ENV PYTHON_VERSION=3.10 \
    PYTHONUNBUFFERED=1 \
    WORKDIR=/app/
WORKDIR $WORKDIR

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python", "main.py"]

EXPOSE 8080:8080