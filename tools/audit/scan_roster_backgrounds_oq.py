"""Run the diagnostic frame scanner on exact-hash passing replay indexes."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import scan_background_transients_oq as scanner


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--indexes',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);digest=sha(a.rom)
    wanted={};indices=[]
    for path in a.indexes:
        q=json.loads(path.read_text());assert q['ROM_sha256']==digest and q['phase']=='replay'
        indices.append(dict(path=str(path),sha256=sha(path),original_passed=q['passed']))
        for case in q['runs']:
            if case['passed']:wanted.setdefault(case['identity']+'-'+case['mode'],case)
    results={}
    for key,case in wanted.items():
        out=a.output/key
        sys.argv=[str(Path(scanner.__file__)),'--route',case['folder'],'--output',str(out)]
        scanner.main();q=json.loads((out/'proof.json').read_text())
        assert q['scan_complete']and q['ROM_sha256']==digest
        results[key]=dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'),
            retained_PNGs=q['retained_PNGs'],admitted_adjacent_triples=q['admitted_adjacent_triples'],
            candidate_events=q['candidate_events'],candidate_sheets=q['sheets'])
        report=dict(scan_complete=len(results)==len(wanted),goal_complete=False,game_changes=False,
            ROM_sha256=digest,indexes=indices,requested_replay_pairs=len(wanted),scanned_pairs=len(results),results=results,
            human_candidate_review_pending=any(r['candidate_events']for r in results.values()),
            scanner_sha256=sha(Path(scanner.__file__)),driver_sha256=sha(Path(__file__)),
            scope='Diagnostic scan of all retained PNGs in the explicitly passing replay set, deduplicated by identity/mode in input-index order. Failed discoveries/replays are not converted into passes and their sampled footage is not called fully scanned. Conservative sprite/OAM/scene admission, transient-only comparison and0..4pixel alignment retain the individual scanner limitations. Candidate images require human/source investigation; even no candidates does not certify all graphics, every powerup, old videos or a final release.')
        (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(scan_complete=True,pairs=len(results),PNGs=sum(r['retained_PNGs']for r in results.values()),
        candidate_events=sum(r['candidate_events']for r in results.values())),indent=2))


if __name__=='__main__':main()
