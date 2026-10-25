"""Read-only size and lossless-repacking feasibility audit of the full roster.

This creates evidence, never edits a cartridge or prepared source asset. Tile
dictionary sizes are storage bounds, not a proof that mapper bank constraints
or simultaneous on-screen poses can be satisfied.
"""
from pathlib import Path
import collections, csv, hashlib, json, re, zlib

R = Path(__file__).resolve().parents[2]
O = R/'build/verification/mmc3-full-roster-feasibility-ne'
O.mkdir(parents=True, exist_ok=False)


def fields(line):
    return dict((k, v.strip('"')) for k, v in re.findall(r'(\w+)=("[^"]*"|[^,]*)', line.split('\t', 1)[1]))


def flip_pair(pair, h=False, v=False):
    tiles = [pair[:16], pair[16:]]
    if v:
        tiles = [t[:8][::-1]+t[8:][::-1] for t in tiles[::-1]]
    if h:
        tiles = [bytes(int(f'{b:08b}'[::-1], 2) for b in t) for t in tiles]
    return b''.join(tiles)


def tile_stats(data):
    chunks = lambda n: [data[i:i+n] for i in range(0, len(data), n)]
    result = dict(bytes=len(data))
    for n in (16, 32, 1024, 2048):
        blocks = chunks(n)
        unique = set(blocks)
        result[str(n)] = dict(blocks=len(blocks), unique=len(unique),
            unique_bytes=sum(map(len, unique)), nonzero=sum(any(x) for x in blocks))
    pairs = set(chunks(32))
    folded = {min(flip_pair(p, h, v) for h in (False, True) for v in (False, True)) for p in pairs}
    result['optimistic_HV_pair_dictionary_bytes'] = len(folded)*32
    result['zlib_whole_stream_bytes_HOST_ONLY'] = len(zlib.compress(data, 9))
    result['zlib_independent_1K_bytes_HOST_ONLY'] = sum(len(zlib.compress(b, 9)) for b in chunks(1024))
    return result


def image(path):
    raw = path.read_bytes()
    prg_size = raw[4]*16384
    chr_size = raw[5]*8192
    assert len(raw) == 16+prg_size+chr_size
    segments = [fields(s) for s in path.with_suffix('.dbg').read_text().splitlines() if s.startswith('seg\t')]
    mask = bytearray(prg_size)
    occupied = []
    for segment in segments:
        if 'ooffs' not in segment or not int(segment['size'], 0):
            continue
        start = int(segment['ooffs'])-16
        size = int(segment['size'], 0)
        if start < 0 or start >= prg_size:
            continue
        assert start+size <= prg_size
        assert not any(mask[start:start+size]), segment['name']
        mask[start:start+size] = bytes([1])*size
        payload = raw[16+start:16+start+size]
        occupied.append(dict(name=segment['name'], offset=start, bytes=size,
            bank=start//8192, trailing_FF_bytes=len(payload)-len(payload.rstrip(b'\xff')),
            host_zlib_bytes=len(zlib.compress(payload, 9))))
    data = raw[16:16+prg_size]
    result = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
        PRG_declared_bytes=prg_size, CHR_declared_bytes=chr_size,
        PRG_linked_segment_bytes=sum(mask), PRG_unallocated_padding_bytes=prg_size-sum(mask),
        PRG_segments=occupied, CHR=tile_stats(raw[16+prg_size:]))
    with (O/(path.stem+'-segments.csv')).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(occupied[0]))
        writer.writeheader()
        writer.writerows(occupied)
    result['PRG_banks'] = [dict(bank=b, linked_bytes=sum(mask[b*8192:(b+1)*8192]),
        non_FF_bytes=sum(v != 255 for v in data[b*8192:(b+1)*8192])) for b in range(prg_size//8192)]
    return result


full = image(R/'build/smb-crossover-mmc5-expanded.nes')
standard = image(R/'build/smb-crossover-mmc3.nes')
report = dict(full=full, standard=standard,
    standard_MMC3_limits=dict(PRG_bytes=524288, CHR_bytes=262144, PRG_RAM_bytes=8192),
    PRG_linked_over_MMC3_bytes=full['PRG_linked_segment_bytes']-524288,
    CHR_page_dedup_over_MMC3_bytes=full['CHR']['1024']['unique_bytes']-262144,
    scope='Exact linked-segment and global tile/page dictionary measurements. Internal reservations/pinned source binaries are included in linked PRG sizes. ZIP/zlib results are host-only compression comparisons, not an NES decoder or a playable MMC3 port. Tile dictionaries do not yet satisfy per-frame mapper residency constraints.')
(O/'measurements.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('full', 'standard')}, indent=2))
for name, result in (('full', full), ('standard', standard)):
    print(json.dumps(dict(target=name, PRG=result['PRG_linked_segment_bytes'], CHR=result['CHR']), indent=2))
print('PRG segments:', [(s['name'], s['bytes']) for s in full['PRG_segments']])
