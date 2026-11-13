FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        siege curl && \
    rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
