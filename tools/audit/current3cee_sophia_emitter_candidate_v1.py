"""One private exact-OAM Sophia horizontal-wave emitter experiment, source only."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

ROOT = Path(__file__).resolve().parents[2]
PARENT_SHA = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


GATE = '''.pushseg
.segment "SOPHIA_WAVE_GATE"
.proc SophiaWaveGate
 lda SelectedCharacter
 cmp #CHARACTER_SOPHIA
 bne Fallback
 lda R1
 cmp #>XgSOPHIAWeapon4Right
 bne Fallback
 lda R0
 cmp #<XgSOPHIAWeapon4Right
 beq PointerReady
 cmp #<XgSOPHIAWeapon4Left
 bne Fallback
PointerReady:
 lda R3
 bne Fallback
 lda R5
 bne Fallback
 lda R7
 cmp #1
 bne Fallback
 lda R4
 cmp #12
 bcc Fallback
 cmp #252
 bcs Fallback
 lda R6
 cmp #3
 bcc Fallback
 lda CurrentOAMOffset
 cmp #244
 bcs Fallback
 tax
 lda GuestOamRotationActive
 beq PhysicalReady
 txa
 clc
 adc RgOamRotation
 tax
PhysicalReady:
 lda R0
 cmp #<XgSOPHIAWeapon4Right
 beq Right
 jmp SophiaWaveLeft
Right:
 jmp SophiaWaveRight
Fallback:
 jmp MetaspriteRenderLoop
.endproc
::SophiaWaveGateEnd:
.assert SophiaWaveGate=$bf33,error,"Fixed current3cee FF gate tail"
.assert *<=$bf8b,error,"Must not reach Darkwing draw owner"
.popseg
.pushseg
.segment "SOPHIA_WAVE_EMITTER"
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.parent / 'candidate.nes') == PARENT_SHA
    pin = json.loads((a.parent / 'source-manifest.json').read_text())
    assert all(sha(a.parent / 'source' / f) == h for f, h in pin.items())
    a.output.mkdir(parents=True, exist_ok=False)
    src = a.output / 'source'
    shutil.copytree(a.parent / 'source', src)
    before = {str(f.relative_to(src)).replace('\\', '/'): sha(f) for f in src.rglob('*') if f.is_file()}
    put(a.output / 'source-before.json', before)
    commands = []

    def build(stem, flag=None):
        cmd = [sys.executable, '-B', str(src / 'tools/build_mmc5_expanded.py'), '--workspace', str(src),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / (stem + '.nes'))]
        if flag:
            cmd += ['--flag-off', flag]
        commands.append(cmd)
        with (a.output / (stem + '.host.log')).open('w') as log:
            r = subprocess.run(cmd, cwd=src, stdout=log, stderr=subprocess.STDOUT)
        assert r.returncode == 0, (a.output / (stem + '.host.log')).read_text()[-5000:]
        return sha(a.output / (stem + '.nes'))

    assert build('baseline') == PARENT_SHA
    ordinary = {mapper: build('ordinary-before-' + mapper, mapper) for mapper in ['mmc3', 'mmc5']}
    old = scoped_load(a.output / 'baseline.nes')
    assert address(old, 'XgSOPHIAWeapon4Right') == 0xc017
    assert address(old, 'XgSOPHIAWeapon4Left') == 0xc00a
    helper = GATE
    records = []
    for face in ['Left', 'Right']:
        symbol = 'XgSOPHIAWeapon4' + face
        at = location(old, symbol)
        record = old['raw'][at:at + 13]
        assert record[0] == 12 and (at - 16) // 8192 == 36
        parts = [record[i:i + 4] for i in range(1, 13, 4)]
        assert all(part[2] == 253 for part in parts)
        assert sorted(part[3] for part in parts) == [4, 244, 252]
        helper += '.proc SophiaWave' + face + '\n'
        for tile, attr, dy, dx in reversed(parts):
            assert not attr & 12
            helper += f''' lda R4
 clc
 adc #${dx:02x}
 sta Sprite_X_Position,x
 lda R6
 clc
 adc #${dy:02x}
 sta Sprite_Y_Position,x
 lda #${attr:02x}
 sta Sprite_Attributes,x
 lda #${tile:02x}
 sta Sprite_Tilenumber,x
 inx
 inx
 inx
 inx
'''
        if face == 'Left':
            helper += ' jmp SophiaWaveTail\n'
        helper += '.endproc\n'
        records.append(dict(symbol=symbol, bank=36, pointer=address(old, symbol), bytes=record.hex(), aliases=[
            'XgSOPHIAWeapon' + str(i) + face for i in range(4, 8)]))
    helper += '''::SophiaWaveTail:
 ; All admitted parts have Yhigh1 and -3<=Yoffset with no underflow.
 ; The native final Y-high ADC therefore leaves V0. Other flags are set by
 ; the identical cursor/rotation epilogue below, including decimal-bit carry.
 clv
 txa
 ldy GuestOamRotationActive
 beq :+
 sec
 sbc RgOamRotation
:
 sta CurrentOAMOffset
 ldy #0
 sec
 rts
::SophiaWaveEmitterEnd:
.assert SophiaWaveLeft=$d523,error,"Current3cee Sophia GFX FF tail"
.assert *<=$d600,error,"Bank36 A-window Water/Ryu/score code begins here"
.popseg
'''
    (src / 'src/sophia_wave_emitter.s').write_text(helper, encoding='utf-8')
    weapon = src / 'src/expanded_weapons.s'
    text = weapon.read_text()
    needle = '  lda #0\n  sta R3\n  jsr MetaspriteRenderLoop\n  lda SelectedCharacter\n  cmp #CHARACTER_RYGAR'
    assert text.count(needle) == 1
    text = text.replace(needle, '  lda #0\n  sta R3\n.if ::ENABLE_MMC5_EXPANDED\n  jsr SophiaWaveGate\n.else\n  jsr MetaspriteRenderLoop\n.endif\n  lda SelectedCharacter\n  cmp #CHARACTER_RYGAR')
    weapon.write_text(text, encoding='utf-8')
    entry = src / 'src/entrypoint.s'
    entry.write_bytes(entry.read_bytes() + b'\n.if ::ENABLE_MMC5_EXPANDED\n.include "sophia_wave_emitter.s"\n.endif\n')
    config = src / 'smb1base-mmc5-expanded.cfg'
    text = config.read_text()
    marker = '    XG_SOPHIA_GFX: load=XG_SOPHIA_MEM, type=ro, optional=yes;'
    assert text.count(marker) == 1
    text = text.replace(marker, marker + '\n    SOPHIA_WAVE_EMITTER: load=XG_SOPHIA_MEM, type=ro, start=$d523, optional=yes;')
    marker = '    METASPRITE: load = PRGA_04, type = ro;'
    assert text.count(marker) == 1
    text = text.replace(marker, marker + '\n    SOPHIA_WAVE_GATE: load=PRGA_04, type=ro, start=$bf33, optional=yes;')
    config.write_text(text, encoding='utf-8')
    build('candidate')
    new = scoped_load(a.output / 'candidate.nes')
    for name, sym in old['syms'].items():
        assert name in new['syms'] and int(sym['val'], 0) == int(new['syms'][name]['val'], 0), ('Moved old symbol', name)
    hook = location(old, 'ExpandedDrawShots')
    call = bytes([0x20, address(old, 'MetaspriteRenderLoop') & 255, address(old, 'MetaspriteRenderLoop') >> 8])
    # The owner has exactly one generic emitter call and retains its R3=0 prefix.
    matches = [i for i in range(hook, location(old, 'ExpandedDrawShots::Done')) if old['raw'][i:i + 3] == call]
    assert len(matches) == 1
    hook = matches[0]
    assert old['raw'][hook - 4:hook] == bytes([0xa9, 0, 0x85, address(old, 'R3')])
    ranges = [(hook, hook + 3, 'sole3B-selected-emitter-call')]
    for begin, end, bank, cpu_begin in [('SophiaWaveGate', 'SophiaWaveGateEnd', 4, 0xbf33),
                                       ('SophiaWaveLeft', 'SophiaWaveEmitterEnd', 36, 0xd523)]:
        start, finish = location(new, begin), location(new, end)
        assert (start - 16) // 8192 == bank and address(new, begin) == cpu_begin
        assert set(old['raw'][start:finish]) == {255}
        ranges.append((start, finish, begin))
    differences = [i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    assert all(any(start <= i < end for start, end, _ in ranges) for i in differences)
    assert old['raw'][:16] == new['raw'][:16] and old['raw'][16 + 128 * 8192:] == new['raw'][16 + 128 * 8192:]
    # Full bank36 A-window subrange is immutable, including hidden bank aliases.
    assert old['raw'][16 + 36 * 8192 + 0x1600:16 + 37 * 8192] == new['raw'][16 + 36 * 8192 + 0x1600:16 + 37 * 8192]
    after = {str(f.relative_to(src)).replace('\\', '/'): sha(f) for f in src.rglob('*') if f.is_file()}
    changed = sorted(f for f in before if before[f] != after[f])
    assert changed == ['smb1base-mmc5-expanded.cfg', 'src/entrypoint.s', 'src/expanded_weapons.s']
    assert set(after) - set(before) == {'src/sophia_wave_emitter.s'}
    overlay = a.output / 'overlay'
    patch = ''
    for name in changed + ['src/sophia_wave_emitter.s']:
        dest = overlay / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / name, dest)
        before_text = (a.parent / 'source' / name).read_text().splitlines(keepends=True) if name in before else []
        patch += ''.join(difflib.unified_diff(before_text, (src / name).read_text().splitlines(keepends=True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'sourcepatch.patch').write_text(patch, encoding='utf-8')
    for mapper in ['mmc3', 'mmc5']:
        assert build('ordinary-after-' + mapper, mapper) == ordinary[mapper]
    put(a.output / 'source-manifest.json', after)
    put(a.output / 'records.json', records)
    put(a.output / 'layout.json', dict(ranges=[dict(start=x, end=y, purpose=z) for x, y, z in ranges],
                                      differing_bytes=len(differences), all_old_symbols=len(old['syms']),
                                      bank36_A_window_1600_2000_exact=True, CHR_and_header_exact=True))
    proof = dict(passed=True, source_only=True, native_run=False, adopted=False,
                 baseline_ROM_sha256=PARENT_SHA, candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
                 fresh_baseline_exact=True, all_old_symbol_values_exact=len(old['syms']),
                 changed_original_source_files=changed, new_source_file='src/sophia_wave_emitter.s',
                 overlay_files=changed + ['src/sophia_wave_emitter.s'], different_ROM_bytes=len(differences),
                 records_sha256=sha(a.output / 'records.json'), source_manifest_sha256=sha(a.output / 'source-manifest.json'),
                 layout_sha256=sha(a.output / 'layout.json'), ordinary_flagoff_exact=ordinary,
                 commands=commands, tool_sha256=sha(__file__),
                 limits='Build/layout/fill/old-address/ordinary source proof only. CPU equivalence, actual IRQ/NMI ownership and costs are separate. No starvation fix, cadence or native-gameplay qualification.')
    put(a.output / 'proof.json', proof)
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
