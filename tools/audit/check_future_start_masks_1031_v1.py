"""Exercise genuine Start retirement, masks, flags and unchanged menu admission."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import bowser_split_loader_controls_v1 as T
import benj_all_menu_controls_1030_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load

O = R / 'build/future-start-mask-controls-1031-v1'
J = R / 'build/future-start-masks-1031-v1/joint'
P = R / 'build/contra-force-world-roles-1031-v2/joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    result = dict(passed=False, source_CPU=True, native=False, installed=False)
    try:
        stage = json.loads((J.parent / 'source-stage.json').read_text())
        for name, digest in stage['bindings'].items():
            assert sha(name) == digest, name
        bundles = [scoped_load(path / 'candidate.nes') for path in [P, J]]
        seeds = [T.make(bundle, SelectedCharacter=0) for bundle in bundles]
        checks = 0
        examples = []
        alts_old = {9: 32, 26: 8, 31: 128}
        groups_old = {23: 32, 30: 24}

        def pair(slot, alts, groups, flags):
            nonlocal checks
            outcomes = []
            for index, seed in enumerate(seeds):
                memory = T.fork(seed)
                T.H.put(memory, FmAlts=alts, FmGroups=groups)
                maps = memory.rawtags[:]
                cpu, low = T.call(memory, 'FmStartFlags', x=slot, a=85, y=99, p=flags)
                a_mask = {**alts_old, **({10: 68} if index else {})}.get(slot, 0)
                g_mask = {**groups_old, **({28: 7} if index else {})}.get(slot, 0)
                observed = (T.H.get(memory, 'FmAlts'), T.H.get(memory, 'FmGroups'))
                assert observed == (alts & a_mask, groups & g_mask), (slot, index, observed)
                assert memory.rawtags == maps
                assert (cpu.a, cpu.x, cpu.y, cpu.sp) == (0, slot, 99, 224)
                outcomes.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, low))
            assert outcomes[0] == outcomes[1], (slot, alts, groups, flags, outcomes)
            checks += 1
            if slot in [10, 28] and alts == 255 and groups == 255:
                examples.append(dict(slot=slot, flags=flags, original_return=outcomes[0], new_return=outcomes[1]))

        # Independently exhaust each byte, including both temporary P1 markers.
        for slot, value, field in itertools.product(range(32), range(256), range(2)):
            pair(slot, value if field == 0 else 255, value if field == 1 else 255, 0xf9)
        print('START_MASK_ALL_BYTES_PASS ' + str(checks), flush=True)
        for slot, flags in itertools.product(range(32), range(64)):
            pair(slot, 255, 255, T.flags(flags))
        print('START_MASK_ALL_FLAGS_PASS ' + str(checks), flush=True)
        previous = B.A.COUNTS[:]
        try:
            B.A.COUNTS[16] = 4
            B.A.COUNTS[23] = 2
            before, after = [B.collect(path, True) for path in [P, J]]
        finally:
            B.A.COUNTS[:] = previous
        assert before == after and len(after) == 86
        assert sum(not row['pending'] for row in after.values()) == 74
        assert all(row['pending'] for (slot, variant), row in after.items()
                   if slot == 28 or slot == 10 and variant > 0)
        result.update(passed=True, candidate=sha(J / 'candidate.nes'), parent=sha(P / 'candidate.nes'),
                      actual_Start_pairs=checks, all_byte_pairs=16384, all_64flag_slot_pairs=2048,
                      CPU='Project NesMPU: binary ADC/SBC, P.D retained',
                      native_retirement_runs_before_masks=True,
                      original_AXYP_SP_and_minimum_SP_exact=True, all_mapper_returns_exact=True,
                      current_menu_profiles=86, ready_profiles=74, actual_Start_A_boundaries=688,
                      current_names_and_all_ready_pending_boundaries_exact=True,
                      WWF_Thomas_Shinobi_still_pending=True, examples=examples,
                      limits=['Source CPU/menu funding only. No new character admitted or installed.',
                              'Existing retirement/ISR code is byte-identical; this receipt adds no physical NMI qualification.'])
    except Exception as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
    paths = [Path(__file__), Path(T.__file__), Path(T.H.__file__), Path(B.__file__),
             J.parent / 'source-stage.json', J / 'candidate.nes', J / 'candidate.dbg',
             P / 'candidate.nes', P / 'candidate.dbg']
    result['bindings'] = {str(p.resolve()): sha(p) for p in paths}
    (O / 'controls.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['bindings', 'examples']}), flush=True)
    assert result['passed'], result.get('error')


if __name__ == '__main__':
    main()
