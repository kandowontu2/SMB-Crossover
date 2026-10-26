"""Bounded real VineObjectHandler -> genuine no-draw Main -> regular NMI chain."""
from pathlib import Path
import argparse,hashlib,itertools,json,traceback
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from current3cee_postdma_mask_cpu_v4 import Bus
from verify_native_relocation import NesMPU
import mm_proto_publication_render_cpu_v2 as render

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def call(b,m,name,x=0,y=0):
    pc=address(b,name);bank=(location(b,name)-16)//8192;win=(pc-0x8000)//8192;m.page(win,bank)
    if win in[1,2]:m[address(b,'CurrentBank'if win==1 else'CurrentBankC')]=bank|128
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0,x,y,0x20,253;c.stPushWord(0x7eff);m.writes=[];trace=[]
    for _ in range(30000):
        if c.pc==0x7f00:break
        trace.append(c.pc);c.step()
    else:raise AssertionError(('Native vine call timeout',name,hex(c.pc)))
    assert c.sp==253
    return c,trace

def run(b,cfg):
    drawn,initial,_,info=render.run(b,cfg);l=lambda n:address(b,n)
    before=bytes(initial[0x200:0x300]);body=set(at for at,v in info['body_writes'])
    pending=initial[render.STATE]
    # Explicit BEFORE-phase actor configuration: a legal growing16px vine
    # in native special slot5, with one segment and no block-buffer writes.
    for name,v in dict(NmiDisable=255,ObjectOffset=5,Vine_FlagOffset=1,Vine_Height=16,Vine_Start_Y_Position=192,FrameCounter=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0).items():initial[l(name)]=v
    for name,v in dict(Enemy_Flag=1,Enemy_ID=0x2f,Enemy_X_Position=96,Enemy_PageLoc=0,Enemy_Y_Position=176,Enemy_Y_HighPos=1).items():initial[l(name)+5]=v
    initial[l('Vine_ObjOffset')]=5
    reservation,rt=call(b,initial,'PlayerOAMReservation')
    R=reservation.a
    assert R%4==0 and 0<R<96
    initial[l('CurrentOAMOffset')]=reservation.a # genuine following GameCore STA
    vc,vt=call(b,initial,'VineObjectHandler',5)
    assert l('RyuPlatformOriginalDrawVine')in vt and l('DrawVine')in vt
    partial=[(at,v)for at,v in initial.writes if 0x200<=at<0x300]
    after=bytes(initial[0x200:0x300]);assert partial and before!=after
    assert initial[render.STATE]==pending
    touched=sorted(body&{at for at,v in partial});changed=[at for at in touched if before[at-0x200]!=after[at-0x200]]
    # Record all overlaps; native GameCore reservation is not assumed equal
    # to the priority renderer's40/44 maximum body reservation.
    # Resume at the real post-physics GameCore draw-admission boundary. The
    # prior OBJECT far scope's bank restoration is BEFORE-phase context,
    # recorded explicitly rather than emulating unrelated enemy physics.
    m=Bus(b,bytes(initial[:0x8000]),(0,0))
    for win,bank in enumerate(initial.banks):m.page(win,bank)
    for name,v in dict(ShouldSkipDrawSprites=1,FramesSinceLastSpriteDraw=2,StarInvincibleTimer=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,AreaParserTaskNum=0,ScrollThirtyTwo=0,NmiSkipped=0,AreaType=1,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=0,ReloadCHRBank=0,DisableScreenFlag=0,GamePauseTimer=0,SavedJoypad1Bits=0).items():m[l(name)]=v
    pattern=bytes([0xad,l('ShouldSkipDrawSprites')&255,l('ShouldSkipDrawSprites')>>8,0xf0])
    starts=[at for at in range(l('GameCoreRoutine'),l('GameCoreRoutine')+512)if bytes(m[at:at+4])==pattern]
    assert len(starts)==1,starts
    c=NesMPU(memory=m,pc=starts[0]);c.a,c.x,c.y,c.p,c.sp=vc.a,vc.x,vc.y,vc.p,253
    c.stPush(0);c.stPushWord(0x82bd);c.stPushWord(l('GameLoop::PauseSkip')-1);m.cpu=c;m.writes=[];trace=[];release=[]
    for _ in range(100000):
        if c.pc==l('IdleLoop'):break
        at=c.pc;start=len(m.writes);trace.append(at);c.step()
        release += [dict(writer_callback_PC=c.pc,bank=m.banks[0],value=v)for p,v in m.writes[start:]if p==l('NmiDisable')and v==0]
    else:raise AssertionError(('No-draw Main did not release',cfg,hex(c.pc)))
    assert l('DrawAllMetasprites')not in trace
    assert m[l('FramesSinceLastSpriteDraw')]==3 and m[l('ShouldSkipDrawSprites')]==0
    assert bytes(m[0x200:0x300])==after and m[render.STATE]==pending
    assert release==[dict(writer_callback_PC=0x8355,bank=126,value=0)],release
    smc=[l(n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[l('FarcallJmpTarget_SMC')+2]
    saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),[m[x]for x in smc]);c.nmi();dma=[]
    for _ in range(100000):
        if c.pc==saved[0]and c.sp==saved[5]:break
        c.step()
        if m.pending_dma:dma.append(bytes(m[0x200:0x300]));m.pending_dma=False
    else:raise AssertionError('Regular NMI did not return')
    assert(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),[m[x]for x in smc])==saved
    assert dma==[after]and m.serial==[8,8]
    assert m[render.STATE]==(cfg['display']^64)
    return dict(cfg=cfg,explicit_before_actor={'native_slot':5,'height':16,'flag':1,'X':96,'Y':176,'start_Y':192},actual_reservation=R,actual_vine_source_stores=partial,
                body_owned_addresses=sorted(body),body_addresses_touched=touched,body_bytes_changed=changed,
                tag_before_vine=pending,tag_after_vine=pending,tag_after_actual_regular_NMI=m[render.STATE],
                no_draw_admission_PC=starts[0],actual_Main_release=release[0],source_at_actual4014_exact_partial_image=True,
                complete_NMI_AXYP_SP_5SMC_banks_restored=True,partial_source_before_hex=before.hex(),partial_source_after_hex=after.hex())

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in['candidate','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    try:
        b=scoped_load(a.candidate)
        for variant,display,shots in itertools.product([0,1],[0,64],[0,1,4]):
            rows.append(run(b,dict(entry='DrawAllMetasprites',variant=variant,display=display,types=[1 if i<shots else 0 for i in range(4)],first=112,flags=0x20)))
        overlaps=[r for r in rows if r['body_bytes_changed']]
        assert overlaps
        (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
        proof=dict(passed=True,source_observation_only=True,native_run=False,adoption_ready=False,ROM_sha256=sha(a.candidate),cases=len(rows),actual_VineObjectHandler_DrawVine_native_leaf_and_no_draw_Main_regularNMI_executed=True,
                   actual_partial4014_source_image_retained=True,NMI_AXYP_SP_5SMC_banks_exact=True,body_priority_turn_body_overlap_cases=sum(bool(r['body_bytes_changed'])and r['cfg']['display']==0 for r in rows),
                   shot_priority_turn_partial_body_overlap_cases=sum(bool(r['body_bytes_changed'])and r['cfg']['display']==64 for r in rows),acknowledges_partial_image_even_when_body_bytes_changed=True,
                   whole_page_or_intact_body_tag_guarantee=False,limitations='Configured legal growing-vine actor/source simulation, not natural vine spawn/playthrough or physical DMA/PPU timing. Resume is the genuine post-physics no-draw admission; unrelated enemy loops and OBJECT far-scope bank restoration are configured before-phase context. No game/source patch is made. A tag identifies completed allocation, not universal source-image integrity.',tool_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed=len(rows)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise
if __name__=='__main__':main()
