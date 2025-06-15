FROM python:3.11-bookworm

WORKDIR /app

COPY . .

RUN chmod +x /app/docker/entrypoint.sh

RUN mv config config-default

RUN pip install .

ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD ["python", "main.py"]
