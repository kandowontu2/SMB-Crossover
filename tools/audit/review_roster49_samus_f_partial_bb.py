"""Audit the real retreat volley, later controller negatives and three-stage route."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=H/'review-bb.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    packets=[]
    for tag in ['h','i','j','k','l']:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{tag}-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text());nr=json.loads((H/f'native-result-{tag}.json').read_text())
        assert nr['exit']==1 and nr['manifest_sha256']==sha(p/'manifest.json')
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']and not m['verified_through_2_2']
        assert m['rom_sha256']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
        assert json.loads((p/'current-c-identity.json').read_text())==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        packets.append(dict(tag=tag,result=m.get('result'),last_trace=rows(p/'trace.csv')[-1],
          files={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()}))
    p=R/'build/roster-through-2-2/root49-f-samus-route-j-2-v0-mmc3';a=rows(p/'bomb-retreat-j.csv');old={};kills=[]
    for z in a:
        for raw in z['actors'].split(';'):
            slot,flag,kind,state,x,y,hp=map(int,raw.split(':'));before=old.get(slot);old[slot]=(flag,kind,state)
            if before and before[0]and before[1]==6 and before[2]<32 and flag and kind==6 and state&32:
                kills.append(dict(frame=int(z['frame']),slot=slot,x=x,y=y,state=state,raw_health=hp,playerX=int(z['x']),playerY=int(z['y']),bombs=z['bombs']))
    assert [(z['frame'],z['slot'])for z in kills]==[(11708,1),(11748,2),(11859,3)]
    assert all(z['y']=='176'and z['state']=='0'for z in a if z['phase']in ['plant','retreat','explode'])
    assert a[-1]['frame']=='11910'and a[-1]['phase']=='done'and a[-1]['ball']=='0'and a[-1]['state']=='0'
    assert min(int(z['x'])for z in a)==1414
    assert not [z for z in rows(p/'stomp-events.csv')if 11600<=int(z['frame'])<=11910]
    i=R/'build/roster-through-2-2/root49-f-samus-route-i-2-v0-mmc3'
    assert rows(i/'inputs.csv')[:11600]==rows(p/'inputs.csv')[:11600]
    assert rows(i/'trace.csv')[:11600]==rows(p/'trace.csv')[:11600]
    jump=rows(i/'step-jump-i.csv');edge=next(z for z in jump if z['mask']=='129')
    assert edge['state']=='0'and int(edge['previousAB'])&128==0 and(edge['leftFoot']=='82'or edge['rightFoot']=='82')
    assert jump[-1]['phase']=='done'and int(jump[-1]['x'])>=1410 and jump[-1]['y']=='80'
    k=R/'build/roster-through-2-2/root49-f-samus-route-k-2-v0-mmc3';u=rows(k/'unmorph-k.csv');assert u[-1]['frame']=='12615'and u[-1]['ball']=='0'and u[-1]['state']=='0'
    l=R/'build/roster-through-2-2/root49-f-samus-route-l-2-v0-mmc3';m=json.loads((l/'manifest.json').read_text());res=m['result']
    assert res['frames']==21109 and res['failure']=='death'and res['stage_entries']=={'0-0':541,'0-1':7949,'0-2':15074,'0-3':17929}
    owners=[z for z in rows(l/'actual-injury-b.csv')if z['event']=='InjurePlayer'and z['slot']==z['owner']];fatal=owners[-1]
    assert fatal['frame']=='21109'and fatal['id']=='45'and fatal['slot']=='0'and fatal['hp']=='80'
    r=dict(status='PASS_ORDINARY_THREE_GOOMBA_RETREAT_VOLLEY_AND_CURRENT_F_FIRST_THREE_STAGES',script_sha256=sha(__file__),checkpoint_sha256=sha(cp),
      packets=packets,actual_three_retreat_volley_kills=kills,retreat_grounded_observations=True,unmorph_after_volley=11910,
      actual_supported_step_jump=dict(first_A=edge,landed=jump[-1]),I_J_literal_prefix=dict(polls_and_frames=11600,fields=list(rows(i/'trace.csv')[0])),
      K_unmorph_grounded=12615,L_three_stages_cleared=True,L_castle_fatal_actual_owner=fatal,
      qualifications=['The J preparation called its volley two Goombas; actual immutable J trace proves three. No original receipt rewritten.',
        'K preparation hypothesized another held-Up exit error at1725. K proves Up exits correctly, then generic combat immediately remorphs and waits for a distant Goomba among pipe walls. The later trace supersedes that earlier diagnosis.',
        'L excludes this bounded pipe corridor from the stationary bomb tactic and follows ordinary retained guidance. It clears1-2 and1-3, but ends on actual living Bowser body contact; no source NPC rectangle/phase defect inferred.',
        'H/J/K are controller-guard negatives; I/L are actual game deaths. None is a complete route or final movie.',
        'Unseeded Easy intrinsic attack observations; Hard acquisition, full arsenal, all enemy/source geometry, audiovisual and lag closure remain open.'],
      host_review_negative='The initial review expected flame ID21. The actual guarded collision has owner0 Bowser ID45 and HP80; the failed reviewer source and correction receipt are retained in review-bb-host-negative.',
      next_action='Inspect the actual L castle Bowser contact and live boss HP/position; preserve its ordinary prefix for a controller recovery, then independently replay a full clear if achieved.',
      goal_complete=False,main_changed=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],sha(out),flush=True)
if __name__=='__main__':main()
