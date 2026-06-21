"""Worker entrypoint — the long-lived process that drains the durable queue.

Run:  .venv/Scripts/python -m tools.runtime.worker
Under NSSM (Windows) / systemd (cloud) this is the supervised service that, with
the Next.js host, forms the single execution substrate. A restart re-attaches to
the queue; Procrastinate's stalled-job recovery re-runs any job whose worker died
mid-flight, so no AgentRun is left orphaned as RUNNING.
"""
from __future__ import annotations

from tools.runtime.app import worker_app


def main() -> None:
    wapp = worker_app()
    with wapp.open():
        # Drain the pipeline queue. Procrastinate installs signal handlers so a
        # SIGINT/SIGTERM stops the worker cleanly after the in-flight job.
        wapp.run_worker(queues=["pipeline"], install_signal_handlers=True)


if __name__ == "__main__":
    main()
