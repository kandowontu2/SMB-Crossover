"""Separate private parser-loop optimization on immutable TMNT multiply2f61.

No production edits, native launch, new audio state or new hardware consumers.
"""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha


PARENT = '2f61cd0ce8d1fdef09185bdeaad3d5fcb1072f6a28cc54c05c0c1c39ca792523'
RECEIPT = 'b94d37e9a96588511791782a40872a051ecdbeac65c84ec09993c4082df9bfb2'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.ready / 'receipt.json') == RECEIPT
    assert sha(a.ready / 'candidate.nes') == PARENT
    old_rom = (a.ready / 'candidate.nes').read_bytes()
    offset = 16 + 63 * 8192
    assert old_rom[offset + 0x180:offset + 0x1b2] == bytes([255]) * 50
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.ready / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/tmnt-native.inc'
    original = path.read_text()
    text = original
    # Taken BCS already proves carry=1. Retain the original initial SEC/SBC,
    # every actual subtraction and last-SBC flags; only skip redundant SEC.
    before = '.assert *=$a6a5,lderror,"Original instruction offset 86a5"\n  .byte $b0,$f9 ; BCS source$86a0'
    after = '.assert *=$a6a5,lderror,"Original instruction offset 86a5"\n  .byte $b0,$fa ; BCS source$86a1: carry already set on the taken edge'
    assert text.count(before) == 1
    text = text.replace(before, after)
    # Identical 17-byte span. Moving DEX to the back edge removes the repeated
    # unconditional JMP and repeated BEQ; ADC, carry early exit and final CMP
    # remain literal original operations, including last-ADC overflow.
    before = '  .assert *=$aad4,lderror,"Original instruction offset 8ad4"\n  JMP $aacc\n'
    after = '  .assert *=$aad4,lderror,"Original instruction offset 8ad4"\n  DEX\n  .byte $d0,$f8 ; BNE source$8acf\n'
    assert text.count(before) == 1
    text = text.replace(before, after)
    # Exact same handler pointers/E2/E3 and restored channel X. Interleaving
    # vectors at offsets0/16/32/48 eliminates only three index LSRs. Padding
    # follows the unconditional indirect JMP and cannot execute.
    start = text.index('  .assert *=$a937,lderror,"Original instruction offset 8937"')
    end = text.index('  .assert *=$a951,lderror,"Original instruction offset 8951"', start)
    text = text[:start] + '''  .assert *=$a937,lderror,"Original instruction offset 8937"
  AND #$30
  TAX
  LDA ::TnParserVectors,x
  STA ::TnAudioZp+$02
  LDA ::TnParserVectors+1,x
  STA ::TnAudioZp+$03
  LDX ::TnAudioRam+$92
  LDA (::TnAudioZp+$00),y
  AND #$0f
  CLC ; The three original LSRs always shifted out zero bits.
  JMP (::TnAudioZp+$02)
  .byte $ff,$ff ; Unreachable tail; preserve following original PCs.
''' + text[end:]
    path.write_text(text)
    path = source / 'src/tmnt_audio.s'
    text = path.read_text()
    before = '.include "tmnt_audio_multiply.s"\n'
    assert text.count(before) == 1
    path.write_text(text.replace(before, before + '.include "tmnt_audio_parser.s"\n'))
    vectors = old_rom[offset + 0xfc4:offset + 0xfcc]
    rows = []
    for index in range(4):
        rows.append(' .byte ' + ','.join(f'${value:02x}' for value in vectors[index * 2:index * 2 + 2]))
        if index != 3: rows.append(' .res 14,$ff')
    helper = '''; Exact original command vectors with direct high-nibble indexing.
; A180..A1B1 was linker-declared FF fill, outside all source data and helpers.
.assert *=$a173,lderror,"Unchanged multiply helper end"
.res 13,$ff
TnParserVectors:
''' + '\n'.join(rows) + '''
.assert TnParserVectors=$a180,lderror,"Verified unused native writer tail"
.assert *=$a1b2,lderror,"Complete four interleaved original vectors"
.export TnParserVectors
'''
    (source / 'src/tmnt_audio_parser.s').write_text(helper)
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    result = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    new_rom = (a.output / 'candidate.nes').read_bytes()
    changes = {n: sum(x != y for x, y in zip(old_rom[16 + n * 8192:16 + (n + 1) * 8192], new_rom[16 + n * 8192:16 + (n + 1) * 8192])) for n in range(128)}
    changes = {n: size for n, size in changes.items() if size}
    assert set(changes) == {63}
    assert old_rom[:16] == new_rom[:16] and old_rom[1048592:] == new_rom[1048592:]
    assert qualified(a.ready / 'candidate.nes').items() <= qualified(a.output / 'candidate.nes').items()
    prep = json.loads((a.ready.parent / 'multiply-current-a983-v1/preparation.json').read_text())
    prep.update(candidate_ROM_sha256=sha(a.output / 'candidate.nes'), parser_parent_sha256=PARENT)
    (a.output / 'preparation.json').write_text(json.dumps(prep, indent=2) + '\n')
    manifest, patch = {}, ''
    for name in ['src/tmnt-native.inc', 'src/tmnt_audio.s', 'src/tmnt_audio_parser.s']:
        old, new = a.ready / 'source' / name, source / name
        manifest[name] = dict(before_sha256=sha(old) if old.exists() else None, after_sha256=sha(new))
        patch += ''.join(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [], new.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(patch)
    proof = dict(passed=True, source_only=True, native_run=False, accepted=False,
                 production_parent_sha256=CURRENT, donor_multiply_sha256=PARENT,
                 candidate_ROM_sha256=sha(a.output / 'candidate.nes'), changed_PRG_bytes=changes,
                 source_changes=manifest, existing_qualified_symbols_exact=True,
                 new_RAM_hardware_accesses=False, original_vectors_hex=vectors.hex(),
                 verified_unused_table_span=[0xa180, 0xa1b2], checker_sha256=sha(Path(__file__)))
    (a.output / 'parser-preparation.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
