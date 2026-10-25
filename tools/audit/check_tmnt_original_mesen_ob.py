"""Bind original Mesen audio calls to the independently executed pinned NSF."""
from pathlib import Path
import argparse
import collections
import csv
import gzip
import hashlib
import json

OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((a.captures/'manifest.json').read_text());assert manifest['passed']and manifest['complete']
    source=json.loads((OUT/'probe-v2/coverage.json').read_text());assert manifest['source_NSF_sha256']==source['source_sha256']
    assert len(manifest['runs'])==16
    rows={};calls=writes=0
    for record in manifest['runs']:
        song=record['song'];d=a.captures/f'song-{song:02d}';actual=collections.defaultdict(list)
        assert sha(d/'calls.csv')==record['CSV_sha256']
        assert sha(d/'calls.csv.gz')==record['packed_sha256']
        assert gzip.decompress((d/'calls.csv.gz').read_bytes())==(d/'calls.csv').read_bytes()
        selected=(d/'source.nsf').read_bytes();original=Path(source['source']).read_bytes()
        assert selected[7]==song and selected[:7]==original[:7]and selected[8:]==original[8:]
        for q in csv.DictReader((d/'calls.csv').open()):actual[int(q['call'])].append((int(q['address']),int(q['value'])))
        n=record['result']['play_calls'];assert record['result']['initializations']==2
        assert record['result']['reason']=='host-song-advancement'
        assert all(-1<=k<n for k in actual)
        expected=json.loads(gzip.decompress((OUT/f'probe-v2/song-{song:02d}.json.gz').read_bytes()))
        compared=0
        for q in expected:
            if q['call']>=n:break
            assert actual[q['call']]==list(map(tuple,q['writes'])),(song,q['call'])
            compared+=1
        assert compared==n+1
        total=sum(len(v)for v in actual.values());assert total==record['result']['writes']
        rows[str(song)]=dict(original_init_and_play_groups=compared,ordered_APU_events=total,matched=True,
                             stopped_before_next_host_initialization=True,CSV_sha256=record['CSV_sha256'])
        calls+=compared;writes+=total
    report=dict(passed=True,original_NSF_sha256=source['source_sha256'],native_songs=16,original_call_groups=calls,
                ordered_APU_events=writes,songs=rows,capture_manifest_sha256=sha(a.captures/'manifest.json'),
                source_coverage_sha256=sha(OUT/'probe-v2/coverage.json'),checker_sha256=sha(Path(__file__)),
                scope='Independent original Mesen NSF calls match original CPU-model APU writes. Source captures end before NSF host song advancement, including short-cue transitions. This does not certify the future game adapter, its mixer, timing, DMC remapping or waveform.')
    (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['passed','native_songs','original_call_groups','ordered_APU_events']}))


if __name__=='__main__':main()
