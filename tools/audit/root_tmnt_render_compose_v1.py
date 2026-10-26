"""Build the disjoint source union of two private turtle rendering proposals."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys

from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['parent', 'scans', 'ammo', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    expected = {'parent': '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd',
                'scans': 'eedf07f7c63f2a2ad286d389a2bfe855dafdd0529bc09f1588476ac5f70c0d47',
                'ammo': 'a2b58350d4b5a4765cd11e5d7e08b37d72f51abdbf1d6debc5b58dcef6c90820'}
    for n, value in expected.items():
        assert sha(getattr(a, n) / 'candidate.nes') == value
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.scans / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    name = 'src/tmnt_equipment_draw.s'
    before, after = (a.parent / 'source' / name).read_text(), (a.ammo / 'source' / name).read_text()
    start, end = before.index(' lda #0\n sta TnTempX\n'), before.index('Hundreds:')
    new_start, new_end = after.index('.if ::MAPPER_MMC5\n jmp ::TnAmmoDecimalLookup'), after.index('Hundreds:')
    old, new = before[start:end], after[new_start:new_end]
    target = source / name
    text = target.read_text()
    assert text.count(old) == 1
    target.write_text(text.replace(old, new))
    helper = (a.ammo / 'source/src/tmnt_ammo_decimal_lookup.s').read_text()
    assert helper.count('.res $e0,$ff ; parent TMNT_CORE ends atB020') == 1
    helper = helper.replace('.res $e0,$ff ; parent TMNT_CORE ends atB020', '.align $100,$ff ; scan helper ends atB058; next page isB100')
    (source / 'src/tmnt_ammo_decimal_lookup.s').write_text(helper)
    entry = source / 'src/entrypoint.s'
    entry.write_text(entry.read_text() + '\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "tmnt_ammo_decimal_lookup.s"\n.endif\n')
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    r = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-5000:]
    parent, scans, ammo, result = [(p / 'candidate.nes').read_bytes() for p in [a.parent, a.scans, a.ammo, a.output]]
    s = {i for i, (x, y) in enumerate(zip(parent, scans)) if x != y}
    m = {i for i, (x, y) in enumerate(zip(parent, ammo)) if x != y}
    assert not s & m and len(s) == 61 and len(m) == 800
    union = bytearray(parent)
    for i in s:
        union[i] = scans[i]
    for i in m:
        union[i] = ammo[i]
    assert bytes(union) == result
    for p in [a.parent, a.scans, a.ammo]:
        assert qualified(p / 'candidate.nes').items() <= qualified(a.output / 'candidate.nes').items()
    sources, patch = {}, ''
    for name in ['src/entrypoint.s', 'src/tmnt_equipment_draw.s', 'src/tmnt_empty_equipment_scans.s', 'src/tmnt_ammo_decimal_lookup.s']:
        before, after = a.parent / 'source' / name, source / name
        sources[name] = dict(before_sha256=sha(before) if before.exists() else None, after_sha256=sha(after))
        patch += ''.join(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],
                         after.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(patch)
    q = dict(prepared=True, source_only=True, native_run=False, accepted=False,
             input_ROMs=expected, candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
             canonical_source_build_exact_disjoint_ROM_union=True, changed_bytes=861, changed_bank=87,
             all_three_parents_qualified_symbols_fixed=True, all_audio_other_banks_CHR_exact=True,
             source_changes=sources, builder_sha256=sha(Path(__file__)),
             limits='Composition proof only. Parent source tests are not relabeled for this ROM. Fresh combined CPU/caller/IRQ, canonical/flagoff and native cadence remain separate gates; primary miss remains open.')
    (a.output / 'preparation.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q), flush=True)


if __name__ == '__main__':
    main()
