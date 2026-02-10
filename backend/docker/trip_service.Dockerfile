FROM dgdo-python-base

WORKDIR /app
COPY services/python/trip_server.py .

EXPOSE 50053
CMD ["python", "trip_server.py"]
