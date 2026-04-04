FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY *.py ./
COPY handlers/ handlers/
COPY services/ services/

RUN uv pip install --system -e .

CMD ["python", "bot.py"]
