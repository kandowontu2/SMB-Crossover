"""Freeze a truthful continuation receipt without promoting unfinished checks."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OUT=ROOT/'build/verification/root-current48-progress-a.json'
PATHS={
 'accepted47':'build/checkpoints/roster-audit-v47/manifest.json',
 'candidate48':'build/checkpoints/roster-audit-v48-provisional-a/candidate.json',
 'cpu_v1_negative':'build/verification/goomba47-48-cpu-a.json',
 'cpu_v2':'build/verification/goomba47-48-cpu-v2-a.json',
 'native_v2_negative':'build/verification/goomba47-48-native-cpu-v2-a.json',
 'cpu_v3':'build/verification/goomba47-48-cpu-v3-a.json',
 'native_v3':'build/verification/goomba47-48-native-cpu-v3-a.json',
 'crowds':'build/verification/goomba47-48-crowd-review-a.json',
 'capture':'build/verification/goomba47-48-ppu-samus-e-a/report.json',
 'audio':'build/verification/goomba47-48-apu-samus-e-a/report.json',
 'audio_classification':'build/verification/goomba47-48-apu-classification/actual-classification.json',
 'cpu_cycle_qualification':'build/verification/goomba47-48-apu-classification/CPU-native-cycle-qualification.json',
 'source_rebuild':'build/checkpoint-tests/source-v48a-rebuild-smoke/report.json',
 'profile_compaction':'build/verification/root-completed-crowd-dbg48-compaction-a/receipt.json',
 'rebuild_compaction':'build/verification/root-completed-rebuild-dbg48-compaction-b/receipt.json',
 'rebuild_compaction_preflight_negative':'build/verification/root-rebuild-dbg48-preflight-negative-a/report.json',
 'ryu_batch2':'build/verification/agent47-ryu-controls-batch2-20261018/handoff.json',
 'ryu_batch3':'build/verification/agent47-ryu-controls-batch3-20261018/handoff.json',
 'samus_batchB':'build/verification/agent47-samus-controller-batch-b/freeze.json',
 'samus_batchC':'build/verification/agent47-samus-controller-batch-c/freeze.json',
 'billB':'build/roster-through-2-2/root47-bill-adaptive-b-3-v0-mmc3/manifest.json',
 'billC':'build/roster-through-2-2/root47-bill-adaptive-c-3-v0-mmc3/manifest.json',
 'final_recording_control':'build/verification/capture45-full-route-review-a/report.json',
}

def main():
    assert not OUT.exists()
    refs={name:dict(path=n,sha256=sha(ROOT/n))for name,n in PATHS.items()}
    cp=ROOT/'build/checkpoints/roster-audit-v48-provisional-a'
    candidate=json.loads((cp/'candidate.json').read_text())
    assert all(sha(cp/f'smb-crossover-{m}.nes')==r['sha256']for m,r in candidate['roms'].items())
    with zipfile.ZipFile(cp/'source-v48a.zip')as z:
        files=json.loads(z.read('archived-file-hashes.json'))
        changed=[n for n,v in files.items()if sha(ROOT/n)!=v]
    assert not changed
    report=dict(status='progress-full-goal-incomplete',goal_complete=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
        accepted_checkpoint='roster-audit-v47',provisional_checkpoint='roster-audit-v48-provisional-a',
        references=refs,source403_matches_frozen_archive=True,
        cpu_cases=82272,native_receipts=128,matched_crowd_updates=13200,
        rgb24_frames_equal=1199,literal_pcm_equal=False,
        full_suite=dict(status='running',root_session=93513,
            command='python tools/verify.py --mmc5 --checkpoint build/checkpoints/roster-audit-v48-provisional-a --jobs 2',
            log='build/verification/roster-audit-v48-full-a.log',
            next='Poll the existing session. When it exits0, bind_validation_v42.py immediately, then run promote_component_v48.py. Do not restart or promote before inspecting actual summary.'),
        root_other_native_jobs='All closed: CPU45312, audio68779, profile compaction46829, rebuild compaction2897, Bill26766.',
        agent_authorizations=dict(
            ryu='Batch4 at most2 nonrecording full-audit attempts/75MB additional; workspace<28.85GB before each.',
            samus='BatchD at most2 nonrecording full-audit attempts/75MB additional; workspace<28.85GB before each.',
            link='Batch at most3 nonrecording full-audit attempts/90MB additional; workspace<28.75GB before each.'),
        route_state=dict(current_hash_verified_final_recordings=2,
            ryu='2-1 cleared;2-2 furthestX1604, unfinished. Best AD; AE trapped between Bloopers.',
            samus='2-1 cleared;2-2 Cheep contactX1286/Y103, unfinished. Best T preserves five land stages.',
            link='New ordinary-input region-clock attemptA died5703 in1-2; next adaptive current-actor revision authorized.',
            bill='New C ordinary-input attempt clears1-1, enters1-2at5798, falls into firstgapX1313/Y243at7711. Prior B heldB fired once; C pulses freshB and defeats both actual Goombas. No ROM defect inferred.'),
        compaction=dict(profile_dbg_count=11,rebuild_dbg_count=34,
            bytes_saved=126486839+389578034,
            scope='Lossless gzip with original-byte SHA roundtrip; canonical/current48/rawroutes/negatives protected. No route deletion or rejected cleanup retry.',
            prior_negative='Old rebuilt DBG differs from canonical DBG despite matchingROM; preflightA mutated nothing. B records that difference and roundtrips each original without claiming canonical DBG identity.'),
        settings='Outlines defaultOFF; optionrowgold. Samus ordinary stomp disabled by2.02 contract; acquired ScrewAttack supplies contactdamage.',
        deferred='173-byte stack-residue proposal remains unapplied; host bus/stack lifetime qualification required.',
        workspace_bytes=workspace_bytes(ROOT),workspace_cap_bytes=30_000_000_000,
        remaining='Finish current fullsuite/acceptance, all14 current-hash ordinary fixed replays/finalrecordings, every special/alternate/upgrade audit, source repairs/lag optimization and full audiovisual review.')
    assert report['workspace_bytes']<report['workspace_cap_bytes']
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report['workspace_bytes'],'bytes; pending fullsuite93513')

if __name__=='__main__':main()
