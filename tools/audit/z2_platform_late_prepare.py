"""Prepare a private, no-new-RAM late small-lift OAM owner on a tested parent."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    parent = a.parent.resolve()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    old = load(parent)
    source = out/'source'
    shutil.copytree(parent.parent/'source', source)
    target = source/'src/metasprite_engine.s'
    text = target.read_text() if target.exists() else (ROOT/'src/metasprite_engine.s').read_text()
    start = text.index('.proc WorldFirebarDrawAdmission\n')
    end = text.index('.endproc', start)+len('.endproc')
    original = text[start:end]
    body = original.split('\n', 1)[1].rsplit('.endproc', 1)[0]
    legacy = '\n'.join(line for line in body.splitlines() if not line.startswith('::'))
    (source/'src/z2_platform_late_legacy.inc').write_text('.proc Z2LateLegacyFirebarAdmission\n'+legacy+'\n.endproc\n')
    size = int(old['syms']['WorldFirebarDrawAdmission']['size'], 0)
    assert size >= 19
    replacement = ('.proc WorldFirebarDrawAdmission\n.if ::ENABLE_MMC5_EXPANDED\n'
                   '::WorldFirebarAdmission:\n farcall Z2LateWorldAdmission\n'
                   f' .res {size-19},$ea\n::WorldFirebarAdmissionDone:\n rts\n'
                   f' .assert *-WorldFirebarDrawAdmission={size},lderror,"Late world admission span"\n'
                   '.else\n'+body+'.endif\n.endproc')
    target.write_text(text[:start]+replacement+text[end:])
    entry = source/'src/entrypoint.s'
    text = entry.read_text()
    anchor = '.include "hot_render_gate.s"'
    assert text.count(anchor) == 1
    entry.write_text(text.replace(anchor, anchor+'\n.include "z2_platform_late_render.s"'))
    shutil.copy2(ROOT/'tools/audit/z2_platform_late_render.candidate.s', source/'src/z2_platform_late_render.s')
    rom = out/'candidate.nes'
    with (out/'host-build.log').open('w') as log:
        result = subprocess.run([sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'),
                                 '--source-overlay', str(source), '--output', str(rom)],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode == 0, (out/'host-build.log').read_text()[-5000:]
    new = load(rom)
    assert old['raw'][16+1048576:] == new['raw'][16+1048576:]
    for n, s in old['syms'].items():
        if 'seg' in s and address(old, n) < 0x8000:
            assert address(old, n) == address(new, n), n
    for n in ['WorldFirebarAdmission', 'WorldFirebarAdmissionDone', 'DrawWorldFirebars',
              'MetaspriteRenderLoop', 'RunSmallPlatform', 'Z2PositionOnPlatform', 'Z2PlatformGroundY']:
        assert address(old, n) == address(new, n), n
    changed = [i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    receipt = dict(compiled=True, adopted=False, passed=False, goal_complete=False,
                   ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
                   parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), existing_RAM_and_CHR_exact=True,
                   changed_PRG_banks=sorted(set((i-16)//8192 for i in changed)),
                   source={str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in source.rglob('*') if p.is_file()},
                   scope='Private late OAM ownership for rotated guest native small lifts only. Original world-firebar body outlined verbatim; native firebars draw first. Authentic masked3-girder rows in existing Z2 PRG art bank; existing bounded rotated MetaspriteRenderLoop. Existing scratch is restored; no new RAM or CHR. Current post-move actor Y intentionally aligns visible girder with resolved passenger. CPU/native qualification pending.')
    (out/'build-proof.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
