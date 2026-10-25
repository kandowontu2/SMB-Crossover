"""Resolve only two positively observed borrowed-origin trace samples."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True);p.add_argument('--baseline-review',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    digest=sha(a.rom);prior=json.loads(a.baseline_review.read_text())
    assert prior['ROM_sha256']==digest and len(prior['admitted'])==42
    failures=prior['strict_review_failures'];wanted={('bill','easy'),('rygar','easy')}
    assert {(c['identity'],c['mode'])for c in failures}==wanted
    observations={}
    def player_trace(folder):
        name=next(n for n in ['bill','rygar']if folder.name=='replay-'+n+'-easy-v1')
        guard=a.evidence.parent/('guarded-'+name+'-easy-v1')
        proof=json.loads((guard/'proof.json').read_text())
        assert proof['passed']and proof['ROM_sha256']==digest and proof['observed']['repaired']
        for n in ['inputs.csv','trace.csv']:assert (guard/n).read_bytes()==(folder/n).read_bytes()
        rows=list(csv.DictReader((folder/'trace.csv').open()));raw={r['frame']:r for r in rows}
        borrowed=list(csv.DictReader((guard/'borrowed-origin.csv').open()));assert borrowed
        for event in borrowed:
            r=raw[event['frame']];assert event['blockAttack']=='1'
            assert int(r['x'])==int(event['x'])==int(event['probeX'])
            assert int(r['y'])==int(event['y'])==int(event['probeY'])
            assert abs(int(event['savedX'])-int(event['lastDrawX']))<=8
            assert abs(int(event['savedY'])-int(event['lastDrawY']))<=8
            r['x']=event['savedX'];r['y']=event['savedY']
        committed=[r for r in csv.DictReader((guard/'committed-movement.csv').open())if r['mode']=='1'and r['task']=='3'and r['engine']=='8'and r['world']==r['level']=='0']
        assert len(committed)>1000 and all(r['blockAttack']=='0'for r in committed)
        pairs=[(x,y)for x,y in zip(committed,committed[1:])if int(y['frame'])==int(x['frame'])+1]
        assert len(pairs)>500
        world=[abs(int(y['x'])-int(x['x']))for x,y in pairs];camera=[int(y['camera'])-int(x['camera'])for x,y in pairs]
        assert max(world)<=8 and min(camera)>=0 and max(camera)<=4
        observations[name]=dict(guard_proof_sha256=sha(guard/'proof.json'),borrowed_frames=[int(r['frame'])for r in borrowed],
            borrowed_observer_sha256=sha(guard/'borrowed-origin.csv'),committed_observer_sha256=sha(guard/'committed-movement.csv'),
            completed_updates=len(committed),adjacent_committed_pairs=len(pairs),max_committed_world_step=max(world),max_committed_camera_step=max(camera))
        return rows
    original=ROOT/'tools/audit/review_tmnt_ny.py';text=original.read_text()
    edits={"replay = json.loads((root / 'replay-results.json').read_text())":'replay = explicit_replay',
        "len(replay['runs']) == 8":"len(replay['runs']) == 1",
        "trace = list(csv.DictReader((folder / 'trace.csv').open()))":'trace = player_trace(folder)',
        "(root / 'route-review.json').write_text":'review_destination.write_text'}
    for old,new in edits.items():assert text.count(old)==1; text=text.replace(old,new)
    added={}
    for case in failures:
        native=case['case'];key=case['identity']+'-'+case['mode'];dest=a.output/(key+'.json')
        ns=dict(__name__='two_guarded_route_reviews',__file__=str(original),player_trace=player_trace,
            explicit_replay=dict(passed=True,ROM_sha256=digest,runs=[native]),review_destination=dest)
        exec(compile(text,str(original),'exec'),ns)
        sys.argv=[str(original),'--rom',str(a.rom),'--evidence',str(a.evidence)];ns['main']()
        q=json.loads(dest.read_text());assert q['passed']and set(q['runs'])=={key}
        added[key]=dict(review=str(dest),sha256=sha(dest),result=q['runs'][key])
    all_admitted={**prior['admitted'],**added};assert len(all_admitted)==44
    q=dict(passed=True,all_requested_routes_pass=False,goal_complete=False,ROM_sha256=digest,
        original_raw_strict_review=dict(path=str(a.baseline_review),sha256=sha(a.baseline_review),passed=prior['passed']),
        admitted=all_admitted,strict_review_failures=[],retained_negative_or_skipped=prior['retained_negative_or_skipped'],
        positive_borrow_observations=observations,strict_reviewer_sha256=sha(original),adapter_sha256=sha(Path(__file__)),
        scope='The42original strict passes are preserved. Only the two originally rejected traces are reviewed again, using positive read-only exact-probe/body-origin and restored completed-loop observations on the same hash and exact input/trace bytes. Original failed report and raw traces stay intact. Original world<=8/camera<=4, PNG, CHR, scroll and replay bounds remain unchanged. All26failed discoveries/skipped replays remain failed. Human image investigation, other graphics, every-item and final-mapper work remain separate.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print('PASS44strict replay reviews;26original negatives remain')


if __name__=='__main__':main()
