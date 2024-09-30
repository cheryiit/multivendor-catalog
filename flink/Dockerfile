FROM flink:1.16.1

# Gerekli Python paketlerini yükleyin
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir requests psycopg2-binary

# İşlerinizi koyacağınız dizin
WORKDIR /flink_jobs

# Flink job dosyalarınızı kopyalayın
COPY ./backend/flink_jobs /flink_jobs