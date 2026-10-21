"""Refresh actual current-family route candidates without shrinking the full goal."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-goal-coverage-ax.json';assert not out.exists()
    old=V/'root49-goal-coverage-aw.json';assert sha(old)=='3b6740fa6c1d9312a075dabe8ab529ab806d03f2485834229850240f283535a7'
    result=json.loads(old.read_text());images={h:(revision,mapper)for revision,c in result['checkpoints'].items()for mapper,h in c['ROMs'].items()}
    admitted={}
    for p in(R/'build/roster-through-2-2').glob('*/manifest.json'):
        m=json.loads(p.read_text());which=images.get(m.get('rom_sha256'))
        if not which or not m.get('verified_through_2_2'):continue
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']
        assert sha(p.parent/'inputs.csv')==m['inputs_sha256']
        key=(m['config']['character'],m['config'].get('variant',0))
        admitted.setdefault(key,[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),frames=m['result']['frames'],recorded=m['config']['record']))
    for q in result['roster']:
        q['pinned_full_clear_candidates']=admitted.get((q['character'],q['variant']),[])
        assert not q['all_specials_upgrades_complete']and not q['final_recording_complete']and not q['overall_complete']
    result.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),
      source_inventory=dict(path='src/inventory_data.inc',sha256=sha(R/'src/inventory_data.inc')),
      new_review_references={n:sha(V/n)for n in[
        'root49-current-d-transfers-a/controller-review-ax.json',
        'root49-current-d-transfers-a/bill-lance-review-ax.json',
        'root49-d-remaining-routes-ax/review.json']},
      completion_scope='Actual full route candidates remain bound to their C/D ROM, mapper and identity. Final build, all weapons/upgrades and final recordings remain unproven.',goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    d=sorted({(q['character'],q['variant'])for q in result['roster']if any(p['revision']=='D'for p in q['pinned_full_clear_candidates'])})
    print(json.dumps(dict(status=result['status'],sha256=sha(out),current_D_clear_identities=d,identities=len(result['roster']))))
if __name__=='__main__':main()
