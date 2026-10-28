"""Finite full-caller/OAM/IRQ/pixel-mask controls for the private Bill anchor."""
from pathlib import Path
import ast,collections,itertools,json,statistics
from check_tmnt_render_oa import address,location,Memory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from final_bill_lance_hard_gallery_source_v2 import BillArena
from final_bill_lance_hard_gallery_source_v1 import OWNER_NAMES,EXTRA_OWNERS
from samus_hud_icon_controls_v1 import setup as foreign_setup,run as observed_run,execute,pixel
from final_item_matrix import ROSTER
from verify_native_relocation import NesMPU
from current_bill_capsule_hud_candidate_v1 import R,B,P,BASE,EXPECTED,sha,put


def helpers():
    path=R/'tools/audit/bill_capsule_hud_controls_v4.py';tree=ast.parse(path.read_text())
    body=[q for q in tree.body if isinstance(q,ast.FunctionDef)and q.name in ['setup','run']]
    assert len(body)==2
    ns=dict(BillArena=BillArena,NesMPU=NesMPU,address=address,location=location)
    exec(compile(ast.Module(body=body,type_ignores=[]),str(path)+'::two-functions','exec'),ns)
    return ns


def compare(old,new,make,turns=1):
    qs=[make(b)for b in [old,new]];history={};coord=False;rows=[]
    for turn in range(turns):
        results=[observed_run(q)for q in qs]
        oc,ow,oe=results[0];nc,nw,ne=results[1]
        target=qs[0].get('SelectedCharacter')==3
        assert [oc.a,oc.x,oc.y,oc.p,oc.sp]==[nc.a,nc.x,nc.y,nc.p,nc.sp]
        assert qs[0].m.banks==qs[1].m.banks
        wanted=[]
        for at,v,index in ow:
            if target and index==20:
                if at%4==0:v=(v-8)&255
                elif at%4==3:v=(v-72)&255
            wanted.append((at,v,index))
        assert nw==wanted,('All ordered OAM',target,turn)
        for a,z in zip(oe,ne):
            want=dict(a)
            if target and a['index']==20:want.update(x=120,y=16)
            assert z==want
        assert len(oe)==len(ne)
        history.update({at:v for at,v,index in wanted})
        coord=coord or(target and any(x['index']==20 for x in oe))
        expected=list(qs[0].m[:0x8000])
        for at,v in history.items():expected[at]=v
        if target:
            for name,amount in [('R4',72),('R6',8)]:
                at=address(old,name)
                if expected[at]!=qs[1].m[at]:
                    assert qs[1].m[at]==(expected[at]-amount)&255,(name,expected[at],qs[1].m[at])
                    expected[at]=qs[1].m[at]
        assert expected==list(qs[1].m[:0x8000]),('Full RAM/live stack/SMC',target,turn)
        rows.append(dict(turn=turn,old_cycles=oc.processorCycles,new_cycles=nc.processorCycles,delta=nc.processorCycles-oc.processorCycles,
            HUD_render_entries=sum(e['index']==20 for e in ne),actual_HUD_OAM_stores=sum(i==20 for at,v,i in nw),
            all_other_OAM_regs_banks_flat_RAM_exact=True))
    return rows


def main():
    out=B/(P+'_controls.json');assert not out.exists()
    old,new=scoped_load(BASE),scoped_load(B/(P+'.nes'))
    build=json.loads((B/(P+'_build.json')).read_text());assert build['passed']and sha(BASE)==EXPECTED and sha(B/(P+'.nes'))==build['candidate_sha256']
    for n in EXTRA_OWNERS:
        if n not in OWNER_NAMES:OWNER_NAMES.append(n)
    H=helpers();rows=[]
    # All legal capsules, both faces/identities/modes. Initial state is typed
    # CPU setup with genuine InventoryCollect consumers, not native acquisition.
    for mode,variant,item,face in itertools.product([0,1],[0,1],range(7),[1,2]):
        def make(b):
            q=H['setup'](b,variant=variant,item=0,face=face)
            if item==6:q.grant(1)
            if item:q.grant(item)
            q.put(CrossoverBehaviorVersion=mode)
            return q
        result=compare(old,new,make,turns=2)
        rows.append(dict(mode=mode,variant=variant,item=item,face=face,turns=result,
            acquisition_scope='Genuine Hard InventoryCollect consumer before renderer checks; mode0 with selected capsule is synthetic geometry only. Classic Easy rejects2.02 gun collection.'))
    edge=[]
    for item,mixed,offset,rotate in itertools.product([2,3,4],[False,True],[0,236,244,248],[False,True]):
        def make(b):
            q=H['setup'](b,item=item,mixed=mixed,rotation=rotate)
            q.put(CurrentOAMOffset=offset)
            return q
        edge.append(dict(item=item,mixed=mixed,offset=offset,rotation=rotate,turns=compare(old,new,make,turns=2)))
    foreign=[]
    for name,slot,char,variant,value,family in ROSTER:
        if char==3:continue
        for selected in [0,1]:
            def make(b):
                q=foreign_setup(b,char,selected)
                if variant:q.set(variant,value)
                return q
            foreign.append(dict(identity=name,selected=selected,turns=compare(old,new,make)))
    samus=[]
    for selected,mixed,offset,rotate in itertools.product([1,2,3,7],[False,True],[0,236,244],[False,True]):
        samus.append(dict(selected=selected,mixed=mixed,offset=offset,rotation=rotate,
            turns=compare(old,new,lambda b:foreign_setup(b,2,selected,offset,rotate,mixed))))
    # Original record bytes, full original masks and all emitted parts; Y=1
    # is accepted by native high-page clipping, so no top part is sacrificed.
    masks=[]
    for selected in range(1,7):
        a=new['raw'][location(new,'RemainingDraw::PickupArts')+8+selected]
        ptr=new['raw'][location(new,'AvArtRightLo')+a]+256*new['raw'][location(new,'AvArtRightHi')+a]
        bank=new['raw'][location(new,'AvArtBanks')+a]&127;at=16+bank*8192+ptr%8192;rec=new['raw'][at:at+new['raw'][at]+1]
        family=new['raw'][location(new,'AvArtFamilies')+a];page=new['raw'][location(new,'AvPhysicalBanks')+family]|1
        opaque={};original={};parts=[]
        for i in range(1,len(rec),4):
            tile,attr,dy,dx=rec[i:i+4];dx=dx-256 if dx>=128 else dx;dy=dy-256 if dy>=128 else dy
            parts.append([120+dx,16+dy,tile,attr])
            for y in range(16):
                for x in range(8):
                    v=pixel(new['raw'],page,tile,attr,x,y)
                    if v:opaque[120+dx+x,17+dy+y]=v;original[192+dx+x,25+dy+y]=v
        assert opaque=={(x-72,y-8):v for (x,y),v in original.items()}
        assert all(0<=x<256 and 0<=y<240 for x,y in opaque)
        assert len(parts)==3 and {p[1]for p in parts}=={1}
        # Entire sprite rectangles, hence every glyph pixel at any digit value,
        # are separated from these exact native/InventoryHud occupied cells.
        occupied=[('weapon name',24,8,79,15),('player name',24,16,79,23),('WORLD/TIME',144,16,231,23),
            ('max score',16,24,71,31),('coin tally/icon',88,24,119,31),('world value',152,24,175,31),('timer',208,24,231,31)]
        for label,x0,y0,x1,y1 in occupied:assert not any(x0<=x<=x1 and y0<=y<=y1 for x,y in opaque),label
        masks.append(dict(selected=selected,art=a,record=list(rec),page=page,parts=parts,full_opaque_mask_pixels=len(opaque),
            opaque_bounds=[min(x for x,y in opaque),min(y for x,y in opaque),max(x for x,y in opaque),max(y for x,y in opaque)],
            full_original_mask_preserved=True,occupied_glyph_cells_disjoint=occupied,
            inventory_ammo='Actual Bill InvAmmoIndex=$FF => the upper-row ammo cells are blanks for every legal gun; no digit is hidden.'))
    # Actual advanced-family arbitration is deliberately unchanged. Demonstrate
    # continued draws rather than infer a permanent missing icon from a still.
    arbitration=[]
    for item in [2,3]:
        q=H['setup'](new,item=item)
        turns=[]
        for tick in range(8):
            _,writes,entries=observed_run(q)
            turns.append(dict(draw=tick,BillDrawTurn=q.get('BillDrawTurn'),HUD=sum(e['index']==20 for e in entries),
                shot_entries=sum(e['index']<10 for e in entries),physical=q.get('SsChrPhysical'),active=q.get('SsChrActive')))
            q.put(CurrentOAMOffset=0)
        assert [bool(z['HUD'])for z in turns]==[True,False]*4,turns
        arbitration.append(dict(item=item,turns=turns,always_visible_HUD=False,
            scope='Actual compiled BillEndDrawPriority + RemainingDraw calls; no source ticks advanced, native phase not reconstructed. Shot family233 and capsule family221 alternate; placement alone cannot remove that flicker.'))
    irqs=[]
    for char,item in [(3,4),(2,1),(2,2)]:
        q=H['setup'](new,item=item)if char==3 else foreign_setup(new,char,item)
        q.m.page(1,61);q.set('CurrentBank',189);image=list(q.m);banks=q.m.banks[:]
        def fresh():
            m=Memory(new);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
        m=fresh();cpu,trace=execute(new,m,'RemainingDraw',record=True)
        start=address(new,'BillCapsuleHudAnchor')
        keys=sorted({(pc,k)for pc,k in trace if k==61 and(start<=pc<start+18 or address(new,'SamusFixedMissileHud')<=pc<address(new,'SamusFixedHudRecord'))})
        def state(m,c):
            return ([c.a,c.x,c.y,c.p&207,c.sp],bytes(m[:0x1c0]+m[0x200:0x800]+m[0x6000:0x8000]),m.banks,
                [w for i,w in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=w[0]<512])
        expected=state(m,cpu)
        for key in keys:
            m=fresh();after,_=execute(new,m,'RemainingDraw',inject=key)
            assert state(m,after)==expected,(char,item,key)
            assert after.processorCycles-cpu.processorCycles==120
        irqs.append(dict(char=char,item=item,actual_hardware_vector_boundaries=keys,IRQ_extra_cycles=120))
    allrows=[t for q in rows+edge+foreign+samus for t in q['turns']]
    result=dict(passed=True,source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(B/(P+'.nes')),
        Bill_cells=len(rows),Bill_and_edge_full_calls=2*sum(len(q['turns'])for q in rows+edge),Bill_rows=rows,edge_cases=edge,
        foreign=foreign,Samus_missile_and_foreign= samus,all_capsule_masks=masks,
        complete_caller_contract='AXYP/SP, mapper banks, ordered full OAM stores/part counts, entire flatRAM including stack/5SMC equal except actual Bill HUD X-72/Y-8 stores and their final coordinate scratch. No masks on unrelated state.',
        cost=dict(min=min(z['delta']for z in allrows),max=max(z['delta']for z in allrows),mean=statistics.mean(z['delta']for z in allrows),
            Bill_HUD_per_call=21,foreign_selected_HUD_per_call=12,Samus_fixed_missile=0,no_selected_HUD=0,
            scope='Measured complete RemainingDraw CPU deltas. No NMI/audio code changes; foreground pressure remains subject to actual strict native checks, no zero-lag claim.'),
        actual_IRQ_boundaries=sum(len(q['actual_hardware_vector_boundaries'])for q in irqs),IRQ=irqs,
        advanced_HUD_intermittency=arbitration,remaining_visual_limit='Laser/Flare HUD is intentionally rejected on the alternate shot-family turn; this preexisting shared-family scheduling remains. No always-visible-HUD claim. No eight-sprite airborne-body/campaign/all-pixels native claim.',
        bindings={str(p):sha(p)for p in [Path(__file__).resolve(),BASE,BASE.with_suffix('.dbg'),B/(P+'.nes'),B/(P+'.dbg'),B/(P+'_build.json'),R/'src/screen_render.s',R/'src/bill_native_rare.s',R/'src/inventory.s',R/'src/metasprite_engine.s',R/'tools/audit/bill_capsule_hud_controls_v4.py',R/'tools/audit/samus_hud_icon_controls_v1.py']})
    put(out,result);print(json.dumps(dict(passed=True,sha256=sha(out),Bill_cells=len(rows),source_full_calls=2*len(allrows),IRQ=result['actual_IRQ_boundaries'],cost=result['cost'])))


if __name__=='__main__':main()
