FROM python:3.11-slim

WORKDIR /app 

COPY pyproject.toml .
RUN poetry install 
COPY . .

CMD [ "poetry", "run", "python", "src/adem/main.py"]