"""Worker entrypoint — the long-lived process that drains the durable queue.

Run:  .venv/Scripts/python -m tools.runtime.worker
Under NSSM (Windows) / systemd (cloud) this is the supervised service that, with
the Next.js host, forms the single execution substrate. On startup it self-heals
(re-queues any job orphaned `doing` by a previous worker that crashed), then drains
the pipeline queue — so a restart resumes work instead of leaving a run orphaned
as RUNNING.
"""
from __future__ import annotations

from tools.runtime.aio import run_async
from tools.runtime.app import app
from tools.runtime.recovery import recover_stalled


async def _run() -> None:
    async with app.open_async():
        # Procrastinate installs signal handlers so SIGINT/SIGTERM stops the worker
        # cleanly after the in-flight job.
        await app.run_worker_async(queues=["pipeline"], install_signal_handlers=True)


def main() -> None:
    info = recover_stalled()
    if info["recovered"]:
        print(f"[worker] recovered {info['recovered']} stalled job(s): {info['job_ids']}",
              flush=True)
    print(f"[worker] starting; pruned {info['pruned_workers']} dead worker row(s)", flush=True)
    run_async(_run())


if __name__ == "__main__":
    main()
