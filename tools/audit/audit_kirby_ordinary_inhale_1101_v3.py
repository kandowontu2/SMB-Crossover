"""Read-only c864 actual Main sweep of ordinary inhaling approaches."""
from pathlib import Path
import collections,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_kirby_owner_main_1101_v2 as K
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=R/'build/kirby-ordinary-inhale-audit-1101-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    b=qualified(K.O/'candidate.nes');assert sha(K.O/'candidate.nes')==K.PIN
    seed,setup=K.cold(b);rows=[];counts=collections.Counter()
    guard=(address(b,'KbBodyContact'),((location(b,'KbBodyContact')-16)//8192)|128)
    for kind in [0,6]:
      for facing in [1,2]:
       for directional in [False,True]:
        for gap in range(-24,33,2):
         m=C.fork(seed);K.scene(m,facing);K.actor(m,kind,112+(gap if facing==1 else-gap))
         observations=[];health0=H.get(m,'KbHealth');last=health0;frames=[]
         for frame in range(12):
          value=64+((1 if facing==1 else 2)if directional else 0)
          K.keys(m,value);o=K.Observe(b)
          def observe(mem,c,i):
           o(mem,c,i)
           tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
           if(c.pc,tag)==guard:
            g=lambda n:mem[address(b,n)+c.x]
            px=H.get(mem,'Player_X_Position')+256*H.get(mem,'Player_PageLoc');ex=g('Enemy_X_Position')+256*g('Enemy_PageLoc')
            py=H.get(mem,'Player_Y_Position');ey=g('Enemy_Y_Position')
            observations.append(dict(frame=frame,slot=c.x,playerX=px,enemyX=ex,playerY=py,enemyY=ey,facing=H.get(mem,'PlayerFacingDir'),action=H.get(mem,'KbAction'),age=H.get(mem,'KbActionAge'),held=H.get(mem,'SavedJoypadBits'),mouth=H.get(mem,'KbMouth'),copy=H.get(mem,'KbCopy'),float=H.get(mem,'KbFloat'),enemy_state=g('Enemy_State'),enemy_high=g('Enemy_Y_HighPos'),forward_delta=(ex-px)*(1 if H.get(mem,'PlayerFacingDir')==1 else -1),vertical_delta=ey-((py+8)&255)))
          c,low=K.call(m,'GameLoop',observe);C.consume(m);hp=H.get(m,'KbHealth')
          if hp!=last:frames.append(dict(frame=frame,old=last,new=hp,injury_entries=o.counts['KbInjuryStart'],guard_entries=len(observations),minimum_SP=low));last=hp
          if hp<health0 or H.get(m,'KbMouth'):break
         counts['cases']+=1;counts['injuries']+=int(last<health0);counts['captures']+=int(bool(H.get(m,'KbMouth')))
         if observations or frames:
          rows.append(dict(kind=kind,facing=facing,directional=directional,initial_gap=gap,health=last,mouth=H.get(m,'KbMouth'),frames=frames,guard_observations=observations))
    injured=[r for r in rows if r['health']<6]
    q=dict(passed=True,read_only_candidate=True,source_CPU=True,native_emulator=False,ROM_sha256=K.PIN,setup=setup,counts=dict(counts),injuries=injured,observed_cases=rows,
      scope='Actual Main/controller with flat native floor and disclosed initial NPC offsets. No ability/health/action/input-edge/outcome seeds. Facing1 and2; B alone or B+direction held for up to12 updates. This is diagnostic, not approval or a full playthrough.',
      bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',K.O/'candidate.nes',K.O/'candidate.dbg']})
    O.mkdir(exist_ok=True);(O/'ordinary-inhale-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts=dict(counts),injuries=[dict(kind=r['kind'],face=r['facing'],direction=r['directional'],gap=r['initial_gap'],frames=r['frames'],contacts=r['guard_observations'][-3:])for r in injured])))

if __name__=='__main__':main()
