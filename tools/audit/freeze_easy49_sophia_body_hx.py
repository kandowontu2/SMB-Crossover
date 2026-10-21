"""Freeze a verified private body stage while preserving remaining scope."""
from pathlib import Path
import csv
import hashlib
import json
import os
import stat
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-source-body-hs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
    out=D/'implementation-stage-freeze-hx.json';assert not out.exists()
    prep=json.loads((D/'preparation.json').read_text())
    for n,h in prep['source_sha256'].items():assert sha(D/'source'/n)==h,n
    review=json.loads((D/'review-hw.json').read_text())
    assert review['status']=='PASS_PRIVATE_BODY_STAGE_STATIC_NATIVE_AND_RELOCATION'
    assert [len(x['strict_calls'])for x in review['maps']]==[46,46]
    assert all(not x['interrupted_gaps']for x in review['maps'])
    artifacts={m:{e:rec(D/'source/build'/('smb-crossover-'+m+'.'+e))for e in ['nes','dbg','lbl','map']}for m in ['mmc3','mmc5']}
    baselines={m:rec(D/'source/build'/('smb-crossover-'+m+'-baseline.nes'))for m in artifacts}
    native={m:{p.name:rec(p)for p in (D/('native-hp-'+m)).iterdir()if p.is_file()}for m in artifacts}
    route=R/'build/roster-through-2-2/root49hu-sophia-body-11-v0-mmc3'
    result=json.loads((route/'result.json').read_text())
    assert result['frames']==6887 and result['failure']=='death' and not result['cleared']
    a=list(csv.DictReader((R/'build/roster-through-2-2/root49hg-sophia-live-11-v0-mmc3/trace.csv').open()))
    b=list(csv.DictReader((route/'trace.csv').open()))
    first={}
    for title,excluded in [('all_fields',set()),('gameplay_except_NMI',{'nmiSkipped'})]:
        for aa,bb in zip(a,b):
            diff={k:[aa[k],bb[k]]for k in aa if k not in excluded and aa[k]!=bb[k]}
            if diff:first[title]=dict(frame=int(aa['frame']),differences=diff);break
    assert first['all_fields']['frame']==637 and first['gameplay_except_NMI']['frame']==663
    ordinary=dict(result=result,first_differences=first,
        receipts={p.name:rec(p)for p in route.iterdir()if p.is_file()},
        command_binding=rec(D/'ordinary-hu/binding.json'),
        qualification='Old fixed tape is not portable to this runtime. Native owned shell collision at6887; no current private castle survival or fullroute claim. Controller-only fresh route remains required after terrain/head/side correction.')
    negatives=[]
    for name in ['root49-sophia-source-body-hl','root49-sophia-source-body-hq']:
        for p in (V/name).glob('*.json'):
            data=json.loads(p.read_text())
            if 'FAIL' in str(data.get('status'))or'NEGATIVE' in str(data.get('status')):negatives.append(rec(p))
    negatives.append(rec(D/'review-hv.json'))
    record=dict(status='FROZEN_PRIVATE_NORMAL_BODY_STAGE_NOT_FULL_SOPHIA_ADMISSION',
        utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        source_catalog=prep['source_sha256'],source_preparation=rec(D/'preparation.json'),
        artifacts=artifacts,baselines=baselines,native_receipts=native,
        compiled_geometry=rec(D/'compiled-geometry-ht.json'),native_static_review=rec(D/'review-hw.json'),
        source_normal_geometry=rec(V/'root49-sophia-body-lead-hj.json'),
        source_other_orientation_contract=rec(V/'agent-lsr-sophia-orientation-source-a/report.json'),
        retained_host_negatives=negatives,ordinary_fixed_negative=ordinary,
        resident_new_bytes=dict(body_dispatch_eligibility=4,firebar_dispatch_eligibility=4),
        old_Ryu_cold_relocated_bytes=844,added_RAM=0,
        remaining_requirements=[
            'Exact source terrain head/side samplers and response, including fractional edges.',
            'Rotated wall/ceiling anchor and last-rectangle epochs; actual vine frame selection.',
            'Actual Ryu source-body/platform caller ABI and interruption regression on this relocation.',
            'Source/native firebar birth/anchor/rotation/pixels and positive overlap parity.',
            'Fresh controller-only through2-2 route, all weapons/upgrades and final recording.',
            'Contextual merge with Bill E followed by actual union verification and lag profiling.'
        ],main_changed=False,accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(record,indent=2)+'\n')
    # Current main remains the previously admitted GQ, independently rechecked.
    checkpoint=R/'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    main=json.loads(checkpoint.read_text())
    assert len(main['source_hashes'])==442
    for n,h in main['source_hashes'].items():assert sha(R/n)==h,n
    for build in main['builds']:
        for item in build['artifacts'].values():assert sha(R/item['path'])==item['sha256']
    total=owned=0;todo=[R]
    while todo:
        with os.scandir(todo.pop())as entries:
            for e in entries:
                try:s=e.stat(follow_symlinks=False)
                except FileNotFoundError:continue
                if getattr(s,'st_file_attributes',0)&0x400:continue
                if stat.S_ISDIR(s.st_mode):todo.append(e.path)
                elif stat.S_ISREG(s.st_mode):
                    total+=s.st_size
                    if any(x in e.path for x in ['root49-sophia-source-body-hl','root49-sophia-source-body-hq','root49-sophia-source-body-hs']):owned+=s.st_size
    assert total<60000000000 and owned<500000000,(total,owned)
    progress=dict(status='ACTIVE_GQ_PRIVATE_E_AND_SOPHIA_BODY_STAGE_HS',utc=record['utc'],
        previous_goal_turn='Progress: AQ/HJ identified and bound actual normal Sophia body discrepancy. Greeting acknowledgment did not replace the goal.',
        this_goal_turn='Progress: implemented private normal Sophia body projection and actual disjoint consumer; both mappers pass source rational edges,92 complete native calls and exact relocation review. Retained timing/fixture/layout negatives change next actions.',
        predecessor=rec(V/'root-current49-progress-aq.json'),predecessor_addendum=rec(V/'root-current49-progress-aq-addendum-hk.json'),
        current_checkpoint=rec(checkpoint),main_GQ442_sources_and8_artifacts_exact=True,
        Sophia_private_stage_freeze=rec(out),Sophia_next=record['remaining_requirements'],
        Link_H_freeze=rec(V/'agent-lsr-link-firebar-h/implementation-freeze.json'),
        union_E='Private source-e unchanged; specialist native/ABI/NMI passed; final strict Pwr review/cost comparison/four ordinary controls remain. No main install.',
        latest_Samus='Current GQ through1-3, castle Y repeats W exactly; source/native bitmap-disjointness not established. Specialist resumes ordinary timing, no runtime correction inferred.',
        phase_ceilings_bytes=dict(global_workspace=60000000000,private_union=600000000,Samus_GQ=800000000,Samus_final_reserve=100000000,Sophia_body_aggregate=500000000,LSR_HS_regression=200000000),
        workspace_bytes=total,Sophia_body_aggregate_bytes=owned,root_live_handles=[],
        full_roster_all_arsenal_final_recordings='Unfinished; current GQ Rygar/Pit/Bass MMC3 Easy routes remain accepted within GU scope.',
        accepted_release=False,goal_complete=False)
    destination=V/'root-current49-progress-ar.json';assert not destination.exists()
    destination.write_text(json.dumps(progress,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],freeze=rec(out),progress=rec(destination),workspace_bytes=total,Sophia_body_bytes=owned)))


if __name__=='__main__':main()
