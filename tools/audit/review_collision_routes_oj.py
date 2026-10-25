"""Strict review of three passing OJ replays, retaining the fourth failure."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    a=p.parse_args();digest=sha(a.rom)
    original_report=a.evidence/'replay-results.json';replay=json.loads(original_report.read_text())
    assert not replay['passed'] and replay['ROM_sha256']==digest
    positive={('sophia','easy'),('sophia','hard'),('chip','easy')}
    assert {(r['identity'],r['mode'])for r in replay['runs']}==positive|{('chip','hard')}
    rejected=[r for r in replay['runs']if not r['passed']]
    assert len(rejected)==1 and rejected[0]['identity']=='chip' and rejected[0]['mode']=='hard'
    assert rejected[0]['skipped']
    selected=[r for r in replay['runs']if r['passed']]
    assert {(r['identity'],r['mode'])for r in selected}==positive
    checks={}

    def player_trace(folder):
        rows=list(csv.DictReader((folder/'trace.csv').open()))
        if 'sophia'not in folder.name:return rows
        mode='easy'if '-easy-'in folder.name else 'hard'
        guard=a.evidence.parent/('guarded-'+mode+'-v1')
        q=json.loads((guard/'proof.json').read_text())
        assert q['passed'] and q['ROM_sha256']==digest and q['observed']['repaired']
        for n in ['inputs.csv','trace.csv']:assert (guard/n).read_bytes()==(folder/n).read_bytes()
        raw={r['frame']:r for r in rows}
        borrowed=list(csv.DictReader((guard/'borrowed-origin.csv').open()))
        for event in borrowed:
            r=raw[event['frame']]
            assert event['blockAttack']=='1'
            assert int(r['x'])==int(event['x'])==int(event['probeX'])
            assert int(r['y'])==int(event['y'])==int(event['probeY'])
            assert abs(int(event['savedX'])-int(event['lastDrawX']))<=8
            assert abs(int(event['savedY'])-int(event['lastDrawY']))<=8
            r['x']=event['savedX'];r['y']=event['savedY']
        committed=list(csv.DictReader((guard/'committed-movement.csv').open()))
        committed=[r for r in committed if r['mode']=='1'and r['task']=='3'and r['engine']=='8'and r['world']==r['level']=='0']
        assert len(committed)>1000 and all(r['blockAttack']=='0'for r in committed)
        adjacent=[(x,y)for x,y in zip(committed,committed[1:])if int(y['frame'])==int(x['frame'])+1]
        assert len(adjacent)>500
        world=[abs(int(y['x'])-int(x['x']))for x,y in adjacent]
        camera=[int(y['camera'])-int(x['camera'])for x,y in adjacent]
        assert max(world)<=8 and min(camera)>=0 and max(camera)<=4
        checks[mode]=dict(guard_proof_sha256=sha(guard/'proof.json'),completed_updates=len(committed),
            adjacent_committed_samples=len(adjacent),max_committed_world_step=max(world),max_committed_camera_step=max(camera),
            borrowed_video_frames=[int(r['frame'])for r in borrowed],borrowed_observer_sha256=sha(guard/'borrowed-origin.csv'),
            committed_observer_sha256=sha(guard/'committed-movement.csv'))
        return rows

    strict=ROOT/'tools/audit/review_tmnt_ny.py';source=strict.read_text()
    anchor="replay = json.loads((root / 'replay-results.json').read_text())";assert source.count(anchor)==1
    source=source.replace(anchor,'replay = explicit_replay')
    anchor="len(replay['runs']) == 8";assert source.count(anchor)==1
    source=source.replace(anchor,"len(replay['runs']) == 3")
    anchor="trace = list(csv.DictReader((folder / 'trace.csv').open()))";assert source.count(anchor)==1
    source=source.replace(anchor,'trace = player_trace(folder)')
    ns=dict(__name__='three_explicit_collision_routes',__file__=str(strict),player_trace=player_trace,
        explicit_replay=dict(passed=True,ROM_sha256=digest,runs=selected))
    exec(compile(source,str(strict),'exec'),ns)
    sys.argv=[str(strict),'--rom',str(a.rom),'--evidence',str(a.evidence)];ns['main']()
    target=a.evidence/'route-review.json';q=json.loads(target.read_text())
    q.update(goal_complete=False,all_four_requested_routes_pass=False,retained_negative_cases=rejected,
        original_replay_report_sha256=sha(original_report),strict_reviewer_sha256=sha(strict),adapter_sha256=sha(Path(__file__)),
        movement_observation=checks,
        scope='Only the three explicitly passing replays are admitted. Chip Hard failed discovery and remains failed in the unchanged original aggregate; this is not a four-route or roster pass. The original bounds, exact replay, CHR, complete PNG and scroll checks stay unchanged. Sophia RAM origins are projected only on positively observed native projectile borrowing; actual committed origins must independently satisfy the original bounds. Human inspection remains sampled.')
    target.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
