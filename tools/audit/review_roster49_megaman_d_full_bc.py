"""Root review of the frozen Mega Man D proof, without retagging it as F."""
from pathlib import Path
import collections,csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-megaman-bass-current-d-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-megaman-d-full-review-bc.json';assert not out.exists()
    freeze=H/'megaman-freeze-aq.json';assert sha(freeze)=='e235052217eaf8d3f0be296d91f101ce880087ee5b12bb85dc63a56e69b8a084'
    f=json.loads(freeze.read_text());counts={}
    for group,files in list(f['proofs'].items())+[('closure',f['functional_closure']),('receipts',f['receipts'])]:
        for name,info in files.items():
            p=(H if group=='receipts'else R)/name
            assert p.stat().st_size==info['bytes']and sha(p)==info['sha256'],name
        counts[group]=len(files)
    cp=R/f['checkpoint'];assert sha(cp)==f['checkpoint_sha256'];c=json.loads(cp.read_text())
    source=V/'root49-sophia-head-axis-d/source'
    assert len(c['source_hashes'])==455
    for n,h in c['source_hashes'].items():assert sha(source/n)==h,n
    for b in c['builds']:
        for info in b['artifacts'].values():assert sha(R/info['frozen_path'])==info['sha256']
    a=R/'build/roster-through-2-2/agent49-currentd-mm-exit-an-1-v0-mmc3'
    b=R/'build/roster-through-2-2/agent49-currentd-mm-fixed-ao-1-v0-mmc3'
    ma,mb=[json.loads((p/'manifest.json').read_text())for p in [a,b]]
    for p,m in [(a,ma),(b,mb)]:
        assert m['controller_only']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['config']['character']==1 and m['config']['variant']==0 and m['config']['mapper']=='mmc3'
        assert m['rom_sha256']==sha(p/'smb-crossover-mmc3.nes')==f['nes_sha256']
        assert m['result']==f['result']and m['result']['cleared']and m['result']['all_six_stages']and m['result']['deaths']==0 and m['result']['failure']is None
    assert mb['verified_through_2_2']and mb['full_frame_audit']and not ma['verified_through_2_2']and not ma['full_frame_audit']
    s=json.loads((b/'stomp-summary.json').read_text());assert s['behavior_version']==0 and not s['illegal_guest_events']and not s['resident_opcode_mismatches']
    literal={}
    for name in ['trace.csv','inputs.csv','events.csv','movement-input.csv']:
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
        literal[name]=sha(b/name)
    trace=rows(b/'trace.csv');assert len(trace)==28951 and len(rows(b/'inputs.csv'))==28950
    active_end=[x for x in trace if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
    assert len(active_end)==25 and active_end[0]['frame']=='28927'and active_end[0]['x']=='40'and active_end[-1]['x']=='61'
    assert not any(x['engine']in ['6','11']for x in trace)
    render=rows(b/'render.csv');state=rows(b/'mm-source-state.csv');oam=rows(b/'oam.csv')
    for z in [render,state]:assert [int(x['frame'])for x in z]==list(range(500,28952))
    assert all(x['behaviorVersion']=='0'for x in render if x['engine']=='8'and x['mode']=='1'and x['task']=='3')
    actual_dma=collections.Counter({int(x['frame'])-1:int(x['dmaCount'])for x in render if int(x['dmaCount'])})
    assert collections.Counter(int(x['frame'])for x in oam)==actual_dma and len(oam)==20071
    assert all(len(bytes.fromhex(x['oamHex']))==256 for x in oam)
    transitions=[];old=None
    for x in state:
        if x['power']!=old:transitions.append((int(x['frame']),int(x['power'])));old=x['power']
    assert transitions[1:]==[(11164,1),(16258,0),(18633,1),(20628,0)],transitions
    shot_types=sorted({int(t)for x in state for t in x['shotTypes'].split(':')})
    assert shot_types==[0,1]and max(int(x['charge'])for x in state)==5 and not any(int(x['dash'])for x in state)
    report=dict(status='PASS_ROOT_FROZEN_D_MEGAMAN_EASY_MMC3_COMPLETE_FIXED',script_sha256=sha(__file__),freeze_sha256=sha(freeze),
      rehashed=counts,immutable_D_sources=455,immutable_D_artifacts=8,literal_streams=literal,result=f['result'],
      fixed_manifest_sha256=sha(b/'manifest.json'),physical_audit_rows=len(render),actual_DMA_snapshots=len(oam),
      OAM_epoch='DMA callback frame is the previous completed endFrame; render frame is callback frame+1. All actual DMA snapshots checked.',
      natural_power_transitions=transitions,observed_shot_types=shot_types,max_charge_frames=5,dash_frames=0,
      limits=f['limits']+['Root validated route and observation domains; not audiovisual correctness or complete natural weapon acquisition.'],
      discovery_full_frame_audit=False,fixed_full_frame_audit=True,retained_reviewer_negative='root49-mm-review-bc-negative/reviewer.py required auditing on discovery; actual manifests qualify AN versus AO.',
      current_F_transfer_complete=False,all_weapons_complete=False,final_recording_complete=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
