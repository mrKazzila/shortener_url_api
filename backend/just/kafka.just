[group('Kafka')]
[doc('Create kafka topics if not exist')]
kafka-topics partitions:
    @echo "[broker] Creating Kafka topics with {{partitions}} partitions..."
    @{{INFRA}} exec -T kafka /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server kafka:9092 --create --if-not-exists \
        --topic new-urls --partitions {{partitions}} --replication-factor 1 > /dev/null

    @{{INFRA}} exec -T kafka /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server kafka:9092 --create --if-not-exists \
        --topic update-urls --partitions {{partitions}} --replication-factor 1 > /dev/null

    @echo "[broker] Kafka topics created."

[group('Kafka')]
[doc('Scaling kafka consumers')]
consumers-scale replicas:
    @echo "[app] Scaling consumers to {{replicas}} replicas..."
    {{APP}} up -d \
        --scale consumer={{replicas}} \
        --scale consumer-update={{replicas}} > /dev/null
    @echo "[app] Consumers scaled."
