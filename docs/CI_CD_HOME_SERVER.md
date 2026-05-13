# Private CI/CD for Home Server (No Public IP/DNS)

This setup is pull-based:
- GitHub runs CI only.
- Your Ubuntu server polls `main` every 2 minutes via `systemd` timer.
- No inbound internet access to server is required for deployment.

## Files added

- `deploy/scripts/deploy_on_server.sh`: deploy agent with lock, state, health-check, rollback
- `deploy/scripts/compute_version.py`: supports `ci` and `deploy` modes
- `deploy/systemd/kshethra-mithram-deploy.service`
- `deploy/systemd/kshethra-mithram-deploy.timer`
- `deploy/docker/daemon.json`: Docker log rotation
- `.github/workflows/ci.yml`: CI build/test only

## 1) Create dedicated deploy user

```bash
sudo adduser --system --home /opt/kshethra-mithram --group templedeploy
sudo usermod -aG docker templedeploy
sudo mkdir -p /opt/kshethra-mithram
sudo chown -R templedeploy:templedeploy /opt/kshethra-mithram
```

## 2) Clone repository with read-only access

Use either:
- deploy SSH key (read-only), or
- fine-grained PAT with read-only `contents`.

As `templedeploy`:

```bash
sudo -u templedeploy -H bash -lc
cd /opt/kshethra-mithram
git clone https://github.com/soorajerajeevan/kshethra-mithram.git .
chmod +x deploy/scripts/deploy_on_server.sh
'
```

## 3) Install and enable timer

```bash
sudo cp deploy/systemd/kshethra-mithram-deploy.service /etc/systemd/system/
sudo cp deploy/systemd/kshethra-mithram-deploy.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kshethra-mithram-deploy.timer
```

Check status/logs:

```bash
systemctl status kshethra-mithram-deploy.timer
journalctl -u kshethra-mithram-deploy.service -f
```

## 4) Configure Docker log rotation

```bash
sudo cp deploy/docker/daemon.json /etc/docker/daemon.json
sudo systemctl restart docker
```

## 5) Firewall hardening

Keep inbound closed from internet. Example baseline:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
# Optionally allow LAN-only SSH, adjust subnet:
sudo ufw allow from 192.168.0.0/16 to any port 22 proto tcp
# Allow SSH via Tailscale interface
sudo ufw allow in on tailscale0 to any port 22 proto tcp
# (Optional) Also allow from Tailnet CGNAT range
sudo ufw allow from 100.64.0.0/10 to any port 22 proto tcp

sudo ufw enable
sudo ufw status verbose
```

## 6) Versioning behavior

Base version is read from `VERSION` (example: `0.1.0`).

On server deploy:
- `python3 deploy/scripts/compute_version.py --mode deploy --commit-sha <sha>`
- Generates: `0.1.0.post<unix_timestamp>+g<short_sha>`

This is passed as Docker `BUILD_VERSION`, then written to `/app/.build-version` in container.

## 7) Integrity, lock, and rollback behavior

`deploy/scripts/deploy_on_server.sh` does:
1. `git fetch --prune origin main`
2. compares current `HEAD` with `origin/main`
3. if changed, checks out exact target commit
4. builds and starts containers
5. checks health (`http://127.0.0.1:5000`)
6. on failure, auto-rolls back to previous commit and restarts
7. stores deployment state in `/opt/kshethra-mithram/.deploy-state/`

State files:
- `last_successful_commit`
- `last_successful_version`
- `previous_successful_commit`

Locking:
- `flock` lock at `/opt/kshethra-mithram/.deploy-state/deploy.lock`
- prevents overlapping timer runs

## 8) Functional validation checklist

1. Push a commit to `main`.
2. Wait up to 2 minutes.
3. Verify logs: `journalctl -u kshethra-mithram-deploy.service -n 200`
4. Verify running version:

```bash
docker exec temple_app cat /app/.build-version
```

## 9) Failure/rollback tests

Build failure simulation:
1. Introduce intentional Docker build error on a test branch merged to `main`.
2. Confirm service remains on previous working commit.

Health failure simulation:
1. Temporarily set `HEALTH_URL` to an invalid endpoint in service file.
2. Run one deploy, verify rollback.
3. Restore service config and redeploy.
