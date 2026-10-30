"""Freeze the read-only FF FX audit, retained negatives and action witnesses."""
from pathlib import Path
import collections, hashlib, itertools, json, sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_palette_audit_v2 as A
H=A.H
O=R/'build/ff-fx-palette-closure-v1'
sha=A.sha


def main():
    O.mkdir(exist_ok=False)
    b=H.C.qualified(H.O/'candidate.nes')
    assert sha(H.O/'candidate.nes')==A.EXPECTED
    root=json.loads((A.P/'source-closure.json').read_text())
    primary=json.loads((R/'build/ff-fx-palette-audit-v2/audit.json').read_text())
    masks=json.loads((R/'build/ff-fx-mask-feasibility-v2/audit.json').read_text())
    for proof in [primary,masks]:
        assert proof['passed']
        for f,h in proof['bindings'].items():assert sha(f)==h,f
    source_bindings={}
    for f in primary['bindings']:
        if f in root['bindings']:
            assert sha(f)==root['bindings'][f],f
            source_bindings[f]=root['bindings'][f]
    assert len(source_bindings)>=10
    witnesses={}
    for kind,keys in [('Bolt',72),('Ice',68)]:
        trace=A.action_trace(b,2,{0:64,31:128,32:64,63:128,64:keys},count=130,start_x=0)
        full=[r for r in trace if sorted(k for k,frame in r['shots'])==[1,1,2 if kind=='Bolt' else 3]]
        assert full,kind
        witnesses[kind]=dict(input_pulses={0:64,31:128,32:64,63:128,64:keys},
            initial_player_x=0,real_source_two_Fire_plus_nonFire_ticks=[r['tick']for r in full],trace=trace)
    donor_rows={'Red':[0x16,0x30,0x36],'Blue':[0x28,0x18,0x21],
        'GuestPhase2':[0x1a,0x27,0x30],'GuestPhase3':[0x16,0x27,0x30],'GuestPhase4':[0x0f,0x24,0x30]}
    needs={'Sword':[0x0c,0x1c,0x2c],'FireIce':[0x16,0x26,0x30,0x12,0x21],
        'FireBolt':[0x16,0x26,0x30,0x18,0x28],'WhiteLight':[0x12,0x21,0x30]}
    allocation=[]
    for family,p0_name,area,ink in itertools.product(needs,donor_rows,range(4),[0,1]):
        # Cross-product intentionally includes body phases, not claims that a
        # class can legally change into another while retaining projectiles.
        p3=primary['world']['native_area_P3_visible'][str(area)]
        wanted=set(needs[family])|({0x0f}if ink else set())
        donors=set(donor_rows[p0_name]+[0x16,0x30,0x27]+p3)
        missing=sorted(wanted-donors)
        allocation.append(dict(family=family,P0=p0_name,area=area,optional_opaque_ink=ink,
            new_P1_colors=missing,one_P1_row_color_feasible=len(missing)<=3))
    out=dict(passed=True,native=False,admitted=False,source_cart=A.EXPECTED,
      additional_legal_witnesses=witnesses,donor_color_feasibility=allocation,
      source_binding_matches=len(source_bindings),source_bindings=source_bindings,
      completed_source_controls=dict(actual_iterator_cases=632,actual_iterator_chunks=1328,
        all_reachable_nonFire_animation_phases=27,actual_native_palette_packet_cases=5,
        actual_native_world_OAM_objects=8,lossless_regridded_masks=1792),
      negatives_retained=[str(R/'build/ff-fx-palette-audit-v1/negative-v1.json'),
         str(R/'build/ff-fx-mask-feasibility-v1/negative-v1.json')],
      limits=['No native execution, cart or root source changes, new allocations, palette implementation or admission.',
        'Fixed-class declared CPU action fixtures supply floor contact after each movement; not a campaign.',
        'Mask color/pixel feasibility is separate from existing1KBwindow/64OAM/eight-sprite and world-priority feasibility.',
        'P0 guest phase cross-product is disclosed donor analysis, not new source animation or legal class-switch evidence.'])
    paths=[Path(__file__),Path(A.__file__),R/'tools/audit/ff_fx_palette_audit_v1.py',
      R/'tools/audit/ff_fx_mask_feasibility_v1.py',R/'tools/audit/ff_fx_mask_feasibility_v2.py',
      A.P/'source-closure.json',R/'build/ff-fx-palette-audit-v2/audit.json',
      R/'build/ff-fx-mask-feasibility-v2/audit.json',
      R/'build/ff-fx-palette-audit-v1/negative-v1.json',R/'build/ff-fx-mask-feasibility-v1/negative-v1.json',
      R/'tools/reference/final_fantasy_host_palette_v2.s']
    out['bindings']={str(f.resolve()):sha(f)for f in paths}
    p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,source_matches=len(source_bindings),path=str(p),sha256=sha(p),
       additional_coexistence={k:v['real_source_two_Fire_plus_nonFire_ticks']for k,v in witnesses.items()})),flush=True)


if __name__=='__main__':main()
