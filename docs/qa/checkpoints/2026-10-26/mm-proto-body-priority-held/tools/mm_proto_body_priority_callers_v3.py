"""Actual post-draw GameCore/IdleLoop/NMI/next-GameLoop continuation.

No register normalization: X/V mapping deltas are carried through genuine
source continuation, interrupt save/restore and UI save/restore until the
next GameLoop's independent random/score work has overwritten them. A small
explicit set of persistent draw-allocation fields remains intentionally
different; those values are recorded rather than broadly masking RAM.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, traceback
import mm_proto_body_priority_partition_v5 as partition
from current3cee_postdma_mask_cpu_v4 import Bus
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def continuation(b,cfg):
    rendered, initial, drawtrace, drawmeta=partition.run(b,cfg)
    m=Bus(b,bytes(initial[:0x8000]),(0,0))
    for slot,bank in enumerate(initial.banks):m.page(slot,bank)
    l=lambda n:address(b,n)
    for name,value in dict(StarInvincibleTimer=cfg.get('star',0),VRAM_Buffer1_Offset=cfg.get('queue',0),
                           VRAM_Buffer_AddrCtrl=0,AreaParserTaskNum=0,ScrollThirtyTwo=0,NmiSkipped=0,
                           AreaType=1,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=cfg.get('irqflag',0),
                           ReloadCHRBank=0,DisableScreenFlag=0,GamePauseTimer=0,SavedJoypad1Bits=0).items():m[l(name)]=value
    # Exact actual caller instruction/return sites. JumpEngine consumes its
    # own table return: it adds no persistent frame above GameCore's return.
    assert bytes(m[0x82bb:0x82be])==bytes([0x20,l('GameLoop')&255,l('GameLoop')>>8])
    assert bytes(m[0x8438:0x843d])==bytes([0xa9,0,0x8d,l('FramesSinceLastSpriteDraw')&255,l('FramesSinceLastSpriteDraw')>>8])
    start=0x8438
    # Stop after the actual next-frame UpdateTopScore farcall, before the
    # first GamePauseStatus read. Its precise compiled source byte pattern
    # has one occurrence in GameLoop, not a synthetic tail trampoline.
    pattern=bytes([0xad,l('GamePauseStatus')&255,l('GamePauseStatus')>>8,0x4a])
    starts=[pc for pc in range(l('GameLoop'),l('GameLoop::PauseSkip'))if bytes(m[pc:pc+4])==pattern]
    assert len(starts)==1,starts
    boundary=starts[0]
    c=NesMPU(memory=m,pc=start);c.a,c.x,c.y,c.p,c.sp=rendered.a,rendered.x,rendered.y,rendered.p,253
    c.stPush(0);c.stPushWord(0x82bd);c.stPushWord(l('GameLoop::PauseSkip')-1)
    assert c.sp==248
    m.cpu=c;m.writes=[];m.stamps=[]
    injected=False;entered_next=False;trace=[];irq_receipt=None;first_next_x=None
    for index in range(200000):
        if entered_next and c.pc==boundary:break
        if c.pc==l('IdleLoop') and not injected:
            assert m[l('NmiDisable')]==0
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),m[l('CurrentBank')],m[l('CurrentBankC')])
            c.nmi();nmi_steps=0
            for nmi_steps in range(100000):
                if c.pc==saved[0]and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError(('Actual NMI timeout',cfg,hex(c.pc)))
            assert (c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),m[l('CurrentBank')],m[l('CurrentBankC')])==saved,('NMI lost incoming draw X/V',cfg,saved,(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),m[l('CurrentBank')],m[l('CurrentBankC')]))
            assert m.serial==[8,8]
            irq_receipt=dict(steps=nmi_steps,saved_registers=list(saved[:6]),restored_exact=True)
            injected=True
        if injected and c.pc==l('GameLoop'):entered_next=True
        at=c.pc;bank=m.banks[(at-0x8000)//8192]if at>=0x8000 else-1
        before=len(m.writes);op=m[c.pc]
        if entered_next and op==0xa2 and m[c.pc+1]==0 and first_next_x is None:
            # There are independent internal X loads in UI callees, but they
            # restore the caller X. This literal LDX0 is the unconditionally
            # executed main GameLoop owner after the UI farcall.
            if bank==126 and l('GameLoop')<=c.pc<boundary:first_next_x=dict(pc=c.pc,bank=bank,before_X=c.x)
        c.step()
        trace.append(dict(pc=at,bank=bank,regs=[c.a,c.x,c.y,c.p&207,c.sp],writes=[(p,v)for p,v in m.writes[before:]if not 0x100<=p<0x200]))
    else:raise AssertionError(('Continuation timeout',cfg,hex(c.pc),m.banks))
    assert injected and entered_next and first_next_x
    return c,m,dict(boundary=boundary,trace=trace,actual_NMI=irq_receipt,main_independent_X_load=first_next_x,draw_return=[rendered.a,rendered.x,rendered.y,rendered.p&207,rendered.sp],cycles=c.processorCycles)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','candidate','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=[scoped_load(q)for q in[a.parent,a.candidate]];rows=[]
    try:
        intentional=['RgOamRotation','GuestOamRotationActive']
        for variant,mask,frame,first,star,irqflag in itertools.product([0,1],[0,15],[0,1],[0,112],[0,4,9],[0,1]):
            cfg=dict(entry='DrawAllMetasprites',variant=variant,types=[mask>>i&1 for i in range(4)],frame=frame,first=first,star=star,irqflag=irqflag,flags=0x20)
            c,m,left=continuation(old,cfg);d,n,right=continuation(new,cfg)
            assert left['draw_return']==right['draw_return'],('Original draw return ABI not retained',cfg,left['draw_return'],right['draw_return'])
            assert(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks))==(d.pc,d.a,d.x,d.y,d.p&207,d.sp,tuple(n.banks)),('Complete caller boundary AXYP/SP/bank mismatch',cfg,(c.pc,c.a,c.x,c.y,c.p,c.sp),(d.pc,d.a,d.x,d.y,d.p,d.sp))
            # Only exact existing allocation fields and the intentionally
            # reordered physical OAM image differ. All SMC/hardware state and
            # every other application RAM byte remains fully compared.
            allowed=set(range(0x100,0x300))|{address(old,name)for name in intentional}
            # Snapshot underlying bus latches; do not perform a second serial
            # input read while comparing application memory after the run.
            diff=[(at,list.__getitem__(m,at),list.__getitem__(n,at))for at in range(0x8000)if list.__getitem__(m,at)!=list.__getitem__(n,at)and at not in allowed]
            assert not diff,('Actual caller leaked physical-index state',cfg,diff[:20])
            assert len(left['trace'])==len(right['trace'])
            for x,y in zip(left['trace'],right['trace']):
                assert(x['pc'],x['bank'],x['writes'])==(y['pc'],y['bank'],y['writes']),('Continuation control/application write divergence',cfg,x,y)
            rows.append(dict(cfg=cfg,parent=left,candidate=right,complete_first_live_boundary=[c.pc,c.a,c.x,c.y,c.p&207,c.sp],intentional_allocation_fields={name:[m[address(old,name)],n[address(new,name)]]for name in intentional}))
        proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),cases=len(rows),complete_actual_continuation_boundary_AXYP_SP_RAM_SMC_banks_and_ordered_application_writes_exact=True,actual_NMI_preserves_changed_return_X_V=True,independent_X_overwrite='Unconditional GameLoop LDX0 after genuine inventory-UI farcall; full live-state boundary after original UpdateTopScore farcall.',intentional_fields=intentional,dead_stack_and_physical_OAM_explicit=True,scope=__doc__,checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');print(json.dumps(proof,indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),completed_cases=len(rows),checker_sha256=sha(__file__)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
