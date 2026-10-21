"""Retain the running integration gates and new ordinary route milestones."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/verification/root-current49-progress-t.json'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pin(n):
    p = R / n
    return dict(path=n, sha256=sha(p), bytes=p.stat().st_size)


def main():
    assert not OUT.exists()
    cp = R / 'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json'
    cat = json.loads(cp.read_text())['source_hashes']
    assert len(cat) == 410 and all(sha(R / n) == h for n, h in cat.items())
    prior = R / 'build/verification/root-current49-progress-s.json'
    assert sha(prior) == '9e8e7ec21aa1f4e2afe17244f9ab374cb373201f7c7a5e0fa026b4fe3f9b53a8'
    refs = [
        'build/verification/root-current49-progress-s.json',
        'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json',
        'build/verification/agent-lsr-s2-head-n2-a/implementation-publication-freeze.json',
        'build/verification/agent-lsr-s2-head-n2-a/actual-review-b.json',
        'build/verification/agent-lsr-s2-head-n2-a/route-handoff-current-i.json',
        'tools/audit/verify_private49_ryu_head_n2.py',
        'build/verification/root49s2-e-bill-cold-mmc3-a.json',
        'build/verification/root49-bill-cold-f/preparation.json',
        'build/verification/root49-bill-cold-f/verify_cpu.py',
        'tools/audit/prepare_bill49_cold_f.py',
        'docs/qa/roster-provisional-v49.md',
    ]
    cmd = ('Get-CimInstance Win32_Process | Where-Object { '
           '$_.ProcessId -eq 85476 -or $_.ProcessId -eq 82208 } | '
           'Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | ConvertTo-Json -Depth 4')
    raw = subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True)
    processes = json.loads(raw) if raw.strip() else []
    if isinstance(processes, dict):
        processes = [processes]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='progress-integration-gates-running-full-goal-incomplete',
        goal_complete=False, accepted_release=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        main_source410_exact=True, working_ROM_checkpoint=cp.parent.name,
        current_S2_recorded_fixed_clears='Mario and Luigi on both mappers; pinned in prior S.',
        immutable_references=[pin(n) for n in refs], observed_root_processes=processes,
        root_jobs=[dict(kind='Full unchanged private Ryu regression suite', session_id=46310,
                       driver_pid=85476, report='build/verification/agent-lsr-s2-head-n2-a/root-qa-suite-a/report.json',
                       status='Running at last authoritative session poll; poll same handle, never restart for elapsed observation timeout.'),
                   dict(kind='Bill F corrected-entry-bank cold CPU group MMC3', session_id=71789,
                        driver_pid=82208, report='build/verification/root49-bill-cold-f/mmc3-a.json',
                        status='Running at last authoritative session poll; old first-case negative retained.')],
        mutable_job_reports_are_not_final_evidence=True,
        root_reserved_bytes=500_000_000, workspace_bytes=used, cap_bytes=50_000_000_000,
        retain_lossless_captures=True,
        specialists=dict(active=['megaman_bass', 'pit_rygar_sophia', 'mario_luigi_scrooge_s2'],
                         idle=['link_simon_ryu', 'samus_contra_s2'],
                         pit_retained_phase_cap_bytes=1_500_000_000),
        recent_agent_milestones_qualified=[
            'Ryu I on private N2 clears first5 stages, enters2-2, fatal Blooper sourcewater geometry unresolved; handoff pinned.',
            'Pit AE on immutableS2 clears castle, enters2-1, next ordinary upperbrick landing adjustment remains live.',
            'Scrooge has verified2-2 grounded roots at1423,1763,2049; ordinary stationary stem microsequence reaches2064/Y112, its fresh verification was running at agent update.',
            'MegaMan F on immutableS2 clears1-3, enterscastle with naturally acquired mushroom/inventory; no fullclear yet.'],
        remaining=['Main promotion awaits broad private regression results and review.',
                   'Bill native46 coverage gaps and full body integration/bank budget remain unresolved.',
                   'Complete every roster/alternate route, every special/upgrade, lag work and retained final recordings.',
                   'Ryu water contact sourcegeometry classification remains required; do not silently route around it.'])
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(path=str(OUT), sha256=sha(OUT), workspace_bytes=used,
                         observed_root_process_count=len(processes))))


if __name__ == '__main__':
    main()
