"""Sample one native Mini update, distinguishing foreground from interrupt work."""
import argparse
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--controller', type=Path, required=True)
    cli.add_argument('--frame', type=int, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    source = args.controller.read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('local MiniSample={["x"]=nil,["frame"]=nil,["complete"]=false}',
            'local MiniSample={["x"]=nil,["frame"]='+str(args.frame)+',["complete"]=false}')
    replace('local lastInstruction', '''local foregroundCounts, interruptCounts, sampleISR = {}, {}, {}
local hardwareInterruptCycles = 0
local lastInstruction''')
    replace('local key=string.format(\'%s:%04x\',bank,pc)', '''local key=string.format('%s:%04x',bank,pc)
 local entering=(bank=='126' and pc==0x8000) or
                ((bank=='127' or bank=='119' or bank=='120' or bank=='125') and pc==0xe33c)
 if lastInstruction then
  local delta=cycle-lastInstruction.cycle-(entering and 7 or 0)
  assert(delta>=0,'Instruction cost cannot be negative')
  local target=lastInstruction.isr and interruptCounts or foregroundCounts
  target[lastInstruction.key]=(target[lastInstruction.key] or 0)+delta
 end
 if entering then
  sampleISR[#sampleISR+1]=state['cpu.sp']
  hardwareInterruptCycles=hardwareInterruptCycles+7
 end
 local instructionIsISR=#sampleISR>0
 if read(pc)==0x40 and instructionIsISR and sampleISR[#sampleISR]==state['cpu.sp'] then
  -- Mapper trampolines also use synthetic RTI; only unwind the actual ISR SP.
  table.remove(sampleISR)
 end''')
    replace('lastInstruction={key=key,cycle=cycle,pc=pc}',
            'lastInstruction={key=key,cycle=cycle,pc=pc,isr=instructionIsISR}')
    replace('floor_probes=floorSamples,', '''floor_probes=floorSamples,
                     foreground_opcodes=foregroundCounts,interrupt_opcodes=interruptCounts,
                     hardware_interrupt_cycles=hardwareInterruptCycles,''')
    prepare(args.output, args.rom, source, {args.controller, Path(__file__)},
            expected=sha(args.rom), timeout=140,
            scope='One controller-reached update with independently stack-matched ISR opcode attribution.',
            allow_interactive=True)
    subprocess.run([sys.executable, '-B', str(args.output / 'run.py')], check=True)


if __name__ == '__main__':
    main()
