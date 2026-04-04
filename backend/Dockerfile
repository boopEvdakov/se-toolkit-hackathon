FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY app/ ./app/
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh
RUN uv pip install --system -e .

EXPOSE 8000

CMD ["./entrypoint.sh"]
