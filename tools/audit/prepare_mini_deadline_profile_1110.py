"""Measure each missed deadline without logging successful frames."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha


def instrument(text):
    substitutions = {
        'local interrupts, isrCycles = {}, 0': '''local interrupts, isrCycles = {}, 0
local missedDeadlines, pendingDeadlines = {}, {}''',
        '   interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}': '''   if phase=='fullstage' and path=='lag_nmi' and active() then
    assert(#missedDeadlines+#pendingDeadlines<32,'Deadline sample bound exceeded')
    local resume=read(0x100+((sp+2)&255))+256*read(0x100+((sp+3)&255))
    local phys=emu.convertAddress(resume)
    pendingDeadlines[#pendingDeadlines+1]={frame=frame,cycle=cycle-7,isr=isrCycles,
      pc=resume,bank=phys and phys.memType==emu.memType.nesPrgRom and phys.address//8192 or -1,
      x=read(0x75)+256*read(0x5c),y=read(0xbd),stack_depth=255-sp}
   end
   interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}''',
        "  if call.name == 'GameLoop' then\n   row.slowest": '''  if call.name == 'GameLoop' then
   for _,deadline in ipairs(pendingDeadlines) do
    deadline.foreground_after_deadline=state['cpu.cycleCount']-deadline.cycle-(isrCycles-deadline.isr)
    deadline.game_loop_entry=call.scene.frame
    deadline.cycle=nil
    deadline.isr=nil
    missedDeadlines[#missedDeadlines+1]=deadline
   end
   pendingDeadlines={}
   row.slowest''',
        'cadence=cadence,route_by_world_x=routeCadence,routines=stats':
            'cadence=cadence,missed_deadlines=missedDeadlines,route_by_world_x=routeCadence,routines=stats',
    }
    for before, after in substitutions.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--controller', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    prepare(args.output, args.rom, instrument(args.controller.read_text(encoding='utf-8')),
            {Path(__file__), args.controller}, expected=sha(args.rom), timeout=150,
            scope='Natural 1-1 with bounded missed-deadline records and no controller changes.',
            allow_interactive=True)
    subprocess.run([sys.executable, '-B', str(args.output / 'run.py')], check=True)
    timing = json.loads((args.output / 'capture/timing.json').read_text())
    deadlines = timing['missed_deadlines']
    assert len(deadlines) == timing['cadence']['fullstage']['lag_nmi']
    assert all(row['foreground_after_deadline'] >= 0 for row in deadlines)
    print(json.dumps(deadlines), flush=True)


if __name__ == '__main__':
    main()
