"""Build a separate, reviewable Gradius native-audio overlay; do not install it."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv/gradius-linked-v1')
ARCHIVE = OUT.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='gradius-linked-v1')
    args = parser.parse_args()
    out = OUT.parent / args.name
    out.mkdir(parents=True, exist_ok=False)
    proof = json.loads((ARCHIVE / 'gradius-relocated-v2/golden-proof.json').read_text())
    assert proof['passed'] and proof['native_songs'] == 32
    source = out / 'overlay'; (source / 'src').mkdir(parents=True)
    bases = {name: sha(ROOT / name) for name in ('src/entrypoint.s', 'src/expanded_audio.s', 'smb1base-mmc5-expanded.cfg')}
    driver = ARCHIVE / 'gradius-relocated-v2/gradius-native.inc'
    prepared = json.loads((ARCHIVE / 'gradius-relocated-v2/preparation.json').read_text())
    assert sha(driver) == prepared['driver_sha256']
    driver_text = driver.read_text()
    for suffix in ('08', '09', '0c'):
        driver_text = driver_text.replace('::GuestNativeStoreSTA' + suffix, '::VgNativeStoreSTA' + suffix)
    (source / 'src/gradius-native.inc').write_text(driver_text)
    shutil.copy2(ROOT / 'tools/reference/gradius_audio_wrapper_nv.s', source / 'src/gradius_audio.s')
    for name in bases:
        content = (ROOT / name).read_text()
        if name == 'src/entrypoint.s':
            anchor = '.include "vic_viper.s"\n'
            assert content.count(anchor) == 1
            content = content.replace(anchor, anchor + '.include "gradius_audio.s"\n')
        elif name == 'src/expanded_audio.s':
            anchor = '  BankPRGC #.bank(ExpandedAudioTick)\n  jsr ExpandedAudioTick\n'
            assert content.count(anchor) == 1
            replacement = '''  BankPRGC #.bank(ExpandedAudioTick)
.if ::ENABLE_MMC5_EXPANDED
  jsr VgAudioDispatch
.else
  jsr ExpandedAudioTick
.endif
'''
            content = content.replace(anchor, replacement)
        else:
            anchor = 'SEGMENTS {\n'
            assert content.count(anchor) == 1
            content = content.replace(anchor, anchor + '    VIC_NATIVE_AUDIO:load=X5_NEW_7A,type=ro;\n')
            anchor = '    BILL_ORBIT_2: load=XG_AUDIO_MEM, type=ro, optional=yes; # Existing C000 FF tail; all prior data fixed.\n'
            assert content.count(anchor) == 1
            content = content.replace(anchor, anchor + '    VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro;\n')
        (source / name).write_text(content)
    command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'), '--source-overlay', str(source),
               '--output', str(out / 'candidate.nes')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (out / 'build-runner.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    record = dict(private_overlay=True, installed_game_files_changed=False, ROM_SHA256=sha(out / 'candidate.nes'),
                  source_originals=bases,
                  overlay={p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*') if p.is_file()},
                  native_driver_proof_sha256=sha(ARCHIVE / 'gradius-relocated-v2/golden-proof.json'))
    (out / 'overlay.json').write_text(json.dumps(record, indent=2) + '\n')
    assert all(sha(ROOT / name) == h for name, h in bases.items())
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
