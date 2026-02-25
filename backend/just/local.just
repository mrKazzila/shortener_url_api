[group('Local')]
[doc('Start grpcui on localhost:50051')]
grpcui:
    grpcui -plaintext localhost:50051

[group('Local')]
[doc('ghz Load test for CreateShortUrl')]
ghz-create:
    ghz --insecure \
      --proto ./proto/shortener/v1/shortener.proto \
      --call shortener.v1.ShortenerService.CreateShortUrl \
      -d '{"target_url":"https://example.com"}' \
      -c 50 \
      --duration 10s \
      --import-paths ./proto \
      localhost:50051

[group('Local')]
[doc('ghz Load test for ResolveKey')]
ghz-redirect key:
    ghz --insecure \
      --proto ./proto/shortener/v1/shortener.proto \
      --call shortener.v1.ShortenerService.ResolveKey \
      -d '{"key":"{{key}}"}' \
      -c 50 \
      --duration 10s \
      --import-paths ./proto \
      localhost:50051

[group('Local')]
[doc('oha Load test for POST create')]
oha-create:
    oha -z 10s -c 50 -m POST -H 'accept: application/json' -d '' 'http://localhost:8000/urls/?url=https%3A%2F%2Fwww.youtube.com%2F'

[group('Local')]
[doc('oha Load test for GET longurl')]
oha-redirect key:
    oha -z 10s -c 50 -r 0 -m GET -H 'accept: */*' 'http://localhost:8000/urls/{{key}}'
