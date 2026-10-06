#!/bin/bash
# git pull + függőségek + újraindítás rebootolás nélkül.
# A setup-systemd.sh telepíti a service-eket és a sudoers szabályt.
# (A fájl egy blokkban fut, mert a git pull felülírhatja önmagát.)
{
set -euo pipefail
BACKEND="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$(cd "$BACKEND/../AngrySenechal2" 2>/dev/null && pwd || true)"

# changed <könyvtár> <fájl> <régi-rev>
changed() { ! git -C "$1" diff --quiet "$3" HEAD -- "$2"; }

cd "$BACKEND"
OLD=$(git rev-parse HEAD)
git pull --ff-only
if changed . requirements.txt "$OLD"; then venv/bin/pip install -r requirements.txt; fi
sudo systemctl restart senechal

if [ -n "$FRONTEND" ] && [ -d "$FRONTEND/.git" ]; then
  cd "$FRONTEND"
  OLD=$(git rev-parse HEAD)
  git pull --ff-only
  # az ng serve figyeli a fájlokat; csak függőségváltozásnál kell újraindítani
  if changed . package-lock.json "$OLD"; then
    npm ci
    if systemctl cat senechal-ng >/dev/null 2>&1; then sudo systemctl restart senechal-ng; fi
  fi
fi
sleep 3
systemctl --no-pager --lines=5 status senechal || true
exit
}
