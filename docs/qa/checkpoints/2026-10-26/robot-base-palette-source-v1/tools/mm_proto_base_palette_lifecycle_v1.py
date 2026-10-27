"""Finite existing-cache caller, invalidation and actual IRQ/lagNMI controls."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback
from mm_proto_cold_palette_cpu_v1 import configured,invoke,application,palette
from mm_proto_cold_palette_lifecycle_v2 import call
from mm_proto_base_palette_cpu_v1 import nmi_seed
from current3cee_postdma_mask_cpu_v4 import run as nmi_run
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'robot-cold-palette-candidate-v2';C=D/'robot-base-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def interrupted(q,target=None,kind='irq',pre=False):
    b=q.b;pc=address(b,'X5GetPlayerColors');bn=(location(b,'X5GetPlayerColors')-16)//8192
    q.m.page(1,bn);q.set('CurrentBank',bn|128)
    c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=90,37,19,0x30,253;c.stPushWord(0x5aff)
    smc=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    hit=False;sites=[]
    for _ in range(100000):
        if c.pc==0x5b00:break
        if not hit and(pre or c.pc==target):
            before=(c.a,c.x,c.y,c.p&207,c.sp,c.pc);state=(q.m.banks[:],q.get('CurrentBank'),q.get('CurrentBankC'),[q.m[x]for x in smc])
            c.nmi()if kind=='nmi'else c.irq()
            for _ in range(100000):
                if(c.a,c.x,c.y,c.p&207,c.sp,c.pc)==before:break
                c.step()
            else:raise AssertionError(('interrupttimeout',kind,before,hex(c.pc)))
            assert state==(q.m.banks[:],q.get('CurrentBank'),q.get('CurrentBankC'),[q.m[x]for x in smc])
            hit=True
        if 0xab60<=c.pc<0xabda and q.m.banks[1]==78:sites.append(c.pc)
        c.step()
    else:raise AssertionError('Producer timeout')
    assert c.sp==253
    return c,sorted(set(sites)),hit


def tail(q,regs):
    # Actual GameCore code immediately after farcallPlayerGfxHandler. Its
    # original farOBJECT scope owns one savedA-bank byte on the real stack.
    b=q.b;raw=b['raw'];at=16+126*8192+(0x83ee&8191)
    assert raw[at:at+6]==bytes([0x20,0xd4,0x84,0xa2,1,0x86])
    q.m.page(1,0);q.set('CurrentBank',128)
    c=NesMPU(memory=q.m,pc=0x83ee);c.a,c.x,c.y,c.p=regs[:4];c.sp=253;c.stPushWord(0x5aff);c.stPush(215)
    q.m.writes=[]
    for _ in range(160000):
        if c.pc==0x5b00:break
        c.step()
    else:raise AssertionError(('Tailtimeout',hex(c.pc)))
    assert c.sp==253
    return c


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);life=[];irqs=[];callers=[];poison=[]
    try:
        bs=[scoped_load(x/'candidate.nes')for x in[P,C]]
        # A writer may publish a cache only because its complete output matches
        # that already supported oldcache state. Compare the whole actual
        # consumer and GameCore continuation to precisely that reference state.
        for variant,mode,tier,hurt in itertools.product([0,1],[0,1],range(3),[0,1]):
            qs=[configured(b,1,variant=variant,engine=8,tier=tier,charge=1,charging=1)for b in bs]
            for q in qs:
                q.put(CrossoverBehaviorVersion=mode,GuestHurtTicks=hurt,DisableScreenFlag=0,InvDirty=1,
                    GameTimerCtrlTimer=1,FramesSinceLastSpriteDraw=0,ShouldSkipDrawSprites=0,Player_Rel_XPos=96,Player_Rel_YPos=160)
                invoke(q,'InventoryHud');invoke(q,'GetPlayerColors')
            assert qs[0].get('VRAM_Buffer1_Offset')==qs[1].get('VRAM_Buffer1_Offset')==47
            # Explicit intentional-cache reference, not a masked RAM outcome.
            qs[0].set('MmLastPalette',2 if tier==2 else 1)
            assert application(qs[0])==application(qs[1])
            cs=[invoke(q,'PlayerGfxHandler')for q in qs]
            regs=[[c.a,c.x,c.y,c.p,c.sp]for c in cs]
            assert regs[0]==regs[1] and application(qs[0])==application(qs[1])
            assert qs[0].m.banks==qs[1].m.banks
            cpus=[tail(q,r)for q,r in zip(qs,regs)]
            assert [(c.a,c.x,c.y,c.p,c.sp)for c in cpus][0]==[(c.a,c.x,c.y,c.p,c.sp)for c in cpus][1]
            assert application(qs[0])==application(qs[1]) and qs[0].m.banks==qs[1].m.banks
            assert qs[0].m.writes==qs[1].m.writes
            callers.append(dict(variant=variant,mode=mode,tier=tier,hurt=hurt,
                reference='OldparentcompleteGetColors plus explicitlydeclaredcache1/2; unchangedoldcachehitconsumer contract',
                full_PlayerGfx_and_realGameCore_tail_AXYP_SP_applicationRAM_orderedwrites_banks_exact=True))
        # Real selection cleanup must permit the refresh, not leave a stale
        # cached special color. Follow with the complete nativeNMI decoder.
        for variant,mode,tier in itertools.product([0,1],[0,1],range(3)):
            qs=[configured(b,1,variant=variant,engine=8,tier=tier,selected=1,cache=2)for b in bs]
            for q in qs:
                q.put(CrossoverBehaviorVersion=mode,MmLastPalette=1,InvDirty=1,DisableScreenFlag=0)
                call(q,'InventorySelectionCommit',a=0,x=1)
                assert q.get('SsLastPalette')==0 and q.get('InvSelected',1)==0
                invoke(q,'InventoryHud');invoke(q,'SpecialPalette');invoke(q,'PlayerGfxHandler')
                assert q.get('SsLastPalette')==1 and q.get('MmLastPalette')==(2 if tier==2 else 1)
                nmi_seed(q)
            result=[nmi_run(b,q,stall=0)for b,q in zip(bs,qs)]
            assert palette(result[0]['writes'])==palette(result[1]['writes'])
            assert result[0]['regs']==result[1]['regs']and result[0]['banks']==result[1]['banks']
            life.append(dict(kind='actualselectioncommit_defaultrefresh',variant=variant,mode=mode,tier=tier,
                palette_refresh_preserved=True,final_PPU_values_exact=True,NMI_delta=result[1]['cycles']-result[0]['cycles']))
        for kind in['star','charge','transform','death_reentry']:
            for variant,tier in itertools.product([0,1],[0,2]):
                qs=[configured(b,1,variant=variant,engine=8,tier=tier,cache=0)for b in bs]
                for q in qs:
                    q.put(GuestPowerupActive=int(kind=='transform'),StarInvincibleTimer=int(kind=='star'),
                        MmChargeFrames=48 if kind=='charge'else 0,MmCharging=int(kind=='charge'),MmFlashPhase=1,MmLastPalette=8)
                    if kind=='death_reentry':
                        q.set('MmDeathFlag',1);call(q,'SpecialClear');q.set('MmDeathFlag',0)
                    invoke(q,'GetPlayerColors')
                if kind!='death_reentry':assert application(qs[0])==application(qs[1]),kind
                for q in qs:
                    q.put(GuestPowerupActive=0,StarInvincibleTimer=0,MmChargeFrames=0,MmCharging=0,VRAM_Buffer1_Offset=0)
                    call(q,'SpecialClear');invoke(q,'SpecialPalette');invoke(q,'PlayerGfxHandler');nmi_seed(q)
                result=[nmi_run(b,q,stall=0)for b,q in zip(bs,qs)]
                assert palette(result[0]['writes'])==palette(result[1]['writes'])
                life.append(dict(kind=kind,variant=variant,tier=tier,clear_and_leave_to_base_refresh_preserved=True,final_PPU_values_exact=True))
        # Every live source read of the private scratch is dominated by the
        # earlySTY at this entry. Poison both legal oldresult1/2 and extremes.
        for mode,tier,charge,star in itertools.product([0,1],range(3),[0,32,33,48,87],[0,1]):
            qs=[configured(bs[1],1,tier=tier,charge=charge,star=star)for _ in range(2)]
            for q,v in zip(qs,[0,255]):q.put(CrossoverBehaviorVersion=mode,MmPaletteIndex=v,MmLastPalette=1)
            cs=[invoke(q,'MegaManPaletteState')for q in qs]
            assert[(c.a,c.x,c.y,c.p,c.sp)for c in cs][0]==[(c.a,c.x,c.y,c.p,c.sp)for c in cs][1]
            assert application(qs[0])==application(qs[1])and qs[0].m.writes==qs[1].m.writes
            poison.append(dict(mode=mode,tier=tier,charge=charge,star=star,initialscratch_0_vs255_output_full_exact=True))
        b=bs[1]
        for engine,tier,charge in[(0,0,0),(8,2,1)]:
            q=configured(b,1,variant=1,engine=engine,tier=tier,charge=charge,charging=int(charge>0))
            _,sites,_=interrupted(q)
            for kind in['irq','nmi']:
                q=configured(b,1,variant=1,engine=engine,tier=tier,charge=charge,charging=int(charge>0))
                c,_,_=interrupted(q,kind=kind,pre=True);expected=application(q);regs=(c.a,c.x,c.y,c.p&207,c.sp);banks=q.m.banks[:]
                for site in sites:
                    q=configured(b,1,variant=1,engine=engine,tier=tier,charge=charge,charging=int(charge>0))
                    c,_,hit=interrupted(q,target=site,kind=kind)
                    assert hit and(c.a,c.x,c.y,c.p&207,c.sp)==regs and application(q)==expected and q.m.banks==banks
                    irqs.append(dict(engine=engine,tier=tier,charge=charge,kind=kind,PC=site,full_return_application_banks_5SMC_exact=True))
        source=C/'source';references={}
        for f in(source/'src').rglob('*'):
            if f.suffix not in['.s','.inc']:continue
            lines=[dict(line=i,text=s.strip())for i,s in enumerate(f.read_text().splitlines(),1)if 'MmPaletteIndex'in s]
            if lines:references[str(f.relative_to(source))]=dict(sha256=sha(f),lines=lines)
        assert set(references)=={'src/megaman_palette.s','src/megaman_weapons.s'}
        put(a.output/'cases.json',dict(callers=callers,lifecycles=life,poison=poison,interrupts=irqs))
        put(a.output/'scratch-read-ownership.json',references)
        put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,
            baseline_ROM_sha256=sha(P/'candidate.nes'),candidate_ROM_sha256=sha(C/'candidate.nes'),
            actual_existingcache_reference_PlayerGfx_GameCore_tail_cases=len(callers),
            actual_selection_invalidation_reset_leave_cases=len(life),scratchpoison_nextcall_cases=len(poison),
            actual_IRQ_cases=sum(x['kind']=='irq'for x in irqs),actual_lagNMI_cases=sum(x['kind']=='nmi'for x in irqs),
            physicalflags_mask=207,flags_note='ActualinterruptRTI virtualB/U only; all physicalstatus/AXY/SP/application/banks/5SMC exact.',
            complete_realcaller_AXYP_SP_RAM_banks_orderedwrites_match_explicit_validoldcache_reference=True,
            scratch_only_readers='Only3readoperands inMegaManPaletteState, afterearlySTYMmPaletteIndex; no externalreaders. Poison0/255 converges before everyactualoutput.',
            intentional_scratch_result='Onlyfirst uncachedtier2append returnsindex2vs newlyskippedoldcachehitindex1; deadbefore nextread, not a broad mask.',
            cases_sha256=sha(a.output/'cases.json'),ownership_sha256=sha(a.output/'scratch-read-ownership.json'),tool_sha256=sha(__file__),
            limits='Finite assembledsourcecontrols. Existingcache reference intentionallypublishes the newlyqualifiedproducerstate, not an unchangeduncached trace claim. CompleteGameCore tail startsactual83ee with documentedfarOBJECTsavedbank; stagedactorsnotnaturalacquisition. LagNMI model is actualNmiDisable255 ISR, not native scheduling. No native recovery or actualnew378deadline pass.'))
        print((a.output/'proof.json').read_text())
    except BaseException as e:
        put(a.output/'failure.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc(),completed=[len(callers),len(life),len(poison),len(irqs)]))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
