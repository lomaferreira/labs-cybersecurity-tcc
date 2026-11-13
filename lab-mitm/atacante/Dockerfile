FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        dsniff tcpdump nmap iproute2 curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /lab

CMD ["tail", "-f", "/dev/null"]
