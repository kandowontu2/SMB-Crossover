"""Attribute one normal NMI's cycle cost to its real mapped instructions."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha


def instrument(text, frame):
    edits = {
        'local isrCompleted, unmatchedReturns = {}, 0': '''local isrCompleted, unmatchedReturns = {}, 0
local nmiSample, nmiHandle, previousNmiInstruction = nil, nil, nil
local nmiFrame = ''' + str(frame) + '''
local function sampleNmiInstruction()
 local state=emu.getState()
 local pc,cycle=state['cpu.pc'],state['cpu.cycleCount']
 if previousNmiInstruction then
  local key=previousNmiInstruction.key
  nmiSample.cycles[key]=(nmiSample.cycles[key] or 0)+cycle-previousNmiInstruction.cycle
 end
 local phys=emu.convertAddress(pc)
 local bank=phys and phys.memType==emu.memType.nesPrgRom and phys.address//8192 or -1
 previousNmiInstruction={key=string.format('%d:%04x',bank,pc),cycle=cycle}
end''',
        '   local duration = cycle+6-entry.cycle': '''   local duration = cycle+6-entry.cycle
   if nmiHandle and entry.path=='normal_nmi' then
    sampleNmiInstruction()
    local key=previousNmiInstruction.key
    nmiSample.cycles[key]=(nmiSample.cycles[key] or 0)+6
    nmiSample.duration=duration
    emu.removeMemoryCallback(nmiHandle,emu.callbackType.exec,0,0xffff)
    nmiHandle=nil
   end''',
        '   interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}': '''   if path=='normal_nmi' and frame==nmiFrame and not nmiSample then
    nmiSample={frame=frame,cycles={}}
    sampleNmiInstruction()
    nmiHandle=emu.addMemoryCallback(sampleNmiInstruction,emu.callbackType.exec,0,0xffff)
   end
   interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}''',
        'cadence=cadence,route_by_world_x=routeCadence,routines=stats':
            'cadence=cadence,nmi_sample=nmiSample,route_by_world_x=routeCadence,routines=stats',
    }
    for before, after in edits.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--controller', type=Path, required=True)
    cli.add_argument('--frame', type=int, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    text = instrument(args.controller.read_text(encoding='utf-8'), args.frame)
    prepare(args.output, args.rom, text, {Path(__file__), args.controller}, expected=sha(args.rom),
            timeout=150, allow_interactive=True, scope='One normal NMI on an exact natural route.')
    subprocess.run([sys.executable, '-B', str(args.output / 'run.py')], check=True)
    sample = json.loads((args.output / 'capture/timing.json').read_text())['nmi_sample']
    assert sample['frame'] == args.frame and sum(sample['cycles'].values()) + 7 == sample['duration']
    banks = {}
    for key, cycles in sample['cycles'].items():
        bank = key.split(':')[0]
        banks[bank] = banks.get(bank, 0) + cycles
    print(json.dumps(dict(frame=sample['frame'], duration=sample['duration'], bank_cycles=banks)), flush=True)


if __name__ == '__main__':
    main()
