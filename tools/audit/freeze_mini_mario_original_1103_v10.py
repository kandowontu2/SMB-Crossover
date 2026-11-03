"""Retain the read-only GB parameter observation, with its visual limitation."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/mini-mario-original-freeze-1103-v10'
P = ROOT/'build/mini-mario-original-1103-v9'
D = ROOT/'docs/qa/checkpoints/2026-11-03/mini-mario-original-v10'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    q = json.loads((P/'receipt.json').read_text())
    assert q['passed'] and q['exit_code'] == 0 and not q['emulated_memory_writes']
    assert q['observation']['unique_matches'] == 1
    assert all(r['parameter_base_addresses'] == [0xDC1E] for r in q['observation']['observations'])
    files = [Path(__file__),ROOT/'tools/audit/check_mini_mario_original_boot_1103_v9.py',
        P/'original.lua',P/'receipt.json',P/'sessions-before.json',
        P/'capture/parameter-observation.json',P/'capture/original-gameboy.png',
        P/'capture/SuperMarioBrosMini-original.log']
    D.mkdir(parents=True,exist_ok=False)
    archive = D/'inputs.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:
            z.writestr(f.relative_to(ROOT).as_posix(),f.read_bytes())
    with ZipFile(archive) as z:
        for f in files:
            assert z.read(f.relative_to(ROOT).as_posix()) == f.read_bytes()
    assert archive.stat().st_size < 64000
    result = dict(passed=True,parameter_binding_only=True,visual_boot_qualified=False,
        original_GB_ROM_SHA256=q['ROM_SHA256'],archive_SHA256=sha(archive.read_bytes()),
        archive_bytes=archive.stat().st_size,frames=1200,parameter_address=0xDC1E,
        screenshot_review='The single original-GB screenshot was viewed and is black. It is retained as a visual limitation; no successful gameplay/visual boot, NES admission or graphics fidelity claim is made.',
        scope='Controller-only originalGB reference, exact22B live parameter block atDC1E found uniquely at300/600/1000frames, including512heldgravity. No memory writes or state/PPU/frame dumps. This strengthens constant binding only; actualGBsource-to-binary and instruction equivalence remain open.',
        bindings={f.relative_to(ROOT).as_posix():sha(f.read_bytes()) for f in files},
        source_files=[f.relative_to(ROOT).as_posix() for f in files[:2]])
    for f in (OUT/'receipt.json',D/'receipt.json'):
        f.write_text(json.dumps(result,indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['mini_mario_current_1102'].update(
        original_GB_parameter_checkpoint=D.relative_to(ROOT).as_posix(),
        original_GB_parameter_scope=result['scope'],original_GB_visual_limitation=result['screenshot_review'])
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))


if __name__=='__main__':
    main()
