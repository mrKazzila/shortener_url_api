# Start grpcui on localhost:50051
[group('Local')]
grpcui:
    grpcui -plaintext localhost:50051


# ghz Load test for CreateShortUrl
[group('Local')]
ghz-create:
    ghz --insecure \
      --proto ./proto/shortener/v1/shortener.proto \
      --call shortener.v1.ShortenerService.CreateShortUrl \
      -d '{"target_url":"https://example.com"}' \
      -c 50 \
      --duration 10s \
      --import-paths ./proto \
      localhost:50051


# ghz Load test for ResolveKey
[group('Local')]
ghz-redirect key:
    ghz --insecure \
      --proto ./proto/shortener/v1/shortener.proto \
      --call shortener.v1.ShortenerService.ResolveKey \
      -d '{"key":"{{key}}"}' \
      -c 50 \
      --duration 10s \
      --import-paths ./proto \
      localhost:50051

# oha Load test for POST create
[group('Local')]
oha-create:
    oha -z 10s -c 50 -m POST -H 'accept: application/json' -d '' 'http://localhost:8000/urls/?url=https%3A%2F%2Fwww.youtube.com%2F'


# oha Load test for GET longurl
[group('Local')]
oha-redirect key:
    oha -z 10s -c 50 -r 0 -m GET -H 'accept: */*' 'http://localhost:8000/urls/{{key}}'
