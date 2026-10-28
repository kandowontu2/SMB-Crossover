"""Eight real whole-frame samples and narrow HUD pixel comparisons.

The six capsule captures were requested after two later complete DMAs.
This does not certify every pose, audio waveform, or continuous HUD admission.
"""
from pathlib import Path
import argparse
import hashlib
import json

from current_roster_compact_11_v1 import png
from final_inventory_compact_capture_v1 import records


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def region(raw, box):
    left, top, right, bottom = box
    return b''.join(raw[(y * 256 + left) * 4:(y * 256 + right) * 4]
                    for y in range(top, bottom))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native', type=Path, required=True)
    args = ap.parse_args()
    out = args.native.resolve()
    ready = out.parent / 'prepared-not-run.json'
    assert sha(ready) == 'aac01161e99a14a9d94a30461dfe5c63cba0fb8744ddc24fb671ee46db26e1db'
    assert json.loads((out.parent / 'launch.json').read_text())['exit_code'] == 0
    assert json.loads((out / 'component-review.json').read_text())['passed']
    assert json.loads((out / 'capsule-hud-native.json').read_text())['passed']
    assert not list(out.glob('*.png')), 'Preserve prior image selections'
    names = ['normal-committed-HUD'] + [name + '-actual-capsule-HUD' for name in
             ['machine', 'spread', 'laser', 'flare', 'machine-rapid1', 'machine-rapid2']]
    names.append('laser-3-source-art')
    aliases = {}
    for line in (out / 'captures-index.jsonl').read_text().splitlines():
        item = json.loads(line)
        if item.get('type') == 'alias':
            aliases[item['name'].removesuffix('.argb')] = item['record']
    targets = {aliases[name] + (2 if name == names[-1] else 0): name for name in names}
    assert len(targets) == 8
    images, metadata = {}, {}
    for item, raw in records(out / 'captures.nesppuv1'):
        number = item['record']
        if number in targets:
            name = targets[number]
            images[name] = raw
            metadata[name] = dict(record=item, raw_sha256=hashlib.sha256(raw).hexdigest())
        if number >= max(targets):
            break
    assert len(images) == 8
    boxes = dict(character_name=[8, 8, 64, 16], coins=[88, 16, 128, 24],
                 world=[144, 8, 192, 24], time_label=[200, 8, 240, 16])
    reference = images[names[0]]
    comparisons = []
    for name in names[1:7]:
        differences = {}
        for label, box in boxes.items():
            before, after = region(reference, box), region(images[name], box)
            differences[label] = sum(before[i:i + 4] != after[i:i + 4]
                                     for i in range(0, len(before), 4))
        comparisons.append(dict(name=name, changed_pixels=differences))
    target = out / 'selected-eight-whole-frames.png'
    png(target, [images[name] for name in names])
    result = dict(passed=all(not any(q['changed_pixels'].values()) for q in comparisons),
                  scope='Six selected capsule epochs preserve these exact static HUD regions and the unchanged coin display. Other pixels/epochs and advanced HUD scheduling remain separate.',
                  ROOT_images_visually_reviewed=False, ready_sha256=sha(ready),
                  native_hud_sha256=sha(out / 'capsule-hud-native.json'),
                  container_sha256=sha(out / 'captures.nesppuv1'), sheet_sha256=sha(target),
                  regions=boxes, comparisons=comparisons,
                  selected=[dict(name=name, row=i // 2, column=i % 2, **metadata[name])
                            for i, name in enumerate(names)])
    proof = out / 'selected-eight-whole-frames.json'
    assert not proof.exists()
    proof.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], sheet=str(target), proof=str(proof))))
    assert result['passed'], 'Preserve actual differing pixels for investigation'


if __name__ == '__main__':
    main()
