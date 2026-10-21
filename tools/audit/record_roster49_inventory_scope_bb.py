"""Credit the assertions actually exercised by current-F Samus inventory fixtures."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-inventory-ba'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'scope-b.json';assert not out.exists()
    review=H/'review.json';assert sha(review)=='f19e3e8108508c22c8b011450f2533ec4d25800ae1a7d48cf9131651e6facbc4';r=json.loads(review.read_text())
    prep=H/'preparation.json';assert sha(prep)==r['preparation_sha256'];p=json.loads(prep.read_text())
    for n,h in p['dependencies'].items():assert sha(R/n)==h,n
    assert len(r['groups'])==2
    for g in r['groups']:
        assert g['exit']==0 and sha(H/f"native-{g['mapper']}.log")==g['host_log_sha256']
        for n,z in g['files'].items():assert sha(H/n)==z['sha256']and(H/n).stat().st_size==z['bytes']
        assert len([n for n in g['files']if n.endswith('.png')])==6
        assert 'PASS 2.02 native inventory for character 2: 6 separate pickups' in(H/f"native-{g['mapper']}.log").read_text()
    actual={
      'MORPH':'Distinct private item1 pickup sets ownership. Down input is supplied; the unchanged fixture does not assert the actual Morph body or bomb use for this item.',
      'MISSILE':'Distinct private item2 pickup, controller special creates RgShotType41 and shared missile stock20→19.',
      'ICE':'Distinct private item3 pickup, controller B creates RgShotType46. No enemy freeze behavior asserted by this arena; separate F lifecycle packet covers that seeded component.',
      'WAVE':'Distinct private item4 pickup, controller B creates SmShotType3. Full sine path, enemy and terrain properties are not asserted here.',
      'VARIA':'Distinct private item5 pickup sets ownership; firebar contact protection is not asserted here.',
      'SCREW':'Distinct private item6 pickup sets ownership; flip/body contact effect is not asserted here.',
      'LONG':'Long/mushroom ownership bits are explicit initial state0x81, not a collected seventh item or a long-beam assertion.'}
    s=dict(status='REHASHED_CURRENT_F_HARD_INVENTORY_ASSERTION_SCOPE',script_sha256=sha(__file__),review_sha256=sha(review),
      primary_cases_each_mapper=6,mappers=['mmc3','mmc5'],actual_asserted_scope=actual,
      qualification='The original report phrase controller Morph/B missile includes supplied Down inputs; it does not add a Morph effect assertion. This additive scope record is authoritative for coverage.',
      visual_inspection='Root viewed actual MMC3 Ice and Wave screenshots. They are isolated frame samples; no full animation/CHR/palette/SFX or source-pixel fidelity acceptance follows.',
      natural_block_reveal_or_drop=False,all_arsenal_complete=False,final_recordings_complete=False,goal_complete=False)
    out.write_text(json.dumps(s,indent=2)+'\n')
    old=V/'root49-goal-coverage-ba.json';assert sha(old)=='1030da619953c2872ba4d71dbb2115f9d8c8a710cf393b8750cabbc8bd8e96d6';coverage=json.loads(old.read_text())
    samus=next(x for x in coverage['roster']if x['character']==2)
    samus['current_F_Hard_private_inventory_fixture']=dict(scope_report=str(out.relative_to(R)),scope_sha256=sha(out),actual_assertions=actual,complete=False)
    coverage.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),goal_complete=False)
    dst=V/'root49-goal-coverage-bb.json';assert not dst.exists();dst.write_text(json.dumps(coverage,indent=2)+'\n')
    print(json.dumps(dict(scope_sha256=sha(out),coverage_sha256=sha(dst),goal_complete=False)),flush=True)
if __name__=='__main__':main()
