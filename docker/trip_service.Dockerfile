FROM dgdo-python-base

WORKDIR /app
COPY services/python/trip_server.py .

EXPOSE 50052
CMD ["python", "trip_server.py"]
