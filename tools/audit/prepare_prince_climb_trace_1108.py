"""Observe the actual source alignment inputs and returns at the first pipe."""
import argparse
from pathlib import Path
import subprocess
import sys

from prepare_prince_resume_1108 import FIRST_PIPE, LEGACY
from prepare_selected_native_packet_v1 import prepare, sha


ALIGN_TRACE = r'''
pipeRoute.alignments={}
emu.addMemoryCallback(function()
 if not sourceActive() or (part~='pipe-up' and part~='pipe-over') or #pipeRoute.alignments>=24 then return end
 local at=emu.convertAddress(0xc40e)
 if not at or at.memType~=emu.memType.nesWorkRam or at.address~=2*8192+0x40e then return end
 assert(ram(0xc40e)==0x8d and ram(0xc40f)==0xa1 and ram(0xc410)==0xc0,'Source align entry')
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local offset=0x100+(sp+1)%256
 local q={before=state(),a=cpu['cpu.a'],x=cpu['cpu.x'],y=cpu['cpu.y'],
  caller=ram(offset)+256*ram(0x100+(sp+2)%256)+1,
  rawX=ps(0x78)+256*ps(0x79),baseColumn=ps(0x7a),index=ps(0x4b1),
  surface=ps(0x7f)+256*ps(0x80),surfaceRow=ps(0x81)}
 pipeRoute.alignments[#pipeRoute.alignments+1]=q
 onReturn(function()
  q.after=state();q.cellX=ps(0x7d)+256*ps(0x7e);q.row=ps(0x7c)
 end)
end,emu.callbackType.exec,0xc40e)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--jump-gap', type=int, default=86)
    parser.add_argument('--moving-approach', type=int)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    rom, output = args.rom.resolve(), args.output.resolve()
    controller = FIRST_PIPE.read_text()
    anchor = 'local function controls_tick(finish)'
    assert controller.count(anchor) == controller.count('enemy.gap<=96') == 1
    pin = sha(rom)
    controller = controller.replace(LEGACY,pin).replace('enemy.gap<=96',f'enemy.gap<={args.jump_gap}')
    if args.moving_approach is not None:
        assert 390 <= args.moving_approach < 448
        approach = "elseif wx()>=400 then\n   completePart();beginPart('pipe-settle');routeEvent('neutral-before-pipe-Up')"
        assert controller.count(approach) == 1
        controller = controller.replace(approach, f"elseif wx()>={args.moving_approach} then\n"
            "   completePart();beginPart('pipe-up');routeEvent('moving-before-pipe-Up')")
    controller = controller.replace(anchor, ALIGN_TRACE+'\n'+anchor)
    prepare(output, rom, controller, [Path(__file__), FIRST_PIPE], expected=pin,
            timeout=120, allow_interactive=True,
            scope='Controller-only first pipe route with at most 24 source alignment records.')
    if args.prepare_only:
        return 0
    return subprocess.call([sys.executable,'-B',output/'run.py'])


if __name__ == '__main__':
    raise SystemExit(main())
