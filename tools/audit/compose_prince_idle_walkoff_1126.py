"""Repair neutral Prince idle/fall/recovery beyond a native pipe cap."""

import argparse
from collections import Counter
import json
from pathlib import Path

import compose_prince_walkoff_narrow_1126 as Narrow


Pipe, H = Narrow.Pipe, Narrow.H
PARENT = Narrow.PARENT
CANDIDATE = 'fbc1ebd24fb347afbf165c34df3e927b7a123c92fed9482219f96ee55bafa0d3'


def workers():
    return Narrow.workers(neutral_pipe=True)


def transform(raw, reverse=False):
    return Narrow.transform(raw, reverse, neutral_pipe=True)


def compose(raw):
    assert H(raw) == PARENT
    image = transform(raw)
    assert H(image) == CANDIDATE
    assert transform(image, reverse=True) == raw
    return image


def inverse(image):
    assert H(image) == CANDIDATE
    raw = transform(image, reverse=True)
    assert H(raw) == PARENT
    return raw


static_extents = Narrow.static_extents


def check(raw, image):
    P = Narrow.Previous
    proof = P.check(raw, image)
    counts = Counter()
    for action, mode in ((0, 0), (1, 1), (1, 255), (3, 255), (4, 255), (7, 3),
                         (7, 4), (10, 1), (17, 0), (17, 3), (17, 4), (24, 1),
                         (28, 2), (28, 6), (42, 1), (49, 3), (49, 4)):
        for input_bits in (0, 1, 2, 4, 8, 16, 32, 64, 128, 255):
            for top in (144, 176, 208):
                for foot_delta in (0, 1, 3, 15, 16, 20):
                    outputs = []
                    for rom in (raw, image):
                        memory = P.fixture(rom, x=770, top=top, foot=top + foot_delta,
                                           action=action, mode=mode)
                        memory[0xDC] = input_bits
                        outputs.append(P.invoke(memory))
                    before, after = outputs
                    counts['control_and_ground_vectors'] += 1
                    allowed = input_bits == 0 and foot_delta < 16
                    if not allowed:
                        assert before == after, (action, mode, input_bits, top, foot_delta, outputs)
                        counts['active_controls_ground_and_deep_returns_exact'] += 1
                    elif before['material'] != after['material']:
                        assert [q['material'] for q in outputs] == [1, 0]
                        counts['neutral_pipe_support_removed'] += 1
    proof['idle_scope'] = dict(counts)
    targets = []
    for left, top, x in ((608, 160, 649), (736, 144, 770)):
        for action, mode in ((0, 0), (7, 3), (7, 4), (17, 0), (17, 3), (17, 4), (49, 3), (49, 4)):
            outputs = [P.invoke(P.fixture(rom, left=left, top=top, x=x, foot=top + 1,
                                          query=left, action=action, mode=mode))
                       for rom in (raw, image)]
            assert [q['material'] for q in outputs] == [1, 0], (left, top, x, action, mode, outputs)
            targets.append(dict(left=left, top=top, x=x, action=action, mode=mode,
                                native_y=top-32, feet=[x+2, x+13], before=outputs[0], after=outputs[1]))
    proof['reported_neutral_idle_targets'] = targets
    for layout in ('brick', 'flat', 'covered'):
        for action, mode in ((0, 0), (1, 1), (4, 255), (7, 3), (49, 3)):
            for top in (112, 144, 160, 176, 208):
                for x in (721, 724, 746, 765, 766, 770):
                    for delta in (0, 1, 3, 15, 16, 20):
                        before, after = (P.invoke(P.fixture(rom, layout=layout, action=action,
                                                           mode=mode, top=top, x=x, foot=top+delta))
                                         for rom in (raw, image))
                        assert before == after, (layout, action, mode, top, x, delta, before, after)
                        counts['neutral_nonpipe_returns_exact'] += 1
    proof['idle_scope'] = dict(counts)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == (Pipe.Packet.R / 'build/prince-walkoff-1126').resolve()
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    if H(raw) == CANDIDATE:
        raw = inverse(raw)
    image = compose(raw)
    proof = check(raw, image)
    proof.update(parent_SHA256=H(raw), candidate_SHA256=H(image), inverse_exact=True,
                 source_SHA256=H(Path(__file__).read_bytes()),
                 worker_source_SHA256=H(Path(Narrow.__file__).read_bytes()),
                 envelope=[Narrow.START, Narrow.END],
                 policy='Additional physical-foot check only for native DC input0 and raw pipe-cap point10..13 at the surface tile; idle/fall/recovery included; current-row/high-foot/climb guards unchanged; nonpipe materials and active controls retain the original rule',
                 native_run=False, installed=False, generated_files=2)
    output.mkdir(exist_ok=True)
    # Both earlier candidates have completed their diagnostic purpose. Delete
    # only this component's four named disposable artifacts, after the new
    # candidate has passed all CPU checks and its byte-for-byte inverse.
    for name in ('candidate.nes', 'receipt.json', 'candidate-narrow.nes', 'receipt-narrow.json'):
        path = output / name
        if path.exists():
            assert path.resolve().parent == output
            path.unlink()
    (output / 'candidate-idle.nes').write_bytes(image)
    (output / 'receipt-idle.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k not in ('examples', 'third_edge_primitive', 'reported_neutral_idle_targets')}), flush=True)


if __name__ == '__main__':
    main()
