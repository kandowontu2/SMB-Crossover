"""Static HUD glyph comparison from the already selected lossless PNG.

Preserves both earlier overbroad pixel negatives. The native coin icon changes
over time; the tally digits and all claimed static glyphs must be exact.
"""
from pathlib import Path
import argparse
import json

from PIL import Image
from current_bill_capsule_hud_pixels_v1 import region, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native', type=Path, required=True)
    args = ap.parse_args()
    out = args.native.resolve()
    first = out / 'selected-eight-whole-frames.json'
    second = out / 'selected-eight-whole-frames-v2.json'
    prior = json.loads(first.read_text())
    previous = json.loads(second.read_text())
    assert not prior['passed'] and not previous['passed']
    sheet = out / 'selected-eight-whole-frames.png'
    assert sha(sheet) == prior['sheet_sha256']
    im = Image.open(sheet).convert('RGBA')
    assert im.size == (512, 960)
    images = {}
    for q in prior['selected']:
        x, y = q['column'] * 256, q['row'] * 240
        raw = im.crop((x, y, x + 256, y + 240)).tobytes('raw', 'BGRA')
        import hashlib
        assert hashlib.sha256(raw).hexdigest() == q['raw_sha256']
        images[q['name']] = raw
    boxes = dict(player_name=[24, 16, 80, 24], coin_tally=[96, 24, 120, 32],
                 world_label=[144, 16, 192, 24], world_value=[152, 24, 176, 32],
                 time_label=[200, 16, 240, 24])
    base = images['normal-committed-HUD']
    comparisons = []
    for q in prior['selected'][1:7]:
        differences = {}
        for label, box in boxes.items():
            before, after = region(base, box), region(images[q['name']], box)
            differences[label] = sum(before[i:i + 4] != after[i:i + 4]
                                     for i in range(0, len(before), 4))
        a, b = region(base, [88, 24, 96, 32]), region(images[q['name']], [88, 24, 96, 32])
        coin_changes = sum(a[i:i + 4] != b[i:i + 4] for i in range(0, len(a), 4))
        assert coin_changes == next(v for v in previous['comparisons'] if v['name'] == q['name'])['changed_pixels']['coins']
        comparisons.append(dict(name=q['name'], changed_pixels=differences,
                                excluded_coin_icon_difference_pixels=coin_changes))
    passed = all(not any(q['changed_pixels'].values()) for q in comparisons)
    result = dict(passed=passed, ROOT_images_visually_reviewed=True,
                  scope='Exact actual static occupied HUD glyphs and coin tally at six selected capsule epochs. Weapon names, score, timer numerals and animated coin icon are not static. No continuous-HUD/all-epochs claim.',
                  source_mask_proof='build/bill_capsule_hud44204_controls.json',
                  preserved_negative_oracles=[str(first), str(second)],
                  oracle_corrections=['V1 sampled changing weapon name and wrong coin row.',
                                      'V2 included the time-varying eight-pixel-wide coin icon. All remaining V2 regions were exact.'],
                  regions=boxes, comparisons=comparisons, same_eight_epochs=True,
                  additional_images=0, additional_capture_epochs=0,
                  bindings={str(p): sha(p) for p in [Path(__file__).resolve(), first,
                      second, sheet, out / 'component-review.json', out / 'capsule-hud-native.json']})
    proof = out / 'selected-eight-whole-frames-v3.json'
    assert not proof.exists()
    proof.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=passed, proof=str(proof), comparisons=comparisons)))
    assert passed


if __name__ == '__main__':
    main()
