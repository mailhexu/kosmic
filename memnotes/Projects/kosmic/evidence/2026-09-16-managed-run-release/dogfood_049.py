#!/usr/bin/env python3
"""Story 049/055 dogfood: multi-process lifecycle, retention, crash, secrets, combined destructive matrix."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "/home/hexu/projects/myagentskills/kosmic")
from skills.scripts import kosmic_runs
from skills.scripts.kosmic_routines import detect_publication_siblings, recover_publication_siblings

OUT = Path(sys.argv[1])
REPO = Path("/home/hexu/projects/myagentskills/kosmic")
CLI = ["python3", str(REPO / "skills/scripts/kosmic_project_skills.py")]
results: list[dict] = []

def record(name, ok, detail):
    results.append({"check": name, "ok": bool(ok), "detail": detail})

# --- 1. lifecycle across independent processes ---
begin = json.loads(subprocess.run(CLI + ["scratch", "begin", "--project", "memnotes/Projects/kosmic", "--purpose", "049-live-probe", "--retention", "disposable"], capture_output=True, text=True, check=True).stdout)
status = json.loads(subprocess.run(CLI + ["scratch", "status", "--project", "memnotes/Projects/kosmic", "--run", begin["run_id"]], capture_output=True, text=True, check=True).stdout)
record("live-status", status["code"] == "OK" and status["live"] is True and status["state"] == "active", status)
run_dir = Path(begin["path"]); (run_dir / "scratch").mkdir(parents=True, exist_ok=True)
(run_dir / "scratch" / "probe.txt").write_text("cross-process promotion payload\n")
promo = json.loads(subprocess.run(CLI + ["scratch", "promote", "--project", "memnotes/Projects/kosmic", "--handle-file", begin["handle_file"], "--source", "scratch/probe.txt", "--destination", ".tmp/049-probe.txt"], capture_output=True, text=True, check=True).stdout)
dest = REPO / ".tmp" / "049-probe.txt"
record("promotion", promo["code"] == "OK" and dest.read_text() == "cross-process promotion payload\n" and promo["destination_sha256"] == promo["source_sha256"], promo)
dest.unlink()
receipt = json.loads(subprocess.run(CLI + ["scratch", "succeed", "--project", "memnotes/Projects/kosmic", "--handle-file", begin["handle_file"]], capture_output=True, text=True, check=True).stdout)
record("success-cleanup", receipt["code"] == "OK" and not run_dir.exists(), receipt)

# --- 2. failed diagnostic retention, capped extension, accounting, dry-run ---
fail = json.loads(subprocess.run(CLI + ["scratch", "begin", "--project", "memnotes/Projects/kosmic", "--purpose", "049-failed-diagnostic"], capture_output=True, text=True, check=True).stdout)
subprocess.run(CLI + ["scratch", "fail", "--project", "memnotes/Projects/kosmic", "--handle-file", fail["handle_file"], "--detail", "reproducer"], capture_output=True, text=True, check=True)
fail_manifest = json.loads((Path(fail["path"]) / "RUN.json").read_text())
expires = datetime.strptime(fail_manifest["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
finished = datetime.strptime(fail_manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
retention_ok = expires - finished == timedelta(hours=72)
over = subprocess.run(CLI + ["scratch", "extend", "--project", "memnotes/Projects/kosmic", "--handle-file", fail["handle_file"], "--until", (finished + timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ")], capture_output=True, text=True)
capped_ok = over.returncode == 2 and "EXTENSION_CAP_EXCEEDED" in over.stderr
within = subprocess.run(CLI + ["scratch", "extend", "--project", "memnotes/Projects/kosmic", "--handle-file", fail["handle_file"], "--until", (finished + timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ")], capture_output=True, text=True)
extend_ok = within.returncode == 0 and json.loads(within.stdout)["code"] == "OK"
gc = json.loads(subprocess.run(CLI + ["scratch", "gc", "--project", "memnotes/Projects/kosmic", "--dry-run"], capture_output=True, text=True, check=True).stdout)
entry = [e for e in gc["entries"] if e["run_id"] == fail["run_id"]]
accounting_ok = bool(entry) and entry[0]["category"] == "retained" and gc["total_bytes"] > 0
record("retention-extension-accounting", retention_ok and capped_ok and extend_ok and accounting_ok,
       {"retention_72h": retention_ok, "cap_enforced": capped_ok, "extend_ok": extend_ok, "gc_category": entry[0]["category"] if entry else None, "total_bytes": gc["total_bytes"]})

# --- 3. holder crash, grace, replay ---
crash = json.loads(subprocess.run(CLI + ["scratch", "begin", "--project", "memnotes/Projects/kosmic", "--purpose", "049-holder-crash", "--active-for", "1h"], capture_output=True, text=True, check=True).stdout)
manifest = json.loads((Path(crash["path"]) / "RUN.json").read_text())
os.kill(manifest["holder_pid"], 9); time.sleep(0.3)
st = json.loads(subprocess.run(CLI + ["scratch", "status", "--project", "memnotes/Projects/kosmic", "--run", crash["run_id"]], capture_output=True, text=True, check=True).stdout)
abandoned_ok = st["code"] == "OK" and st.get("abandoned_candidate") is True and "grace_until" in st
replay = json.loads(subprocess.run(CLI + ["scratch", "succeed", "--project", "memnotes/Projects/kosmic", "--handle-file", crash["handle_file"]], capture_output=True, text=True, check=True).stdout)
record("holder-crash-recovery", abandoned_ok and replay["code"] == "OK" and not Path(crash["path"]).exists(), {"status": st, "replay": replay["code"]})

# --- 4. secrets absent ---
secret = "token=dogfood-SUPERSECRET-049"
seeded = json.loads(subprocess.run(CLI + ["scratch", "begin", "--project", "memnotes/Projects/kosmic", "--purpose", secret, "--retention", "disposable"], capture_output=True, text=True, check=True).stdout)
seed_dir = Path(seeded["path"])
manifest_text = (seed_dir / "RUN.json").read_text()
history_text = (REPO / ".tmp/kosmic/history.jsonl").read_text()
handle_text = Path(seeded["handle_file"]).read_text()
leak = any("dogfood-SUPERSECRET" in t for t in (manifest_text, history_text, handle_text))
subprocess.run(CLI + ["scratch", "succeed", "--project", "memnotes/Projects/kosmic", "--handle-file", seeded["handle_file"]], capture_output=True, check=True)
record("secret-redaction", not leak, {"purpose_redacted": "[redacted]" in manifest_text})

# --- 5. Story 055 combined destructive matrix in an isolated real worktree ---
with tempfile.TemporaryDirectory(prefix="dogfood-055-", dir=str(REPO / ".tmp")) as tmp:
    vault = Path(tmp) / "vault"
    vault.mkdir()
    subprocess.run(["git", "init", "-q", str(vault)], check=True)
    (vault / ".gitignore").write_text(".tmp/\n")
    (vault / "seed.txt").write_text("base\n")
    subprocess.run(["git", "-C", str(vault), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(vault), "-c", "user.email=d@x", "-c", "user.name=d", "commit", "-qm", "base"], check=True)
    project = vault / "Projects" / "demo"; project.mkdir(parents=True)
    (project / "ProjectEntry.md").write_text("---\nproject_id: demo\nnworking_state: working-tree\n---\n# Demo\n".replace("nworking", "working"))
    h1 = kosmic_runs.begin_run(vault, purpose="055-expired", retention="diagnostic")
    kosmic_runs.finish_run(h1.handle_file, "failed")
    h1_expires = datetime.strptime(json.loads((h1.path / "RUN.json").read_text())["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    h2 = kosmic_runs.begin_run(vault, purpose="055-abandoned", active_for=timedelta(hours=1))
    m2 = json.loads((h2.path / "RUN.json").read_text())
    os.kill(m2["holder_pid"], 9); time.sleep(0.3)
    past_grace = datetime.strptime(m2["lease_expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) + kosmic_runs.UNLOCK_GRACE + timedelta(minutes=1)
    kosmic_runs._clock = lambda: past_grace
    applied = kosmic_runs.report_runs(vault, action="gc-apply")
    kosmic_runs._clock = None
    gc_ok = len(applied.operations) == 1 and not h2.path.exists() and h1.path.exists()
    unrelated_ok = (vault / "seed.txt").read_text() == "base\n"
    history = [json.loads(l) for l in (vault / ".tmp/kosmic/history.jsonl").read_text().splitlines()]
    deltas_ok = bool(history) and all("git_delta" in rec for rec in history)
    kosmic_runs._clock = lambda: h1_expires + timedelta(minutes=1)
    startup = kosmic_runs.startup_collect(vault, max_entries=1, max_bytes=1 << 20)
    kosmic_runs._clock = None
    startup_ok = len(startup.operations) == 1 and not h1.path.exists()
    dest = vault / "published"; dest.mkdir()
    (dest / "value").write_text("old\n")
    stage = vault / ".tmp" / "stage"; stage.mkdir(parents=True)
    (stage / "value").write_text("new\n")
    crashed = subprocess.run([sys.executable, "-c",
        "import sys; from pathlib import Path; from skills.scripts.kosmic_routines import publish_tree; "
        "publish_tree(Path(sys.argv[1]), Path(sys.argv[2]))", str(stage), str(dest)],
        cwd=str(REPO), env={**os.environ, "KOSMIC_FAIL_STAGE": "crash-after-backup"}, check=False)
    now = datetime.now(timezone.utc)
    states = detect_publication_siblings(dest, now=now)
    marker_path = states[0].path / ".kosmic-publish-marker.json"
    marker = json.loads(marker_path.read_text())
    marker["grace_expires_at"] = (now - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    marker_path.write_text(json.dumps(marker))
    recovery = [r for r in recover_publication_siblings(dest, now=now) if r.action == "restored"]
    pub_ok = crashed.returncode == 86 and len(recovery) == 1 and (dest / "value").read_text() == "old\n"
    record("combined-destructive-matrix", gc_ok and unrelated_ok and deltas_ok and startup_ok and pub_ok,
           {"gc_removed_abandoned": len(applied.operations), "expired_retained_then_removed": startup_ok,
            "unrelated_preserved": unrelated_ok, "git_delta_recorded": deltas_ok, "publication_restored": pub_ok})

OUT.write_text(json.dumps({"checks": results, "all_ok": all(c["ok"] for c in results)}, indent=2))
print(json.dumps({"all_ok": all(c["ok"] for c in results), "failed": [c["check"] for c in results if not c["ok"]]}))
