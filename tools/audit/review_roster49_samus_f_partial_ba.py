"""Verify additional ordinary bomb kills and fresh-edge unmorph evidence."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=H/'review-ba.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for q in b['artifacts'].values():assert sha(R/q['path'])==sha(R/q['frozen_path'])==q['sha256']
    packets=[]
    for letter in ['e','f','g']:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{letter}-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
        nr=json.loads((H/f'native-result-{letter}.json').read_text())
        assert nr['exit']==1 and nr['manifest_sha256']==sha(p/'manifest.json')
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['rom_sha256']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'and not m['verified_through_2_2']
        identity=json.loads((p/'current-c-identity.json').read_text());assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        if letter=='e':assert m['result']['failure']=='death'and m['result']['frames']==9457
        else:assert m.get('result')is None,'F/G stopped on controller guards; do not invent a game death result'
        packets.append(dict(tag=letter,result=m.get('result'),last_trace=rows(p/'trace.csv')[-1],identity=identity,
          manifest_sha256=sha(p/'manifest.json'),native_result_sha256=sha(H/f'native-result-{letter}.json'),
          files={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()}))
    kills=[]
    for tag,expected in [('f',[(9665,3),(9803,1)]),('g',[(10705,0)])]:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{tag}-2-v0-mmc3';a=rows(p/'actor-bombs-f.csv')
        observed=[];old={}
        for z in a:
            for raw in z['actors'].split(';'):
                slot,flag,kind,state,x,y,hp=map(int,raw.split(':'))
                before=old.get(slot);old[slot]=(flag,kind,state)
                if before and before[0]and before[1]==6 and before[2]<32 and flag and kind==6 and state&32:
                    assert any(int(b.split(':')[0])==58 for b in z['bombs'].split(';'))
                    assert z['ball']=='1'
                    observed.append((int(z['frame']),slot));kills.append(dict(tag=tag,frame=int(z['frame']),slot=slot,enemy_id=kind,state=state,x=x,y=y,raw_health=hp,playerX=int(z['x']),playerY=int(z['y']),bombs=z['bombs']))
        assert observed==expected,(tag,observed)
        lo,hi=(9541,10090)if tag=='f'else(10530,10770)
        assert not [z for z in rows(p/'stomp-events.csv')if lo<=int(z['frame'])<=hi]
    p=R/'build/roster-through-2-2/root49-f-samus-route-g-2-v0-mmc3';u=rows(p/'unmorph-edge-g.csv')
    assert u[0]['ball']=='1'and u[-1]['ball']=='0'and u[-1]['state']=='0'and u[-1]['phase']=='done'and u[-1]['frame']=='10015'
    assert any(z['previousDirections']=='0'and z['mask']=='8'for z in u)
    result=dict(status='PASS_THREE_ADDITIONAL_ORDINARY_BOMB_KILLS_AND_FRESH_UP_UNMORPH_COMPONENTS',script_sha256=sha(__file__),checkpoint_sha256=sha(cp),
      sources_rehashed=len(c['source_hashes']),generated_rehashed=11,primary_artifacts_rehashed=8,packets=packets,three_actual_bomb_kills=kills,
      actual_unmorph=dict(first_frame=int(u[0]['frame']),completed_grounded_frame=10015,trace_sha256=sha(p/'unmorph-edge-g.csv')),
      retained_failures=dict(E='Fatal rear Koopa2/X797 against stationary ballSamus810; front-only wait ignored rear approach.',
        F='Controller guard after Up was first held at bomb-boost apex and never released on landing.',G='Controller guard after stale reference Up action remained nearest despite actual upright grounded form.'),
      G_hook_qualification='SamusCanStand entry bank/opcodes attained. Last-byte hook points into trailing Offsets data and is not a return witness; prefix entries used logger frame0 until policy started. No return ABI or exact prefix-hook time claim.',
      next_action='H preserves actual G10770 and advances a reference Up action only after actual SmBall0/SmCrouch0/grounded. Continue the ordinary route, then independently replay any real clear.',
      limitations=['Unseeded Easy intrinsic bombs, not Hard item acquisition or all-arsenal completion.',
        'The raw negative enemy health word on the defeated F slot3 remains visible; it is not interpreted as live positive HP.',
        'APU events retained, but no final audible/video/SFX review or source rectangle fidelity certification.',
        'E/F/G are retained negatives, not completed routes. No runtime code changed.'],goal_complete=False,main_changed=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),flush=True)
if __name__=='__main__':main()
