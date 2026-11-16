"""New ordinary-input successor: vertical first-Goomba hop before the ledge."""
from hashlib import sha256
from pathlib import Path

import replay_dkjr_platform_footer_current_1116 as Frozen

FROZEN_SHA='bc880e6df58247824f7dfb239d0888f3708ed6928fc80ab1bc5bad71248e3dd8'


def controller(raw,*,source=False):
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SHA
    text=Frozen.source_controller(raw) if source else Frozen.controller(raw)
    old="""  if right and grounded and y==176 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('second-gap-enemy-hop')
"""
    new="""  if right and grounded and y==176 and updates>=rearm and nearEnemy(player)then
   -- Stop forward input for the first ground Goomba. Its natural stomp
   -- bounce must not carry this fixed-arc jumper into the falling Goomba.
   if player>=1136 and player<1182 then right=false end
   hold=updates+8;rearm=updates+47;remember('second-gap-enemy-hop')
"""
    assert text.count(old)==1
    result=text.replace(old,new,1)
    assert result.replace(new,old,1)==text
    Frozen.Frozen.Frozen.Prior.Ground.LuaRuntime().compile(result)
    assert not any(w in result for w in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return result


if __name__=='__main__':
    import argparse
    from diagnose_dkjr_ledge_controls_root_1116 import execute
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit',type=int,default=15000)
    execute(controller,limit=ap.parse_args().limit)
