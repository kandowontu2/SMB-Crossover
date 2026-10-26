"""Prepare a private ACBD multiply helper and accurate MMC5 product CPU memory.

No production edits or native launch. Source product registers are NMI-only,
mutually exclusive with the existing Proto audio user; they are not restored.
"""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import Memory
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha


class MathMemory(Memory):
    def __init__(self, bundle):
        self.operands = [37, 149]
        self.math_events = []
        self.executing_PC = None
        super().__init__(bundle)

    def __getitem__(self, at):
        if isinstance(at, int) and at in [0x5205, 0x5206]:
            value = (self.operands[0] * self.operands[1]) >> (8 if at == 0x5206 else 0)
            self.math_events.append(['R', at, value & 255, self.executing_PC])
            return value & 255
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if isinstance(at, int) and at in [0x5205, 0x5206]:
            self.operands[at - 0x5205] = value
            self.math_events.append(['W', at, value, self.executing_PC])
        super().__setitem__(at, value)


HELPER = '''; MMC5-only native TMNT music. No persistent multiplier operand owner.
; AudioUpdate selects either char1 Proto or char19 TMNT inside one NMI; IRQ
; touches neither product register. Both users write their operands before reads.
; Preserve original E2/E4/E5, final-ADC V, D/I/X/Y, C=0 and final A/N/Z.
.proc TnFastProduct
 and #15
 beq Zero
 cmp #2
 bcc One
 sta $5205
 lda a:TnAudioRam+4,x
 sta $5206
 lda $5205
 sta z:TnAudioZp+4
 ; Reproduce the ORIGINAL last repeated-add ADC overflow, including wrap.
 sec
 sbc a:TnAudioRam+4,x
 clc
 adc a:TnAudioRam+4,x
 lda $5206
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 lda z:TnAudioZp+4
 jmp $acd9                  ; Authentic four ASL/ROL pairs and final LDA/RTS.
One:
 lda a:TnAudioRam+4,x
 sta z:TnAudioZp+4
 lsr a
 lsr a
 lsr a
 lsr a
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 clv                        ; Original last ADC is coefficient + zero.
 clc
 lda z:TnAudioZp+5
 rts
Zero:
 lda #0
 sta z:TnAudioZp+4
 sta z:TnAudioZp+5
 lda #$ff
 sta z:TnAudioZp+2
 clc                        ; Incoming V remains live for the zero case.
 lda #0
 rts
.endproc
.assert TnFastProduct=$a125,lderror,"Verified unused native writer tail"
.assert *<=$a200,lderror,"Retain original duration helper and all later PCs"
.export TnFastProduct
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.ready / 'receipt.json') == '97a8dd5abe01d8d9217800ed8c1be22ebf050a3dbce04a8ae800d670b754b3a6'
    parent = (a.ready / 'candidate.nes').read_bytes()
    assert sha(a.ready / 'candidate.nes') == 'a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003'
    assert parent[16 + 63 * 8192 + 0x125:16 + 63 * 8192 + 0x200] == bytes([255]) * 219
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.ready / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/tmnt-native.inc'
    text = path.read_text()
    old = '  .assert *=$acbd,lderror,"Original instruction offset 8cbd"\n  AND #$0f\n  .assert *=$acbf,lderror,"Original instruction offset 8cbf"\n  STA ::TnAudioZp+$02\n'
    assert text.count(old) == 1
    text = text.replace(old, '  .assert *=$acbd,lderror,"Original instruction offset 8cbd"\n  JMP ::TnFastProduct\n  NOP ; Four-byte span; old internal counter store is no longer an entry.\n')
    path.write_text(text)
    path = source / 'src/tmnt_audio.s'
    text = path.read_text()
    assert text.count('.include "tmnt_audio_writers.s"\n') == 1
    path.write_text(text.replace('.include "tmnt_audio_writers.s"\n', '.include "tmnt_audio_writers.s"\n.include "tmnt_audio_multiply.s"\n'))
    (source / 'src/tmnt_audio_multiply.s').write_text(HELPER)
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    result = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    child = (a.output / 'candidate.nes').read_bytes()
    bank = lambda data, n: data[16 + n * 8192:16 + (n + 1) * 8192]
    deltas = {n: sum(x != y for x, y in zip(bank(parent, n), bank(child, n))) for n in range(128)}
    deltas = {n: count for n, count in deltas.items() if count}
    assert set(deltas) == {63} and parent[:16] == child[:16] and parent[1048592:] == child[1048592:]
    assert qualified(a.ready / 'candidate.nes').items() <= qualified(a.output / 'candidate.nes').items()
    prep = json.loads((a.ready.parent / 'current-swap-v2/preparation.json').read_text())
    prep['candidate_ROM_sha256'] = sha(a.output / 'candidate.nes')
    prep['source_multiply_parent_sha256'] = sha(a.ready / 'candidate.nes')
    (a.output / 'preparation.json').write_text(json.dumps(prep, indent=2) + '\n')
    names = ['src/tmnt-native.inc', 'src/tmnt_audio.s', 'src/tmnt_audio_multiply.s']
    manifest, patch = {}, ''
    for name in names:
        prior = a.ready / 'source' / name
        after = source / name
        manifest[name] = dict(before_sha256=sha(prior) if prior.exists() else None, after_sha256=sha(after))
        patch += ''.join(difflib.unified_diff(prior.read_text().splitlines(True) if prior.exists() else [], after.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(patch)
    receipt = dict(passed=True, accepted=False, source_only=True, native_run=False,
                   accepted_parent_ROM_sha256=CURRENT, donor_a983_ROM_sha256=sha(a.ready / 'candidate.nes'),
                   candidate_ROM_sha256=sha(a.output / 'candidate.nes'), changed_PRG_bytes=deltas,
                   changed_source_files=manifest, existing_qualified_symbols_exact=True,
                   verified_original_unused_A125_A1FF_bytes=219, no_new_RAM=True,
                   hardware_multiplier_reads_product_not_operand_restore=True,
                   Mesen_model_source='https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h',
                   tool_sha256=sha(Path(__file__)), limits='Private source assembly only. Hardware math ownership/full-domain/original/IRQ/outer/cadence qualification is separate; existing unsupported nested-NMI domain is not claimed.')
    (a.output / 'multiply-preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
