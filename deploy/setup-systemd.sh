#!/bin/bash
# Átállás cron @reboot + run.sh helyett systemd-re. Egyszeri futtatás a célgépen,
# a szolgáltatást futtató felhasználóként (sudo joggal):  bash deploy/setup-systemd.sh
# Újrafuttatható; a meglévő /etc/senechal.env fájlt nem írja felül.
set -euo pipefail

APP_USER="$(id -un)"
BACKEND="$(cd "$(dirname "$0")/.." && pwd)"
BASE="$(dirname "$BACKEND")"
FRONTEND="${BASE}/AngrySenechal2"
RUN_SH="${RUN_SH:-${BASE}/run.sh}"
ENV_FILE="/etc/senechal.env"

[ "$APP_USER" != "root" ] || { echo "Ne root-ként futtasd, hanem a szolgáltatás felhasználójaként."; exit 1; }
[ -x "${BACKEND}/venv/bin/python3" ] || { echo "Hiányzik: ${BACKEND}/venv/bin/python3"; exit 1; }
[ -f "$RUN_SH" ] || [ -f "$ENV_FILE" ] || { echo "Nincs ${RUN_SH}, ebből nyerném ki a környezeti változókat (RUN_SH=... felülírja)."; exit 1; }

NG_BIN="$(command -v ng || true)"
sudo -v

echo "== 1/6 Környezeti fájl (${ENV_FILE})"
if [ -f "$ENV_FILE" ]; then
  echo "   már létezik, nem írom felül"
else
  # a run.sh 'export KEY=value' soraiból KEY=value (külső idézőjelek nélkül)
  grep -E '^[[:space:]]*export[[:space:]]+[A-Za-z_][A-Za-z0-9_]*=' "$RUN_SH" \
    | sed -E 's/^[[:space:]]*export[[:space:]]+//' \
    | sed -E "s/^([A-Za-z_][A-Za-z0-9_]*)=[\"'](.*)[\"']$/\1=\2/" \
    | sudo tee "$ENV_FILE" >/dev/null
  sudo chown root:"$APP_USER" "$ENV_FILE"
  sudo chmod 640 "$ENV_FILE"
  echo "   létrehozva; kulcsok: $(sudo cut -d= -f1 "$ENV_FILE" | tr '\n' ' ')"
fi
for k in token DATABASE_URL; do
  sudo grep -q "^${k}=." "$ENV_FILE" || { echo "HIBA: ${k} hiányzik/üres a ${ENV_FILE}-ban"; exit 1; }
done

echo "== 2/6 systemd unitok"
sudo tee /etc/systemd/system/senechal.service >/dev/null <<UNIT
[Unit]
Description=Senechal API + Discord bot
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
User=${APP_USER}
WorkingDirectory=${BACKEND}
EnvironmentFile=${ENV_FILE}
ExecStart=${BACKEND}/venv/bin/python3 server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

UNITS="senechal"
if [ -n "$NG_BIN" ] && [ -d "$FRONTEND" ]; then
  NG_DIR="$(dirname "$(readlink -f "$NG_BIN")")"
  sudo tee /etc/systemd/system/senechal-ng.service >/dev/null <<UNIT
[Unit]
Description=Senechal Angular dev server (ng serve)
After=network-online.target

[Service]
User=${APP_USER}
WorkingDirectory=${FRONTEND}
Environment=PATH=${NG_DIR}:/usr/local/bin:/usr/bin:/bin
ExecStart=${NG_BIN} serve
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
  UNITS="senechal senechal-ng"
else
  echo "   FIGYELEM: 'ng' vagy ${FRONTEND} nem található, a frontend unit kimarad."
fi

echo "== 3/6 deploy.sh"
chmod +x "${BACKEND}/deploy/deploy.sh"
echo "   ${BACKEND}/deploy/deploy.sh"

echo "== 4/6 sudoers (jelszó nélküli restart)"
SUDO_TMP="$(mktemp)"
{
  echo "${APP_USER} ALL=(root) NOPASSWD: /bin/systemctl restart senechal, /bin/systemctl restart senechal-ng"
  echo "${APP_USER} ALL=(root) NOPASSWD: /usr/bin/systemctl restart senechal, /usr/bin/systemctl restart senechal-ng"
} > "$SUDO_TMP"
sudo visudo -cf "$SUDO_TMP" >/dev/null
sudo install -m 440 -o root -g root "$SUDO_TMP" /etc/sudoers.d/senechal
rm -f "$SUDO_TMP"

echo "== 5/6 régi folyamatok leállítása, cron @reboot sor törlése"
crontab -l > "${BASE}/crontab.backup.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
if crontab -l 2>/dev/null | grep -q 'run\.sh'; then
  crontab -l | grep -v 'run\.sh' | crontab -
fi
pkill -f "venv/bin/python3 server.py" 2>/dev/null || true
pkill -f "ng serve" 2>/dev/null || true
sleep 2
# a nyers titkokat tartalmazó fájl ne maradjon használatban
if [ -f "$RUN_SH" ]; then mv "$RUN_SH" "${RUN_SH}.old"; fi

echo "== 6/6 indítás"
sudo systemctl daemon-reload
# shellcheck disable=SC2086
sudo systemctl enable --now $UNITS
sleep 5
# shellcheck disable=SC2086
systemctl --no-pager --lines=8 status $UNITS || true

cat <<MSG

Kész.
  Logok:   journalctl -u senechal -f   (frontend: journalctl -u senechal-ng -f)
  Deploy:  ${BACKEND}/deploy/deploy.sh
  Régi script: ${RUN_SH}.old — a titkok átkerültek ${ENV_FILE}-ba, a régi fájlt töröld
  (shred -u), és a Discord tokent/secretet érdemes lecserélni.
MSG
