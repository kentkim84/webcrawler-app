FROM postgres:15

# Install pgvector extension
RUN apt-get update && \
    apt-get install -y postgresql-15-pgvector && \
    rm -rf /var/lib/apt/lists/*

# Copy initialization SQL scripts
COPY init.sql /docker-entrypoint-initdb.d/

# Expose Postgres port
EXPOSE 5432