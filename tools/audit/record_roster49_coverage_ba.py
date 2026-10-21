"""Retain full goal scope while crediting the first current-F complete replay."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-goal-coverage-ba.json';assert not out.exists()
    old=V/'root49-goal-coverage-az.json';assert sha(old)=='d159145c1e0ed0732f719d54138684341b04bb3f34c17532fa106acff46df375'
    result=json.loads(old.read_text());images={h:(revision,mapper)for revision,c in result['checkpoints'].items()for mapper,h in c['ROMs'].items()};admitted={}
    for p in(R/'build/roster-through-2-2').glob('*/manifest.json'):
        m=json.loads(p.read_text());which=images.get(m.get('rom_sha256'))
        if not which or not m.get('verified_through_2_2'):continue
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']and not m['result']['failure']
        assert sha(p.parent/'inputs.csv')==m['inputs_sha256']
        key=(m['config']['character'],m['config'].get('variant',0))
        admitted.setdefault(key,[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),frames=m['result']['frames'],recorded=m['config']['record']))
    for q in result['roster']:
        q['pinned_full_clear_candidates']=admitted.get((q['character'],q['variant']),[])
        q['current_working_F_full_clear_candidates']=[x for x in q['pinned_full_clear_candidates']if x['revision']=='F']
        assert not q['base_moves_and_power_tiers_complete']and not q['all_specials_upgrades_complete']and not q['final_recording_complete']and not q['overall_complete']
    sophia=next(q for q in result['roster']if q['character']==11)
    assert len(sophia['current_working_F_full_clear_candidates'])==1
    sophia['current_F_complete_route_root_review']=dict(path='build/verification/root49-sophia-f-full-review-ba.json',sha256=sha(V/'root49-sophia-f-full-review-ba.json'),
      scope='Easy MMC3 only, all six stages,25404 frames,zero deaths,independent whole-nine-stream replay and25 real2-3 controller rows. Not all source geometry/arsenal or a final video.')
    samus=next(q for q in result['roster']if q['character']==2)
    samus['scoped_Easy_intrinsic_attack_progress'].update(additional_reports={n:sha(V/n)for n in ['root49-current-f-samus-a/review-ba.json','root49-current-f-samus-a/review-bb.json']},
      additional_observed='Three additional bomb defeats in F/G, a three-Goomba ground-retreat volley in J, supported16px step jump and genuine released Up unmorph. Ordinary L clears1-1/1-2/1-3 then dies21109 to living Bowser0 ID45/HP80.',
      superseded_controller_diagnoses='J initially described as two Goombas: actual trace has three. K initial held-Up explanation is superseded by actual remorph/wait for a Goomba across pipe walls. All original receipts retained.',complete=False)
    result.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),new_review_references={n:sha(V/n)for n in ['root49-sophia-f-full-review-ba.json','root49-current-f-samus-a/review-ba.json','root49-current-f-samus-a/review-bb.json']},
      completion_scope='First complete current F proof is Sophia/Easy/MMC3 only. Every14-identity,66-inventory-entry, acquisition/interaction/lag, original shortcut/nonshortcut and final retained-movie requirement remains required. Prior C/D/E proofs retain original image scope.',goal_complete=False)
    assert len(result['roster'])==14 and sum(len(q['inventory_2_02'])for q in result['roster'])==66
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],sha256=sha(out),current_F_clears=[q['name']for q in result['roster']if q['current_working_F_full_clear_candidates']],identities=14,inventory=66)),flush=True)
if __name__=='__main__':main()
