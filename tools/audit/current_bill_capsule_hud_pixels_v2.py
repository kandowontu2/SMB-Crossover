"""Recheck the same eight epochs using the actual occupied HUD cells.

V1 incorrectly called the changing weapon row a character-name region and
used y16 for the coin row. Preserve that negative and its exact source.
No additional images, capture epochs, or native execution are generated.
"""
from pathlib import Path
import argparse
import hashlib
import json

from current_bill_capsule_hud_pixels_v1 import region, sha
from final_inventory_compact_capture_v1 import records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native', type=Path, required=True)
    args = ap.parse_args()
    out = args.native.resolve()
    first = out / 'selected-eight-whole-frames.json'
    prior = json.loads(first.read_text())
    assert not prior['passed']
    assert sha(out / 'selected-eight-whole-frames.png') == prior['sheet_sha256']
    assert sha(out / 'captures.nesppuv1') == prior['container_sha256']
    assert json.loads((out / 'component-review.json').read_text())['passed']
    assert json.loads((out / 'capsule-hud-native.json').read_text())['passed']
    selected = {q['record']['record']: q for q in prior['selected']}
    images = {}
    for item, raw in records(out / 'captures.nesppuv1'):
        number = item['record']
        if number in selected:
            assert hashlib.sha256(raw).hexdigest() == selected[number]['raw_sha256']
            images[selected[number]['name']] = raw
        if number >= max(selected):
            break
    assert len(images) == 8
    # Actual source-qualified occupied cells from the complete-caller controls.
    # Score/timer numbers and weapon names deliberately change during this suite.
    boxes = dict(player_name=[24, 16, 80, 24], coins=[88, 24, 120, 32],
                 world_label=[144, 16, 192, 24], world_value=[152, 24, 176, 32],
                 time_label=[200, 16, 240, 24])
    reference = images['normal-committed-HUD']
    comparisons = []
    for name in [q['name'] for q in prior['selected'][1:7]]:
        differences = {}
        for label, box in boxes.items():
            before, after = region(reference, box), region(images[name], box)
            differences[label] = sum(before[i:i + 4] != after[i:i + 4]
                                     for i in range(0, len(before), 4))
        comparisons.append(dict(name=name, changed_pixels=differences))
    controls = out.parents[1] / 'bill_capsule_hud44204_controls.json'
    assert sha(controls) == 'f704990288a95de336108c17ac7fd44f12d03c3761b019c253304f2e35830432'
    result = dict(passed=all(not any(q['changed_pixels'].values()) for q in comparisons),
                  scope='Same six selected capsule epochs: actual occupied static HUD cells and unchanged coin display. No continuous HUD, every-pixel, or all-epoch claim.',
                  ROOT_images_visually_reviewed=True,
                  superseded_pixel_oracle=dict(path=str(first), sha256=sha(first),
                      reason='V1 player-name box sampled the changing weapon name, and coin box sampled y16 rather than y24. Its zero-difference WORLD/TIME observations remain valid.'),
                  regions=boxes, comparisons=comparisons,
                  same_eight_epochs=True, additional_images=0,
                  bindings={str(p): sha(p) for p in [Path(__file__).resolve(), first,
                      out / 'selected-eight-whole-frames.png', controls,
                      out / 'component-review.json', out / 'capsule-hud-native.json']})
    proof = out / 'selected-eight-whole-frames-v2.json'
    assert not proof.exists()
    proof.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], proof=str(proof), comparisons=comparisons)))
    assert result['passed'], 'Preserve actual differing pixels for investigation'


if __name__ == '__main__':
    main()
