# Container image for the Uzbekistan Power Sector Transition Tracker (Plotly Dash).
# Works on Hugging Face Spaces (Docker SDK, port 7860) and any Docker host.
# Render uses render.yaml (native Python runtime) and ignores this file.
FROM python:3.11-slim

WORKDIR /app

# Install deps first so they cache across code changes.
COPY dashboard/requirements.txt ./dashboard/requirements.txt
RUN pip install --no-cache-dir -r dashboard/requirements.txt

# App code + the processed CSVs the dashboard reads (.dockerignore trims the rest).
COPY . .

EXPOSE 7860
CMD ["gunicorn", "--chdir", "dashboard", "app:server", \
     "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120"]
