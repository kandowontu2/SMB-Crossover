"""Capture each new family's own NES soundtrack; retain lossless data externally.

The input NSF rips and their provenance are in reference/new-roster-audio.
This is source extraction, not ROM gameplay verification.
"""
from pathlib import Path
import concurrent.futures
import gzip
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import run_mesen

SOURCES = ROOT/'reference/new-roster-audio'
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-23-new-roster-music')
KINDS = ('normal', 'water', 'underground', 'castle', 'bonus', 'intro', 'star',
         'die', 'game_over', 'win', 'win_castle', 'hurry')
# Track numbers use the source NSF's one-based song numbering, not the order
# of its accompanying M3U playlist. Names are retained in that original file.
TRACKS = {
    'kirby':  (2,44,19,29,34,35,3,40,12,6,8,13),
    'chip':   (2,4,5,8,12,13,14,15,16,11,11,10),
    'tmnt':   (2,5,3,10,8,1,11,15,13,12,12,6),
    'mac':    (20,22,1,23,2,1,23,7,9,6,4,23),
    'mike':   (1,2,4,5,14,11,22,13,15,9,17,5),
    'mario3': (9,11,12,23,13,1,14,43,42,38,39,27),
    'vic':    (3,6,4,9,5,1,10,13,13,14,14,10),
    'zelda2': (5,4,4,12,7,2,15,24,24,6,17,15),
    'cv3':    (1,6,3,12,20,20,15,27,28,16,19,15),
    'darkwing':(5,7,7,8,12,2,16,13,13,3,3,16),
}


def prepare_sources():
    # The supplied Crossover2 NSFE has named SMB3 selections in a different
    # order from old NSF rips. Convert that exact driver/data, not its indices.
    source = next((ROOT/'reference/crossover2/extracted/binaryData').glob('*GameSuperMarioBros3_Nsfe.bin'))
    data = source.read_bytes()
    chunks = {}
    offset = 4
    while offset < len(data):
        size, kind = struct.unpack_from('<I4s', data, offset)
        chunks[kind] = data[offset+8:offset+8+size]
        offset += 8+size
    info = chunks[b'INFO']
    header = bytearray(128)
    header[:5] = b'NESM\x1a'
    header[5:8] = bytes((1, info[8], info[9]+1))
    header[8:14] = info[:6]
    header[110:112] = struct.pack('<H', 16639)
    header[112:120] = chunks.get(b'BANK', bytes(8))[:8]
    header[120:122] = struct.pack('<H', 19997)
    header[122:124] = info[6:8]
    target = SOURCES/'mario3/crossover-named.nsf'
    target.write_bytes(header + chunks[b'DATA'])
    cv3 = next((ROOT/'reference/crossover2/extracted/binaryData').glob('*GameCastlevania3_Nsf.bin'))
    (SOURCES/'cv3').mkdir(exist_ok=True)
    (SOURCES/'cv3/crossover.nsf').write_bytes(cv3.read_bytes())
    result = {}
    for role in TRACKS:
        path = target if role == 'mario3' else next((SOURCES/role).glob('*.nsf'))
        result[role] = path
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = prepare_sources()
    plan = {role: dict(source=str(path.relative_to(ROOT)).replace('\\','/'),
                      source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      tracks=dict(zip(KINDS, TRACKS[role])))
            for role, path in sources.items()}
    (SOURCES/'playlist-plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    jobs = {}
    for role, spec in plan.items():
        for kind, track in spec['tracks'].items():
            key = f'{role}-{track:02d}'
            length = 15000 if kind not in ('die','game_over','win','win_castle') else 1800
            jobs[key] = dict(role=role, track=track, frames=max(length, jobs.get(key, {}).get('frames', 0)))

    def capture(item):
        key, job = item
        folder = OUT/key
        folder.mkdir(exist_ok=True)
        csv = folder/'apu.csv'
        zipped = folder/'apu.csv.gz'
        receipt = folder/'complete.json'
        if receipt.exists() and zipped.exists():
            prior = json.loads(receipt.read_text())
            if prior['frames'] == job['frames'] and prior['source_sha256'] == plan[job['role']]['source_sha256']:
                assert hashlib.sha256(gzip.decompress(zipped.read_bytes())).hexdigest() == prior['capture_sha256']
                return key, prior
        data = bytearray(sources[job['role']].read_bytes())
        data[7] = job['track']
        rom = folder/'source.nsf'
        rom.write_bytes(data)
        script = folder/'capture.lua'
        script.write_text(f'AUDIO_OUTPUT=[=[{csv.as_posix()}]=]\nAUDIO_BEGIN=0\nAUDIO_END={job["frames"]}\nAUDIO_NATIVE="nsf"\nAUDIO_FREEZE=false\ndofile([=[{(ROOT/"tools/reference/capture_expanded_audio.lua").as_posix()}]=])\n')
        namespace = dict(run_mesen.__dict__)
        # Isolate logs, too, while using the existing guarded emulator driver.
        text = (ROOT/'tools/run_mesen.py').read_text().replace("    output = ROOT / 'build/verification'\n", '    output = ISOLATED_OUTPUT\n')
        namespace.update(__file__=str(ROOT/'tools/run_mesen.py'), __name__='_new_music_capture', ISOLATED_OUTPUT=folder)
        exec(compile(text, str(ROOT/'tools/run_mesen.py'), 'exec'), namespace)
        code = namespace['run'](script, rom, timeout=55)
        assert code == 0, key
        raw = csv.read_bytes()
        zipped.write_bytes(gzip.compress(raw, mtime=0))
        assert gzip.decompress(zipped.read_bytes()) == raw
        record = dict(**job, source_sha256=plan[job['role']]['source_sha256'],
                      capture_sha256=hashlib.sha256(raw).hexdigest(),
                      path=str(zipped), bytes=len(raw), compressed_bytes=zipped.stat().st_size)
        receipt.write_text(json.dumps(record, indent=2)+'\n')
        csv.unlink()  # Exact lossless gzip above is retained beside its receipt.
        return key, record

    manifest = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for key, record in pool.map(capture, jobs.items()):
            manifest[key] = record
            (SOURCES/'captures-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
            print(f'{key}: {len(manifest)}/{len(jobs)} complete', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
