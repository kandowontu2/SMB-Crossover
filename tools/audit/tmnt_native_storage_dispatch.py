"""Remove proven-dead entry A/C/N/Z preservation from native TMNT dispatch.

Creates a fresh private source candidate; never changes the ready-v1 donor.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    frozen = json.loads((a.ready / 'receipt.json').read_text())
    assert frozen['parent_ROM_sha256'] == CURRENT
    assert sha(a.ready / 'candidate.nes') == frozen['candidate_ROM_sha256'] == '8e2fa5de95edc5be33bbb20fa9262c2f58e3ebfcb793d82a740275a16409b790'
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.ready / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/tmnt_audio_resident.s'
    before = path.read_bytes()
    text = before.decode()
    assert not b'\r\n' in before
    old = '''::TnAudioDispatch:
 php
 pha
 lda a:SelectedCharacter
 cmp #19
 bne TnAudioLegacy
 pla
 plp
 lda #$bf                      ; Native engine A000 bank63.
'''
    new = '''::TnAudioDispatch:
 ; Both actual destinations overwrite A/N/Z and C before reading them.
 ; LDA/CMP preserve V/D/I; no entry register save is live on either path.
 lda a:SelectedCharacter
 cmp #19
 bne TnAudioLegacy
 lda #$bf                      ; Native engine A000 bank63.
'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    old = ''' jmp TnAudioUpdate
::TnAudioLegacy:
 pla
 plp
 jmp LmNativeMusicGate
'''
    new = ''' jmp TnAudioUpdate
 .res 4,$ea                    ; Unreachable padding preserves real labels.
::TnAudioLegacy:
 jmp LmNativeMusicGate
 .res 2,$ea                    ; Keep every following owned entry fixed too.
'''
    assert text.count(old) == 1
    path.write_bytes(text.replace(old, new).encode())
    cmd = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
           '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    r = subprocess.run(cmd, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    old, new = (a.ready / 'candidate.nes').read_bytes(), (a.output / 'candidate.nes').read_bytes()
    bank = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    deltas = {n: sum(x != y for x, y in zip(bank(old, n), bank(new, n))) for n in range(128)}
    deltas = {n: count for n, count in deltas.items() if count}
    assert set(deltas) == {125, 127} and deltas[125] == deltas[127]
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    assert qualified(a.ready / 'candidate.nes') == qualified(a.output / 'candidate.nes')
    # The standalone metadata is unchanged and is needed by full linked tests.
    preparation = json.loads((a.ready.parent / 'current-swap-v2/preparation.json').read_text())
    preparation['candidate_ROM_sha256'] = sha(a.output / 'candidate.nes')
    preparation['source_rebase_parent_candidate_sha256'] = sha(a.ready / 'candidate.nes')
    preparation['source_dispatch_optimization_only'] = True
    (a.output / 'preparation.json').write_text(json.dumps(preparation, indent=2) + '\n')
    proof = dict(passed=True, parent_ROM_sha256=CURRENT, frozen_ready_sha256=sha(a.ready / 'receipt.json'),
                 donor_ROM_sha256=sha(a.ready / 'candidate.nes'), candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
                 changed_PRG_bytes_from_8e2=deltas, all_qualified_symbols_exact=True,
                 CHR_exact=True, changed_source_file='src/tmnt_audio_resident.s',
                 before_source_sha256=sha(a.ready / 'source/src/tmnt_audio_resident.s'), after_source_sha256=sha(path),
                 source_only=True, native_run=False, production_changes=False,
                 checker_sha256=sha(Path(__file__)),
                 limits='Private source assembly only. ABI/flag liveness/full outer/IRQ checks are separate; no native cadence claim.')
    (a.output / 'dispatch-preparation.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
