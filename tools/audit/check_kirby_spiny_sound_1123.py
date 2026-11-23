"""Check every needle-pool occupancy against the native launch routine."""

from hashlib import sha256
from itertools import product
import json

import compose_kirby_spiny_sound_1123 as Fix
import replay_kirby_stock_native_1122 as Kirby


def main():
    installed = Kirby.ROM.read_bytes()
    parent = Fix.inverse(installed) if sha256(installed).hexdigest() == Fix.CANDIDATE else installed
    candidate = Fix.compose(parent)
    assert Fix.inverse(candidate) == parent
    host = Kirby.Food.Cpu.Host
    authority = Kirby.Food.Cpu.Authority
    cpu = host.N
    symbols = authority.scoped_load(authority.AUTHORITY)
    bundles = [dict(symbols, raw=image) for image in (parent, candidate)]
    address = {n: host.address(symbols, n) for n in ('KbShotType', 'KbShotKind', 'KbShotAge',
                                                    'KbShotVXHi', 'KbShotVYHi', 'Square1SoundQueue')}
    queue = address['Square1SoundQueue']
    controlled = (*range(0x17B), *range(0x200, 0x800), *range(0x5C00, 0x8000))
    velocities = [(254, 255), (0, 253), (2, 255)]
    outcomes = []
    for occupied, facing, prior_cue in product(range(8), (1, 2), (0, 2)):
        states, times = [], []
        for bundle in bundles:
            m = cpu.fresh(bundle)
            cpu.put(m, SelectedCharacter=13, KbVariant=0, KbCopy=11, PlayerFacingDir=facing,
                    Player_X_Position=0xFA, Player_PageLoc=1, Player_Y_Position=176,
                    Square1SoundQueue=prior_cue)
            for slot in range(3):
                if occupied & (1 << slot):
                    for name, value in (('KbShotType', 3), ('KbShotKind', 11), ('KbShotAge', 24)):
                        m[address[name] + slot] = value
            result = cpu.invoke(m, 'KbWeapons::CopyAttack', p=0x30)
            times.append(result['CPU'])
            states.append(m)
        old, new = states
        open_slots = [slot for slot in range(3) if not occupied & (1 << slot)]
        new_cue = 32 if open_slots else prior_cue
        old_cue = 32 if len(open_slots) == 3 else prior_cue
        assert new[queue] == new_cue and old[queue] == old_cue
        assert [a for a in controlled if old[a] != new[a]] == ([queue] if new_cue != old_cue else [])
        for i, slot in enumerate(open_slots):
            assert new[address['KbShotType'] + slot] == 3 and new[address['KbShotKind'] + slot] == 11
            assert (new[address['KbShotVXHi'] + slot], new[address['KbShotVYHi'] + slot]) == velocities[i]
        for slot in range(3):
            if occupied & (1 << slot):
                assert new[address['KbShotAge'] + slot] == 24
        outcomes.append(dict(occupied=occupied, facing=facing, prior_cue=prior_cue, shots=len(open_slots),
                             before=old_cue, after=new_cue, cycles=times))
    report = dict(ROM=Fix.CANDIDATE, cases=len(outcomes),
                  recovered_cues=sum(row['before'] != row['after'] for row in outcomes),
                  no_free_slot_cases=sum(not row['shots'] for row in outcomes),
                  max_extra_cycles=max(row['cycles'][1] - row['cycles'][0] for row in outcomes),
                  allowed_application_delta='Square1SoundQueue for a partial volley', files=0)
    report['receipt_SHA256'] = sha256(json.dumps(outcomes, separators=(',', ':')).encode()).hexdigest()
    print('KIRBY NEEDLE POOL ' + json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
