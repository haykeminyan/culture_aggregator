FROM python:3.13 as base
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base as build
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Default command
CMD ["./entrypoint.sh"]
