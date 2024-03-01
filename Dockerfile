FROM ghcr.io/mgoltzsche/mopidy:0.12.0

# Install bats
USER root:root
ARG BATS_VERSION=1.10.0
RUN set -eux; \
	wget -qO - https://github.com/bats-core/bats-core/archive/refs/tags/v${BATS_VERSION}.tar.gz | tar -C /tmp -xzf -; \
	/tmp/bats-core-$BATS_VERSION/install.sh /opt/bats; \
	ln -s /opt/bats/bin/bats /usr/local/bin/bats; \
	rm -rf /tmp/bats-core-$BATS_VERSION

COPY mopidy.conf /etc/mopidy/mopidy.conf

# Install mopidy-webm3u extension from source
COPY dist /extension/dist
RUN python -m pip install /extension/dist/*
USER mopidy:audio
