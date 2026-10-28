"""Build an unhooked RCR palette successor on the exact root33d2 baseline.

Only18 sparse source preimages are restored while another agent owns shared
sources. Extra CHR is patched into authenticated zero padding for this private
component test; shared source/incbin allocation and native play remain open.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    overlay = R/'build/river-city-palette-runtime-v3-overlay'
    base = R/'build/river-city-palette-baseline-v3.nes'
    assert sha(base) == '33d2c7a7bf58aa040f2911d44f1d59dddb4c9b40b3e8727334cf46db74915f97'
    receipt = overlay/'runtime-build.json'
    assert not receipt.exists()
    wrapper = (R/'src/river_city.s').read_text().replace(
        '.include "river_city_render.s"', '.include "river_city_shared_palette_render.inc"').replace(
        '.include "river_city_art.inc"', '.include "river_city_shared_palette_art.inc"').replace(
        '.incbin "chr/characters/river-city.chr"',
        '.incbin "chr/characters/river-city-shared-palette.chr",0,8192')
    (overlay/'src/river_city.s').write_text(wrapper, newline='\n')
    unpatched = R/'build/river-city-palette-private-v3-linked.nes'
    command = ['python', '-B', str(R/'tools/build_mmc5_expanded.py'), '--source-overlay',
               str(overlay), '--output', str(unpatched)]
    result = subprocess.run(command, cwd=R, capture_output=True, text=True)
    (overlay/'runtime-build.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stdout+result.stderr
    raw = bytearray(unpatched.read_bytes())
    chrbase = 16+1048576
    start = chrbase+677*1024
    assert base.read_bytes()[start:start+3072] == bytes(3072)
    assert raw[start:start+3072] == bytes(3072)
    atlas = R/'chr/characters/river-city-shared-palette.chr'
    assert len(atlas.read_bytes()) == 11264
    raw[start:start+3072] = atlas.read_bytes()[8192:]
    output = R/'build/river-city-palette-private-v3.nes'
    assert not output.exists()
    output.write_bytes(raw)
    for suffix in ('.dbg', '.lbl', '.map'):
        shutil.copyfile(unpatched.with_suffix(suffix), output.with_suffix(suffix))
    paths = [Path(__file__), base, base.with_suffix('.dbg'), output,
             output.with_suffix('.dbg'), output.with_suffix('.lbl'), atlas,
             R/'src/river_city_shared_palette_art.inc',
             R/'src/river_city_shared_palette_render.inc',
             R/'src/river_city_core.s', R/'src/river_city_combat.s', R/'src/river_city_state.inc']
    paths += [p for p in overlay.rglob('*') if p.is_file()]
    proof = dict(passed=True, native_run=False, scope=__doc__, ROM_sha256=sha(output),
                 baseline_sha256=sha(base), extra_CHR_pages=[677,678,679],
                 body_CHR_pages=list(range(716,724)), command=command,
                 limits=['Unhooked private component; shared allocation/menu/native gameplay unqualified.',
                         'No all-area NES palette or cadence acceptance.'],
                 bindings=[dict(path=str(p), sha256=sha(p)) for p in paths])
    receipt.write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, ROM_sha256=sha(output))))


if __name__ == '__main__':
    main()
