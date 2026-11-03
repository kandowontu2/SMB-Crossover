"""Save exact first-mushroom and full-stage native passes without a ROM copy."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-earned-freeze-1103-v90';D=R/'docs/qa/checkpoints/2026-11-03/bub-earned-native-v90'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);files=[Path(__file__)];rows=[]
    for identity,name in [(0,'bub'),(1,'bob')]:
        for task in ['mushroom','full11']:
            p=R/f'build/bub-initial-tier-native-1103-v88/{name}-{task}';c=p/'capture'
            ready=json.loads((p/'ready.json').read_text());binding=json.loads((c/'binding.json').read_text());result=json.loads((c/'result.json').read_text())
            assert ready['ROM_sha256']==binding['ROM_sha256']==PIN and binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
            for f,h in ready['bindings'].items():assert sha(f)==h,f
            assert result['passed']and result['controller_only']and result['active_data_writes']==result['late_enables']==0
            payload=c/('earned-mushroom.json'if task=='mushroom'else'full11.json');q=json.loads(payload.read_text());assert q['passed']
            if task=='mushroom':
                obs=q['observer'];assert q['identity']==identity and q['source_flags']==1 and q['native_status']==1 and q['observed_immature']and q['observed_mature']and q['lives']==2
                image=c/'earned-first-mushroom-complete.png'
            else:
                obs=json.loads((c/'bub-observer.json').read_text());assert q['full_stage']and(q['world'],q['level'],q['engine'])==(0,1,8)
                assert q['initial_lives']==q['final_lives']==2 and not q['helpers_added']and len(q['clears'])==7 and obs['pops']==17 and obs['source_bubble_ride_restarts']==6
                files.append(c/'bub-observer.json');image=c/'actual-active-1-2.png'
            assert obs['passed']and obs['identity']==identity and obs['failures']==0
            files.extend([p/'controller.lua',p/'ready.json',c/'binding.json',c/'result.json',payload,image])
            rows.append(dict(identity=identity,task=task,frames=result['frames'],completed_Main=obs['completed_Main'],checks=obs['checks'],failures=0,lives=[2,2],helpers_added=False,packet=p.relative_to(R).as_posix()))
    tools=['prepare_bub_head_candidate_1103_v81.py','prepare_bub_earned_alignment_1103_v83.py','prepare_bub_item_diagnostic_1103_v84.py','prepare_bub_start_status_1103_v85.py','prepare_bub_status_history_1103_v86.py','prepare_bub_initial_tier_1103_v87.py','prepare_bub_initial_tier_native_1103_v88.py']
    files.extend(R/'tools/audit'/n for n in tools)
    for rel in ['build/bub-head-root-candidate-1103-v81/candidate.json','build/bub-head-root-candidate-1103-v81/bub-mushroom/capture/callback-error.json','build/bub-head-earned-alignment-1103-v83/bub-mushroom/capture/callback-error.json','build/bub-head-item-diagnostic-1103-v84/bub-item/capture/item-current.json','build/bub-head-start-status-1103-v85/bub-status/capture/status-writes.json','build/bub-head-status-history-1103-v86/bub-history/capture/status-writes.json','build/bub-initial-tier-1103-v87/initial-tier.s','build/bub-initial-tier-1103-v87/initial-tier.cfg','build/bub-initial-tier-1103-v87/initial-tier.bin','build/bub-initial-tier-1103-v87/private-image.bin','build/bub-initial-tier-1103-v87/proposal.json']:
        files.append(R/rel)
    D.mkdir(parents=True);archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    assert archive.stat().st_size<1_000_000
    with zipfile.ZipFile(archive)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    out=dict(passed=True,installed=False,fully_qualified=False,ROM_SHA256=PIN,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),rows=rows,source_files=[str(f.relative_to(R)).replace('\\','/')for f in [Path(__file__),*(R/'tools/audit'/n for n in tools)]],scope='Actual cold-menu controller-only first-mushroom emergence/maturity/collection/native transformation/source01 and separate full1-1/active1-2/no-life-loss for both identities. All four retained endpoint images visually reviewed. No helper added. Parent head post-render/nested IRQ and plainbrick audio scopes remain pending; no flower/Downloads/audio-fidelity/release claim.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,rows=rows),indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';h=json.loads(handoff.read_text());b=h['bub_original_upgrades_current_1102'];b['current_native_checkpoint']=D.relative_to(R).as_posix();b['current_native_rows']=rows
    b['latest_candidate']['native_progress']='Both88 earnedfirstmushrooms and both separate fullnonshortcut1-1 pass; four endpoints viewed. Bub13460frames, Bob13513frames; eachfullroute17naturalpops/6originalbubble rides/lives2to2/nohelpers. No flower or currentDownloads qualification; expanded posthead/nested audio proof remains pending.'
    h['root_queue_current_1102'].update(status='FREE',next='Currentcf7 Bub/Bob actualmushroom+full1-1 pass, checkpoint90. Need actualflower, expandedparentheadIRQ/plainbrickproof and exactfinalcold/Downloads delivery. Prince114 combatFF failure and DK17API integration remain private.')
    handoff.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,rows=rows)))
if __name__=='__main__':main()
