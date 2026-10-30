"""Actual linked FF palette queues, native consumption, bounds and ISR contracts.

This proves the body/world packet only. FX allocation and native character
admission remain separate, and no gameplay result is injected by an observer.
"""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_wram_host_controls_v7 as H
import ff_joint_actual_main_v2 as M
import ff_joint_typed_controls_v1 as T
import ff_host_pickups_vectors_v2 as V
from ff_wram_host_isr_v4 import clone
from check_tmnt_render_oa import address,location
O=R/'build/ff-joint-body-palette-1030-v2';H.O=O/'joint';sha=T.sha
BODY=[[0x16,0x30,0x36],[0x28,0x18,0x21],[0x1a,0x27,0x30],[0x16,0x27,0x30],[0x0f,0x24,0x30]]
AREA=[[0x0f,0x30,0x10],[0x0f,0x36,0x17],[0x0c,0x3c,0x1c],[0x00,0x30,0x10]]
BACK=[0x22,0x22,0x0f,0x0f,0x0f,0x22,0x0f,0x0f]


def duplicate(seed):
    return clone(seed,H.start(seed,'FwCheck'))[0]


def seed(b,cold=False):
    m=H.make(b)
    if not cold:H.invoke(m,'FwLoad');H.invoke(m,'FwEnsure')
    H.put(m,GuestPowerupActive=0,GuestLegacyHurt=0,GuestPowerupAge=0,
          StarInvincibleTimer=0,BackgroundColorCtrl=0,FfVariant=0,AreaType=1,
          VRAM_Buffer1_Offset=0)
    m.writes.clear();m.ram_writes.clear()
    return m


def packet(m):
    a=address(m.bundle,'VRAM_Buffer1');n=H.get(m,'VRAM_Buffer1_Offset')
    return list(m[a:a+n+1])


def expected(variant,area,bg=0,phase=None):
    p=variant//2 if phase is None else phase
    back=BACK[bg if bg else area] if (bg if bg else area)<8 else 0x0f
    return [0x3f,0x1d,3,*AREA[area],0x3f,0x19,3,0x16,0x30,0x27,
            0x3f,0x10,4,back,*BODY[p],0]


def source_colors(b):
    # Compare literal rows with the actual source-linked tables, not a copy
    # of the new compositor's own table used as its expected result.
    for n,row in [('FfPaletteRed',BODY[0]),('FfPaletteBlue',BODY[1])]:
        at=location(b,n);assert list(b['raw'][at+1:at+4])==row
    at=location(b,'GuestPowerupPalette::Colors')
    assert list(b['raw'][at+9:at+18])==sum(BODY[2:],[])
    return dict(passed=True,original_class_rows=2,existing_guest_flash_rows=3)


def colors(b):
    seeds=[seed(b,False),seed(b,True)];rows=[]
    for cold,variant,area,bg in itertools.product([0,1],range(4),range(4),range(9)):
        m=duplicate(seeds[cold]);H.put(m,FfVariant=variant,AreaType=area,BackgroundColorCtrl=bg)
        before=bytes(m[0x5c00:0x5c80]);ack=H.get(m,'FfPaletteAck');ram=bytes(m.ram[3]);executed=[]
        def observe(mem,c,i):
            if 0xa000<=c.pc<0xc000 and mem.rawtags[1]==3:executed.append(c.pc)
        c,_=H.invoke(m,'GetPlayerColors',hook=observe,a=0x55,x=7,y=91,p=0x71)
        assert packet(m)==expected(variant,area,bg),('actual GetPlayerColors packet',cold,variant,area,bg,packet(m))
        assert bytes(m[0x5c00:0x5c80])==before and bytes(m.ram[3])==ram
        if cold:assert H.get(m,'FfPaletteAck')==ack and not executed
        else:assert H.get(m,'FfPaletteAck')==variant//2;H.exact(m)
        rows.append([cold,variant,area,bg,c.processorCycles])
    return dict(passed=True,actual_GetPlayerColors_cases=len(rows),rows=rows,
                genuine_world_P2_P3_and_class_backdrop_exact=True,cold_no_RAM3_execution=True)


def capacity(b):
    bases=[seed(b),seed(b,True)];rows=[];queue=address(b,'VRAM_Buffer1')
    for cold,offset in itertools.product([0,1],range(256)):
        m=duplicate(bases[cold]);H.put(m,VRAM_Buffer1_Offset=offset,FfPaletteAck=0x79)
        # Sentinel writes are fixture setup, before the actual callback.
        for i in range(256):m[queue+i]=(i*17+31)&255
        before=bytes(m[queue:queue+256]);m.writes.clear()
        c,_=H.invoke(m,'FwForceColors',a=0x55,x=7,y=91,p=0x71)
        assert (c.a,c.x,c.y,c.p,c.sp)==(0x55,7,91,0x71,224)
        if offset<65:
            assert H.get(m,'VRAM_Buffer1_Offset')==offset+19
            assert list(m[queue+offset:queue+offset+20])==expected(0,1)
            assert bytes(m[queue:queue+offset])==before[:offset]
            assert bytes(m[queue+offset+20:queue+256])==before[offset+20:]
            assert H.get(m,'FfPaletteAck')==(0x79 if cold else 0)
        else:
            assert H.get(m,'VRAM_Buffer1_Offset')==offset
            assert bytes(m[queue:queue+256])==before
            assert H.get(m,'FfPaletteAck')==(0x79 if cold else 255)
            # Retried by the real next UI tick, not a synthetic force.
            if not cold:
                H.put(m,VRAM_Buffer1_Offset=0)
                H.invoke(m,'FwPaletteTick')
                assert packet(m)==expected(0,1) and H.get(m,'FfPaletteAck')==0
        rows.append([cold,offset,c.processorCycles])
    body=[]
    for offset in range(256):
        m=duplicate(bases[0]);H.put(m,VRAM_Buffer1_Offset=offset,FfPaletteAck=1)
        for i in range(256):m[queue+i]=(i*11+9)&255
        before=bytes(m[queue:queue+256]);H.invoke(m,'FwPaletteTick')
        if offset<77:
            assert H.get(m,'VRAM_Buffer1_Offset')==offset+7 and H.get(m,'FfPaletteAck')==0
            assert list(m[queue+offset:queue+offset+8])==expected(0,1)[12:]
            assert bytes(m[queue+offset+8:queue+256])==before[offset+8:]
        else:
            assert H.get(m,'VRAM_Buffer1_Offset')==offset and H.get(m,'FfPaletteAck')==1
            assert bytes(m[queue:queue+256])==before
        assert bytes(m[queue:queue+offset])==before[:offset]
        body.append(offset)
    return dict(passed=True,full_force_offsets=len(rows),cached_body_offsets=len(body),
                queue_capacity=84,all_canaries_and_complete_packet_retry_pass=True,rows=rows)


def transitions(b):
    base=seed(b);rows=[]
    for variant,mode in itertools.product(range(4),['base','star','powerup','hurt']):
        m=duplicate(base);H.put(m,FfVariant=variant,FfPaletteAck=255)
        for age in range(64):
            H.put(m,FrameCounter=age,GuestPowerupAge=age,VRAM_Buffer1_Offset=0,
                  StarInvincibleTimer=20 if mode=='star' else 0,
                  GuestPowerupActive=int(mode in ['powerup','hurt']),
                  GuestLegacyHurt=int(mode=='hurt'),R0=0xa5,R1=0x5a)
            phase=(age//4 if mode=='star' else age//6 if mode=='powerup' else 0)&3
            phase=phase+1 if phase else variant//2
            previous=H.get(m,'FfPaletteAck')
            c,_=H.invoke(m,'FwPaletteTick')
            want=expected(variant,1,phase=phase)
            if previous==255:assert packet(m)==want
            elif previous!=phase:assert packet(m)==want[12:]
            else:assert H.get(m,'VRAM_Buffer1_Offset')==0
            assert H.get(m,'FfPaletteAck')==phase
            if previous!=255:assert [H.get(m,'R0'),H.get(m,'R1')]==[0xa5,0x5a]
            rows.append([variant,mode,age,phase,c.processorCycles])
        H.put(m,GuestPowerupActive=0,StarInvincibleTimer=0,VRAM_Buffer1_Offset=0)
        H.invoke(m,'FwForceColors');assert packet(m)==expected(variant,1)
        H.exact(m)
    return dict(passed=True,actual_UI_ticks=len(rows),source_flash_phases_and_restoration_exact=True,
                cached_tick_CPU=[min(r[-1]for r in rows),max(r[-1]for r in rows)],rows=rows)


def cold_and_foreign(b):
    base=seed(b,True);rows=[]
    for selected,poison,target in itertools.product(range(33),range(16),['FwPaletteTick','FwForceColors']):
        if selected!=22 and poison:continue
        m=duplicate(base);H.put(m,SelectedCharacter=selected,FfPaletteAck=0x79)
        before=bytes(m[0x5c00:0x5c80])+bytes(m[0x5fc1:0x5fcf]);ram=bytes(m.ram[3]);points=[]
        def observe(mem,c,i):
            if c.pc>=0x8000 and mem.rawtags[(c.pc-0x8000)//8192]==3:points.append(c.pc)
        # Deliberately poison each member of a genuinely loaded cookie too.
        if selected==22:
            H.invoke(m,'FwLoad');m.ram[3][0x1fe0+poison]^=1;ram=bytes(m.ram[3])
        H.invoke(m,target,hook=observe)
        assert not points and bytes(m.ram[3])==ram
        assert bytes(m[0x5c00:0x5c80])+bytes(m[0x5fc1:0x5fcf])==before
        if selected!=22 or target=='FwPaletteTick':assert H.get(m,'VRAM_Buffer1_Offset')==0
        else:assert packet(m)==expected(0,1)
        rows.append([selected,poison,target])
    return dict(passed=True,foreign_and_full_cookie_rejection_cases=len(rows),rows=rows,
                no_source_state_or_ACK_writes_and_no_RAM3_execution=True)


def native_consumption(b):
    base=M.setup(b);rows=[]
    for variant,area in itertools.product(range(4),range(4)):
        m=duplicate(base);H.put(m,FfVariant=variant,AreaType=area,BackgroundColorCtrl=0,
                               GuestPowerupActive=0,StarInvincibleTimer=0,VRAM_Buffer1_Offset=0)
        H.invoke(m,'GetPlayerColors');assert packet(m)==expected(variant,area)
        m.vram[0x3f14:0x3f18]=bytes([0x0f,0x1c,0x36,0x17])
        H.put(m,NmiDisable=0)
        c=H.start(m,'FwCheck');r=V.interrupt(m,c,'NMI')
        assert list(m.vram[0x3f10:0x3f14])==[BACK[area],*BODY[variant//2]]
        assert list(m.vram[0x3f19:0x3f1c])==[0x16,0x30,0x27]
        assert list(m.vram[0x3f1d:0x3f20])==AREA[area]
        assert list(m.vram[0x3f14:0x3f18])==[0x0f,0x1c,0x36,0x17]
        assert H.get(m,'VRAM_Buffer1_Offset')==0
        H.finish(m,c);H.exact(m);rows.append([variant,area,r['CPU']])
    return dict(passed=True,actual_normal_NMI_consumptions=len(rows),rows=rows,
                actual_PPU_palette_writes_match=True,world_P1_not_recolored=True)


def actual_main(b):
    base=M.setup(b);rows=[]
    for variant,mode in itertools.product(range(4),['base','star']):
        m=duplicate(base);H.put(m,FfVariant=variant);H.invoke(m,'FwEnsure')
        H.put(m,VRAM_Buffer1_Offset=0,GuestPowerupActive=0,StarInvincibleTimer=20 if mode=='star'else 0,
              SavedJoypadBits=0,A_B_Buttons=0,Left_Right_Buttons=0,NmiDisable=255,FrameCounter=4)
        points=[]
        def observe(mem,c,i):
            if c.pc==address(b,'FwPaletteTick') and mem.rawtags[1]==190:points.append([i,H.get(mem,'NmiDisable')])
        c,_=M.invoke_main(m,observe)
        assert len(points)==1,('actual Main UI hook',variant,mode,points)
        assert points[0][1]!=0,'Main must own the native queue while constructing packets'
        assert H.get(m,'NmiDisable')==0
        # Other genuine Main HUD packets can coexist. Require the authentic
        # body command as a decoded command, not an arbitrary byte substring.
        q=packet(m);i=0;commands=[]
        while i<len(q) and q[i]:
            size=q[i+2]&0x3f;commands.append(q[i:i+3+size]);i+=3+size
        phase=2 if mode=='star'else variant//2
        assert expected(variant,1,phase=phase)[12:-1] in commands,(variant,mode,commands)
        H.exact(m);rows.append([variant,mode,c.processorCycles,points[0][1]])
    return dict(passed=True,whole_Main_cases=len(rows),once_per_Main_real_UI_service=True,
                native_queue_ownership_observed=True,rows=rows)


def interruptions(b):
    base=seed(b);snapshots=[]
    for target,ack in [('FwForceColors',0),('FwPaletteTick',1),('FwPaletteTick',0)]:
        m=duplicate(base);H.put(m,FfPaletteAck=ack,NmiDisable=255)
        seen=set()
        def observe(mem,c,i):
            op=bytes(mem[c.pc:c.pc+3]);tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            important=op in [b'\x8d\x16\x51',b'\x8d\x15\x51'] or c.pc in [address(b,n)for n in[
                'FwPaletteMapC','FfHostPaletteC','FfPalettePhaseC','FfQueueBodyC','FwCheck']]
            if important or i<12:
                key=(c.pc,tag,op)
                if key not in seen:seen.add(key);snapshots.append((target,ack,i,clone(mem,c)))
        H.invoke(m,target,hook=observe)
    rows=[]
    for target,ack,step,(state,cpu) in snapshots:
        # Main owns the queue with NmiDisable!=0. A normal NMI is legal at
        # the cached no-write path and after complete return, covered above.
        cases=[('NMI',255),('IRQ',255)]
        if target=='FwPaletteTick'and ack==0:cases+=[('NMI',0)]
        for kind,lag in cases:
            m,c=clone(state,cpu);H.put(m,NmiDisable=lag)
            if kind=='IRQ'and c.p&c.INTERRUPT:continue
            r=V.interrupt(m,c,kind);H.finish(m,c);H.exact(m)
            rows.append(dict(target=target,ack=ack,step=step,lag=lag,**r))
    return dict(passed=True,real_ISR_cases=len(rows),snapshots=len(snapshots),rows=rows,
                all33SMC_APXY_live_page1_R01_R67_maps_and_RAM3_verified=True,
                queue_writer_normal_NMI_not_fabricated=True)


def main():
    out=O/'body-palette-controls-v1.json';assert not out.exists()
    p=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'source-closure.json').read_text())
        for f,v in h['bindings'].items():assert sha(f)==v,f
        b=H.C.qualified(H.O/'candidate.nes')
        for n,fn in [('source_rows',source_colors),('actual_colors',colors),('capacity',capacity),
                     ('transitions',transitions),('cold_and_foreign',cold_and_foreign),
                     ('native_NMI_queue_consumption',native_consumption),('actual_Main',actual_main),('actual_ISR',interruptions)]:
            p['checks'][n]=fn(b);print(n,'PASS',flush=True)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in [Path(__file__),Path(H.__file__),Path(M.__file__),Path(T.__file__),Path(V.__file__),
                    O/'source-closure.json',H.O/'candidate.nes',H.O/'candidate.dbg']}
    target=out if p['passed']else O/'body-palette-controls-negative-v1.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],checks=list(p['checks']),error=p.get('error'),path=str(target))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
