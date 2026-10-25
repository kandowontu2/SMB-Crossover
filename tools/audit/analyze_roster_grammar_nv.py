"""Read-only, lossless frame-grammar capacity experiment; never installs assets."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/reference'))
import build_new_roster_audio as codec
import build_playlist_audio as legacy

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')


def prepare(mode):
    manifest = json.loads((codec.SOURCE / 'captures-manifest.json').read_text())
    plan = json.loads((codec.SOURCE / 'playlist-plan.json').read_text())
    plan['meta'] = {**plan['kirby'], 'tracks': {**plan['kirby']['tracks'], 'normal': 13, 'hurry': 13}}
    music = {f"{role if role != 'meta' else 'kirby'}-{p['tracks'][kind]:02d}"
             for role, p in plan.items() for kind in codec.AREAS + ['hurry']}
    needed = {f"{role if role != 'meta' else 'kirby'}-{n:02d}"
              for role, p in plan.items() for n in p['tracks'].values()}
    streams = {}; metadata = {}
    for key in sorted(needed):
        record = manifest[key]
        fs, dpcm = codec.frames(record)
        found = codec.cycle(fs) if key in music else None
        segments = {'intro': fs[:found[0]], 'loop': fs[found[0]:found[0] + found[1]]} if found else {'intro': fs}
        metadata[key] = dict(capture_sha256=record['capture_sha256'], frames=len(fs), loop=found,
                             dpcm_writes_not_encoded=dpcm)
        for label, seq in segments.items():
            streams[key + '-' + label] = ([codec.encode([f]) for f in seq]
                                          if mode == 'frames' else legacy.tokens(seq))
        print('loaded', key, flush=True)
    return streams, metadata


def grammar(source, count, first):
    literals = {}; symbols = []; streams = {}
    def symbol(token):
        if token not in literals:
            literals[token] = len(symbols); symbols.append(token)
        return literals[token]
    for key, seq in source.items():
        streams[key] = [symbol(t) for t in seq]
    n_literal = len(symbols)
    sizes = [len(t) for t in symbols]
    definitions = {}; codes = {}; depths = [0] * len(symbols)
    for code in range(first, first + count):
        pairs = Counter()
        for seq in streams.values():
            pairs.update(zip(seq, seq[1:]))
        if not pairs:
            break
        pair, frequency = max(pairs.items(), key=lambda item:
                              item[1] * (sizes[item[0][0]] + sizes[item[0][1]] - 1))
        saved = frequency * (sizes[pair[0]] + sizes[pair[1]] - 1) - sizes[pair[0]] - sizes[pair[1]] - 4
        if saved <= 0:
            break
        sid = len(symbols)
        definitions[sid] = pair; codes[sid] = code
        symbols.append(bytes([code])); sizes.append(1)
        depths.append(1 + max(depths[pair[0]], depths[pair[1]]))
        for key, seq in streams.items():
            dst = []; i = 0
            while i < len(seq):
                if i + 1 < len(seq) and seq[i] == pair[0] and seq[i + 1] == pair[1]:
                    dst.append(sid); i += 2
                else:
                    dst.append(seq[i]); i += 1
            streams[key] = dst
        if (code - first) % 8 == 0 or code == first + count - 1:
            print('macro', code, 'depth', depths[-1], 'tokens', sum(map(len, streams.values())), flush=True)
    expanded = {}
    def expand(sid):
        if sid not in expanded:
            expanded[sid] = (expand(definitions[sid][0]) + expand(definitions[sid][1])
                             if sid in definitions else symbols[sid])
        return expanded[sid]
    for key, seq in streams.items():
        assert b''.join(expand(sid) for sid in seq) == b''.join(source[key]), key
    return streams, symbols, definitions, codes, max(depths, default=0), n_literal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['frames', 'commands'], default='frames')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    out = ARCHIVE / args.name
    out.mkdir(parents=True, exist_ok=False)
    began = time.time()
    source, metadata = prepare(args.mode)
    first = 0x82 if args.mode == 'frames' else 0x20
    streams, symbols, definitions, codes, depth, literals = grammar(source, 0xfe - first, first)
    terminator = b'\x00' if args.mode == 'frames' else b'\x1f'
    dictionary = b''.join(symbols[a] + symbols[b] + terminator for a, b in definitions.values())
    sizes = {}; unique = {}
    for key, seq in streams.items():
        ending = b'\xfe' if args.mode == 'frames' else b'\x1c'
        if not (key.endswith('-intro') and metadata[key.rsplit('-', 1)[0]]['loop']):
            ending = b'\xff'
        raw = b''.join(symbols[sid] for sid in seq) + ending
        packed = codec.lz(raw)
        (out / (key + '.bin')).write_bytes(packed)
        unique[packed] = True
        sizes[key] = dict(raw=len(raw), compressed=len(packed), sha256=hashlib.sha256(packed).hexdigest())
    (out / 'dictionary.bin').write_bytes(dictionary)
    (out / 'grammar.json').write_text(json.dumps(dict(
        codes={str(codes[sid]): [symbols[a].hex(), symbols[b].hex()] for sid, (a, b) in definitions.items()},
        mode=args.mode, source_tokens='full frames' if args.mode == 'frames' else 'register commands'), indent=2) + '\n')
    total = sum(map(len, unique)) + len(dictionary) + 3 * len(definitions)
    report = dict(bytes=total, reserved_bytes=26 * 8192, fits=total <= 26 * 8192,
                  mode=args.mode, full_capture_roundtrip=True, installed_assets_changed=False,
                  grammar_macros=len(definitions), dictionary_bytes=len(dictionary), maximum_stack=depth,
                  distinct_literal_tokens=literals, captured_tracks=len(metadata), streams=sizes,
                  captures=metadata, elapsed_seconds=time.time() - began)
    (out / 'capacity.json').write_text(json.dumps(report, indent=2) + '\n')
    local = ROOT / 'build/verification/roster-audio-nv'
    local.mkdir(exist_ok=True)
    pointer = dict(path=str(out / 'capacity.json'), sha256=hashlib.sha256((out / 'capacity.json').read_bytes()).hexdigest(),
                   bytes=total, fits=report['fits'], mode=args.mode, stack=depth)
    (local / (args.name + '-location.json')).write_text(json.dumps(pointer, indent=2) + '\n')
    print(json.dumps(pointer), flush=True)


if __name__ == '__main__':
    main()
