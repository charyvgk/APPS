FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Match the default Cloud Agent runtime user when present.
RUN if ! id ubuntu >/dev/null 2>&1; then \
      useradd -m -s /bin/bash ubuntu; \
    fi

USER ubuntu
WORKDIR /home/ubuntu
