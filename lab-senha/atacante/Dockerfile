FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        john curl ca-certificates gobuster && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /lab
COPY wordlist.txt /lab/wordlist.txt
COPY dir_wordlist.txt /lab/dir_wordlist.txt

CMD ["tail", "-f", "/dev/null"]
