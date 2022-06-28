FROM python:3.9.7

WORKDIR /app
COPY src /app/src
COPY templates /app/templates

WORKDIR /app/src
RUN pip install -r requirements.txt
CMD ["uvicorn", "codegen_api:app", "--host", "0.0.0.0", "--port", "5678"]
