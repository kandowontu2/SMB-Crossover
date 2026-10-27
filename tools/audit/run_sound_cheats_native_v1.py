"""One bounded frontend run using the existing emulator without copying it."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(args.rom) == args.sha256
    runtime = Path('C:/Mesen2')
    user = runtime/'settings.json'
    original = sha(user)
    config = json.loads(user.read_text(encoding='utf-8-sig'))
    assert not config['Nes']['RemoveSpriteLimit'] and not config['Nes']['AdaptiveSpriteLimit']
    assert config['Nes']['PpuExtraScanlinesBeforeNmi'] == config['Nes']['PpuExtraScanlinesAfterNmi'] == config['Emulation']['RunAheadFrames'] == 0
    assert sha(runtime/'Mesen.exe') == '8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9'
    assert sha(runtime/'MesenCore.dll') == '4bd40dfc6512328d56d8ad0563263b52be57bac726d8804f0720e461e558cd41'
    script = R/'tools/audit/sound_cheats_menu_native_v1.lua'
    inputs = [args.rom, args.rom.with_suffix('.dbg'), args.rom.with_suffix('.lbl'), script,
              Path(__file__), R/'tools/run_mesen.py', R/'tools/audit/run_mesen_isolated.py',
              R/'tools/audit/capture_budget.py', runtime/'Mesen.exe', runtime/'MesenCore.dll']
    bindings = {str(p.resolve()): sha(p) for p in inputs}
    args.output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, '-B', str(R/'tools/audit/run_mesen_isolated.py'),
               '--output', str(args.output.resolve()), '--emulator', str(runtime/'Mesen.exe'),
               str(script), str(args.rom.resolve()), '--timeout', '180',
               '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
               '--option=--nes.randomizeCpuPpuAlignment=false',
               '--option=--nes.randomizeMapperPowerOnState=false']
    receipt = dict(ROM_sha256=args.sha256, settings_before=original, bindings=bindings,
                   shared_runtime_used_without_copy=True, no_user_settings_write=True,
                   maximum_screenshots=6, per_frame_files=0,
                   settings_functional_input=True, retries=0)
    path = args.output/'launch.json'
    path.write_text(json.dumps(receipt, indent=2)+'\n')
    result = subprocess.run(command, cwd=R)
    changed = [p for p, expected in bindings.items() if sha(p) != expected]
    receipt.update(exit_code=result.returncode, settings_after=sha(user), changed_inputs=changed)
    path.write_text(json.dumps(receipt, indent=2)+'\n')
    assert receipt['settings_after'] == original, 'Human configuration changed; reject this run context'
    assert not changed, 'Bound inputs changed during native run'
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
