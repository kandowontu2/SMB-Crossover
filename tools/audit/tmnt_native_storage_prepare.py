"""Rebase native TMNT privately onto a byte-exact current50b5 source freeze.

No production or Git write and no native emulator launch. This is an enabling
source experiment, including owner4 coexistence with the installed CV3 owner3.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
from tmnt_native_storage_driver import ROOT, CURRENT, sha
from check_tmnt_audio_fallback_oc import qualified

OC = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc')

ADMISSION = '''
::TnDmcOwnerAdmission:
 php
 pha
 cmp #4
 bne TnAdmissionCheckOld
 lda #0
 sta a:TnDmcDrain
::TnAdmissionCheckOld:
 lda a:BassDmcActive
 eor #4
 bne TnAdmissionStore
 pla
 pha
 cmp #4
 beq TnAdmissionStore
 lda a:GuestCombinedEnable
 and #15
 sta $4015
 lda #0
 sta a:TnAudioDacHold
 pla
 pha
 bne TnAdmissionNewOwner
 lda #1
 bne TnAdmissionDrain
::TnAdmissionNewOwner:
 lda #0
::TnAdmissionDrain:
 sta a:TnDmcDrain
::TnAdmissionStore:
 pla
 sta a:BassDmcActive
 plp
 rts
.export TnDmcOwnerAdmission
'''

COMPLETION = '''::TnDmcEndedGate:
 php
 lda a:SelectedCharacter
 eor #19
 bne TnDmcLegacyEnd
 lda a:BassDmcActive
 eor #4
 bne TnDmcLegacyEnd
 lda #44
 sta a:TnAudioDacHold
 lda #0
 sta a:BassDmcActive ; completion holds DAC, unlike an explicit owner stop
 plp
 rts
::TnDmcLegacyEnd:
 plp
 jmp Cv3DmcEndedGate

'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'driver', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--swap', action='store_true')
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    frozen = json.loads((a.baseline / 'frozen-source.json').read_text())
    assert frozen['canonical_baseline_exact'] and frozen['parent_ROM_sha256'] == CURRENT
    assert sha(a.baseline / 'baseline.nes') == CURRENT
    assert all(sha(a.baseline / 'source' / n) == h for n, h in frozen['source_files'].items())
    driver = json.loads((a.driver / 'preparation.json').read_text())
    assert driver['duration_optimization'] and driver['bank99_storage_swap'] == a.swap
    assert sha(a.driver / 'tmnt-native.inc') == driver['driver_sha256']
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.baseline / 'source', source)
    changed = {}

    def write(name, text):
        path = source / name
        before = path.read_bytes() if path.exists() else None
        ending = '\r\n' if before and b'\r\n' in before else '\n'
        raw = text.replace('\r\n', '\n').replace('\n', ending).encode()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        changed[name] = dict(before_sha256=hashlib.sha256(before).hexdigest() if before is not None else None,
                             after_sha256=sha(path))

    def text(name):
        return (source / name).read_text()

    def replace(name, old, new):
        value = text(name)
        assert value.count(old) == 1, (name, value.count(old), old[:80])
        write(name, value.replace(old, new))

    held = OC / 'candidate-v7/source'
    held_manifest = json.loads((OC / 'work-packet-v1/manifest.json').read_text())
    held_bindings = {}
    for name in ['src/tmnt_audio.s', 'src/tmnt_audio_writers.s', 'src/tmnt_audio_resident.s', 'audio/tmnt/native-drum.dmc']:
        path = held / name
        assert sha(path) == held_manifest['source_files'][name], name
        held_bindings[name] = sha(path)
    write('src/tmnt_audio.s', (held / 'src/tmnt_audio.s').read_text().replace('eor #3', 'eor #4'))
    writers = (held / 'src/tmnt_audio_writers.s').read_text()
    writers = writers.replace('lda #3                        ; Separate native-music DMC owner.', 'lda #4                        ; Separate native-music DMC owner.')
    assert writers.count('Owner:sta a:BassDmcActive') == 1
    writers = writers.replace('Owner:sta a:BassDmcActive', 'Owner:jsr Cv3DmcOwnerWrite')
    write('src/tmnt_audio_writers.s', writers)
    dest = source / 'audio/tmnt/native-drum.dmc'
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(held / 'audio/tmnt/native-drum.dmc', dest)
    changed['audio/tmnt/native-drum.dmc'] = dict(before_sha256=None, after_sha256=sha(dest))
    native = (a.driver / 'tmnt-native.inc').read_text()
    if a.swap:
        assert native.count('.segment "TMNT_MENU_UI_PREFIX"\n  .incbin "bank99-prefix.bin"\n') == 1
        native = native.replace('.segment "TMNT_MENU_UI_PREFIX"\n  .incbin "bank99-prefix.bin"\n', '')
    write('src/tmnt-native.inc', native)
    samus = text('src/samus_audio.s')
    begin = samus.index('.proc SamusAudioUpdate\n')
    end = samus.index('.endproc\n', begin) + len('.endproc\n')
    original = samus[begin:end]
    cold = original.replace('.proc SamusAudioUpdate', '.proc SamusAudioCold')
    old_return = '  jsr CrossoverGraphicsBank\n  pla\n  BankPRGA a\n  rts\n'
    assert cold.count(old_return) == 1
    cold = cold.replace(old_return, '  jmp SamusAudioFixedReturn\n')
    write('src/tmnt_audio_samus_cold.s', '.pushseg\n.segment "TMNT_SAMUS_AUDIO_COLD"\n' + cold + '.export SamusAudioCold\n.popseg\n')
    hs = (held / 'src/samus_audio.s').read_text()
    start = hs.index('.if ::ENABLE_MMC5_EXPANDED\n.proc SamusAudioUpdate\n')
    finish = hs.index('.else\n.proc SamusAudioUpdate\n', start)
    write('src/samus_audio.s', samus[:begin] + hs[start:finish] + '.else\n' + original + '.endif\n' + samus[end:])
    resident = (held / 'src/tmnt_audio_resident.s').read_text().split('; Exact-ID foreground admissions')[0]
    resident = resident.replace('lda #$fb                      ; Native engine A000 bank7B.', 'lda #$bf                      ; Native engine A000 bank63.')
    if a.swap:
        assert resident.count('lda #$fc') == 2
        resident = resident.replace('lda #$fc', 'lda #$e3')
    dstart, dend = resident.index('::TnDmcEnded:\n'), resident.index('::TnAudioInitGate:\n')
    resident = resident[:dstart] + COMPLETION + resident[dend:]
    resident = resident.replace('TnAudioAdapterReturn,TnDmcEnded,', 'TnAudioAdapterReturn,TnDmcEndedGate,')
    resident = resident.replace(' jmp ExpandedAudioTick\n', ' pla\n plp\n jmp LmNativeMusicGate\n', 1)
    resident = resident.replace('::TnAudioDispatch:\n', '::TnAudioDispatch:\n php\n pha\n', 1)
    resident = resident.replace(' bne TnAudioLegacy\n', ' bne TnAudioLegacy\n pla\n plp\n', 1)
    stop = '::TnAudioStop:\n'
    assert resident.count(stop) == 1
    resident = resident.replace(stop, stop + ' lda a:BassDmcActive\n beq TnStopOwned\n eor #4\n bne TnForgetOldMusic\n::TnStopOwned:\n')
    assert resident.count(' sta a:BassDmcActive\n sta a:TnAudioDacHold') == 1
    resident = resident.replace(' sta a:BassDmcActive\n sta a:TnAudioDacHold', ' jsr Cv3DmcOwnerWrite\n sta a:TnAudioDacHold')
    resident = resident.replace(' lda #$ff\n sta a:XgAudioCharacter', '::TnForgetOldMusic:\n lda #$ff\n sta a:XgAudioCharacter')
    write('src/tmnt_audio_resident.s', resident + ADMISSION)
    replace('src/gradius_audio.s', 'Legacy:\n  jmp LmNativeMusicGate\n', 'Legacy:\n  jmp TnAudioDispatch\n')
    replace('src/guest_audio.s', '  jsr Cv3DmcEndedGate\n', '  jsr TnDmcEndedGate\n')
    replace('src/cv3_dmc_owner.inc', '.proc Cv3DmcOwnerWrite\n sta BassDmcActive\n', '.proc Cv3DmcOwnerWrite\n jsr TnDmcOwnerAdmission\n')
    replace('src/cv3_dmc_complete.s', ' lda #3\n sta BassDmcActive\n', ' lda #3\n jsr TnDmcOwnerAdmission\n')
    replace('src/music_drivers/audio.s', '.proc AudioInit\n  lda #0\n  sta PauseModeFlag\n',
            '.proc AudioInit\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioInitGate\n  nop\n  nop\n.else\n  lda #0\n  sta PauseModeFlag\n.endif\n')
    replace('src/music_drivers/audio.s', '.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n  lda OperMode\n',
            '.proc AudioUpdate\n.if ::ENABLE_CROSSOVER\n.if ::ENABLE_MMC5_EXPANDED\n  jsr TnAudioGlobalGate\n.else\n  lda OperMode\n.endif\n')
    write('src/entrypoint.s', text('src/entrypoint.s') + '\n.if ::ENABLE_MMC5_EXPANDED\n.include "tmnt_audio_samus_cold.s"\n.include "tmnt_audio.s"\n.endif\n')
    cfg = text('smb1base-mmc5-expanded.cfg')
    old = next(line for line in cfg.splitlines(True) if line.strip().startswith('X5_NEW_3F:'))
    memories = [('TN_PREFIX_MEM', 0xa000, 0x2c), ('TN_WRITERS_MEM', 0xa02c, 0x1d4),
                ('TN_DURATION_MEM', 0xa200, 0x100), ('TN_PRODUCTS_MEM', 0xa300, 0x100),
                ('TN_PAD_MEM', 0xa400, 0x29), ('TN_MOVED_MEM', 0xa429, 0x1e9),
                ('X5_NEW_3F', 0xa612, 0x19ee)]
    cfg = cfg.replace(old, ''.join(f'    {name}:start=${start:04x},size=${size:04x},type=ro,file=%O,fill=yes,fillval=$ff,bank=$3f;\n' for name, start, size in memories))
    bname = 'X5_NEW_7C'
    if a.swap:
        old = next(line for line in cfg.splitlines(True) if line.strip().startswith('X5_NEW_63:'))
        cfg = cfg.replace(old, old.replace('size=$2000', 'size=$008a') + '    TN_STORAGE_B_MEM:start=$c08a,size=$1f76,type=ro,file=%O,fill=yes,fillval=$ff,bank=$63;\n')
        bname = 'TN_STORAGE_B_MEM'
    else:
        old = next(line for line in cfg.splitlines(True) if line.strip().startswith('X5_NEW_7C:'))
        cfg = cfg.replace(old, old.replace('start=$a000', 'start=$c000'))
    segments = [('TMNT_NATIVE_AUDIO_PREFIX', 'TN_PREFIX_MEM'), ('TMNT_NATIVE_AUDIO_WRITERS', 'TN_WRITERS_MEM'),
                ('TMNT_DURATION_HELPER', 'TN_DURATION_MEM'), ('TMNT_DURATION_TABLE', 'TN_PRODUCTS_MEM'),
                ('TMNT_MOVED_SOURCE', 'TN_MOVED_MEM'), ('TMNT_NATIVE_AUDIO_A', 'X5_NEW_3F'),
                ('TMNT_NATIVE_AUDIO_B', bname)]
    cfg = cfg.replace('SEGMENTS {\n', 'SEGMENTS {\n' + ''.join(f'    {name}:load={load},type=ro,optional=yes;\n' for name, load in segments) + '    TMNT_SAMUS_AUDIO_COLD:load=X5_NEW_7D,type=ro,start=$d700;\n', 1)
    write('smb1base-mmc5-expanded.cfg', cfg)
    cmd = [sys.executable, str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
           '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    r = subprocess.run(cmd, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    old, new = (a.baseline / 'baseline.nes').read_bytes(), (a.output / 'candidate.nes').read_bytes()
    bank = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    deltas = {n: sum(x != y for x, y in zip(bank(old, n), bank(new, n))) for n in range(128)}
    deltas = {n: count for n, count in deltas.items() if count}
    assert old[:16] == new[:16] and old[16 + 1048576:] == new[16 + 1048576:]
    assert all(bank(old, n) == bank(new, n) for n in [115, 123])
    if a.swap:
        assert bank(old, 124) == bank(new, 124)
        assert bank(old, 99)[:138] == bank(new, 99)[:138]
    qb, qn = qualified(a.baseline / 'baseline.nes'), qualified(a.output / 'candidate.nes')
    moved = {str(k): [v, qn.get(k)] for k, v in qb.items() if qn.get(k) != v}
    assert all(len(k) > 1 and k[0] == 'SamusAudioUpdate' for k, v in qb.items() if qn.get(k) != v), moved
    assert len(moved) == 10, moved
    diff = ''
    for name in changed:
        if name.endswith('.dmc'): continue
        before = (a.baseline / 'source' / name).read_text() if (a.baseline / 'source' / name).exists() else ''
        diff += ''.join(difflib.unified_diff(before.splitlines(True), (source / name).read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(diff)
    result = dict(passed=True, source_rebase_only=True, native_run=False, accepted=False,
                  parent_ROM_sha256=CURRENT, candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
                  changed_source_files=changed, changed_PRG_bytes=deltas, CHR_exact=True,
                  Mac123_Mike115_exact=True, existing_CV3_owner=3, native_TMNT_owner=4,
                  original_public_runtime_addresses_retained=len(qb) - len(moved),
                  root_authorized_genuine_private_Samus_label_exceptions=moved,
                  held_source_bindings=held_bindings, standalone_source=driver,
                  shared125_overlays_limited_by_current_CV3_producer=True,
                  tool_sha256=sha(Path(__file__)),
                  limits='Canonical private source assembly plus structure. Original-linked calls/state, complete owner/tail/interrupt behavior, unaffected outer audio, native DMA and matched cadence remain unqualified.')
    (a.output / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'candidate_ROM_sha256', 'changed_PRG_bytes', 'root_authorized_genuine_private_Samus_label_exceptions']}))


if __name__ == '__main__':
    main()
