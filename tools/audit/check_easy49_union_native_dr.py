"""Recheck C's native fallback against N on the actual combined DQ bytes."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-union-native-dr.json'
    assert not out.exists()
    dp = V / 'root49-body-victory-union-dq/report.json'
    assert sha(dp) == '40b361bb28db5f1e923c8079d1256bddfd622714ddd46ec44f9110f3039536a7'
    control = V / 'agent-lsr-victory-repair-c/check-cpu-v2.py'
    assert sha(control) == 'c70a2f75624d30739f55ec3014b2817bf7ac70b27809381b080065264fe218cd'
    # Reuse only the frozen seed/bus definitions; never execute or rewrite its old report.
    text = control.read_text()
    preamble, unused = text.split('\nreport=', 1)
    ns = dict(__file__=str(control))
    exec(compile(preamble, str(control), 'exec'), ns)
    Image, g, core, seed, at, RET = (ns[k] for k in ('Image', 'g', 'core', 'seed', 'at', 'RET'))
    rows = []
    for mapper in ('mmc3', 'mmc5'):
        old = Image(V / 'agent49-bill-source-body-f/source-n/build' / f'smb-crossover-{mapper}.nes')
        new = Image(dp.parent / 'source/build' / f'smb-crossover-{mapper}.nes')
        for im in (old, new):
            im._cached_banks = {0x8000: im.hook('PlayerBGCollision')['physical_bank'], 0xa000: 1,
                                0xc000: 0, 0xe000: im.hook('GuestFootContactSide')['physical_bank']}
        count, histogram = 0, {}
        for character in (0, 8):
            for mode in (0, 1):
                for state in (0, 1, 2):
                    for flags in (0, 1, 0x40, 0x81, 0xff):
                        ram, sp, banks = seed(old, count, character)
                        ram[at(old.ram['CrossoverBehaviorVersion'])] = mode
                        ram[at(old.ram['Player_State'])] = state
                        regs = [count & 255, (count * 3) & 255, (count * 7) & 255, flags, sp]
                        a = g.execute(old, core.NesMPU, ram, regs, banks, old.sym('PlayerCtrlRoutine')['val'], RET)
                        b = g.execute(new, core.NesMPU, ram, regs, banks, new.sym('GuestVictoryControl')['val'], RET)
                        assert all(a[k] == b[k] for k in ('regs', 'ram', 'trace', 'banks')), (mapper, character, mode, state, flags)
                        delta = b['cycles'] - a['cycles']
                        assert delta == (10 if character == 0 else 14)
                        histogram[str(delta)] = histogram.get(str(delta), 0) + 1
                        count += 1
        assert count == 60
        rows.append(dict(mapper=mapper, cases=count, N_ROM_sha256=sha(old.path), DQ_ROM_sha256=sha(new.path),
                         every_register_all8flags_SP_all10240RAM_banks_and_ordered_writes_exact=True,
                         rare_cycle_delta_histogram=histogram))
    result = dict(status='PASS_ACTUAL_DQ_NATIVE_VICTORY_FALLBACK_120_CASES', script_sha256=sha(__file__),
                  DQ_report_sha256=sha(dp), frozen_seed_bus_source_sha256=sha(control), mappers=rows,
                  comparison='Actual combined DQ rare entry versus N original PlayerCtrlRoutine; no B experiment and no historical BY transfer assumption.',
                  main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], sha(out))


if __name__ == '__main__':
    main()
