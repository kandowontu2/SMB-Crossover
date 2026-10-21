"""Review actual controller negatives and independently recheck Lance's C clear."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
STREAMS='inputs.csv trace.csv events.csv render.csv oam.csv chr.csv scroll-writes.csv audio-events.csv stomp-events.csv'.split()
def main():
    out=D/'controller-review-ax.json';assert not out.exists()
    checkpoint=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    assert sha(checkpoint)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    cp=json.loads(checkpoint.read_text())
    for n,h in cp['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in cp['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in cp['builds']:
        for a in b['artifacts'].values():assert sha(R/a['path'])==sha(R/a['frozen_path'])==a['sha256']
    expected=next(b for b in cp['builds']if b['mapper']=='mmc5')['artifacts']['nes']['sha256']
    old=R/'build/roster-through-2-2/root49-current-d-samus-fixed-a-2-v0-mmc5'
    evidence=[]
    for suffix,tag,frame,pose in [
      ('b','injury-b',2351,(857,176)),('c','pacing-c',None,(897,176)),
      ('d','pacing-d',3006,(1242,176)),('e','defense-e',3016,(1212,176)),
      ('f','takeoff-f',None,(481,176)),('g','pipe-g',None,(883,176))]:
        p=R/f'build/roster-through-2-2/root49-d-samus-m5-{tag}-2-v0-mmc5'
        m=json.loads((p/'manifest.json').read_text());t=rows(p/'trace.csv')
        assert m['rom_sha256']==expected==sha(p/'smb-crossover-mmc5.nes')
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['verified_through_2_2']
        assert (int(t[-1]['x']),int(t[-1]['y']))==pose
        if frame:
            assert m['result']['failure']=='death'and m['result']['frames']==frame
        else:
            assert m.get('result')is None
            expected_bound='Bounded actual first Goomba/pipe takeoff'if suffix=='c'else'Actual pose reference stalled; retain diagnosis'
            assert expected_bound in (D/f'native-mmc5-{suffix}.log').read_text()
        q=rows(p/'actual-injury-b.csv')
        owners=[x for x in q if x['event']=='InjurePlayer'and x['slot']==x['owner']]
        if suffix=='b':
            assert all((p/n).read_bytes()==(old/n).read_bytes()for n in STREAMS)
            hit=next(x for x in owners if int(x['frame'])==2351)
            assert (hit['slot'],hit['id'],hit['ex'],hit['ey'])==('2','6','869','184')
        if suffix=='d':
            hit=next(x for x in owners if int(x['frame'])==3006)
            assert(hit['slot'],hit['id'],hit['estate'],hit['ex'],hit['ey'])==('0','6','1','1230','158')
        if suffix=='e':
            hit=next(x for x in owners if int(x['frame'])==3016)
            assert hit['ball']=='1'and hit['playerBox']=='113:195:127:208'
        entries={}
        for x in t:
            if x['engine']=='8'and x['mode']=='1'and x['task']=='3':entries.setdefault(x['world']+'-'+x['level'],int(x['frame']))
        evidence.append(dict(tag=tag,manifest_sha256=sha(p/'manifest.json'),result=m.get('result'),last_trace=t[-1],
          actual_active_stage_entries=entries,injury_owners=owners,
          files={n.name:dict(bytes=n.stat().st_size,sha256=sha(n))for n in p.iterdir()if n.is_file()},
          classification='Actual native death'if frame else'Ordinary controller reference bound, not a native crash',
          source_collision_bug_proven=False))
    agent=V/'specialist-bill-combined-route-a'
    freeze=agent/'lance-proof-freeze-aw.json';f=json.loads(freeze.read_text())
    assert sha(freeze)=='efcea156ca32c976919a8e41e8baad81c60a5c67d7fc17caf562c0940897aa9c'
    for n,h in f['files'].items():assert sha(R/n)==h,n
    handoff=agent/'handoff-c-aw.json';h=json.loads(handoff.read_text())
    assert sha(handoff)==f['handoff_sha256']=='ee0094bd9e6a0b838f670fb7a6de72f11e6cfa6408970f2a10579bf8c2652493'
    p=R/h['proof'];before=R/h['comparison']['reference']
    m=json.loads((p/'manifest.json').read_text());result=json.loads((p/'result.json').read_text())
    assert m['verified_through_2_2']and result['cleared']and result['all_six_stages']and result['deaths']==0
    assert result['frames']==31258 and result['polls']==31257 and result['stage_entries']['1-2']==31234
    assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
    assert sha(p/'smb-crossover-mmc3.nes')==m['rom_sha256']==h['ROM_sha256']=='a4765d19bb90d476f78e14240f4d3b2bf8ee0fa0eda7f8425a9aaea407921005'
    a,b=rows(p/'trace.csv'),rows(before/'trace.csv');fields=h['comparison']['fields']
    assert len(a)==len(b)==31258 and all(all(x[k]==y[k]for k in fields)for x,y in zip(a,b))
    a,b=rows(p/'bill-telemetry.csv'),rows(before/'bill-telemetry.csv');fields=h['comparison']['native_telemetry_fields']
    assert len(a)==len(b)==30759 and all(all(x[k]==y[k]for k in fields)for x,y in zip(a,b))
    identity=json.loads((p/'ordinary-identity.json').read_text())
    assert identity['selected']==3 and identity['variant']==1 and identity['mode']==0 and identity['outlinesOff']==1
    result=dict(status='REVIEWED_SAMUS_MMC5_CONTROLLER_EVIDENCE_AND_ACTUAL_C_LANCE_FULL_CLEAR',script_sha256=sha(__file__),
      main_D_source455_generated11_artifact8_rehashed=True,checkpoint_sha256=sha(checkpoint),Samus_MMC5=evidence,
      Lance_C_MMC3=dict(freeze_sha256=sha(freeze),rehashed_files=len(f['files']),identity=identity,
       result=result,exact_19_fields=31258,exact_16_native_fields=30759,
       whole_streams_literal={n:((p/n).read_bytes()==(before/n).read_bytes()if(before/n).exists()else None)for n in STREAMS},
       discovery_hardware_streams_absent=[n for n in STREAMS if not(before/n).exists()],
       final_recording=False,D_transfer=False,arsenal_complete=False),
      diagnosis=['B observer is neutral over all nine full audit CSVs and binds actual Goomba2 at2351.',
       'D reaches1242 then actual fallingGoomba0; E Down really morphs and cannot provide the proposed crouch beam.',
       'F retreat/freshjump passes1-1; underground held-A reference stalls at481. G freshA passes that barrier but later retains stationaryB at883.',
       'H explicitly advances stationary attack proposals to restore B-release/rise sequences. It is a separate candidate, not yet a completed route.',
       'No scoped controller negative justifies a runtime collision patch. Actual frozenC Lance proof remainsC, not automaticallyD or MMC5.'],
      all_roster_complete=False,all_arsenal_complete=False,final_recordings_complete=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),Samus_candidates=len(evidence),Lance_files=len(f['files']))))
if __name__=='__main__':main()
