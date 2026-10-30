"""Real lag-NMI/IRQ cuts while FF spells publish upper sprite windows.

Foreground DrawAll owns the OAM/palette staging transaction; normal NMI is
tested after its completed publication, never fabricated mid-transaction.
"""
from pathlib import Path
import json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_upper_fx_windows_controls_1030_v2 as U
from ff_wram_host_isr_v4 import clone
H=U.H;P=U.P;F=U.F;V=U.V;O=U.O;sha=U.sha;address=U.address


def fixture(b):
    m=U.M.setup(b)
    H.put(m,PlayerOutlinesOff=1,NmiDisable=255,ShouldSkipDrawSprites=0,
          VRAM_Buffer1_Offset=0,PlayerFacingDir=1,FrameCounter=0,
          GuestPowerupActive=0,StarInvincibleTimer=0,FfAction=0)
    for i in range(24):m[address(b,'ObjectMetasprite')+i]=0
    for i in range(36):m[address(b,'FfProjectile')+i]=0
    for slot,entry in[(0,144),(12,149),(24,154)]:U.set_projectile(m,slot,entry,1)
    # Render stress explicitly stages all three source spell families. It is
    # not an earned cast sequence: Ice/Bolt do not coexist in legal play.
    for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                ('Enemy_X_Position',192),('Enemy_PageLoc',0),
                ('Enemy_Y_Position',160),('Enemy_Y_HighPos',1),('Enemy_SprAttrib',0)]:
        m[address(b,n)]=v
    m[address(b,'ObjectMetasprite')+1]=address(b,'METASPRITE_GOOMBA_WALKING_1')
    H.invoke(m,'FwHostGraphics');H.invoke(m,'FwForceColors')
    return m


def complete_publication(m,c):
    assert c.sp==224
    H.exact(m)
    H.put(m,NmiDisable=0)
    q=H.NesMPU(memory=m,pc=0x5b00)
    q.a=91;q.x=7;q.y=133;q.p=0x30;q.sp=224
    r=V.interrupt(m,q,'NMI')
    assert any(a==0x4014 and v==2 for a,v in m.writes)
    return (bytes(m[512:768]),H.get(m,'CurrentOAMOffset'),
            m.chr_latches[:],bytes(m[address(m.bundle,'CurrentCHRBank'):address(m.bundle,'CurrentCHRBank')+12]),
            bytes(m[address(m.bundle,'X5ChrMode'):address(m.bundle,'X5ChrMode')+12]),
            bytes(m[0x5c00:0x5c80]),m.rawtags[:],(c.a,c.x,c.y,c.p,c.sp)),r


def run(b):
    m=fixture(b);snapshots=[];seen=set();windows=set()
    names=['FfHostDecodeFx','FfHostRenderChunk','FfRamPhysicalChr','FfGraphicsBank']
    entries={address(b,n):n for n in names}
    def observe(mem,c,i):
        raw=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if raw!=3:return
        name=entries.get(c.pc)
        if name:
            window=c.y if name=='FfRamPhysicalChr'else H.get(mem,'FfTargetY')
            if name=='FfRamPhysicalChr' and window in[5,6,7]:windows.add(window)
            key=(name,window,H.get(mem,'FfTargetW'),H.get(mem,'FfTargetPage'))
            if key not in seen:
                seen.add(key);snapshots.append((key,i,clone(mem,c)))
    c,_=F.invoke_drawall(m,observe)
    expected,_=complete_publication(m,c)
    assert windows=={5,6,7},windows
    rows=[];masked=0
    for key,step,(state,cpu)in snapshots:
        for kind in['NMI','IRQ']:
            q,d=clone(state,cpu)
            if kind=='IRQ'and d.p&d.INTERRUPT:
                before=(d.a,d.x,d.y,d.p,d.sp,d.pc);d.irq()
                assert before==(d.a,d.x,d.y,d.p,d.sp,d.pc)
                masked+=1;continue
            irq=V.interrupt(q,d,kind)
            H.finish(q,d)
            got,nmi=complete_publication(q,d)
            assert got==expected,('Interrupted whole DrawAll/final NMI differs',key,kind)
            rows.append(dict(cut=list(key),step=step,interrupt=irq,final_normal_NMI=nmi))
    return dict(passed=True,actual_snapshots=len(snapshots),actual_lag_NMI_IRQ_cases=len(rows),
                masked_IRQ_requests=masked,published_upper_windows=sorted(windows),rows=rows,
                complete_OAM_source_state_CHR_hardware_and_shadows_registers_and_maps_exact=True,
                renderer_stress_not_earned_three_family_coexistence=True)


def main():
    target=O/'upper-window-ISR-v1.json';assert not target.exists()
    proof=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'upper-window-controls-v2.json').read_text());assert h['passed']
        for p,v in h['bindings'].items():assert sha(p)==v,p
        b=H.C.qualified(H.O/'candidate.nes')
        proof['checks']['actual_active_FX_interruptions']=run(b)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(U.__file__),Path(V.__file__),
        R/'tools/audit/ff_wram_host_isr_v4.py',O/'upper-window-controls-v2.json',H.O/'candidate.nes',H.O/'candidate.dbg']}
    out=target if proof['passed']else O/'upper-window-ISR-negative-v1.json'
    assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],error=proof.get('error'),path=str(out))),flush=True)
    assert proof['passed']


if __name__=='__main__':main()
