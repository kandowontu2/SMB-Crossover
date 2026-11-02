"""Choose a genuine turbo windup before the observed first-enemy collision."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from check_excitebike_host_1101_v1 import fixture,tick,wx
import check_hogan_current_bounded_v1 as M
from prepare_excitebike_dispatch_1101_v1 import O,save,sha


def main():
    results=[]
    for pad in [1,65]:
      for windup in [40,60,80,90,100]:
        m,_=fixture();start=wx(m)
        for epoch in range(windup):tick(m,epoch,pad)
        for epoch in range(windup,windup+4):tick(m,epoch,pad|8)
        speed=m.ram[2][0x90]+256*m.ram[2][0x94];angle=m.ram[2][0xac]
        displacement=wx(m)-start;minimum=176;crashes=set();heat=set()
        for elapsed in range(150):
            controls=pad|(128 if elapsed<8 else 0)|(8 if elapsed<36 else 0)
            tick(m,windup+4+elapsed,controls)
            minimum=min(minimum,M.get(m,'Player_Y_Position'))
            crashes.add(m.ram[2][0x98]);heat.add(m.ram[2][0x3e0])
        assert M.get(m,'Player_Y_Position')==176 and M.get(m,'Player_State')==0
        results.append(dict(throttle=pad,windup=windup,prelean=4,launch_speed=speed,
                            launch_angle=angle,windup_displacement=displacement,
                            rise=176-minimum,crash_states=sorted(crashes),heat_states=sorted(heat)))
    choices=[q for q in results if q['throttle']==65 and q['rise']>30 and q['crash_states']==[0]and q['heat_states']==[0]]
    assert choices
    selected=min(choices,key=lambda q:q['windup'])
    q=dict(passed=True,results=results,selected=selected,native=False,
           scope='Ten in-memory original motor/air/lean fixtures choose the shortest tested turbo windup. Native level ceiling/enemy collision is deliberately not inferred.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'host-kernel.bin',O/'native3/capture/result.json',O/'native3/capture/diagnosis.json']})
    save('controller-windup-CPU.json',q);print(json.dumps(q))


if __name__=='__main__':main()
