FROM dgdo-python-base

WORKDIR /app
COPY services/python/telemetry_server.py .

EXPOSE 50054
CMD ["python", "telemetry_server.py"]
