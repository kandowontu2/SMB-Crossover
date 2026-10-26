"""Build only the reachable-NOP jump repair on frozen combined4285 sources."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
PARENT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-parodius-combined-f35-v1')
EXPECTED = '4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    parent = PARENT/'candidate.nes'
    assert sha(parent) == EXPECTED
    source = out/'source'
    shutil.copytree(PARENT/'source', source)
    target = source/'src/metasprite_engine.s'
    original = target.read_bytes()
    nl = b'\r\n' if b'\r\n' in original else b'\n'
    before = b' farcall Z2LateWorldAdmission\n .res 20,$ea\n::WorldFirebarAdmissionDone:'
    after = b' farcall Z2LateWorldAdmission\n jmp WorldFirebarAdmissionDone\n .res 17,$ea\n::WorldFirebarAdmissionDone:'
    before, after = before.replace(b'\n', nl), after.replace(b'\n', nl)
    assert original.count(before) == 1
    target.write_bytes(original.replace(before, after))
    command = [sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'),
               '--source-overlay', str(source), '--output', str(out/'candidate.nes')]
    with (out/'host-build.log').open('w') as log:
        rc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
    assert rc == 0, (out/'host-build.log').read_text()[-4000:]
    old, new = load(parent), load(out/'candidate.nes')
    assert qualified(parent) == qualified(out/'candidate.nes')
    assert len(old['raw']) == len(new['raw'])
    start, done = address(old, 'WorldFirebarDrawAdmission'), address(old, 'WorldFirebarAdmissionDone')
    assert done-start == 38 and int(old['syms']['WorldFirebarDrawAdmission']['size'], 0) == 39
    first = location(old, 'WorldFirebarDrawAdmission')+18
    assert old['raw'][first:first+20] == bytes([0xea])*20
    expected = bytes([0x4c, done & 255, done >> 8])
    changes = [i for i,(x,y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    assert changes == list(range(first, first+3)), changes
    assert (first-16)//8192 == 4 and new['raw'][first:first+3] == expected
    assert new['raw'][first+3:first+20] == bytes([0xea])*17
    assert new['raw'][first+20] == 0x60
    files = {}
    for f in sorted((PARENT/'source').rglob('*')):
        if f.is_file():
            rel = f.relative_to(PARENT/'source')
            q = source/rel
            assert q.is_file()
            if rel.as_posix() != 'src/metasprite_engine.s':
                assert f.read_bytes() == q.read_bytes(), str(rel)
            files[rel.as_posix()] = sha(q)
    patch = ('--- a/src/metasprite_engine.s\n+++ b/src/metasprite_engine.s\n@@\n'
             '  farcall Z2LateWorldAdmission\n- .res 20,$ea\n+ jmp WorldFirebarAdmissionDone\n'
             '+ .res 17,$ea\n ::WorldFirebarAdmissionDone:\n  rts\n')
    (out/'review.patch').write_text(patch, encoding='utf-8')
    (out/'source-manifest.json').write_text(json.dumps(files, indent=2)+'\n', encoding='utf-8')
    proof = dict(passed=True, source_only=True, native_run=False, adopted=False,
                 parent=str(parent), parent_ROM_sha256=EXPECTED,
                 candidate_ROM_sha256=sha(out/'candidate.nes'), command=command,
                 changed_ROM_offsets=changes, changed_bank=4,
                 helper_PC=start, genuine_Done_PC=done, helper_bytes=39,
                 old_NOP_cycles=40, new_JMP_cycles=3, exact_cycle_saving=37,
                 all_qualified_labels_exact=True, all_RAM_labels_exact=True,
                 CHR_and_all_other_ROM_bytes_exact=True,
                 sole_changed_source='src/metasprite_engine.s', source_files=len(files),
                 source_manifest_sha256=sha(out/'source-manifest.json'),
                 source_before_sha256=hashlib.sha256(original).hexdigest(),
                 source_after_sha256=sha(target), tool_sha256=sha(Path(__file__)),
                 limits='Canonical assembly and exact three-byte delta only. CPU helper/caller/interrupt proof is separate; no native cadence or adoption claim.')
    (out/'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
