"""Extract eight whole PPU samples from the frozen Bill gun component run.

These are two capture epochs after the named art events, not proof that the
event and displayed body share a DMA epoch. No frame directory is created.
"""
from pathlib import Path
import argparse
import hashlib
import json

from current_roster_compact_11_v1 import png
from final_inventory_compact_capture_v1 import records


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native', type=Path, required=True)
    args = ap.parse_args()
    out = args.native.resolve()
    ready = out.parent / 'prepared-not-run.json'
    q = json.loads(ready.read_text())
    assert sha(ready) == 'b3530700636d8013e5ec9634ee95fb38420f242ff45bb6e1e9b2e54bc484713f'
    assert json.loads((out.parent / 'launch.json').read_text())['exit_code'] == 0
    assert json.loads((out / 'native-bill-gallery.json').read_text())['passed']
    assert q['storage']['maximum_offline_selected_PNGs'] == 8
    assert not list(out.glob('*.png')), 'Preserve earlier image selections'
    names = [
        'normal-1-source-art', 'machine-1-source-art',
        'spread-1-source-art', 'laser-1-source-art',
        'flare-1-source-art', 'machine-rapid1-1-source-art',
        'machine-rapid2-1-source-art', 'laser-3-source-art',
    ]
    aliases = {}
    for line in (out / 'captures-index.jsonl').read_text().splitlines():
        item = json.loads(line)
        if item.get('type') == 'alias':
            aliases[item['name'].removesuffix('.argb')] = item['record']
    targets = {aliases[name] + 2: name for name in names}
    assert len(targets) == 8
    chosen = {}
    metadata = {}
    for item, raw in records(out / 'captures.nesppuv1'):
        number = item['record']
        if number in targets:
            name = targets[number]
            chosen[name] = raw
            metadata[name] = dict(record=item, raw_sha256=hashlib.sha256(raw).hexdigest())
        if number >= max(targets):
            break
    assert len(chosen) == 8
    target = out / 'selected-eight-whole-frames.png'
    png(target, [chosen[name] for name in names])
    result = dict(
        scope='Eight selected whole PPU buffers only; no all-frame or exact art-event/DMA-epoch verdict.',
        ROOT_images_visually_reviewed=False,
        ready_sha256=sha(ready),
        native_result_sha256=sha(out / 'native-bill-gallery.json'),
        container_sha256=sha(out / 'captures.nesppuv1'),
        sheet_sha256=sha(target),
        selected=[dict(name=name, row=i // 2, column=i % 2, **metadata[name])
                  for i, name in enumerate(names)],
    )
    proof = out / 'selected-eight-whole-frames.json'
    assert not proof.exists()
    proof.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(sheet=str(target), proof=str(proof), selected=8)))


if __name__ == '__main__':
    main()
