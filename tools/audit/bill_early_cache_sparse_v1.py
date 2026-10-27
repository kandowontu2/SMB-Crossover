"""One sparse expanded-MMC5 Bill cache-admission experiment; no native."""
from pathlib import Path
import configparser
import difflib
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
P = 'bill_early_cache'
BASE = B / 'samus_fixed_hud_current4a.nes'
EXPECTED = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from prepare_cv3_dmc_mirror import prepare

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
GUARD = '.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n'


def main():
    assert sha(BASE) == EXPECTED
    old = scoped_load(BASE)
    src = R / 'src/remaining_weapons.s'
    text = src.read_text()
    changed = text
    token = '  cmp #CHARACTER_BILL\n  beq PrepareEnemies\n'
    assert changed.count(token) == 1
    changed = changed.replace(token, '  cmp #CHARACTER_BILL\n' + GUARD +
        '  beq BillEarlyCacheJump\n.else\n  beq PrepareEnemies\n.endif\n')
    token = ('  lda SelectedCharacter\n  cmp #CHARACTER_SAMUS\n'
             '  jeq SamusEmpty\n  jmp EnemiesReady\nPrepareActiveEnemies:\n')
    assert changed.count(token) == 1
    changed = changed.replace(token, GUARD +
        '  lda SelectedCharacter\n  cmp #CHARACTER_SAMUS\n'
        '  bne EnemiesReady\n  jmp SamusEmpty\n'
        'BillEarlyCacheJump:\n  jmp ::BillEarlyCacheGate\n.else\n' +
        token.removesuffix('PrepareActiveEnemies:\n') + '.endif\nPrepareActiveEnemies:\n')
    token = '  jmp Missile\n  .res 15,$ea\nMissile:\n'
    assert changed.count(token) == 1
    changed = changed.replace(token, '  jmp Missile\n' + GUARD +
        '::BillEarlyCacheGate:\n  lda InvFresh\n  and #Select_Button\n'
        '  beq BillEarlyNoSelect\n  jmp RemainingWeapons::PrepareActiveEnemies\n'
        'BillEarlyNoSelect:\n  ldx #9\n  jmp ::BillEarlyCachePool\n'
        '  .assert *-::BillEarlyCacheGate=15,error,"Existing unreachable15B pad"\n'
        '.else\n  .res 15,$ea\n.endif\nMissile:\n')
    token = '  jmp HighByte\n  .res 24, $ea\nHighByte:\n'
    assert changed.count(token) == 1
    changed = changed.replace(token, '  jmp HighByte\n' + GUARD +
        '::BillEarlyCachePool:\n  lda RgShotType,x\n  bne BillEarlyRange\n'
        'BillEarlyNext:\n  dex\n  bpl ::BillEarlyCachePool\n'
        '  jmp RemainingWeapons::EnemiesReady\n'
        'BillEarlyRange:\n  cmp #32\n  bcc BillEarlyNext\n  cmp #47\n'
        '  bcc BillEarlyPrepare\n  bcs BillEarlyNext\n'
        'BillEarlyPrepare:\n  jmp RemainingWeapons::PrepareActiveEnemies\n'
        '  .assert *-::BillEarlyCachePool=24,error,"Existing unreachable24B pad"\n'
        '.else\n  .res 24, $ea\n.endif\nHighByte:\n')
    pad15 = location(old, 'RemainingWeapons::Missile') - 15
    pad24 = location(old, 'AvHomeFriction::HighByte') - 24
    for at, size, target in [(pad15, 15, 'RemainingWeapons::Missile'),
                             (pad24, 24, 'AvHomeFriction::HighByte')]:
        assert old['raw'][at:at + size] == b'\xea' * size
        assert old['raw'][at - 3:at] == bytes([0x4c, address(old, target) & 255, address(old, target) >> 8])
        assert not any(int(q.get('val', '0'), 0) in range(address(old, target) - size, address(old, target))
                       and q.get('seg') == old['syms'][target]['seg'] for q in old['syms'].values())
    overlay = B / (P + '_remaining_weapons.s')
    ep = B / (P + '_entrypoint.s')
    out = B / (P + '.nes')
    for f in [overlay, ep, out]:
        assert not f.exists(), ('No overwriting frozen output', f)
    overlay.write_text(changed, newline='\n')
    main_source = R / 'src/entrypoint.s'
    raw_ep = main_source.read_bytes()
    needle = b'.include "remaining_weapons.s"'
    assert raw_ep.count(needle) == 1
    ep.write_bytes(raw_ep.replace(needle, b'.include "' + overlay.name.encode() + b'"'))
    c = B / (P + '_main.c')
    assert not c.exists()
    c.write_bytes((R / 'src/main.c').read_bytes())
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(R / 'build_options.ini')
    defs = {k: v for s in cfg.values() for k, v in s.items()}
    defs.update(MAPPER_MMC3='0', MAPPER_MMC5='1', ENABLE_CROSSOVER='1', ENABLE_MMC5_EXPANDED='1')
    command = [str(R / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502x', '-t', 'nes', '-g', '-Oisr',
        '-vm', '-T', '-C', str(R / 'smb1base-mmc5-expanded.cfg'), '--ld-args', '--dbgfile,' + str(out.with_suffix('.dbg')),
        '--include-dir', str(R), '--asm-include-dir', str(B), '--asm-include-dir', str(R / 'src'),
        '--asm-include-dir', str(R), '--bin-include-dir', str(R), '-m', str(out.with_suffix('.map')),
        '-Ln', str(out.with_suffix('.lbl')), '-o', str(out)]
    for k, v in defs.items():
        command += ['--asm-define', k + '=' + v, '-D', k + '=' + v]
    command += [str(c), str(ep)]
    run = subprocess.run(command, cwd=R, capture_output=True, text=True)
    out.with_suffix('.build.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stdout + run.stderr
    prepare(R, out)
    new = scoped_load(out)
    changes = [i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    assert changes and all((i - 16) // 8192 == 6 for i in changes)
    moved = {n: [q.get('val'), new['syms'].get(n, {}).get('val')] for n, q in old['syms'].items()
             if q.get('val') != new['syms'].get(n, {}).get('val') or q.get('seg') != new['syms'].get(n, {}).get('seg')}
    real_moves = {n: v for n, v in moved.items() if not n.split('::')[-1].startswith('LOCAL-MACRO_SYMBOL-')}
    assert not real_moves, real_moves
    patch = B / (P + '.patch')
    patch.write_text(''.join(difflib.unified_diff(text.splitlines(True), changed.splitlines(True),
        fromfile='current6be/src/remaining_weapons.s', tofile='private/src/remaining_weapons.s')), newline='\n')
    proof = dict(source_only=True, native_run=False, parent_sha256=EXPECTED,
        candidate_sha256=sha(out), ROM=str(out), changed_bank=6, changed_bytes=len(changes),
        exact_unexpected_ROM_bytes=0, all_header_CHR_other_banks_exact=True,
        genuine_old_labels_RAM_and_segments_exact=len(old['syms']) - len(moved),
        automatic_debug_macro_serial_changes=moved, no_real_label_moves=True,
        pads=[dict(offset=pad15, size=15, previous_unreachable_NOPs=True),
              dict(offset=pad24, size=24, previous_unreachable_NOPs=True)],
        no_new_RAM_segments_or_NMI_code=True, source_overlay=dict(path=str(overlay), sha256=sha(overlay)),
        patch_sha256=sha(patch), command=command,
        bindings={str(f): sha(f) for f in [Path(__file__), BASE, BASE.with_suffix('.dbg'), BASE.with_suffix('.lbl'),
            src, main_source, R / 'src/main.c', R / 'smb1base-mmc5-expanded.cfg', R / 'build_options.ini', overlay, ep, c]})
    proof_file = B / (P + '_build.json')
    assert not proof_file.exists()
    proof_file.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: proof[k] for k in ['candidate_sha256', 'changed_bytes', 'no_real_label_moves']}))


if __name__ == '__main__':
    main()
