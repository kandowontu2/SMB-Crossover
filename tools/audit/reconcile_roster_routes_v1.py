"""Add a separately retained controller retry to the frozen8ff route evidence."""
from pathlib import Path
import copy,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    original=D/'current8ff-roster-v1/proof.json';retry=D/'current8ff-bass-retry-v1/proof.json'
    old=json.loads(original.read_text());q=json.loads(retry.read_text())
    assert old['complete']and not old['passed']and q['passed']and q['replay']['passed']
    assert old['ROM_sha256']==q['ROM_sha256']=='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
    failed=[r for r in old['runs']if not r['passed']];assert len(failed)==1 and failed[0]['identity']=='bass'
    result=copy.deepcopy(old);row=next(r for r in result['runs']if r['identity']=='bass')
    folder=retry.parent/'discovery';native=json.loads((folder/'manifest.json').read_text())
    motion=json.loads((folder/'completed-loop-motion.json').read_text());assert motion['passed']and native['chr_commit']['passed']
    row.update(passed=True,folder=str(folder),result=native['result'],motion=motion,chr_commit=native['chr_commit'],exit=0,
               source_policy=str(retry.parent/'policy.lua'),policy_sha256=q['new_policy_sha256'],
               trace_summary={},replay=dict(folder=str(retry.parent/'direct'),exit=0,passed=True,
                                          physical_frames=q['replay']['physical_frames'],proof_sha256=q['replay']['proof_sha256']))
    assert len(result['runs'])==38 and len({r['identity']for r in result['runs']})==37
    assert all(r['passed']and r['replay']['passed']for r in result['runs'])
    result.update(passed=True,goal_complete=False,visual_qualification_passed=False,route_profiles=38,identities=37,
                  direct_frames=sum(r['replay']['physical_frames']for r in result['runs']),
                  original_failed_run_retained=failed[0],original_aggregate_sha256=sha(original),retry_proof_sha256=sha(retry),
                  scope='All37 identities/38profiles cleared1-1 without death and independently replayed exact controller/trace/result to actual PPU lossless frames on8ff ONLY. BassHard uses an additive controller jump correction; original failure remains immutable. This is route progress, not every powerup/allHard or visual completion. A real SMB3 P-bar cloud-font defect was found; custom fade and other source/music work remain open. Current installed9bac is a later hash, not silently covered by this aggregate.')
    out=D/'current8ff-roster-reconciled-v1';out.mkdir(exist_ok=False)
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k]for k in ['passed','ROM_sha256','route_profiles','identities','direct_frames','visual_qualification_passed']}))


if __name__=='__main__':main()
