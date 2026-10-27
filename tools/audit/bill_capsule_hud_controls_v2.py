"""Actual compiled RemainingDraw, art bounds, live-state and IRQ controls."""
from pathlib import Path
import argparse,itertools,json,statistics,traceback
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,PARENT,sha,put,OWNER_NAMES,EXTRA_OWNERS
from final_bill_lance_hard_gallery_source_v2 import BillArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU
from smb3_host_current3b_boundaries_v2 import execute
from final_item_matrix import ROSTER


def setup(b,char=3,variant=0,item=4,face=1,mixed=False,rotation=False):
    q=BillArena(b,variant)
    if char==3:
        if item:q.grant(item)
        q.put(PlayerFacingDir=face,Player_MovingDir=face)
        if item in [2,3]:q.buttons(64)
    else:q.put(SelectedCharacter=char);q.set('InvSelected',item,char)
    q.put(AvDrawIndex=20,CurrentOAMOffset=0,GuestOamRotationActive=int(rotation),RgOamRotation=11 if rotation else 0)
    if mixed:
        for n,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('Enemy_X_Position',200),('Enemy_PageLoc',0),('Enemy_Y_Position',160),('Enemy_Y_HighPos',1),('InvPickupOwner',char),('InvPickup',4)]:q.set(n,v,5)
    return q


def run(q):
    original=NesMPU.step;records=[];coords=[];entries=[];b=q.b
    code=bytes([0xa9,192,0x85,address(b,'R4'),0xa9,0,0x85,address(b,'R5'),0x85,address(b,'R3'),0xa9,24,0x85,address(b,'R6')])
    if 'BillHudAnchor'in b['syms']:
        code=bytes([0x20,address(b,'BillHudAnchor')&255,address(b,'BillHudAnchor')>>8,0x85,address(b,'R4'),0xa9,0,0x85,address(b,'R5'),0x85,address(b,'R3'),0x84,address(b,'R6'),0xea])
    start=location(b,'RemainingDraw::Hud');data=b['raw'][start:location(b,'RemainingDraw::Draw')]
    assert data.count(code)==1
    block=address(b,'RemainingDraw::Hud')+data.index(code)
    def step(c):
        bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        index=q.get('AvDrawIndex');before=len(q.m.writes)
        if c.pc==block+14 and bank==61:coords.append(dict(x=q.get('R4'),y=q.get('R6'),A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp))
        if c.pc==address(b,'MetaspriteRenderLoop') and bank==(location(b,'MetaspriteRenderLoop')-16)//8192:
            entries.append(dict(index=index,pointer=q.get('R0')+256*q.get('R1'),Cbank=q.m.banks[2],x=q.get('R4'),y=q.get('R6'),offset=q.get('CurrentOAMOffset')))
        original(c)
        records.extend(dict(address=at,value=v,index=index)for at,v in q.m.writes[before:]if 0x200<=at<0x300)
    NesMPU.step=step
    try:c,_=q.invoke('RemainingDraw')
    finally:NesMPU.step=original
    return c,records,coords,entries


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    try:
        assert sha(PARENT/'candidate.nes')==SHA
        old=scoped_load(PARENT/'candidate.nes');new=scoped_load(a.packet/'candidate.nes');layout=json.loads((a.packet/'layout.json').read_text());assert layout['passed']
        for n in EXTRA_OWNERS:
            if n not in OWNER_NAMES:OWNER_NAMES.append(n)
        rows=[];deltas=[];allcoords=0;allarts=0
        scenarios=list(itertools.product([0,1],[0,2,3,4,5],[1,2],[False,True],[False,True]))
        for variant,item,face,mixed,rotation in scenarios:
            qs=[setup(b,variant=variant,item=item,face=face,mixed=mixed,rotation=rotation)for b in [old,new]]
            turns=[]
            for turn in range(4):
                outcomes=[run(q)for q in qs];oc,ow,ob,oe=outcomes[0];nc,nw,nb,ne=outcomes[1]
                assert (oc.a,oc.x,oc.y,oc.p,oc.sp)==(nc.a,nc.x,nc.y,nc.p,nc.sp)
                assert qs[0].m.banks==qs[1].m.banks
                assert len(ow)==len(nw) and len(oe)==len(ne) and len(ob)==len(nb)
                expected=[]
                for w in ow:
                    z=dict(w)
                    if w['index']==20:
                        if w['address']%4==0:z['value']=(z['value']-8)&255
                        elif w['address']%4==3:z['value']=(z['value']-80)&255
                    expected.append(z)
                assert nw==expected,('ordered native OAM',variant,item,face,mixed,rotation,turn)
                for o,n in zip(oe,ne):
                    expected_render=dict(o)
                    if o['index']==20:expected_render.update(x=o['x']-80,y=o['y']-8)
                    assert n==expected_render
                for o,n in zip(ob,nb):
                    assert (o['x'],o['y'],n['x'],n['y'])==(192,24,112,16)
                    assert (o['X'],o['SP'],o['P']&0xcd)==(n['X'],n['SP'],n['P']&0xcd)
                allcoords+=len(nb);allarts+=sum(e['index']==20 for e in ne)
                memory=list(qs[0].m[:0x8000])
                for w in expected:memory[w['address']]=w['value']
                if nb:
                    # Only the producer's final coordinate scratch is allowed
                    # to remain different. Every other flat byte, stack and all
                    # five SMC fields are compared without a mask.
                    for name,amount in [('R4',80),('R6',8)]:
                        at=address(old,name)
                        if memory[at]!=qs[1].m[at]:
                            assert qs[1].m[at]==(memory[at]-amount)&255
                            memory[at]=qs[1].m[at]
                assert memory==list(qs[1].m[:0x8000]),('full flat RAM/stack/SMC',variant,item,face,mixed,rotation,turn)
                delta=nc.processorCycles-oc.processorCycles;assert delta==30*len(nb),(delta,len(nb))
                deltas.append(delta);turns.append(dict(turn=turn,old_cycles=oc.processorCycles,new_cycles=nc.processorCycles,delta=delta,HUD_producers=len(nb),HUD_render_entries=sum(e['index']==20 for e in ne),actual_OAM_stores=len(nw)))
            rows.append(dict(variant=variant,item=item,face=face,mixed=mixed,rotation=rotation,turns=turns))
        foreign=[]
        for name,slot,char,variant,value,family in ROSTER:
            if char==3:continue
            for selected in [0,1]:
                qs=[setup(b,char=char,item=selected)for b in [old,new]]
                if variant:
                    for q in qs:q.set(variant,value)
                outcomes=[run(q)for q in qs];oc,ow,ob,oe=outcomes[0];nc,nw,nb,ne=outcomes[1]
                assert (oc.a,oc.x,oc.y,oc.p,oc.sp)==(nc.a,nc.x,nc.y,nc.p,nc.sp)
                assert ow==nw and oe==ne and list(qs[0].m[:0x8000])==list(qs[1].m[:0x8000]) and qs[0].m.banks==qs[1].m.banks
                assert [(z['x'],z['y'])for z in nb]==[(192,24)]*len(nb)
                assert nc.processorCycles-oc.processorCycles==29*len(nb)
                foreign.append(dict(identity=name,char=char,selected=selected,old_cycles=oc.processorCycles,new_cycles=nc.processorCycles,delta=nc.processorCycles-oc.processorCycles,HUD_producers=len(nb),entire_output_state_and_OAM_exact=True))
        helper=[]
        for char,flags,x in itertools.product([0,2,3,4,11,17],[0x20,0x21,0x22,0x60,0x28,0xa0,0xe3,0xef],[0,217]):
            m=Memory(new);m.page(1,61);m[address(new,'SelectedCharacter')]=char
            c=NesMPU(memory=m,pc=address(new,'BillHudAnchor'));c.a=59;c.x=x;c.y=173;c.p=flags;c.sp=253;c.stPushWord(0x5aff)
            for _ in range(50):
                if c.pc==0x5b00:break
                c.step()
            assert c.pc==0x5b00 and c.sp==253 and c.x==x and c.p&0xcf==flags&0xcf
            assert(c.a,c.y)==((112,16)if char==3 else(192,24))
            helper.append(dict(char=char,flags=flags,X=x,cycles=c.processorCycles))
        bounds=[]
        for item in range(1,7):
            art=new['raw'][location(new,'RemainingDraw::PickupArts')+8+item]
            ptr=new['raw'][location(new,'AvArtRightLo')+art]+256*new['raw'][location(new,'AvArtRightHi')+art]
            bank=new['raw'][location(new,'AvArtBanks')+art]&127;at=16+8192*bank+ptr%8192;size=new['raw'][at]
            assert size==12;record=list(new['raw'][at:at+size+1]);xs=[112+(record[k]-256 if record[k]>127 else record[k])for k in [4,8,12]];ys=[16+(record[k]-256 if record[k]>127 else record[k])for k in [3,7,11]]
            assert sorted(xs)==[100,108,116] and set(ys)=={1}
            bounds.append(dict(item=item,art=art,bank=bank,pointer=ptr,record=record,OAM_bounds=[min(xs),min(ys),max(xs)+7,max(ys)+15],visible_pixel_bounds=[100,2,123,17],max_weapon_name_x=79,coin_row_y=24,WORLD_begin_x=144))
        # Hardware-vector IRQ at every reached changed instruction in a full
        # real RemainingDraw continuation. Only IRQ-tagged writes are excluded
        # from the ordered main bus, never an ordinary source store.
        irqs=[]
        for char,item in [(3,4),(2,1)]:
            q=setup(new,char=char,item=item);q.m.page(1,61);q.set('CurrentBank',189)
            image=list(q.m);banks=q.m.banks[:]
            def fresh():
                m=Memory(new);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
            base=fresh();c,trace=execute(new,base,'RemainingDraw',record=True)
            block=address(new,'RemainingDraw::Hud')+0x21
            keys=sorted({(pc,bank)for pc,bank in trace if bank==61 and(address(new,'BillHudAnchor')<=pc<address(new,'BillHudAnchor')+20 or address(new,'RemainingDraw::Hud')<=pc<address(new,'RemainingDraw::Draw')+6 or pc==address(new,'RemainingDraw::ArtPointer'))})
            assert keys
            raw=lambda m:bytes(m[:256]+m[512:2048]+m[0x6000:0x8000])
            bus=lambda m:[(at,v)for i,(at,v)in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=at<512]
            expected=([c.a,c.x,c.y,c.p&0xcf,c.sp],raw(base),base.banks,bus(base))
            for key in keys:
                m=fresh();after,_=execute(new,m,'RemainingDraw',inject=key)
                assert ([after.a,after.x,after.y,after.p&0xcf,after.sp],raw(m),m.banks,bus(m))==expected,('IRQ continuation',char,key)
                irq=[(at,v)for at,v in m.irq_writes if not 256<=at<512]
                assert irq==[(0x2006,0),(0x5128,0),(0x2005,32),(0x2005,0),(0x2006,128)]
                assert after.processorCycles-c.processorCycles==120
            irqs.append(dict(char=char,item=item,boundaries=len(keys),keys=keys,IRQ_cycles=120))
        put(a.output/'controls.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),parent_ROM_sha256=SHA,
            actual_Bill_full_RemainingDraw_calls=len(rows)*4*2,paired_Bill_cells=len(rows),rows=rows,actual_HUD_producers=allcoords,actual_HUD_render_entries=allarts,
            foreign_identities=35,foreign_full_calls=len(foreign)*2,foreign=foreign,helper_ABI_cases=len(helper),helper=helper,all6Bill_pickup_art_bounds=bounds,
            genuine_IRQ_boundary_cases=sum(z['boundaries']for z in irqs),IRQ=irqs,
            max_whole_call_extra_cycles=max(deltas),mean_extra_cycles=statistics.mean(deltas),extra_per_Bill_HUD_producer=30,extra_per_foreign_HUD_producer=29,
            caller_contract='Full final AXYP/SP/banks/all flat non-ROM RAM including full stack/SMC exact except proven Bill HUD OAM x-80/y-8 stores and final coordinate scratch. Ordered complete OAM stores/art pointers/other fields exact. Genuine helper preservesX/P; callerY overwritten by ArtPointer TAY and all full callers close exactly.',
            limits='Finite assembled CPU and exact record bounds; no native image, actual PPU palette/CHR contention, waveform or physical cadence qualification. Extra29/30cycles per selected HUD draw are material and disclosed. No whole-roster gameplay or acquisition claim.'))
        files={Path(__file__),a.packet/'candidate.nes',a.packet/'candidate.dbg',a.packet/'source-manifest.json',a.packet/'layout.json',a.packet/'implementation.patch',PARENT/'candidate.nes',PARENT/'candidate.dbg'}
        files.update(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
        print(json.dumps(dict(passed=True,ROM_sha256=sha(a.packet/'candidate.nes'),paired_Bill_cells=len(rows),foreign_cells=len(foreign),IRQ_cases=sum(z['boundaries']for z in irqs),controls_sha256=sha(a.output/'controls.json'))))
    except Exception as e:
        put(a.output/'failure.json',dict(passed=False,source_only=True,native_run=False,error=str(e),traceback=traceback.format_exc()));raise


if __name__=='__main__':main()
