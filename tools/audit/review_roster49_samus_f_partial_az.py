"""Audit ordinary intrinsic bomb witnesses and retain every current F failure."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=H/'review-az.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    runs=[]
    for letter,frames in [('a',8310),('b',8328),('c',9659),('d',9486)]:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{letter}-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['rom_sha256']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
        assert not m['verified_through_2_2']and m['result']['frames']==frames and m['result']['failure']=='death'
        identity=json.loads((p/'current-c-identity.json').read_text());assert identity==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        injury=rows(p/'actual-injury-b.csv');owners=[z for z in injury if z['event']=='InjurePlayer'and z['slot']==z['owner']]
        runs.append(dict(tag=letter,manifest_sha256=sha(p/'manifest.json'),result=m['result'],identity=identity,
          fatal_actual_owner=owners[-1],source_collision_defect_proven=False,
          files={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()}))
    p=R/'build/roster-through-2-2/root49-f-samus-route-c-2-v0-mmc3';a=rows(p/'first-bombs-c.csv');transitions=[];old={}
    for z in a:
        for i,field in enumerate(z['enemies'].split(';')[:2]):
            v=field.split(':');state=(v[1],v[3],v[6])
            if state!=old.get(i):transitions.append(dict(frame=int(z['frame']),slot=i,flag=int(v[1]),state=int(v[3]),health=int(v[6]),bombs=z['bombs'],playerX=int(z['x']),playerY=int(z['y'])));old[i]=state
    assert any(z['frame']==8316 and z['slot']==0 and z['state']==34 for z in transitions)
    assert any(z['frame']==8336 and z['slot']==1 and z['state']==34 for z in transitions)
    assert all(any(z['slot']==i and z['flag']==0 for z in transitions)for i in [0,1])
    assert any(z['ball']=='1'for z in a)and min(int(z['y'])for z in a)<140
    assert a[-1]['frame']=='8388'and a[-1]['phase']=='done'and a[-1]['ball']=='0'and a[-1]['state']=='0'
    stomps=[z for z in rows(p/'stomp-events.csv')if 8110<=int(z['frame'])<=8388];assert not stomps
    assert runs[-1]['fatal_actual_owner']['id']=='0','D waited for Goombas while a nearer Koopa approached'
    result=dict(status='REVIEWED_F_ORDINARY_MORPH_BOMB_KILLS_BOOST_UNMORPH_WITH_FOUR_RETAINED_ROUTE_NEGATIVES',
      script_sha256=sha(__file__),checkpoint_sha256=sha(cp),runs=runs,
      concrete_intrinsic_attack_evidence=dict(transitions=transitions,ordinary_morph=True,grounded_bomb_creation=True,
        actual_bomb_boost_peakY=min(int(z['y'])for z in a),two_actual_Goombas_defeated=True,no_stomps_in_this_window=True,
        all_three_bombs_expired=True,grounded_unmorph_frame=8388),
      next_action='D actual fatal is Koopa0 at853/Y184 versusballSamus840/Y176, while bombcontroller only waited for farther Goombas. Account for every approaching owner before committing to that control; do not infer a runtime or source-geometry defect.',
      limits=['Ordinary Easy intrinsic abilities only; no Hard Morph pickup/ownership proof.',
        'Per-frame APU writes retained, but no audible waveform/movie or every-SFX claim.',
        'Four real deaths remain failures, not complete routes; earlier1-1 clear is only a partial route.',
        'Native enemy boxes/HP and source bitmap/fractional geometry are not automatically equivalent.'],
      main_changed=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),flush=True)
if __name__=='__main__':main()
