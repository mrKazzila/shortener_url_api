# Create kafka topics if not exist
[group('Kafka')]
kafka-topics partitions:
    @echo "[broker] Creating Kafka topics with {{partitions}} partitions..."
    @docker exec kafka /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server kafka:9092 --create --topic new-urls --partitions {{partitions}} --replication-factor 1 || true
    @docker exec kafka /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server kafka:9092 --create --topic update-urls --partitions {{partitions}} --replication-factor 1 || true
    @echo "[broker] Kafka topics created."

# Scaling kafka consumers
[group('Kafka')]
consumers-scale replicas:
    @echo "[app] Scaling consumers to {{replicas}} replicas..."
    {{APP}} up -d \
        --scale consumer={{replicas}} \
        --scale consumer-update={{replicas}}
    @echo "[app] Consumers scaled."
