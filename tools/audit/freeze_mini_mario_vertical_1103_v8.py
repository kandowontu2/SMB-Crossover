"""Retain original vertical arithmetic, exact source defaults and bounded episodes."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/mini-mario-vertical-freeze-1103-v8'
DEST = ROOT/'docs/qa/checkpoints/2026-11-03/mini-mario-vertical-v8'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    source_names = ('port_mini_mario_air_y_1103_v5.py',
        'prepare_mini_mario_core_defaults_1103_v6.py', 'check_mini_mario_bound_gravity_1103_v7.py')
    files = [Path(__file__), *(ROOT/'tools/audit'/name for name in source_names)]
    y = ROOT/'build/mini-mario-motion-1103-v5'
    defaults = ROOT/'build/mini-mario-defaults-1103-v6'
    bound = ROOT/'build/mini-mario-motion-1103-v7'
    y_receipt = json.loads((y/'receipt.json').read_text())
    bound_receipt = json.loads((bound/'receipt.json').read_text())
    defaults_receipt = json.loads((defaults/'receipt.json').read_text())
    assert y_receipt['passed'] and y_receipt['cases'] == 315036
    assert y_receipt['code_bytes'] == 842 and y_receipt['Y_added_bytes'] == 359
    assert y_receipt['code_sha256'] == sha((y/'motion-xy.bin').read_bytes())
    assert bound_receipt['passed'] and bound_receipt['changed_code_bytes'] == 0
    assert bound_receipt['total_Y_cases'] == 482241 and len(bound_receipt['ballistic_episodes']) == 35
    assert defaults_receipt['passed'] and defaults_receipt['default_hold_gravity'] == 512
    assert sha((defaults/'direct-inputs.zip').read_bytes()) == defaults_receipt['archive_SHA256']
    files += [y/name for name in ('receipt.json','original-air-y.c','motion-xy.s',
        'motion-xy.cfg','motion-xy.bin','motion-xy.lbl')]
    files += [defaults/'receipt.json',defaults/'direct-inputs.zip',bound/'receipt.json']
    DEST.mkdir(parents=True, exist_ok=False)
    target = DEST/'inputs.zip'
    with ZipFile(target,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:
            z.writestr(f.relative_to(ROOT).as_posix(),f.read_bytes())
    assert target.stat().st_size < 128000
    with ZipFile(target) as z:
        for f in files:
            assert z.read(f.relative_to(ROOT).as_posix()) == f.read_bytes()
    result = dict(passed=True,installed=False,ROM_produced=False,
        checkpoint=DEST.relative_to(ROOT).as_posix(),archive_bytes=target.stat().st_size,
        archive_SHA256=sha(target.read_bytes()),
        scope='Mini original-C versus assembled6502 vertical arithmetic315036cases, plus482241source-gravity512cases including35Y-before-X ballistic episodes.842Bcombined component, horizontal483Bprefix unchanged. SourceGBStudio4.2.0 immutable defaults/bootstrap/schema loading and original Mini sprite definitions preserved compactly. Native RAM/code/menu not allocated; no emulator captures or per-case files.',
        ballistic_peaks={e['movement']:e['maximum_rise_pixels'] for e in bound_receipt['ballistic_episodes'] if e['held_frames']==64},
        remaining='Full caller/state/terrain/lifecycle/render/audio/menu and native1-1; actualGBsource-to-binary/instruction proof. Unscaled normal jumps do not clear48/64pxpipes in this collision-free model; requested innatewallgrab needs deliberate adaptation and native verification. No helper added or crossing certified.',
        bindings={f.relative_to(ROOT).as_posix():sha(f.read_bytes()) for f in files},
        source_files=[f.relative_to(ROOT).as_posix() for f in files[:4]])
    for f in (OUT/'receipt.json',DEST/'receipt.json'):
        f.write_text(json.dumps(result,indent=2)+'\n')
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['mini_mario_current_1102'].update(
        vertical_status='SOURCE_C_VS_6502_JUMP_FALL_AND_GRAVITY512_PASS_NO_GAMEPLAY',
        vertical_checkpoint=DEST.relative_to(ROOT).as_posix(),vertical_scope=result['scope'],
        vertical_remaining=result['remaining'])
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))


if __name__=='__main__':
    main()
