"""Offline whole-frame contact sheets from the already completed 0a route replays."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageDraw

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
NATIVE = D/'mega-proto-pivot-routes0a-static-v1/native'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    # No reconstructed pixels, fitted crops, interpolation, or inferred OAM.
    # Captions use the actual captured PPU frame ID, not source-update ordinals.
    plans = [
        ('megaman-easy', 'body-1942-adjacent', list(range(1938, 1954))),
        ('megaman-easy', 'first-mushroom-block', list(range(767, 783))+[790, 800, 810, 818]),
        ('proto-easy', 'first-item-approach', [690, 710, 730, 750, 770, 790, 810, 828]),
    ]
    bindings = []
    for case, label, frames in plans:
        root = NATIVE/(case+'-direct')
        proof = json.loads((root/'proof.json').read_text())
        assert proof['passed'] and proof['ROM_sha256'] == '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
        image = Image.new('RGB', (1024, ((len(frames)+3)//4)*260), '#202020')
        draw = ImageDraw.Draw(image)
        for i, frame in enumerate(frames):
            source = root/'frames'/f'{frame:06d}.png'
            actual = Image.open(source).convert('RGB')
            assert actual.size == (256, 240)
            x, y = i % 4*256, i//4*260
            image.paste(actual, (x, y+20))
            draw.text((x, y), f'{case} PPU {frame}', fill='white')
            bindings.append(dict(sheet=label, case=case, frame=frame,
                                 source=str(source), sha256=sha(source)))
        target = a.output/(label+'-actual-PPU.png')
        image.save(target)
    report = dict(offline_only=True, native_launches=0, saved_actual_whole_images=True,
                  source_native_proof=str(NATIVE/'proof.json'), source_native_proof_sha256=sha(NATIVE/'proof.json'),
                  frames=bindings,
                  limits='Selected actual RGB frames only. No all-frame visual review, live-slot attribution, opaque-part count, sound audition, or universal flicker/fairness claim.')
    (a.output/'selected-frames.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(output=str(a.output), selected_actual_frames=len(bindings)), indent=2))


if __name__ == '__main__':
    main()
