"""Measure which code banks consume DK Jr's first twelve idle updates."""
from collections import Counter
import json
from pathlib import Path

import audit_dkjr_installed_ingress_1108_v1 as I


def main():
    raw = I.ROM.read_bytes()
    assert I.sha(raw) == I.PIN
    cpu, invoke = I.N.NesMPU, I.N.invoke
    active = False
    epoch = 0
    banks, pcs = Counter(), Counter()

    class Trace(cpu):
        def step(self):
            if not active:
                return super().step()
            pc = self.pc
            bank = self.memory.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else 'RAM'
            cycles = self.processorCycles
            result = super().step()
            cost = self.processorCycles-cycles
            banks[str(bank)] += cost
            pcs[f'{bank}:{pc:04x}'] += cost
            return result

    def measure(memory, label, *args, **kwargs):
        nonlocal active, epoch
        if label == 'GameCoreRoutine':
            epoch += 1
            active = 2 <= epoch <= 13
        try:
            return invoke(memory,label,*args,**kwargs)
        finally:
            active = False

    I.N.NesMPU, I.N.invoke = Trace, measure
    try:
        profile = I.cpu(raw, (I.BASE/'native-cookie-v90.bin').read_bytes())
    finally:
        I.N.NesMPU, I.N.invoke = cpu, invoke
    idle = profile['controls'][0]
    assert idle['control'] == 'idle' and idle['updates'] == 12
    assert round(idle['mean_CPU']*12) == sum(banks.values())
    output = I.R/'build/dkjr-idle-profile-1108'
    output.mkdir()
    result = dict(passed=True, parent_SHA256=I.PIN, source_CPU_fixture=True,
                  idle=idle, cycles_by_bank=banks.most_common(), hot_PCs=pcs.most_common(40),
                  scope='Foreground GameCoreRoutine only. Cold raw40 fixture, not a native menu or video cadence test.')
    (output/'profile.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(idle=idle, cycles_by_bank=banks.most_common(10))))


if __name__ == '__main__':
    main()
