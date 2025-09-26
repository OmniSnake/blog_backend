FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]