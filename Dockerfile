FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src

RUN chmod +x ./build.sh ./test.sh

CMD ["./build.sh"]
