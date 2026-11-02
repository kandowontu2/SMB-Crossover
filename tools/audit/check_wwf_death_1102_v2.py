"""Check actual death service completion for all wrestlers and foreign parity."""
import json
from pathlib import Path
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/wwf-death-1102-v2'
BASE = R / 'build/metal-reservation-1102-v42/candidate.nes'


def state(m, z):
    return (tuple(z[k] for k in ['A', 'X', 'Y', 'P']), bytes(m[:256]), bytes(m[0x200:0x800]),
            bytes(m[0x5c00:0x8000]), tuple(bytes(x) for x in m.ram), tuple(m.rawtags),
            bytes(m[0x15a:0x17b]), tuple(m.chr_latches), m.upper, m.lastset)


def main():
    before, after = [M.fresh(scoped_load(p)) for p in [BASE, O / 'candidate.nes']]
    negative = M.fork(before)
    M.put(negative, SelectedCharacter=29, FmGroups=0, OperMode=1, GameEngineSubroutine=11,
          MmDeathFlag=1, MmDeathAge=0, MmDeathPit=1, TimerControl=255)
    for _ in range(10):
        M.invoke(negative, 'HuDeath')
    assert M.get(negative, 'MmDeathAge') == 0 and M.get(negative, 'GameEngineSubroutine') == 11
    foreign = 0
    for char in [*range(29), *range(30, 41), 127, 255]:
        for flags in [0x30, 0xf1]:
            pair = []
            for seed in [before, after]:
                m = M.fork(seed)
                M.put(m, SelectedCharacter=char, OperMode=1, GameEngineSubroutine=11,
                      MmDeathFlag=1, MmDeathAge=30, MmDeathPit=1, TimerControl=255)
                # Resolve the real typed death target without executing an
                # unrelated source owner's uninitialized private code image.
                z = M.invoke(m, 'WfResolve', a=24, p=flags)
                pair.append(state(m, z))
            assert pair[0] == pair[1], ('Foreign death ABI', char, flags)
            foreign += 1
    nondeath = 0
    for variant in range(6):
        for row in [n for n in range(36) if n != 8]:
            for flags in [0x30, 0xf1]:
                pair = []
                for seed in [before, after]:
                    m = M.fork(seed)
                    M.put(m, SelectedCharacter=29, FmGroups=variant)
                    z = M.invoke(m, 'WfResolve', a=3 * row, p=flags)
                    pair.append(state(m, z))
                assert pair[0] == pair[1], ('Other WWF service', variant, row, flags)
                nondeath += 1
    own = []
    for variant in range(6):
        for pit, duration in [(1, 150), (0, 168)]:
            m = M.fork(after)
            M.put(m, SelectedCharacter=29, FmGroups=variant, OperMode=1,
                  GameEngineSubroutine=11, MmDeathFlag=1, MmDeathAge=0, MmDeathPit=pit,
                  TimerControl=255, NumberofLives=2)
            for tick in range(1, duration + 1):
                M.invoke(m, 'HuDeath')
                assert M.get(m, 'MmDeathAge') == tick
                assert M.get(m, 'GameEngineSubroutine') == (6 if tick == duration else 11)
                assert M.get(m, 'TimerControl') == (0 if tick == duration else 255)
            M.invoke(m, 'PlayerLoseLife')
            assert M.get(m, 'NumberofLives') == 1
            own.append(dict(variant=variant, pit=bool(pit), actual_death_ticks=duration,
                            native_lives_before=2, native_lives_after=1))
    invalid = 0
    for variant in range(6, 8):
        pair = []
        for seed in [before, after]:
            m = M.fork(seed)
            M.put(m, SelectedCharacter=29, FmGroups=variant, OperMode=1,
                  GameEngineSubroutine=11, MmDeathFlag=1, MmDeathAge=30, MmDeathPit=1)
            z = M.invoke(m, 'WfResolve', a=24)
            pair.append(state(m, z))
        assert pair[0] == pair[1]
        invalid += 1
    q = dict(passed=True, ROM_SHA256=sha(O / 'candidate.nes'), native=False,
             actual_foreign_resolver_full_state_cases=foreign, actual_invalid_WWF_selectors=invalid,
             actual_other_WWF_service_full_state_cases=nondeath,
             actual_WWF_native_death_and_life_loss_cases=own,
             original_negative=dict(actual_calls=10, death_age=0, engine=11, stalled=True),
             scope='Actual foreign typed resolution and all other WWF service targets remain exact. '
                   'Real public HuDeath and native PlayerLoseLife; both pit and normal guest-death '
                   'durations complete for all6 WWF identities. Source-game endurance/death artwork '
                   'and full-stage replay remain separate. Fixtures set declared death state in memory.',
             bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), BASE,
                 O / 'candidate.nes', O / 'assembly.json']})
    (O / 'CPU.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in q.items() if k not in ['bindings', 'actual_WWF_native_death_and_life_loss_cases']}))


if __name__ == '__main__':
    main()
