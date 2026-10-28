"""One sparse current326 Bill inert-pool experiment; never launches native."""
from pathlib import Path
import argparse
import configparser
import difflib
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
P = 'bill_inert_pool'
BASE = B / 'zelda2_easy_glove.nes'
EXPECTED = '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from prepare_cv3_dmc_mirror import prepare

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finish-built', action='store_true')
    parser.add_argument('--refresh-guard', action='store_true')
    parser.add_argument('--ordinary', action='store_true')
    parser.add_argument('--verify-build', action='store_true')
    args = parser.parse_args()
    assert sha(BASE) == EXPECTED
    if args.ordinary:
        original = json.loads((B / 'bill_early_cache_flagoff.json').read_text())
        rows = []
        for row in original['rows']:
            target = B / (P + '_ordinary_' + row['mapper'] + '.nes')
            assert not target.exists()
            command = [s.replace('bill_early_cache_main.c', P + '_main.c')
                        .replace('bill_early_cache_entrypoint.s', P + '_entrypoint.s')
                        .replace('bill_early_cache_flagoff.nes', target.name) for s in row['command']]
            expanded = [s for s in command if s.startswith('ENABLE_MMC5_EXPANDED=')]
            assert all(s == 'ENABLE_MMC5_EXPANDED=0' for s in expanded)
            # The original command relied on the actual default0. Make it
            # explicit in this fresh ordinary build without changing options.
            if not expanded:
                command[-2:-2] = ['--asm-define', 'ENABLE_MMC5_EXPANDED=0', '-D', 'ENABLE_MMC5_EXPANDED=0']
            run = subprocess.run(command, cwd=R, capture_output=True, text=True)
            target.with_suffix('.log').write_text(run.stdout + run.stderr)
            assert run.returncode == 0, run.stdout + run.stderr
            assert sha(target) == row['expected']
            rows.append(dict(mapper=row['mapper'], sha256=sha(target), expected=row['expected'], command=command))
        receipt = B / (P + '_ordinary.json')
        assert not receipt.exists()
        receipt.write_text(json.dumps(dict(passed=True, native_run=False,
                           same_overlay_sha256=sha(B / (P + '_remaining_weapons.s')), rows=rows,
                           ordinary_command_reference_sha256=sha(B / 'bill_early_cache_flagoff.json')),
                           indent=2) + '\n', newline='\n')
        print(json.dumps(dict(passed=True, rows=[{k: x[k] for k in ['mapper', 'sha256']} for x in rows])))
        return
    old = scoped_load(BASE)
    source = R / 'src/remaining_weapons.s'
    text = source.read_text()
    samus = ('  jsr AdvanceFreeze\n  jsr Screw\n  ldx #0\n  stx AvSlot\n'
             '  stx RgSlot\n  dex\n  clc                         ; Each original empty slot compared type0 to32.\n  jmp Done\n')
    assert text.count(samus) == 1
    changed = text.replace(samus,
        '  jsr AdvanceFreeze\n  jsr Screw\n'
        '.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n'
        '  clc                         ; Samus empty slots compare type0 to32.\n'
        'BillNoAdvancedFinish:\n'
        '.endif\n  ldx #0\n  stx AvSlot\n  stx RgSlot\n  dex\n'
        '.if !(::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5)\n'
        '  clc                         ; Original ordinary-target instruction order.\n'
        '.endif\n  jmp Done\n')
    pool = ('::BillEarlyCachePool:\n  lda RgShotType,x\n  bne BillEarlyRange\n'
            'BillEarlyNext:\n  dex\n  bpl ::BillEarlyCachePool\n'
            '  jmp RemainingWeapons::EnemiesReady\nBillEarlyRange:\n'
            '  cmp #32\n  bcc BillEarlyNext\n  cmp #47\n'
            '  bcc BillEarlyPrepare\n  bcs BillEarlyNext\n'
            'BillEarlyPrepare:\n  jmp RemainingWeapons::PrepareActiveEnemies\n'
            '  .assert *-::BillEarlyCachePool=24,error,"Existing unreachable24B pad"\n')
    assert changed.count(pool) == 1
    changed = changed.replace(pool,
        '::BillEarlyCachePool:\n  lda RgShotType,x\nBillEarlyRange:\n'
        '  cmp #32\n  bcc BillEarlyNext\n  cmp #47\n  bcc BillEarlyPrepare\n'
        'BillEarlyNext:\n  dex\n  bpl ::BillEarlyCachePool\n'
        '  ; No32..46 consumer: keep freeze clocks, omit the inert second scan.\n'
        '  ; Final slot0 carry is0 below32,1 above46; AdvanceFreeze preserves it.\n'
        '  jsr RemainingWeapons::AdvanceFreeze\n'
        '  jmp RemainingWeapons::BillNoAdvancedFinish\n'
        'BillEarlyPrepare:\n  jmp RemainingWeapons::PrepareActiveEnemies\n'
        '  .assert *-::BillEarlyCachePool=23,error,"Existing owned24B pool span"\n'
        '  .res 1,$ea\n'
        '  .assert *-::BillEarlyCachePool=24,error,"Existing owned24B pool span"\n')
    empty_at = location(old, 'RemainingWeapons::SamusEmpty')
    freeze_at = location(old, 'RemainingWeapons::AdvanceFreeze')
    pool_at = location(old, 'BillEarlyCachePool')
    assert freeze_at - empty_at == 19
    assert old['raw'][pool_at + 24:pool_at + 27] == bytes([0xae, address(old, 'MmMul') + 2 & 255, (address(old, 'MmMul') + 2) >> 8])
    leaves = [B / (P + suffix) for suffix in ['_remaining_weapons.s', '_entrypoint.s', '_main.c', '.nes', '_build.json']]
    overlay, entry, main_c, out, proof_path = leaves
    if args.verify_build:
        out = B / (P + '_verify.nes')
        proof_path = B / (P + '_verify_build.json')
        assert not out.exists() and not proof_path.exists()
    ep = (R / 'src/entrypoint.s').read_bytes()
    include = b'.include "remaining_weapons.s"'
    assert ep.count(include) == 1
    entry_bytes = ep.replace(include, b'.include "' + overlay.name.encode() + b'"')
    if args.verify_build:
        assert overlay.read_text() == changed and entry.read_bytes() == entry_bytes
        assert main_c.read_bytes() == (R / 'src/main.c').read_bytes()
    elif args.refresh_guard:
        failure = json.loads((B / (P + '_guard_negative.json')).read_text())
        import zipfile
        assert sha(B / (P + '_guard_negative.zip')) == failure['archive_sha256']
        assert sha(out) == failure['expanded_ROM_sha256']
        with zipfile.ZipFile(B / (P + '_guard_negative.zip')) as saved:
            for leaf in [overlay, proof_path]:
                assert leaf.read_bytes() == saved.read(leaf.name)
        overlay.write_text(changed, newline='\n')
    elif args.finish_built:
        failure = json.loads((B / (P + '_build_negative.json')).read_text())
        assert failure['passed'] is False and not proof_path.exists()
        for path, expected in failure['bindings'].items():
            assert sha(path) == expected, path
        assert overlay.read_text() == changed and entry.read_bytes() == entry_bytes
        assert main_c.read_bytes() == (R / 'src/main.c').read_bytes()
    else:
        assert not any(p.exists() for p in leaves), 'Never overwrite frozen candidate leaves'
        overlay.write_text(changed, newline='\n')
        entry.write_bytes(entry_bytes)
        main_c.write_bytes((R / 'src/main.c').read_bytes())
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(R / 'build_options.ini')
    defines = {k: v for section in cfg.values() for k, v in section.items()}
    defines.update(MAPPER_MMC3='0', MAPPER_MMC5='1', ENABLE_CROSSOVER='1', ENABLE_MMC5_EXPANDED='1')
    command = [str(R / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502x', '-t', 'nes', '-g', '-Oisr', '-vm', '-T',
               '-C', str(R / 'smb1base-mmc5-expanded.cfg'), '--ld-args', '--dbgfile,' + str(out.with_suffix('.dbg')),
               '--include-dir', str(R), '--asm-include-dir', str(B), '--asm-include-dir', str(R / 'src'),
               '--asm-include-dir', str(R), '--bin-include-dir', str(R), '-m', str(out.with_suffix('.map')),
               '-Ln', str(out.with_suffix('.lbl')), '-o', str(out)]
    for k, v in defines.items():
        command += ['--asm-define', k + '=' + v, '-D', k + '=' + v]
    command += [str(main_c), str(entry)]
    if not args.finish_built:
        run = subprocess.run(command, cwd=R, capture_output=True, text=True)
        out.with_suffix('.build.log').write_text(run.stdout + run.stderr)
        assert run.returncode == 0, run.stdout + run.stderr
        prepare(R, out)
    if args.refresh_guard:
        assert sha(out) == failure['expanded_ROM_sha256'], 'Guard-only repair must retain exact expanded candidate'
    new = scoped_load(out)
    changes = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    assert changes and all((i - 16) // 8192 == 6 for i in changes)
    assert all(empty_at <= i < freeze_at or pool_at <= i < pool_at + 24 for i in changes)
    allowed = {prefix + name for prefix in ['', 'AvHomeFriction::']
               for name in ['BillEarlyRange', 'BillEarlyNext', 'BillEarlyPrepare']}
    moved = {n: [v.get('val'), new['syms'].get(n, {}).get('val')] for n, v in old['syms'].items()
             if v.get('val') != new['syms'].get(n, {}).get('val') or v.get('seg') != new['syms'].get(n, {}).get('seg')}
    real_moves = {n: v for n, v in moved.items() if not n.split('::')[-1].startswith('LOCAL-MACRO_SYMBOL-')}
    assert set(real_moves) <= allowed, real_moves
    patch = B / (P + '.patch')
    patch.write_text(''.join(difflib.unified_diff(text.splitlines(True), changed.splitlines(True),
                     fromfile='current326/src/remaining_weapons.s', tofile='private/src/remaining_weapons.s')), newline='\n')
    proof = dict(passed=True, source_only=True, native_run=False, parent_sha256=EXPECTED,
                 candidate_sha256=sha(out), ROM=str(out), changed_bytes=len(changes), changed_banks=[6],
                 no_unexpected_ROM_bytes=True, header_CHR_other_banks_exact=True,
                 real_private_label_moves=real_moves, automatic_macro_label_changes=len(moved) - len(real_moves),
                 original_shared_empty_span=19, original_owned_pool_span=24, new_allocated_bytes=0,
                 all_other_old_labels_exact=True, no_new_RAM_or_NMI_or_bank_roundtrip=True,
                 command=command, overlay=str(overlay), patch_sha256=sha(patch),
                 bindings={str(p): sha(p) for p in [Path(__file__), BASE, BASE.with_suffix('.dbg'), BASE.with_suffix('.lbl'),
                     source, R / 'src/entrypoint.s', R / 'src/main.c', R / 'smb1base-mmc5-expanded.cfg',
                     R / 'build_options.ini', overlay, entry, main_c]})
    proof_path.write_text(json.dumps(proof, indent=2) + '\n', newline='\n')
    print(json.dumps({k: proof[k] for k in ['candidate_sha256', 'changed_bytes', 'real_private_label_moves']}))


if __name__ == '__main__':
    main()
