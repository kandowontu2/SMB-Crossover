"""Private HUD-only lag repair; keep the frozen NV music checkpoint intact."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-vic-hud-nw/candidate-v1')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='candidate-v1')
    args = parser.parse_args(); out = OUT.parent / args.name
    out.mkdir(parents=True, exist_ok=False)
    overlay = out / 'overlay'; (overlay / 'src').mkdir(parents=True)
    original = ROOT / 'src/remaining_audio.s'
    text = original.read_text()
    anchor = '.proc RemainingAudioBegin\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + '''
.if ::MAPPER_MMC5 .and ::ENABLE_MMC5_EXPANDED
  ; Audio also advances on lag NMIs. Re-establish only the HUD background
  ; font after the previous scanline IRQ selected the level font. Sprite
  ; CHR and its pending publication remain paired with the committed OAM.
  lda DisableScreenFlag
  bne HudFontDone
  lda InvHudActive
  beq HudFontDone
  lda X5HudChrUpper
  and #3
  sta $5130
  lda InvHudPhysical
  sta $5128
  ; MMC5 captures upper CHR bits when each bank register is written. The
  ; later world-font IRQ expects the ordinary zero upper latch.
  lda #0
  sta $5130
HudFontDone:
.endif
''')
    (overlay / 'src/remaining_audio.s').write_text(text)
    (overlay / 'smb1base-mmc5-expanded.cfg').write_bytes((ROOT / 'smb1base-mmc5-expanded.cfg').read_bytes())
    command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'), '--source-overlay', str(overlay),
               '--output', str(out / 'candidate.nes')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (out / 'build-runner.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    proof = dict(parent='gradius-native-audio-nv', original_audio_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                 overlay_audio_sha256=hashlib.sha256((overlay / 'src/remaining_audio.s').read_bytes()).hexdigest(),
                 ROM_SHA256=hashlib.sha256((out / 'candidate.nes').read_bytes()).hexdigest(),
                 installed_game_sources_changed=False)
    (out / 'overlay.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
