FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT [ "python3", "run.py" ]
EXPOSE 80