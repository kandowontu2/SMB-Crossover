"""Measure actual physical-frame lag in the retained current-F Samus route."""
from pathlib import Path
import collections,csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';P=R/'build/roster-through-2-2/root49-f-samus-route-s-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def stats(a):
    return dict(physical_frames=len(a),lag_NMI_frames=sum(int(z['lagNmi'])for z in a),lag_NMI_fraction=round(sum(int(z['lagNmi'])for z in a)/len(a),6),
      frames_with_scanline_sprite_overload=sum(int(z['maxSprites'])>8 for z in a),actual_DMA_count=sum(int(z['dmaCount'])for z in a),max_scanline_sprites=max(int(z['maxSprites'])for z in a))
def main():
    out=V/'root49-samus-f-real-lag-profile-bd.json';assert not out.exists()
    m=json.loads((P/'manifest.json').read_text());assert m['rom_sha256']=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
    assert m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']and m.get('result')is None
    trace=rows(P/'trace.csv');render=rows(P/'render.csv');assert [int(z['frame'])for z in render]==list(range(500,len(trace)+1))
    indexed={int(z['frame']):z for z in trace};deltas=[]
    for z in render:
        f=int(z['frame']);t=indexed[f]
        assert all(z[k]==t[k]for k in ['world','level','engine','x','y','mode','task'])
        delta=(int(t['nmiSkipped'])-int(indexed[f-1]['nmiSkipped']))%256
        assert delta in [0,1]and delta==int(z['lagNmi']),(f,delta,z['lagNmi'])
        deltas.append(delta)
    active=[z for z in render if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['screenDisabled']=='0']
    stages=collections.defaultdict(list);regions=collections.defaultdict(list)
    for z in active:
        stage=f"{int(z['world'])+1}-{int(z['level'])+1}"
        stages[stage].append(z);regions[(stage,int(z['x'])//128*128)].append(z)
    heat=[dict(stage=k[0],x_start=k[1],x_end=k[1]+127,**stats(a))for k,a in regions.items()if len(a)>=90]
    heat.sort(key=lambda z:(-z['lag_NMI_fraction'],-z['physical_frames']))
    windows={}
    for name,lo,hi in [('three_goomba_bomb_retreat',11600,11920),('castle_live_boss',21000,21060),('fourth_pipe_stationary_out_of_range_controller',26743,27641)]:
        a=[z for z in active if lo<=int(z['frame'])<=hi]
        windows[name]=dict(frame_range=[lo,hi],**stats(a))
    result=dict(status='MEASURED_REAL_F_SAMUS_MMC3_EASY_PARTIAL_ROUTE_LAG_BASELINE',script_sha256=sha(__file__),manifest_sha256=sha(P/'manifest.json'),render_sha256=sha(P/'render.csv'),trace_sha256=sha(P/'trace.csv'),
      physical_frame_counter_agreement=len(deltas),all_active=stats(active),by_stage={k:stats(a)for k,a in stages.items()},highest_lag_regions=heat[:12],observed_windows=windows,
      interpretation='Skipped physical NMI frames are directly checked against modulo256 NmiSkipped increments; this is not a wall-clock emulator speed or logical game-update FPS measurement. Sprite count retains the latest actual DMA image as the audit does.',
      limitations=['Partial route with stationary controller discovery intervals; aggregate rates are not representative final-playthrough rates.',
        'Windows are observed scenes, not matched-workload ability-cost experiments or E/F performance comparisons. Do not attribute all lag to a named attack.',
        'F prior active Ice palette leaf reduction is separate. Further whole-game and ability optimization remains required.'],
      source_anchors={n:sha(R/n)for n in ['src/reset.s','src/game.s','tools/playthroughs/roster_audit.lua']},runtime_changed=False,lag_optimization_complete=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out));print(json.dumps(result['by_stage']));print(json.dumps(heat[:3]))
if __name__=='__main__':main()
