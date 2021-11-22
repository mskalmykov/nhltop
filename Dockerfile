FROM python:3.9 as builder
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get -y install libmariadb3 libmariadb-dev
RUN pip install --upgrade pip
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim
RUN apt-get update && apt-get -y install libmariadb3 libmariadb-dev
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
WORKDIR /app
COPY ./nhltop.py .
COPY ./app.py .
EXPOSE 5000
CMD ["python", "-m", "flask", "run", "-h", "0.0.0.0"]
