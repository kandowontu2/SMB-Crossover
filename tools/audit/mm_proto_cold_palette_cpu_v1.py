"""Finite actual producer ABI, cold two-episode and complete NMI controls."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from current3cee_postdma_mask_cpu_v4 import run as nmi_run

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'root-current-roster-composition-v1'
C=D/'robot-cold-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def invoke(q,name,p=0x30):
    b=q.b;s=b['syms'][name];g=b['segs'][s['seg']];at=address(b,name);bank=(int(g['ooffs'],0)-16)//8192;window=(at-0x8000)//8192
    q.m.page(window,bank)
    if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
    q.m.writes=[];c=NesMPU(memory=q.m,pc=at);c.a,c.x,c.y,c.p,c.sp=0x5a,37,19,p,0xfd;c.stPushWord(0x5aff)
    for _ in range(100000):
        if c.pc==0x5b00:break
        c.step()
    else:raise AssertionError(('Timeout',name,hex(c.pc)))
    assert c.sp==0xfd
    return c


def application(q):return bytes(q.m[:0x100])+bytes(q.m[0x200:0x8000])
def palette(writes):
    result={};high=None;ptr=0;ctrl=0
    for at,v in writes:
        if at==0x2000:ctrl=v
        elif at==0x2006:
            if high is None:high=v
            else:ptr=((high<<8)|v)&0x3fff;high=None
        elif at==0x2007:
            a=ptr
            if 0x3f00<=a<0x4000:
                a=0x3f00+(a&31)
                if a in[0x3f10,0x3f14,0x3f18,0x3f1c]:a-=16
            result[a]=v;ptr=(ptr+(32 if ctrl&4 else 1))&0x3fff
    return result


def configured(b,char,variant=0,engine=0,offset=0,selected=0,guest=0,star=0,charge=0,charging=0,cache=0,tier=0):
    q=Arena(b,char);q.put(ProtoVariant=variant,RlVariant=variant,GameEngineSubroutine=engine,
        GuestPowerupActive=guest,StarInvincibleTimer=star,MmChargeFrames=charge,MmCharging=charging,
        SsLastPalette=cache,PlayerStatus=tier,VRAM_Buffer1_Offset=offset,OperMode_Task=3,
        AreaType=1,BackgroundColorCtrl=0,NmiDisable=255,MmLastPalette=0)
    q.set('InvSelected',selected,char)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    rows=[];flows=[]
    try:
        bs=[scoped_load(P/'candidate.nes'),scoped_load(C/'candidate.nes')]
        cases=[]
        for char in range(20):
            for engine,selected in itertools.product([0,8],[0,1]):cases.append(dict(char=char,engine=engine,selected=selected))
        for char,variant,tier,offset in itertools.product([1,9],[0,1],range(3),[0,25,64,65,237]):
            cases.append(dict(char=char,variant=variant,tier=tier,offset=offset))
        for flag, value in itertools.product(['guest','star','charge','charging'],[1,33,87]):
            for char,variant in[(1,0),(1,1),(9,0)]:cases.append(dict(char=char,variant=variant,**{flag:value}))
        for flags in range(64):
            pval=0x30|sum((1<<bit)for j,bit in enumerate([0,1,2,3,6,7])if flags>>j&1)
            cases.append(dict(char=1,variant=1,flags=pval))
        for spec in cases:
            settings={k:v for k,v in spec.items()if k!='flags'};q=[configured(b,**settings)for b in bs]
            c=[invoke(z,'X5LegacyGetPlayerColors',spec.get('flags',0x30))for z in q]
            assert [(z.a,z.x,z.y,z.p,z.sp)for z in c][0]==[(z.a,z.x,z.y,z.p,z.sp)for z in c][1],('AXYP',spec)
            ss=address(bs[0],'SsLastPalette')
            before,after=[application(z)for z in q]
            differences=[i for i,(x,y)in enumerate(zip(before,after))if x!=y]
            # app() removes the256-byte stack interval, so undo its index shift.
            real=[i if i<0x100 else i+0x100 for i in differences]
            final=q[1].get('VRAM_Buffer1_Offset')
            expected=spec['char']in[1,9]and spec.get('engine',0)==0 and not spec.get('selected',0)and not any(spec.get(k,0)for k in['guest','star','charge','charging'])and not(spec['char']==9 and spec.get('variant',0))and 19<=final<84
            assert real==([ss]if expected else[]),('RAM',spec,real,expected,final)
            if expected:assert q[1].get('SsLastPalette')==1
            a_w=[(at,v)for at,v in q[0].m.writes if not 0x100<=at<0x200]
            b_w=[(at,v)for at,v in q[1].m.writes if not 0x100<=at<0x200 and at!=ss]
            assert a_w==b_w,('Ordered writes',spec)
            assert q[0].m.banks==q[1].m.banks and q[0].m[0x1fe:0x200]==q[1].m[0x1fe:0x200]
            rows.append(dict(spec=spec,intentional_cache_publication=expected,old_cycles=c[0].processorCycles,new_cycles=c[1].processorCycles,delta=c[1].processorCycles-c[0].processorCycles))
        # Actual cold and next-normal palette producers, then the entire linked
        # NMI/audio/input pipeline. This is a configured producer-chain fixture,
        # not a claim to execute every instruction of two complete Main frames.
        for char,variant,tier in[(1,0,0),(1,1,0),(1,1,2),(9,0,0)]:
            qs=[];details=[]
            for b in bs:
                q=configured(b,char,variant=variant,tier=tier);clocks=[]
                for name in['GetPlayerColors','MegaManPaletteState']:
                    c=invoke(q,name);clocks.append((name,c.processorCycles))
                if char==1 and variant:invoke(q,'ProtoFixQueuedPalette')
                initial_offset=q.get('VRAM_Buffer1_Offset');initial_ss=q.get('SsLastPalette')
                q.set('GameEngineSubroutine',8)
                for name in['SpecialPalette','MegaManPaletteState']:
                    c=invoke(q,name);clocks.append((name,c.processorCycles))
                if char==1 and variant:invoke(q,'ProtoFixQueuedPalette')
                size=q.get('VRAM_Buffer1_Offset');packet=list(q.m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+size])
                q.array('VRAM_Buffer1',packet+[32,122,3,4,0,0,0]);q.set('VRAM_Buffer1_Offset',size+6)
                q.put(NmiDisable=0,DisableScreenFlag=0,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,
                    ReloadCHRBank=1,X5WideChrActive=1,VRAM_Buffer_AddrCtrl=0,SmFreezePalettePending=0,PnBombCapturePending=0,InvHudActive=0,X5HudChrUpper=0,SsChrActive=0)
                q.array('CurrentCHRBank',[0,20,21,22,23,24,25,26,4,5,6,7]);q.array('X5ChrMode',[129]+[0]*11)
                qs.append(q);details.append(dict(initial_offset=initial_offset,initial_cache=initial_ss,final_palette_packet_bytes=size,packet=packet,producer_cycles=clocks))
            assert details[0]['initial_offset']==details[1]['initial_offset']==25
            assert details[0]['final_palette_packet_bytes']==50 and details[1]['final_palette_packet_bytes']==25
            out=[nmi_run(b,q,stall=0)for b,q in zip(bs,qs)]
            assert out[0]['regs']==out[1]['regs']and out[0]['banks']==out[1]['banks']and out[0]['serial']==out[1]['serial']and out[0]['reads']==out[1]['reads']
            assert palette(out[0]['writes'])==palette(out[1]['writes'])
            flows.append(dict(char=char,variant=variant,tier=tier,details=details,
                full_NMI_old=out[0]['cycles'],full_NMI_new=out[1]['cycles'],full_NMI_delta=out[1]['cycles']-out[0]['cycles'],
                final_PPU_palette_nametable_values_exact=True,source_register_bank_input_read_outcomes_exact=True))
        put(a.output/'cases.json',rows);put(a.output/'cold-producer-NMI.json',flows)
        put(a.output/'proof.json',dict(passed=True,native_run=False,baseline_ROM_sha256=sha(P/'candidate.nes'),candidate_ROM_sha256=sha(C/'candidate.nes'),
            actual_complete_legacy_producer_cases=len(rows),all64_physical_flag_patterns=True,
            full_AXYP_SP_live_stack_application_RAM_banks_and_ordered_writes_exact_except_declared_cache=True,
            intent_only='SsLastPalette becomes1 only after qualified cold robot default full19-byte palette append.',
            cold_two_episode_producer_chains=len(flows),entire_NMI_audio_input_pipeline_cases=len(flows),
            producer_added_cycles=[min(r['delta']for r in rows),max(r['delta']for r in rows)],
            full_NMI_cycle_deltas=[r['full_NMI_delta']for r in flows],
            cases_sha256=sha(a.output/'cases.json'),flows_sha256=sha(a.output/'cold-producer-NMI.json'),tool_sha256=sha(__file__),
            limits='Configured actual producers and complete NMI; no full two-GameLoop/native recovery claim. Synthetic oversized/wrapping initial buffers are guard controls, not legal gameplay. Additional helper stack writes below finalSP are dead callee slots; live caller bytes exact. IRQ/lifecycle/ordinary/canonical controls remain separate.'))
        print((a.output/'proof.json').read_text())
    except BaseException as e:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(e),traceback=traceback.format_exc(),cases_completed=len(rows),flows_completed=len(flows)))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
