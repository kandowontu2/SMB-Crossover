"""Stage a narrow Grant grip-contact repair without changing the live source."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from check_tmnt_render_oa import load, location

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/smb3-shrink-pc'
HELPER = '''; SMB wall-contact adapter: keep the original foot probe and the
; side contact that admitted the grip. A short floating block can touch
; Grant's body while ending above his feet. Source wall speed stays +/-1.
.pushseg
.segment "CV3_GRIP"
.proc Cv3GripWall
 stx Cv3Temp3
 jsr Cv3SolidPoint
 bcs Done
 ldx Cv3Temp3
 ldy #20
 jmp Cv3SolidPoint
Done:rts
.endproc
.popseg
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    parent = json.loads((PARENT / 'manifest.json').read_text())
    assert sha(PARENT / 'candidate.nes') == parent['rom_sha256']
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    stage = out / 'source'
    with zipfile.ZipFile(PARENT / 'source.zip') as z:
        assert z.testzip() is None
        assert all((stage / n).resolve().is_relative_to(stage) for n in z.namelist())
        z.extractall(stage)
    assert all(sha(stage / n) == h for n, h in parent['source_files'].items())
    changes = {}

    def replace(relative, old, new):
        path = stage / relative
        before = sha(path)
        text = path.read_text()
        assert text.count(old) == 1, relative
        path.write_text(text.replace(old, new))
        changes[relative] = dict(before=before, after=sha(path))

    replace('src/cv3_abilities.s', 'WallPoint:\n ldy #31\n jsr Cv3SolidPoint\n jcc Lost\n',
            'WallPoint:\n ldy #31\n jsr Cv3GripWall\n jcc Lost\n')
    replace('src/cv3.s', '.include "cv3_motion_data.inc"',
            '.include "cv3_grip.s"\n.include "cv3_motion_data.inc"')
    replace('smb1base-mmc5-expanded.cfg', 'CV3_CORE:load=X5_NEW_52,type=ro;',
            'CV3_CORE:load=X5_NEW_52,type=ro;\n    CV3_GRIP:load=X5_NEW_52,type=ro;')
    helper = stage / 'src/cv3_grip.s'
    assert not helper.exists()
    helper.write_text(HELPER)
    changes['src/cv3_grip.s'] = dict(before=None, after=sha(helper))
    command = [sys.executable, str(stage / 'tools/build_mmc5_expanded.py'), '--workspace', str(stage),
        '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(out / 'candidate.nes')]
    z = subprocess.run(command, cwd=stage, capture_output=True, text=True)
    (out / 'build.log').write_text(z.stdout + z.stderr)
    assert z.returncode == 0, (z.stdout + z.stderr)[-3000:]
    old, new = load(PARENT / 'candidate.nes'), load(out / 'candidate.nes')
    assert len(old['raw']) == len(new['raw']) == 2097168
    helper_at = location(new, 'Cv3GripWall')
    assert (helper_at - 16) // 8192 == 82
    original_at = location(old, 'Cv3GrantClimb')
    point = int(old['syms']['Cv3SolidPoint']['val'], 0)
    needle = bytes((0xa0, 31, 0x20, point & 255, point >> 8))
    code = old['raw'][original_at:original_at + 256]
    assert code.count(needle) == 1
    call_at = original_at + code.index(needle) + 3
    differences = [i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    assert set(differences) <= set(range(call_at, call_at + 2)) | set(range(helper_at, helper_at + 17))
    assert len(differences) == 19
    assert old['raw'][:16] == new['raw'][:16] and old['raw'][16 + 1048576:] == new['raw'][16 + 1048576:]
    report = dict(prepared=True, accepted=False, ROM_sha256=sha(out / 'candidate.nes'),
        parent_ROM_sha256=parent['rom_sha256'], changes=changes, helper_bytes=17,
        changed_ROM_bytes=[dict(offset=i, before=old['raw'][i], after=new['raw'][i]) for i in differences],
        prior_instruction_addresses_and_RAM_and_CHR_preserved=True, driver_sha256=sha(Path(__file__)),
        scope='Two bytes retarget the existing wall-retention JSR to an appended17bytebank82helper. Foot contact stays first; the exact side contact used for grip admission is a fallback. No speed/jump/area/body changes. All other ROM bytes, header and CHR are exact. Added first-probe call depth is two stack bytes and requires native stack/IRQ/SMC guards before adoption. Live source and public ROMs untouched.')
    (out / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('prepared', 'ROM_sha256', 'helper_bytes')}, indent=2))


if __name__ == '__main__':
    main()
