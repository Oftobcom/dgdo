FROM dgdo-python-base

WORKDIR /app
COPY services/python/trip_request_server.py .

EXPOSE 50051
CMD ["python", "trip_request_server.py"]
