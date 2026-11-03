"""Bind actual current Bub/Bob full-stage passes; earned block remains open."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-full11-1102-v80';D=R/'docs/qa/checkpoints/2026-11-03/bub-upgrade-full11-v80'
PIN='b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53'

def main():
    O.mkdir(exist_ok=True);D.mkdir(parents=True);files=[Path(__file__),R/'tools/audit/prepare_bub_upgrade_stairs_1102_v78.py',R/'tools/audit/prepare_bob_upgrade_full11_1102_v79.py'];rows=[]
    for identity,folder in [(0,'bub-upgrades-root-route-1102-v78/bub-full11'),(1,'bub-upgrades-root-bob-1102-v79/bob-full11')]:
        p=R/'build'/folder;c=p/'capture';ready=json.loads((p/'ready.json').read_text());binding=json.loads((c/'binding.json').read_text());q=json.loads((c/'full11.json').read_text());obs=json.loads((c/'bub-observer.json').read_text());result=json.loads((c/'result.json').read_text())
        assert ready['ROM_sha256']==binding['ROM_sha256']==obs['ROM_sha256']==PIN
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
        assert q['passed'] and q['full_stage'] and q['why']=='actual-active1-2-all-four-pipes-three-pits'
        assert (q['world'],q['level'],q['engine'])==(0,1,8) and q['initial_lives']==q['final_lives']==2 and not q['helpers_added']
        assert obs['passed'] and obs['identity']==identity and obs['failures']==0 and obs['checks']>60_000
        assert len(q['clears'])==7 and obs['pops']==17 and obs['source_bubble_ride_restarts']==6
        assert result['passed'] and result['controller_only'] and result['active_data_writes']==result['late_enables']==0 and result['screenshots']==4
        for f,h in ready['bindings'].items():assert sha(f)==h,f
        for e in q['actual_normal_pit_jump_entries']+q['actual_stair_jump_entries']:
            assert e['native_state']==0 and(e['foot'][1]['solid'] or e['foot'][3]['solid']) and not e['support_marker'] and e['source_held']&128
        files += [p/'controller.lua',p/'ready.json',c/'binding.json',c/'full11.json',c/'bub-observer.json',c/'result.json',c/'actual-active-1-2.png']
        rows.append(dict(identity=identity,frames=result['frames'],completed_Main=obs['completed_Main'],checks=obs['checks'],failures=0,lives=[2,2],active_world=0,active_level=1,engine=8,natural_pops=17,original_bubble_rides=6,helpers_added=False,source=p.relative_to(R).as_posix()))
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    with zipfile.ZipFile(archive) as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    out=dict(passed=True,ROM_SHA256=PIN,installed=False,source_ROM_unchanged=True,full_nonshortcut1_1=True,earned_block_upgrades_qualified=False,helpers_added=False,rows=rows,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),bindings={f.relative_to(R).as_posix():sha(f) for f in files},scope='Exact candidate actualcold native menu/Select identity, full1-1 fourpipes+threepits andactive1-2 withnaturalcombat/originalbubbleabilities/no life loss, actualsourcejumpentry/physicalCHR/OAM/palette/PPUdeadline guards. Endpoints visually reviewed. No Downloads/fullpowered/shortcut/earnedblock/audiofidelity claim. Current shared-source head bridge still needs repair and bothidentities earned upgrades before delivery.')
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,rows=rows),indent=2)+'\n')
    handoff=R/'docs/qa/continuation-current.json';q=json.loads(handoff.read_text());q['bub_original_upgrades_current_1102']['actual_full11']=out['rows'];q['bub_original_upgrades_current_1102']['full11_checkpoint']=D.relative_to(R).as_posix();q['bub_original_upgrades_current_1102']['status']='PRIVATE_BUB_BOB_FULL11_PASS_EARNED_BLOCK_BRIDGE_OPEN'
    q['root_queue_current_1102'].update(status='FREE',last_sessions=dict(Bub78=3746,Bob79=14926),next='BothBub/Bob b7e2 fullnonshortcut1-1pass; helperdeferredHuHead10 repairthenrealearnedblocktesting. Rootqueuefree; installed9cfunchanged.')
    handoff.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,rows=rows)))
if __name__=='__main__':main()
