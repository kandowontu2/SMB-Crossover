"""Freeze qualified offline FF combat/API, preserving all prior negatives."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v3 as T
from check_tmnt_render_oa import address
C=T.C;sha=T.sha
P=R/'build/final-fantasy-host-combat-v2';O=R/'build/final-fantasy-host-combat-qualified-v2'

def main():
    assert not O.exists();O.mkdir()
    packets=[P/'build-proof.json',R/'build/final-fantasy-host-combat-controls-v3/controls.json',
             R/'build/final-fantasy-host-combat-controls-v4/controls.json',R/'build/final-fantasy-host-combat-controls-v5/controls.json']
    proofs=[json.loads(p.read_text())for p in packets];assert all(p['passed']for p in proofs)
    bindings={}
    for p,d in zip(packets,proofs):
        for path,h in d['bindings'].items():
            assert sha(path)==h,path
            assert bindings.get(path,h)==h,path
            bindings[path]=h
        bindings[str(p.resolve())]=sha(p)
    b=C.bundle(P)
    # Validate every guarded entry's actual stores, independently of RAM
    # snapshots; no PPU/MMIO reads can hide an inactive hardware write.
    guard_cases=[]
    bank=address(b,'CurrentBank')
    allowed={bank,0x5115}|set(range(0x100,0x200))
    for owner in list(range(34))+[255]:
        if owner==22:continue
        for name in ['FfHostFresh','FfHostNewEnemy','FfHostTarget','FfHostDamage','FfHostContact','FfHostWeapons']:
            m=T.make(b);T.put(m,SelectedCharacter=owner,FfReady=119,FfDamage=255,FfAction=1)
            m.writes.clear();T.run(m,name,a=255,x=2,y=167,p=0xf9)
            assert all(a in allowed for a,v in m.writes),(owner,name,[(a,v)for a,v in m.writes if a not in allowed])
            guard_cases.append([owner,name])
    guards=O/'guard-stores.json';guards.write_text(json.dumps(dict(passed=True,cases=len(guard_cases),
        allowed_only='Actual far-call CurrentBank+5115 and page1/SMC/stack. No application or other MMIO writes.',rows=guard_cases),indent=2)+'\n')
    bindings[str(guards.resolve())]=sha(guards)
    k=R/'build/final-fantasy-ram3-kernel-v1';v1=R/'build/final-fantasy-host-combat-v1'
    old,new=(k/'ram3.bin').read_bytes(),(P/'ram3.bin').read_bytes()
    assert new[0xa00:0xa00+3211]==old[0xa00:0xa00+3211]
    assert new[0x275:0x275+20]==old[0x275:0x275+20]
    assert all(a==z for i,(a,z)in enumerate(zip(old,new))if not 0x1700<=i<0x18ec)
    for name in ['art.bin','art.chr']:assert (P/name).read_bytes()==(k/name).read_bytes()==(v1/name).read_bytes()
    pixel=R/'build/final-fantasy-current-component-v2/cpu-controls-v1/controls.json'
    d=json.loads(pixel.read_text());assert d['passed']and d['rendered_entry_facing_shadow_cases']==632
    for path,h in d['bindings'].items():assert sha(path)==h,path
    bindings.update(d['bindings']);bindings[str(pixel.resolve())]=sha(pixel)
    negatives=[R/'build/final-fantasy-host-combat-controls-v1/controls.json',
               R/'build/final-fantasy-host-combat-controls-v2/controls.json']
    for p in negatives:
        z=json.loads(p.read_text());assert not z['passed']
        for path,h in z['bindings'].items():assert sha(path)==h,path
        bindings.update(z['bindings']);bindings[str(p.resolve())]=sha(p)
    notes=dict(v1_product_negative='Actual foreign FfHostFresh stores FfReady119->0 for7different tags. Fixed only in private v2 with an8-byte owner guard.',
        fixture_negatives=['RAM snapshots read2007 and advance its buffered-read state; proven first diff is the2007 byte. Corrected by comparing actual RAM separately from MMIO plus strict inactive store classification.',
                           'Reuse expected Goomba100HP, but genuine2.02 table gives75HP. Corrected surviving same-ID test uses actual White25damage and expects50HP.',
                           'Timeline actors originally sat outside the actual half-open native/source hitboxes. Corrected only typed actor positions, preserving all source behavior/assertions.'],
        synthetic_pool_stress='Three simultaneous White-light records test bounded source-pool/identity consumption only. Not naturally admitted by the30prepare/23life timelines and not performance/cadence evidence.')
    notespath=O/'retained-negatives.json';notespath.write_text(json.dumps(notes,indent=2)+'\n');bindings[str(notespath.resolve())]=sha(notespath)
    for p in [Path(__file__),R/'tools/audit/prepare_ff_host_combat_v2.py',R/'tools/audit/ff_host_combat_controls_v2.py',
              R/'tools/audit/ff_host_combat_probe_v3.py']:
        bindings[str(p.resolve())]=sha(p)
    entries={n:dict(virtual_PC=f'{address(b,n):04X}',raw_A=3)for n in
             ['FfHostTarget','FfHostDamage','FfHostContact','FfHostWeapons','FfHostNewEnemy','FfHostFresh']}
    api={
      'FfHostWeapons':'Public once-per-active-logical-update consumer: selected22+engine8+pausebit0clear+TimerControl0+MmDeathFlag0. Calls actual FfWeapons once, then each eligible native actor receives source melee and actual slots0/12/24. Dead native actors are excluded from later hits. A/X/Y/N/Z/C volatile; original caller must supply source movement/action tick first. No input/resource ownership.',
      'FfHostTarget':'Typed Xnative0..5. Cset gives genuine inclusive native BoundBoxCtrlData converted to half-open world X/page/Y/width/height. Signed left offsets, page carry, eligibility and below-screen top overflow qualified. X retained; A/Y/N/Z/C volatile. Scratch source fields are outputs.',
      'FfHostContact':'Internal active-combat call: A=FFmelee or0/12/24source projectile, Xeligible native identity. Cset after accepted nonimmune damage, source masks own repeated contact admission. X retained; A/Y/flags volatile. Preserves normal native ObjectOffset on defeat.',
      'FfHostDamage':'Internal typed accepted-source-damage consumer. Selected22/X0..5/FfDamage nonzero guarded; caller must provide active eligible target and current source receipt. Not an independent pause/eligibility service. Actual16-bit native HP,202table,600/900/1100Bowser, default armor; genuine ShellOrBlockDefeat/HandleEnemyFBallCol and later native deferred score consumption qualified.',
      'FfHostNewEnemy':'Typed genuine new native identity callback, including same-ID reuse. Run after actual native CheckpointEnemyID HP/flash reset; not by observing ID changes each frame. Complete A/X/Y/P preserved for all64live flag combinations, including foreign/invalidX. Source per-action/per-projectile hit masks clear only that identity. This source callback is not installed in a cart yet.',
      'FfHostFresh':'Public new-game selected-owner constructor. Own22 resets genuine source life/progression/phase state while retaining selected menu class. A/X/Y/N/Z/C volatile on own path; V/D/I retained. Foreign paths perform no application/MMIO stores, X/Y+V/D/I retained; A/N/Z/C volatile.'}
    h=dict(passed=True,status='OFFLINE_FF_COMBAT_COMPONENT_CPU_QUALIFIED_WITH_EXPLICIT_INTEGRATION_GAPS',
        native=False,full_Main=False,loader=False,resource_grant=False,shared_or_Downloads_changed=False,
        image=str((P/'ram3.bin').resolve()),image_sha256=sha(P/'ram3.bin'),
        original_v1_image_sha256=sha(v1/'ram3.bin'),virtual_A='rawRAM3 A000..<C000',host_combat='B700..<B8EC',
        host_combat_bytes=492,added_bytes_over_v1=8,added_state_bytes=0,
        original_CORE_ART_CHR='3211BsourceCORE/20Bnativepublisher/3410BART/32768BCHR byteexact.',
        genuine_parent=str((C.E.P/'candidate.nes').resolve()),parent_ROM_sha256=sha(C.E.P/'candidate.nes'),
        entries=entries,API=api,
        counts=dict(native_geometry=3087,HP=1092,native_defeats=256,melee_contacts=864,spell_contacts=1080,
                    native_source_edges=1496,reuse_APXY64=384,reuse_foreign=1536,fresh_own=256,fresh_foreign=384,
                    real_movement_action_sequences=7,empty_field_source_tick_pairs=96,source_bytes_per_pair=143,
                    native_defeat_indices_APXY64=9216,real_vector_interrupts=1062,actual_score_digit_cases=48,
                    lower_foreign_guards=4608,invalid_reuse_APXY64=192,inactive_actual_store_cases=len(guard_cases),
                    inherited_unchanged_pixel_cases=632,inherited_genuine_OAM_chunks=1328),
        remaining=[
          'No cartridge header, resource lease, CHRcarrier, loader, shared hook or character admission. Parent root owns integration. Actual hook route coverage and completeMain/native later required.',
          'One actual owner must age surviving native MmEnemyFlash2 per active update and route native FF enemy flash visuals; current component publishes2 but does not age it, and current renderer has no FF flash owner. Observed2,2,2,2 retained.',
          'SourceSFX queues are qualified through native consumers. Audio/NMI installation, themes/APU waveform, host render/palette/terrain/items/death/scene and per-player progression integration remain separate acceptance work.',
          'Standalone typed Damage/Contact are internal active-eligible services; only public Weapons applies pause/engine/death guards. Callers must retain this distinction.',
          'No fullMain frame budget or native cadence claim. ThreeWhite pool stress is synthetic; native actor fields/typed ground inputs do not prove natural terrain/admission reachability.',
          'Inherited632pixel/1328nativeOAM proofs are reused only because complete original CORE/ART/CHR/publisher bytes and all evidence bindings are exact; no new native RGB/render integration claim.'
        ],bindings=bindings)
    out=O/'handoff.json';out.write_text(json.dumps(h,indent=2)+'\n')
    for p,v in bindings.items():assert sha(p)==v,p
    print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(bindings),image_sha256=h['image_sha256'])))
if __name__=='__main__':main()
