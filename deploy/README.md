# Deployment

The single execution substrate is one long-lived host running two supervised
processes: the **Next.js webapp** (control/read plane) and the **durable-queue
worker** (`tools/runtime/worker.py`). Supervision is what turns "we have a queue"
into "runs survive a crash/reboot" — the worker must come back and self-heal.

## Local (Windows) — NSSM services

| Path | What |
|---|---|
| `Run Worker.bat` | Dev: run the worker in the foreground (Ctrl+C to stop). |
| `windows/install-services.ps1` | Install `MAS-Worker` (and optionally `MAS-Webapp`) as reboot-durable services. |
| `windows/uninstall-services.ps1` | Remove them. |

Prereqs: NSSM on PATH (`choco install nssm`), `.venv` with deps, run as Administrator.

```powershell
powershell -ExecutionPolicy Bypass -File deploy\windows\install-services.ps1
Start-Service MAS-Worker
Get-Service MAS-*
```

> **Honest status:** the worker binary these point at is proven (see
> `scripts/prove-restart-survival.py`). The service *wrappers* are operator-run and
> not yet installed/verified on a host by the build. `MAS-Webapp` is gated behind
> `-IncludeWebapp` until the P2 console build exists (it needs `npm run build`).

## Cloud (Linux) — systemd

The same two processes as `systemd` units with `Restart=always` +
`WantedBy=multi-user.target`. Templates land with the cloud-deploy slice; the
worker command is identical (`.venv/bin/python -m tools.runtime.worker`).

## Connections (Supabase)

- Worker holds **one** direct/session connection (`DIRECT_URL`, :5432) for the
  queue listener — budget for it on the free tier (~60 direct conns).
- The webapp uses the pooled connection for request-path queries.
- Migrations + the procrastinate schema apply over `DIRECT_URL`.
