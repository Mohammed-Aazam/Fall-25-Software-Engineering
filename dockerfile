FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the app (listening on all interfaces)
COPY boot.sh .
RUN chmod +x boot.sh

CMD ["./boot.sh"]
