"""Trace the first wrong write and prove private no-op selection repair."""
from pathlib import Path
import argparse, hashlib, json
import robots_weapon_cpu_v1 as cpu


class TraceMemory(cpu.Memory):
    def __init__(self, bundle):
        self.write_sites = []
        self.executing_pc = None
        super().__init__(bundle)

    def __setitem__(self, at, value):
        if isinstance(at, int) and self.executing_pc is not None:
            before = list.__getitem__(self, at)
            if before != value:
                self.write_sites.append(dict(pc=self.executing_pc, address=at, before=before, after=value))
        super().__setitem__(at, value)


class TraceMPU(cpu.NesMPU):
    def step(self):
        self.memory.executing_pc = self.pc
        return super().step()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    cpu.Memory, cpu.NesMPU = TraceMemory, TraceMPU
    old, new = cpu.load(a.baseline), cpu.load(a.candidate)
    labels = lambda path: {q[2]: q[1] for line in path.with_suffix('.lbl').read_text().splitlines()
                           if len(q := line.split()) == 3}
    old_labels, new_labels = labels(a.baseline), labels(a.candidate)
    assert all(new_labels.get(name) == val for name, val in old_labels.items()), 'An existing exported label moved'
    ram = [name for name, s in old['syms'].items() if 'seg' in s and cpu.address(old, name) < 0x8000]
    assert all(name in new['syms'] and cpu.address(old, name) == cpu.address(new, name) for name in ram)
    rows = []
    first = None
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        for passive in [False, True]:
            for button, paused in [(32, 0), (32, 1), (1, 1), (2, 1)]:
                pair = []
                for b in [old, new]:
                    q = cpu.Arena(b, char, proto)
                    mask = 1 | ((1 << (9 if char == 1 else 8)) if passive else 0)
                    q.set('InvOwnedLo', mask & 255, char)
                    q.set('InvOwnedHi', mask >> 8, char)
                    q.array('MmBulletType', [1, 1, 0, 1])
                    q.put(SavedJoypad1Bits=button, InvPrevious=0, GamePauseStatus=paused,
                          MmCharging=1, MmChargeFrames=48)
                    q.m.write_sites = []
                    q.invoke('InventoryUiTick')
                    state = dict(selection=q.get('InvSelected', char),
                                 shots=[q.get('MmBulletType', i) for i in range(4)],
                                 charge=q.get('MmChargeFrames'), charging=q.get('MmCharging'))
                    pair.append(state)
                    if b is old and first is None:
                        targets = {cpu.address(b, n): n for n in ['BassSourceKill', 'MmChargeFrames', 'MmCharging']}
                        targets.update({cpu.address(b, 'MmBulletType')+i: 'MmBulletType+'+str(i) for i in range(4)})
                        writes = [dict(**w, symbol=targets[w['address']]) for w in q.m.write_sites if w['address'] in targets]
                        assert writes
                        first = dict(case=dict(character=char, proto=proto, passive=passive, button=button, paused=paused),
                                     changed_effect_writes=writes)
                assert pair[0]['selection'] == pair[1]['selection'] == 0
                assert pair[0]['shots'] == [0, 0, 0, 0] and pair[0]['charge'] == 0
                assert pair[1]['shots'] == [1, 1, 0, 1] and pair[1]['charge'] == 48 and pair[1]['charging'] == 1
                rows.append(dict(character=char, proto=proto, passive=passive, button=button, paused=paused,
                                 before=pair[0], after=pair[1]))
    real = []
    for char, proto in [(1, 0), (1, 1), (9, 0)]:
        limit = 8 if char == 1 else 7
        for selected in range(limit+1):
            for button, paused in [(32, 0), (32, 1), (1, 1), (2, 1)]:
                if selected == 0 and button == 32 and paused:
                    continue
                pair = []
                for b in [old, new]:
                    q = cpu.Arena(b, char, proto)
                    owned = (1 << (limit+1))-1
                    q.set('InvOwnedLo', owned & 255, char)
                    q.set('InvOwnedHi', owned >> 8, char)
                    q.set('InvSelected', selected, char)
                    if selected:
                        types = [9, 10, 11, 12, 19, 15, 17, 20]
                        q.set('RgShotType', types[selected-1], 9)
                        q.put(SsHeld=10 if selected == 1 else 0,
                              SsFreeze=10 if selected == 3 else 0,
                              SsBodyStop=12)
                    else:
                        q.set('MmBulletType', 1, 3)
                    q.put(SavedJoypad1Bits=button, InvPrevious=0, GamePauseStatus=paused)
                    q.invoke('InventoryUiTick')
                    pair.append(dict(selection=q.get('InvSelected', char),
                                     shots=[q.get('MmBulletType', i) for i in range(4)],
                                     special=[q.get('RgShotType', i) for i in range(10)],
                                     held=q.get('SsHeld'), freeze=q.get('SsFreeze'), stop=q.get('SsBodyStop')))
                assert pair[0] == pair[1]
                assert pair[1]['selection'] != selected
                assert not any(pair[1]['shots']+pair[1]['special'])
                assert pair[1]['held'] == pair[1]['freeze'] == pair[1]['stop'] == 0
                real.append(dict(character=char, proto=proto, from_selection=selected, button=button, paused=paused,
                                 to_selection=pair[1]['selection']))
    proof = dict(passed=True, base_ROM_sha256=cpu.digest(old['raw']), candidate_ROM_sha256=cpu.digest(new['raw']),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 noop_cases=len(rows), real_transition_cases=len(real), RAM_symbols_unchanged=len(ram),
                 all_preexisting_exported_labels_unchanged=True,
                 CHR_unchanged=old['raw'][16+1048576:]==new['raw'][16+1048576:],
                 source_contract='MegaManBase.updateWeaponsVec lines697..716 destroys projectile/rush/carry objects only inside oldWeapon != curWeapon.',
                 first_wrong_write=first,
                 scope='Exact assembled public InventoryUiTick entry with coherent isolated robot inventories and fresh button edges. No native game-loop/interrupt/audio/PPU/controller-only proof; private proposal only.')
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    (a.output/'noop-cases.json').write_text(json.dumps(rows, indent=2)+'\n')
    (a.output/'real-transition-cases.json').write_text(json.dumps(real, indent=2)+'\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
