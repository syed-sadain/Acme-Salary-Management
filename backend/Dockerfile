FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake a fully-seeded 10k-employee database into the image so the container is
# immediately demo-able. In a real deployment this would instead run against a
# persistent volume / managed Postgres and seeding would be a one-off job.
RUN python seed.py --count 10000 --reset

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
