FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    XDG_RUNTIME_DIR=/tmp/runtime-root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      retroarch retroarch-assets \
      libretro-nestopia libretro-snes9x libretro-genesis-plus-gx \
      libretro-mgba libretro-gambatte libretro-ppsspp \
      xvfb fluxbox x11vnc novnc websockify ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /roms /config /tmp/runtime-root \
 && chmod 700 /tmp/runtime-root

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/roms", "/config"]
EXPOSE 6090
ENTRYPOINT ["/entrypoint.sh"]
