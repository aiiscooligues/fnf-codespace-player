FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    WINEPREFIX=/wine \
    WINEDEBUG=-all

RUN dpkg --add-architecture i386 \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      wine64 wine32:i386 p7zip-full xvfb fluxbox x11vnc novnc websockify python3 ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /games /config /wine

COPY entrypoint.sh /entrypoint.sh
COPY allowlist.example.json /config/allowlist.json
RUN chmod +x /entrypoint.sh

VOLUME ["/games", "/config", "/wine"]
EXPOSE 6080
ENTRYPOINT ["/entrypoint.sh"]
