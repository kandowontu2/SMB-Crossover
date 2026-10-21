"""Credit verified routes/components while preserving every original deliverable."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-goal-coverage-bo.json';assert not out.exists()
    old=V/'root49-goal-coverage-bb.json';assert sha(old)=='0363d4cf0cf73cd31fe68b9df7283e51b0eb93759799472839bcc9ce217187d5';j=json.loads(old.read_text())
    images={h:(rev,mapper)for rev,c in j['checkpoints'].items()for mapper,h in c['ROMs'].items()};clears={}
    for p in(R/'build/roster-through-2-2').glob('*/manifest.json'):
        m=json.loads(p.read_text());which=images.get(m.get('rom_sha256'))
        if not which or not m.get('verified_through_2_2'):continue
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']and m['result']['failure']is None
        assert sha(p.parent/'inputs.csv')==m['inputs_sha256']
        key=(m['config']['character'],m['config'].get('variant',0));clears.setdefault(key,[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),frames=m['result']['frames'],recorded=m['config']['record']))
    for q in j['roster']:
        q['pinned_full_clear_candidates']=clears.get((q['character'],q['variant']),[])
        q['current_working_F_full_clear_candidates']=[x for x in q['pinned_full_clear_candidates']if x['revision']=='F']
        assert not q['base_moves_and_power_tiers_complete']and not q['all_specials_upgrades_complete']and not q['final_recording_complete']and not q['overall_complete']
    bill=next(q for q in j['roster']if q['character']==3 and q['variant']==0)
    bill['current_F_complete_route_root_review']=dict(path='build/verification/root49-bill-f-full-review-bi.json',sha256=sha(V/'root49-bill-f-full-review-bi.json'),scope='Easy MMC3 only,34401physical frames,zero deaths,25actual2-3 control rows40to70; actual natural Bowser injury/tier loss retained. Not complete arsenal/source geometry/audio/movie.')
    mm=next(q for q in j['roster']if q['character']==1)
    mm['additional_D_complete_route_root_review']=dict(path='build/verification/root49-megaman-d-full-review-bc.json',sha256=sha(V/'root49-megaman-d-full-review-bc.json'),scope='Frozen D/Easy/MMC3 only,28951physical frames,zero deaths,25actual2-3 controls40to61. Observed basic shots/charge≤5/no dash; full arsenal, currentF and final media pending.')
    samus=next(q for q in j['roster']if q['character']==2)
    samus['additional_current_F_progress']=dict(references={n:sha(V/n)for n in ['root49-samus-f-progress-review-bc.json','root49-samus-f-later-review-bg.json']},scope='T clears1-1..2-1 and enters2-2 at28513, dies29733 toGrey1. Actual four additional pipe plant beam defeats, real supported pipe jump. Not a full clear.',
      newer_V_quarantined='V coral jump29923..29931 produces actual14/16px X steps and Y185→192; this is unexplained invalid motion requiring coordinate-writer diagnosis. Do not admit V as valid progress or evade it via controller changes.',complete=False)
    samus['current_F_Hard_seeded_components']=dict(passive_adoption_sha256=sha(V/'root49-current-f-samus-passives-bc/adoption-e.json'),other_component_review_sha256=sha(V/'root49-current-f-samus-components-bd/review.json'),
      scope='First Ice freezes withoutdamage/lazy0; second actual shot thaws75to35; native frozen platform/noinjury; authored Screw contact protection/defeat. Bothmaps: forced-roll missile world-ammo recovery, weapon OAM slot admission and authored sound channel output/restoration. Each fixture retains explicit authored-state limitations; not natural acquisition/full arsenal.',complete=False)
    j['performance_progress']=dict(real_partial_route_profile_sha256=sha(V/'root49-samus-f-real-lag-profile-bd.json'),actual_exclusive_profile_sha256=sha(V/'root49-samus-f-exclusive-profile-review-bl.json'),
      scope='Measured real Samus F lag and exact14850-frame passive replay CPU scopes; child IRQ/NMI work excluded by actual nesting depth, exact RAM farcall continuation bound. New optimization still required.',complete=False)
    assert len(j['roster'])==14 and sum(len(q['inventory_2_02'])for q in j['roster'])==66
    assert {q['name']for q in j['roster']if q['current_working_F_full_clear_candidates']}=={'Sophia','Bill'}
    j.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),global_cap_bytes=80000000000,global_allocation_sha256=sha(V/'root49-global-allocation-bm.json'),
      completion_scope='Current F complete independently verified Easy/MMC3 routes: Sophia and Bill only. Earlier D MegaMan newly admitted with original scope. All14identities,66inventory entries, source behaviors/lag, original1-1 shortcut/nonshortcut/everyenemy/item requirements and all retained final recordings remain required.',goal_complete=False)
    out.write_text(json.dumps(j,indent=2)+'\n');print('INCOMPLETE_FULL_GOAL_INDEX',sha(out),flush=True)
if __name__=='__main__':main()
