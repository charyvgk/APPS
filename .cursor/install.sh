#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

dotnet restore src/CentralFlagging.sln
dotnet build src/CentralFlagging.sln --no-restore -c Release
