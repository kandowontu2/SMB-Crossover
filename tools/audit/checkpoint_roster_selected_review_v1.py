"""Combine exact earlier-hash selected-image review coverage without closing findings."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current8ff-roster-review-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=D/'selected27-final-review-v1/proof.json';packet=D/'selected27-final-packet-v1/proof.json'
    assert sha(p)=='61271b5bc288a8dfb8657258b3a237ba1dc08bd875301f361ab84fe8cf41d8b0'
    assert sha(packet)=='29cba7bff2d1bce63b988f267f79a16f430c1cddbab20fee7b7b69526df41dcd'
    q=json.loads(p.read_text());k=json.loads(packet.read_text())
    for name,v in q['immutable_input_bindings'].items():assert sha(Path(name))==v,name
    assert sha(ROOT/'tools/audit/final_roll_items_roster_review.py')==k['tool_sha256']
    report=ROOT/'docs/qa/final-roll-items-roster-review-2026-10-25.txt';assert sha(report)==k['report_sha256']
    old=ROOT/'docs/qa/checkpoints/2026-10-25/m3-hud-5ec8/earlier8ff-root-selected-review.json'
    r=json.loads(old.read_text());assert r['ROM_sha256']==q['ROM_sha256']
    coverage={}
    for group in [r['refs'],q['profiles']]:
        for row in group:
            key=row['identity']+':'+row['mode'];frames=[s['frame']for s in row['samples']]
            if key in coverage:assert coverage[key]==frames
            coverage[key]=frames
    assert len(coverage)==38 and len({x.split(':')[0]for x in coverage})==37 and sum(map(len,coverage.values()))==304
    out=ROOT/'docs/qa/checkpoints/2026-10-25/roster8ff-selected-review';out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(p,out/'agent-selected-review.json');shutil.copy2(packet,out/'agent-packet.json')
    proof=dict(selected_review_complete=True,visual_qualification_passed=False,goal_complete=False,ROM_sha256=q['ROM_sha256'],
               profiles=38,identities=37,selected_actual_frames=304,coverage=coverage,
               every_frame_manually_reviewed=False,independently_rechecked_agent_file_bindings=len(q['immutable_input_bindings']),
               refs={str(x):sha(x)for x in [p,packet,old,report,ROOT/'tools/audit/final_roll_items_roster_review.py']},
               open_visibility_findings=q['open_visibility_findings'],
               scope='All37 identities have eight selected actual PPU frames per38profiles reviewed acrossROOT andagent, with duplicateBass samples countedonce. Conservative scanner verified193035actualPPUframes, not manual inspection of all frames. Known SMB3 font defect independently repaired on later5ec; earlier8ffcaptures never relabeledcurrent. Octopusbodydropout/Sophiaeffectoverlap remain open; no every-item/source/SFX/lag verdict.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k]for k in ['selected_review_complete','visual_qualification_passed','profiles','identities','selected_actual_frames','independently_rechecked_agent_file_bindings']}))


if __name__=='__main__':main()
