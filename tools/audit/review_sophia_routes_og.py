"""Keep strict route bounds while measuring the actual restored player origin."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True); p.add_argument('--evidence', type=Path, required=True)
    a = p.parse_args(); checks = {}

    def player_trace(folder):
        mode = 'easy' if '-easy-' in folder.name else 'hard'
        guard = a.evidence.parent / ('guarded-'+mode+'-v3')
        q = json.loads((guard/'proof.json').read_text())
        assert q['passed'] and q['ROM_sha256'] == sha(a.rom) and q['observed']['repaired']
        for name in ['inputs.csv','trace.csv']:
            assert (guard/name).read_bytes() == (folder/name).read_bytes()
        rows = list(csv.DictReader((folder/'trace.csv').open()))
        raw = {r['frame']: r for r in rows}
        borrow = list(csv.DictReader((guard/'borrowed-origin.csv').open()))
        for event in borrow:
            r = raw[event['frame']]
            assert event['blockAttack'] == '1'
            assert int(r['x']) == int(event['x']) == int(event['probeX'])
            assert int(r['y']) == int(event['y']) == int(event['probeY'])
            assert abs(int(event['savedX'])-int(event['lastDrawX'])) <= 8
            assert abs(int(event['savedY'])-int(event['lastDrawY'])) <= 8
            # Only this positively observed source-owned borrow is projected.
            # Original trace bytes and the original failed report stay intact.
            r['x'] = event['savedX']; r['y'] = event['savedY']
        committed = list(csv.DictReader((guard/'committed-movement.csv').open()))
        committed = [r for r in committed if r['mode']=='1' and r['task']=='3' and r['engine']=='8' and r['world']==r['level']=='0']
        assert len(committed) > 1000
        # Match the original review's adjacent-video-frame admission. A real
        # injury state can separate two engine8 samples by dozens of frames.
        adjacent = [(x,y) for x,y in zip(committed,committed[1:]) if int(y['frame'])==int(x['frame'])+1]
        assert len(adjacent)>500
        world = [abs(int(y['x'])-int(x['x'])) for x,y in adjacent]
        camera = [int(y['camera'])-int(x['camera']) for x,y in adjacent]
        assert max(world) <= 8 and min(camera) >= 0 and max(camera) <= 4
        assert all(r['blockAttack'] == '0' for r in committed)
        checks[mode] = dict(guard_proof_sha256=sha(guard/'proof.json'),
            completed_updates=len(committed),adjacent_committed_samples=len(adjacent),max_committed_world_step=max(world),
            max_committed_camera_step=max(camera),borrowed_video_frames=[int(r['frame']) for r in borrow],
            borrowed_observer_sha256=sha(guard/'borrowed-origin.csv'),
            committed_observer_sha256=sha(guard/'committed-movement.csv'))
        return rows

    replay = json.loads((a.evidence/'replay-results.json').read_text())
    assert len(replay['runs']) == 2 and {(r['identity'],r['mode']) for r in replay['runs']} == {('sophia','easy'),('sophia','hard')}
    original = ROOT/'tools/audit/review_tmnt_ny.py'; source = original.read_text()
    anchor = "len(replay['runs']) == 8"; assert source.count(anchor) == 1
    source = source.replace(anchor,"len(replay['runs']) == 2")
    anchor = "trace = list(csv.DictReader((folder / 'trace.csv').open()))"; assert source.count(anchor) == 1
    source = source.replace(anchor,'trace = player_trace(folder)')
    namespace = dict(__name__='observed_sophia_review',__file__=str(original),player_trace=player_trace)
    exec(compile(source,str(original),'exec'),namespace)
    sys.argv = [str(original),'--rom',str(a.rom),'--evidence',str(a.evidence)]
    namespace['main']()
    path = a.evidence/'route-review.json'; report = json.loads(path.read_text())
    report['original_review_sha256'] = sha(original)
    report['adapter_sha256'] = sha(Path(__file__))
    report['movement_observation'] = checks
    report['fixture_correction'] = ('The raw video-frame RAM trace can catch MegaManWeapons while it temporarily lends player coordinates to PlayerHeadCollision. Only positively observed MmBlockAttack=1 origins matching the exact probed block cell are projected to MmSavedPlayer. Actual body-draw origins stay within8pixels of those saved origins; completed GameLoop returns must restore the borrow and satisfy the same world<=8/camera<=4 bounds. All original input/trace bytes, screenshots and the failed raw-world report remain retained. Exact replay, deaths, PNG coverage, CHR and scroll assertions are unchanged.')
    path.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
