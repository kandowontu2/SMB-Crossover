"""Bind the repaired DK Jr scroll witness to an actual controller replay."""
import argparse
import json
from pathlib import Path

import check_dkjr_scroll_publish_1110_v1 as S

R = S.R


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    args = ap.parse_args()
    proof_path, vector_path = (S.OUT/name for name in ['camera-proof.json', 'camera-vectors.json'])
    proof, vectors = [json.loads(p.read_text()) for p in (proof_path, vector_path)]
    pin = proof['memory_only_SHA256']
    assert proof['passed'] and vectors['passed'] and pin == vectors['memory_only_SHA256'] == R.I.sha(args.rom.read_bytes())
    old, _, _, labels = R.pinned_inputs()
    span = json.loads(S.SPAN.read_text())
    mid = R.OAM.compose(old, span['patches'])
    assert R.I.sha(mid) == proof['base_SHA256'] and R.I.sha(R.OAM.compose(mid, proof['patches'])) == pin
    lua = R.controller(bytes.fromhex(proof['cookie']), labels)
    lua = R.OAM.replace_once(lua, R.PIN, pin)
    lua = R.OAM.replace_once(lua,
        'emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4016)',
        '''local pendingScroll
pipe.scroll={calls=0,mismatches=0}
emu.addMemoryCallback(function()
 if not active() or not pendingScroll then return end
 local map=emu.convertAddress(0xa9d4)
 if not map or map.memType~=emu.memType.nesPrgRom or map.address//8192~=1 then return end
 local q=pipe.scroll
 q.calls=q.calls+1
 local got=read(0x75a)
 if got~=pendingScroll.expected then
  q.mismatches=q.mismatches+1
  if not q.first_mismatch then
   q.first_mismatch={frame=frame,x=pendingScroll.x,camera=pendingScroll.camera,actual=got,expected=pendingScroll.expected}
  end
 end
 q.last={frame=frame,x=pendingScroll.x,camera=pendingScroll.camera,actual=got,expected=pendingScroll.expected}
 pendingScroll=nil
end,emu.callbackType.exec,0xa9d4)
emu.addMemoryCallback(function(_,value)
 if value~=5 or not active() or pipe.source_defeat_write then return end
 local map=emu.convertAddress(0xc06b)
 if not map or map.memType~=emu.memType.nesWorkRam or map.address~=2*8192+0x6b then return end
 local pc=emu.getState()['cpu.pc']
 local at=pc and emu.convertAddress(pc)
 pipe.source_defeat_write={frame=frame,source_main=updates,pc=pc,physical=at and at.address,
  x=xpos(),y=read(0xbd),camera=camera(),source_x=private(2,0),source_y=private(2,1),
  native_state=read(0x1e),native_y_speed=read(0x8e),enemy=goomba()}
end,emu.callbackType.write,0xc06b)
emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4016)''')
    lua = R.OAM.replace_once(lua,
        ' if inram(C.main,2,0xc000) and active() then updates=updates+1 end',
        ''' if inram(C.main,2,0xc000) and active() then
  updates=updates+1
  local x,cam=xpos(),camera()
  pendingScroll={x=x,camera=cam,expected=math.max(0,math.min(255,x-cam))}
 end''')
    lua = R.OAM.replace_once(lua,
        ' pipe.max_x=math.max(pipe.max_x,x)\n pipe.stationary=(x==lastX) and (pipe.stationary+1) or 0;lastX=x',
        ' pipe.stationary=(x<=pipe.max_x) and (pipe.stationary+1) or 0\n pipe.max_x=math.max(pipe.max_x,x)')
    lua = R.OAM.replace_once(lua,
        ' pipe.reason=reason;pipe.cleared=clear;pipe.x=xpos();pipe.y=read(0xbd)',
        ''' pipe.reason=reason;pipe.cleared=clear;pipe.x=xpos();pipe.y=read(0xbd)
 pipe.scroll.qualified=pipe.scroll.calls>100 and pipe.scroll.mismatches==0
 if not pipe.scroll.qualified then clear=false end''')
    R.V.prepare(S.OUT/'native', args.rom, lua,
                [Path(__file__), R.BASE, R.FRONTEND_PROOF, R.OAM_MANIFEST, R.ROUTE_SOURCE,
                 R.V.SOURCE, R.V.LAYOUT, proof_path, vector_path, S.SPAN, S.SOURCE],
                expected=pin, timeout=240, allow_interactive=True,
                scope='DK Jr controller cold/OAM/idle/hop/first-pipe. Verify exact pre-step 075A at the real ScrollHandler and record first source defeat write.')


if __name__ == '__main__':
    main()
