FROM flink:1.19.0

# Install dependencies including PostgreSQL dev libraries
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl libpq-dev gcc && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /flink_jobs

# Copy Flink job files
COPY ./backend/flink_jobs /flink_jobs

# Copy the entire backend directory into the root of the container
COPY ./backend /backend

# Set PYTHONPATH to include the root directory so that 'backend' is in the Python path
ENV PYTHONPATH="/"

# Create logs directory and set permissions
RUN mkdir -p /flink_jobs/logs && chmod -R 777 /flink_jobs/logs

RUN curl -L -o /opt/flink/lib/flink-connector-kafka-1.17.2.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
RUN curl -L -o /opt/flink/lib/flink-sql-connector-kafka-3.2.0-1.19.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
RUN curl -L -o /opt/flink/lib/kafka-clients-2.8.0.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.0/kafka-clients-2.8.0.jar

# Default command
CMD ["flink", "run", "-d", "-py", "/flink_jobs/flink_job.py", "--pyRequirements", "/opt/flink/requirements.txt"]
