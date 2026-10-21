"""Credit scoped attack work while preserving every missing final-goal requirement."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=V/'root49-goal-coverage-az.json';assert not out.exists()
    old=V/'root49-goal-coverage-ay.json';assert sha(old)=='ed41c919651049f297488fa6c11b1242d67717bedc39674b3c7e7a567fde3bed'
    result=json.loads(old.read_text());cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    result['checkpoints']['F']=dict(path=str(cp.relative_to(R)),sha256=sha(cp),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in c['builds']})
    result['current_working_revision']='F'
    images={h:(revision,mapper)for revision,c in result['checkpoints'].items()for mapper,h in c['ROMs'].items()};admitted={}
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
        q['current_working_F_full_clear_candidates']=[x for x in q['pinned_full_clear_candidates']if x['revision']=='F']
        assert not q['base_moves_and_power_tiers_complete']and not q['all_specials_upgrades_complete']and not q['final_recording_complete']and not q['overall_complete']
    samus=next(q for q in result['roster']if q['character']==2)
    ice=next(q for q in samus['inventory_2_02']if q['name']=='ICE')
    ice['scoped_verified_components']=dict(revision='F',mappers=['mmc3','mmc5'],
      evidence_kind='Initial-state native scenarios with controller-created shots plus exact compiled source/order/ABI oracles; not ordinary item acquisition.',
      components=['Freeze/thaw/invulnerability/pierce/damage order and360 completed-update STOP.',
        'Actual cannon suppression, expiry/resume, defeated/absent cleanup and beam pool cleanup.',
        'Source NSF24 hit cue trigger/no-retrigger/release, independent OAM palette lease, NMI/DMA pending ownership.',
        'Measured single-active-leaf speedup with exact full RAM/register/stack/mapper/ordered-write outputs.'],
      references={n:sha(V/n)for n in ['root49-ice-state-review-ay/review.json',
        'root49-freeze-render-fast-f/leaf-review-c.json','root49-freeze-render-fast-f/native-review-e/review.json',
        'root49-freeze-render-fast-f/matched-native-cost-f.json']},
      still_required=['Ordinary pickup/emergence/icon/ownership flow on final image.',
        'Remaining standing/air/water interactions and all relevant enemy source-geometry cases.',
        'Final complete route, decoded movie review and broader lag/regression closure.'])
    run=R/'build/roster-through-2-2/root49-f-samus-route-c-2-v0-mmc3'
    samus['scoped_Easy_intrinsic_attack_progress']=dict(revision='F',mapper='mmc3',
      observed='Ordinary Down morphs, grounded B creates bombs, real bomb boosts occur, both first underground Goombas are removed, bomb pools expire and Up restores grounded nonball control.',
      source_kind='Unseeded ordinary controller route with actual native read-only logs; later death9659 retained.',
      manifest_sha256=sha(run/'manifest.json'),bomb_trace_sha256=sha(run/'first-bombs-c.csv'),
      complete=False,exclusions=['Not Hard Morph item acquisition.','No all-enemy/block/SFX/ammo or full-route/final-media claim.'])
    result.update(script_sha256=sha(__file__),prior_index_sha256=sha(old),
      source_inventory=dict(path='src/inventory_data.inc',sha256=sha(R/'src/inventory_data.inc')),
      new_review_references={n:sha(V/n)for n in ['root49-sophia-d-full-review-az.json',
        'root49-freeze-render-fast-f/native-review-e/review.json','root49-freeze-render-fast-f/matched-native-cost-f.json',
        'root49-freeze-fast-adoption-f/main-smoke/review.json']},
      completion_scope='C/D/E/F successes retain actual image/mapper/identity/mode scope. F is installed with scoped Ice speedup, but no F complete route admitted. All14 identities,66inventory entries, original shortcut/nonshortcut scope and final retained recordings stay required.',goal_complete=False)
    assert len(result['roster'])==14 and sum(len(q['inventory_2_02'])for q in result['roster'])==66
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),current_F_clears=[q['name']for q in result['roster']if q['current_working_F_full_clear_candidates']],identities=14,inventory=66)))
if __name__=='__main__':main()
