"""Keep C/D successes distinct from installed E and preserve the full roster goal."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-goal-coverage-ay.json';assert not out.exists()
    old=V/'root49-goal-coverage-ax.json';assert sha(old)=='19b30cd07b7fc804c0499b44609fe1a96089d8f233b91e3148e1787c10e99691'
    result=json.loads(old.read_text())
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json';c=json.loads(cp.read_text())
    result['checkpoints']['E']=dict(path=str(cp.relative_to(R)),sha256=sha(cp),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']})
    result['current_working_revision']='E'
    images={h:(revision,mapper)for revision,c in result['checkpoints'].items()for mapper,h in c['ROMs'].items()}
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
        q['current_working_E_full_clear_candidates']=[x for x in q['pinned_full_clear_candidates']if x['revision']=='E']
        assert not q['base_moves_and_power_tiers_complete']and not q['all_specials_upgrades_complete']and not q['final_recording_complete']and not q['overall_complete']
    result.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),
      source_inventory=dict(path='src/inventory_data.inc',sha256=sha(R/'src/inventory_data.inc')),
      new_review_references={n:sha(V/n)for n in[
        'root49-current-d-transfers-a/samus-mmc5-review-ay.json','root49-parent-modes-review-ay.json',
        'root49-ice-integrated-e/root-review-az/review.json','root49-ice-integrated-e/route-review-ba.json',
        'root49-main-ice-e-smoke/review.json']},
      completion_scope='Actual full route candidates retain C/D/E ROM, mapper, identity and mode scope. E is installed but two Samus fixed transfers fail; no E full route admitted. Final all-weapons/upgrades/lag and retained recordings remain open.',
      goal_complete=False)
    assert len(result['roster'])==14
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),current_E_clear_identities=[q['name']for q in result['roster']if q['current_working_E_full_clear_candidates']],identities=14)))
if __name__=='__main__':main()
