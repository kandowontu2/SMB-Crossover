"""Compile the disjoint current-parent movement and HUD-data proposals privately."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
CHIP = '22fdf1f6ed7e70f87344cc17733f76da60e376ebfc9314c2cb9358587dd45fcf'
HUD = 'bb5bf4fa4189ede2ab4f9ee0eb6e8e54dd67b1c77eb1c78e7c50a1079d4fc1db'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    chip = D / 'chip-hot-control-current6c-v2'
    hud = D / 'parodius-hud-readability6c69-candidate-v1'
    cr = chip / 'freeze-v1/readiness-source-only.json'
    hr = hud / 'ready-v1/proof.json'
    assert sha(cr) == '0ee3af8e2960d87a2b4184e0c42a9a851f826c7e81766ba586389561a5ef3fa8'
    assert sha(hr) == '7e719fe3bcf9e6e7f2b0085c5ff77515483e09cbb6c9f8b4b3f870b1086365a4'
    cq = json.loads(cr.read_text())
    hq = json.loads(hr.read_text())
    assert cq['source_ready'] and not cq['native_executed']
    assert hq['passed'] and not hq['native_run']
    for row in cq['bindings']:
        assert sha(row['path']) == row['sha256'], row['path']
    hm = hud / 'ready-v1/manifest.json'
    assert sha(hm) == hq['manifest_sha256']
    hb = json.loads(hm.read_text())
    for f, h in hb.items():
        assert sha(f) == h, f
    parent = D / 'world-firebar-padding-v2/candidate.nes'
    assert sha(parent) == PARENT and sha(chip / 'candidate.nes') == CHIP and sha(hud / 'candidate.nes') == HUD
    raw = parent.read_bytes()
    craw = (chip / 'candidate.nes').read_bytes()
    hraw = (hud / 'candidate.nes').read_bytes()
    assert len(raw) == len(craw) == len(hraw)
    cd = {i for i, (x, y) in enumerate(zip(raw, craw)) if x != y}
    hd = {i for i, (x, y) in enumerate(zip(raw, hraw)) if x != y}
    assert len(cd) == 202 and len(hd) == 622 and not cd.intersection(hd)
    expected = bytearray(raw)
    for i in cd:
        expected[i] = craw[i]
    for i in hd:
        expected[i] = hraw[i]
    inventory = json.loads((hud / 'source-manifest.json').read_text())
    assert len(inventory) == 872
    for n, h in inventory.items():
        assert sha(hud / 'source' / n) == h, n
    source = out / 'source'
    shutil.copytree(hud / 'source', source)
    changes = ['src/x5_bounce.s', 'src/characters.s', 'src/megaman_weapons.s', 'src/tmnt_probe_gates.s']
    rebase = json.loads((D / 'chip-hot-control-v5/rebase-current6c-v1/proof.json').read_text())
    for row in rebase['files']:
        n = row['relative_path']
        assert n in changes and sha(source / n) == row['current_before_sha256']
        assert sha(chip / 'source' / n) == row['candidate_after_sha256']
        shutil.copy2(chip / 'source' / n, source / n)
        inventory[n] = row['candidate_after_sha256']
    (out / 'source-manifest.json').write_text(json.dumps(inventory, indent=2) + '\n')
    output = out / 'candidate.nes'
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(output)]
    with (out / 'ROOT-build.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert output.read_bytes() == bytes(expected), 'Fresh compilation must equal the exact disjoint byte composition.'
    for n, h in inventory.items():
        assert sha(source / n) == h, n
    result = dict(passed=True, source_only=True, native_run=False, production_changes=False, adopted=False,
                  goal_complete=False, parent_ROM_sha256=PARENT, candidate_ROM_sha256=sha(output),
                  chip_ROM_sha256=CHIP, hud_ROM_sha256=HUD, chip_bindings_verified=len(cq['bindings']),
                  hud_bindings_verified=len(hb), frozen_source_files=len(inventory),
                  changed_source_files=changes + ['chr/characters/parodius-hud.chr', 'src/parodius_hud.inc'],
                  changed_ROM_bytes=len(cd | hd), disjoint_ROM_changes=True, exact_fresh_compilation=True,
                  command=command, compiler_sha256=sha(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                  source_manifest_sha256=sha(out / 'source-manifest.json'), tool_sha256=sha(__file__),
                  limits='Composition only. Component caller/IRQ and HUD queue evidence remains distinct; fresh native gameplay/menu/timing qualification is required. No held Chip music imported.')
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
