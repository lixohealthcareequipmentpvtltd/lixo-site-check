#!/usr/bin/env bash
# check.sh [URL] — is the Lixo live site AND its database answering?
# Exit 0 = HTTP 200 on one of TRIES tries (WAIT seconds apart); exit 1 = down. One blip does not count as down.
set -u
URL=${1:-https://erp.lixo.co.in/health/ready}
TRIES=${TRIES:-2}
WAIT=${WAIT:-20}
code=000
for i in $(seq 1 "$TRIES"); do
  code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' "$URL" 2>/dev/null) || true
  code=${code:-000}
  if [ "$code" = 200 ]; then echo "UP   $URL  HTTP 200 (try $i)"; exit 0; fi
  echo "try $i: $URL  HTTP $code"
  if [ "$i" -lt "$TRIES" ]; then sleep "$WAIT"; fi
done
echo "DOWN $URL  HTTP $code after $TRIES tries"
exit 1
