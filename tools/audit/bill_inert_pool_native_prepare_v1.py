"""Final narrow source checks + one adaptive BillHard readiness. No native."""
from pathlib import Path
import argparse
import contextlib
import io
import itertools
import json
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools/audit'))
import bill_inert_pool_cpu_v1 as C
import current_roster_compact_11_v1 as route
H = C.H
P = B / 'verification/bill-inert-pool326-hard-ready-v1'
FINAL = B / 'bill_inert_pool_final.json'
put = lambda p, q: p.write_text(json.dumps(q, indent=2) + '\n', newline='\n')


def strict_writes(q, row):
    end = max(int(s['start'], 0) + int(s['size'], 0) for s in q.b['segs'].values()
              if s['name'] in ('"SHORTRAM"', '"SMCCODE"'))
    return [(a, v) for _, _, a, v, _ in row['writes'] if not end <= a < 0x200]


def full_order_pair(old, new, pool=(), **kwargs):
    flags = kwargs.pop('flags', 0x20)
    qs = [H.setup(b, pool=pool, **kwargs) for b in [old, new]]
    out = [H.run(q, 'RemainingWeapons', flags=flags) for q in qs]
    assert H.regs(out[0][0]) == H.regs(out[1][0]) and C.app(qs[0]) == C.app(qs[1])
    assert qs[0].m.banks == qs[1].m.banks
    assert strict_writes(qs[0], out[0][1]) == strict_writes(qs[1], out[1][1])


def carry_contract(b):
    lengths = {'imp': 1, 'acc': 1, 'imm': 2, 'zpg': 2, 'zpx': 2, 'zpy': 2,
               'rel': 2, 'inx': 2, 'iny': 2, 'abs': 3, 'abx': 3, 'aby': 3, 'ind': 3}
    allowed = {'LDA', 'LDX', 'STA', 'ORA', 'DEC', 'DEX', 'BEQ', 'BNE', 'BPL', 'JMP', 'JSR', 'RTS'}
    spans = [('RemainingWeapons::AdvanceFreeze', H.address(b, 'RemainingWeapons::SamusInput')),
             ('SamusFrozenDecrement', H.address(b, 'SamusFrozenDecrement') + int(b['syms']['SamusFrozenDecrement']['size']))]
    rows = []
    for name, end in spans:
        pc = H.address(b, name)
        while pc < end:
            at = H.location(b, name) + pc - H.address(b, name)
            code = b['raw'][at]
            mnemonic, mode = H.NesMPU.disassemble[code]
            assert mnemonic in allowed, (name, hex(pc), mnemonic)
            length = lengths[mode]
            operand = int.from_bytes(b['raw'][at + 1:at + length], 'little') if length > 1 else None
            if mnemonic == 'JSR':
                assert operand == H.address(b, 'SamusFrozenDecrement')
            if mnemonic == 'JMP':
                assert H.address(b, name) <= operand < end, 'Real long-branch target stays inside this proved span'
            if mnemonic in ('STA', 'DEC'):
                assert operand in {H.address(b, n) for n in ['AvStopwatch', 'AvFrozen', 'AvFrozenHi', 'RgEnemyStun', 'LsrFrozenPose']}
            rows.append(dict(pc=pc, code=list(b['raw'][at:at + length]), mnemonic=mnemonic, mode=mode))
            pc += length
        assert pc == end
    return dict(all_possible_source_instructions_preserve_CV=True, no_pool_or_loop_cursor_writes=True, instructions=rows)


def main():
    global P
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=P)
    args = ap.parse_args()
    P = args.output.resolve()
    assert P.is_relative_to(B.resolve()) and not P.exists(), 'Preserve prior readiness'
    if FINAL.exists():
        assert H.sha(FINAL) == 'b8911cf548d27b0354e3fae4fe072269d3882d9da43712a50010a4271422e7be'
    cpu_path = B / 'bill_inert_pool_cpu.json'
    cpu = json.loads(cpu_path.read_text())
    assert cpu['passed'] and H.sha(cpu_path) == 'ac2e81574a2239313cd4abb1bda7f27b68014f3d4acff9264b6d819af343c94d'
    assert cpu['tool_sha256'] == H.sha(Path(C.__file__))
    for path, sha in cpu['dependencies'].items():
        assert H.sha(path) == sha, path
    build_path = B / 'bill_inert_pool_verify_build.json'
    build = json.loads(build_path.read_text())
    for path, sha in build['bindings'].items():
        assert H.sha(path) == sha, path
    assert build['passed'] and build['changed_bytes'] == 31 and build['changed_banks'] == [6]
    rom = B / 'bill_inert_pool.nes'
    assert H.sha(rom) == build['candidate_sha256'] == H.sha(B / 'bill_inert_pool_verify.nes') == cpu['candidate_sha256']
    ordinary_path = B / 'bill_inert_pool_ordinary.json'
    ordinary = json.loads(ordinary_path.read_text())
    assert ordinary['passed'] and ordinary['same_overlay_sha256'] == H.sha(B / 'bill_inert_pool_remaining_weapons.s')
    assert [q['sha256'] for q in ordinary['rows']] == ['d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833']
    old, new = H.scoped_load(C.BASE), H.scoped_load(rom)
    n = 0
    for char, pool, mode, flags in itertools.product([i for i in range(20) if i != 3],
                                                    [(), (1,) * 4, (1,) * 10], [0, 1], [0x20, 0x21, 0x60, 0x61]):
        full_order_pair(old, new, pool, char=char, mode=mode, flags=flags)
        n += 1
    foreign = n
    n = 0
    for kind, slot, mode, variant, flags in itertools.product([42, 43], [0, 4, 9], [0, 1], [0, 1], [0x20, 0x21, 0x60, 0x61]):
        pool = [0] * 10
        pool[slot] = kind
        full_order_pair(old, new, pool, mode=mode, variant=variant, flags=flags)
        n += 1
    for pool, mode, variant, flags in itertools.product([(), (1,), (1,) * 4, (8,) * 10], [0, 1], [0, 1], [0x20, 0x21, 0x60, 0x61]):
        full_order_pair(old, new, pool, mode=mode, variant=variant, flags=flags, select=0x20)
        n += 1
    final = dict(passed=True, native_run=False, candidate_sha256=H.sha(rom), parent_sha256=H.sha(C.BASE),
                 inherited_exact_CPU_receipt=dict(path=str(cpu_path), sha256=H.sha(cpu_path), counts=cpu['counts']),
                 additional_no_cursor_exception_ordered_foreign=foreign,
                 additional_no_cursor_exception_ordered_advanced_freshSelect=n,
                 static_complete_freeze_contract=carry_contract(new),
                 fresh_rebuild=dict(path=str(build_path), sha256=H.sha(build_path), same_ROM=True),
                 ordinary=dict(path=str(ordinary_path), sha256=H.sha(ordinary_path)),
                 limits='Source-only. Real complete callers save620..680 in480 typed cases; no native recovery or route-speed claim. All byte values cover admission, but foreign advanced32..41/44..46 do not execute a wrong-family driver under Bill C-bank. Foreign true advanced code is byte-exact/unreached by the Bill-only gate. Larger313583 Main/130852 DrawAll exclusive owners remain unlocalized; this is a local optimization.')
    if FINAL.exists():
        assert json.loads(FINAL.read_text()) == final, 'Reused exact source controls; no old receipt mutation'
    else:
        put(FINAL, final)

    # This is the surviving actual adaptive parent, not either replay packet.
    parent = B / 'verification/bill-early-cache-pair-ready-v1/candidate9ea'
    prior = json.loads((parent / 'ready.json').read_text())
    result = json.loads((parent / 'result.json').read_text())
    assert result['passed'] and result['frames'] == 6091 and prior['config']['replay'] is None
    policy = Path(prior['config']['policy'])
    assert policy.name == 'roster_samus_contra.lua' and H.sha(policy) == prior['bindings'][str(policy)]
    navigation = R / 'tools/playthroughs/roster_samus_contra_nav.lua'
    assert H.sha(navigation) == prior['bindings'][str(navigation)]
    with contextlib.redirect_stdout(io.StringIO()):
        route.prepare(argparse.Namespace(identity='bill', mode='hard', rom=rom,
                      expected_sha256=H.sha(rom), output=P, frames=8000, policy=policy, replay=None))
    ready_path = P / 'ready.json'
    ready = json.loads(ready_path.read_text())
    cfg = ready['config']
    assert cfg['replay'] is None and cfg['policy'] == policy.as_posix() and cfg['limit'] == 8000
    assert (cfg['character'], cfg['variant'], cfg['mode_value']) == (3, 0, 1)
    assert cfg['capture_bytes'] == 512 * 1024 * 1024
    put(P / 'command.json', ready['command'])
    ready['Bill_inert_pool_source'] = dict(source_only=final, source_proof_sha256=H.sha(FINAL),
        inherited_Controller=dict(ready=str(parent / 'ready.json'), ready_sha256=H.sha(parent / 'ready.json'),
                                 result_sha256=H.sha(parent / 'result.json'), policy_sha256=H.sha(policy),
                                 navigation_sha256=H.sha(navigation), actual_prior_adaptive=True),
        native_scope='ONE new adaptive BillHard1-1 to25controlled1-2 updates;8000cap; no fixed-poll extrapolation, seeds, retries or launch by this preparer.',
        hardware='Literal shared all256 DMA/E008/deadline/CHR/IRQ/NMI/AXY/P/SP/5SMC/bank/input/death/motion guards unchanged.',
        performance='No timing observer added. Whole-route wall/Main counts are not matched-work FPS; source saving is separately scoped.')
    ready['storage'] = dict(total_per_run_bytes=2_000_000_000, total_per_run_files=64,
                            one_compact_PPU_container_bytes=cfg['capture_bytes'], native_PNG_files=0,
                            maximum_offline_selected_frames=8, central_capture_lease_required=True)
    ready['maximum_native_launches'] = 1
    ready['native_grant_required'] = True
    ready['environment'] = dict(emulator='C:/Mesen2/Mesen.exe', core='C:/Mesen2/MesenCore.dll',
        actual_adjacent_settings='C:/Mesen2/settings.json', no_settings_write_restore_or_copy=True,
        actual_cli=[v for v in ready['command'] if v.startswith('--option=')],
        scope='Actual explicit existing runtime and adjacent settings bound for ROOT prelaunch review; no native grant or run.')
    deps = {Path(p) for p in ready['bindings']}
    deps.update({Path(__file__).resolve(), Path(C.__file__).resolve(), Path(H.__file__).resolve(),
                 R / 'tools/audit/bill_inert_pool_sparse_v1.py', FINAL, cpu_path, build_path, ordinary_path,
                 B / 'bill_inert_pool_remaining_weapons.s', B / 'bill_inert_pool.patch', P / 'command.json',
                 parent / 'ready.json', parent / 'result.json', navigation, policy,
                 Path('C:/Mesen2/Mesen.exe'), Path('C:/Mesen2/MesenCore.dll'), Path('C:/Mesen2/settings.json')})
    ready['bindings'] = {str(p): H.sha(p) for p in sorted(deps)}
    put(ready_path, ready)
    print(json.dumps(dict(ready=str(ready_path), sha256=H.sha(ready_path), bindings=len(deps),
                         final_source_sha256=H.sha(FINAL), candidate_sha256=H.sha(rom), command=ready['command'])))


if __name__ == '__main__':
    main()
