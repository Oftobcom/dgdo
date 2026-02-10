# -------------------------------
# Base image: official PostgreSQL
# -------------------------------
FROM postgres:15

# -------------------------------
# Labels / metadata
# -------------------------------
LABEL maintainer="Rahmatjon I. Hakimov <rahmatjon@gmail.com>"
LABEL description="PostgreSQL + PostGIS for DG Do project"

# -------------------------------
# Install PostGIS and utilities
# -------------------------------
RUN apt-get update && \
    apt-get install -y postgis postgresql-15-postgis-3 postgresql-15-postgis-3-scripts && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------
# Set default environment variables
# -------------------------------
ENV POSTGRES_USER=dgdo_admin
ENV POSTGRES_PASSWORD=dgdo_password
ENV POSTGRES_DB=dgdo_db
ENV POSTGRES_INITDB_WALDIR=/var/lib/postgresql/data/pg_wal

# -------------------------------
# Copy initialization SQL scripts
# These scripts will be executed when the container is created
# -------------------------------
COPY 001_init_schema.sql /docker-entrypoint-initdb.d/

# -------------------------------
# Expose default PostgreSQL port
# -------------------------------
EXPOSE 5432

# -------------------------------
# Use official entrypoint and command
# This will initialize Postgres and run any scripts in /docker-entrypoint-initdb.d/
# -------------------------------
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
