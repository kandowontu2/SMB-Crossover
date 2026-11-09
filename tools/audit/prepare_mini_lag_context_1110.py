"""Measure lag by native engine phase and the prior NMI cost on one route."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_mini_deadline_profile_1110 import instrument
from prepare_selected_native_packet_v1 import prepare, sha


def with_context(text):
    replacements = {
        'local missedDeadlines, pendingDeadlines = {}, {}': '''local missedDeadlines, pendingDeadlines = {}, {}
local lagContexts, previousNormal = {}, nil''',
        '   local duration = cycle+6-entry.cycle': '''   local duration = cycle+6-entry.cycle
   if entry.path=='normal_nmi' then
    previousNormal={frame=entry.frame,cycles=duration,buffer=entry.buffer,
                    render_disabled=entry.render_disabled,engine=entry.engine}
   end''',
        "   if phase=='fullstage' and path=='lag_nmi' and active() then": '''   if path=='lag_nmi' then
    local key=string.format('%s/%02x/%02x/%02x/%s',phase,r('OperMode'),r('OperMode_Task'),
                            r('GameEngineSubroutine'),tostring(active()))
    lagContexts[key]=(lagContexts[key] or 0)+1
   end
   if phase=='fullstage' and path=='lag_nmi' and active() then''',
        'x=read(0x75)+256*read(0x5c),y=read(0xbd),stack_depth=255-sp}':
            'x=read(0x75)+256*read(0x5c),y=read(0xbd),stack_depth=255-sp,prior_normal=previousNormal}',
        'interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}': '''interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7,frame=frame,
     buffer=r('VRAM_Buffer_AddrCtrl'),render_disabled=r('DisableScreenFlag'),engine=r('GameEngineSubroutine')}''',
        'missed_deadlines=missedDeadlines,route_by_world_x':
            'missed_deadlines=missedDeadlines,lag_contexts=lagContexts,route_by_world_x',
    }
    text = instrument(text)
    for before, after in replacements.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--controller', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    source = args.controller.read_text(encoding='utf-8')
    # The compact native symbol map includes most stage state but not every
    # NMI scratch byte. Use the candidate's installed symbols for the rest.
    from profile_mini_busy_1108_v1 import address, bundle
    symbols = bundle(args.rom.read_bytes())
    text = with_context(source)
    for name in ('VRAM_Buffer_AddrCtrl', 'DisableScreenFlag'):
        text = text.replace(f"r('{name}')", f'read({address(symbols, name)})')
    prepare(args.output, args.rom, text,
            {Path(__file__), args.controller, Path(instrument.__code__.co_filename)},
            expected=sha(args.rom), timeout=150, allow_interactive=True,
            scope='Bounded native lag contexts and prior NMI cost, with the exact route controller.')
    subprocess.run([sys.executable, '-B', str(args.output / 'run.py')], check=True)
    timing = json.loads((args.output / 'capture/timing.json').read_text())
    assert sum(timing['lag_contexts'].values()) == timing['interrupts']['lag_nmi']['calls']
    assert len(timing['missed_deadlines']) == timing['cadence']['fullstage']['lag_nmi']
    print(json.dumps(dict(contexts=timing['lag_contexts'], deadlines=timing['missed_deadlines'])), flush=True)


if __name__ == '__main__':
    main()
