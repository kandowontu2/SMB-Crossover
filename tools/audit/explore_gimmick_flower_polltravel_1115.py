"""One genuine current590 mature capture, two measured ordinary launch branches."""
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import replay_gimmick_flower_polltravel_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source
import check_gimmick_natural_flower_1114 as G
import explore_gimmick_flower_star_1115 as Plan


def capture(raw):
    original=Source.Runner.Frames.frame;found={};ticks=0
    class Captured(Exception):pass
    def frame(m,*args,**kwargs):
        nonlocal ticks
        q=original(m,*args,**kwargs)
        if kwargs.get('whole_pass'):
            ticks+=1
            for i in range(6):
                if tuple(G.N.get(m,n,i)for n in('Enemy_Flag','Enemy_ID','PowerUpType'))==(1,46,1)and G.N.get(m,'Enemy_State',i)>=128:
                    assert G.N.get(m,'GmRam0039')==0 and G.N.get(m,'GmNextSpecial')==1
                    found.update(memory=G.N.fork(m),Main=ticks,state=G.state(m),slot=i)
                    raise Captured()
        return q
    with patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold),patch.object(Source.Runner.Frames,'frame',frame):
        try:Source.Runner.run(raw,'mr_gimmick',1700)
        except Captured:pass
    assert found,'Actual590 mature Flower prefix not captured'
    return found


if __name__=='__main__':
    raw=Factory.ROM.read_bytes();assert sha256(raw).hexdigest()==Factory.PIN
    def forbid(*args,**kwargs):raise RuntimeError('Current Flower planner attempted output or Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid):
        seed=capture(raw);rows=[]
        # Current failed takeoff1243 misses the actual side collision by one
        # pixel; test only the adjacent ordinary threshold and its old control.
        # G.state uses its frozen parent's score helper; only the branch's
        # binding authority changes to current590. Do not replace that helper.
        facade=SimpleNamespace(bindings=Factory.bindings,Previous=G.F.Previous)
        with patch.object(G,'F',facade):
            for target in(1244,1245):
                q=Plan.opposite_scene(seed['memory'],8,target)
                rows.append(q)
    result=dict(ROM_SHA256=Factory.PIN,capture={k:v for k,v in seed.items()if k!='memory'},branches=rows,
        outputs=0,Mesen_run=False,gameplay_seeds=0,scope='Actual590 genuine-prefix ordinary-input branches; not production/native acceptance')
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
