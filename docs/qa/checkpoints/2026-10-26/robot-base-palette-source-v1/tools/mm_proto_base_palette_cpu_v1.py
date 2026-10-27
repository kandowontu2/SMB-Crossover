"""Completed-producer ABI and exact redundant-body palette source controls."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback
from mm_proto_cold_palette_cpu_v1 import configured,invoke,application,palette
from current3cee_postdma_mask_cpu_v4 import run as nmi_run
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'robot-cold-palette-candidate-v2';C=D/'robot-base-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def diffs(qs):
    aa,bb=[application(q)for q in qs]
    return [i if i<256 else i+256 for i,(a,b)in enumerate(zip(aa,bb))if a!=b]


def nmi_seed(q):
    q.put(NmiDisable=0,DisableScreenFlag=0,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,
        ReloadCHRBank=1,X5WideChrActive=1,VRAM_Buffer_AddrCtrl=0,SmFreezePalettePending=0,
        PnBombCapturePending=0,InvHudActive=0,X5HudChrUpper=0,SsChrActive=0)
    q.array('CurrentCHRBank',[0,20,21,22,23,24,25,26,4,5,6,7]);q.array('X5ChrMode',[129]+[0]*11)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);direct=[];flows=[]
    try:
        bs=[scoped_load(x/'candidate.nes')for x in[P,C]]
        specs=[dict(char=ch,engine=e,selected=s)for ch,e,s in itertools.product(range(20),[0,8],[0,1])]
        specs += [dict(char=1,variant=v,mode=m,tier=t,charge=f,charging=c,engine=8)
                  for v,m,t,f,c in itertools.product([0,1],[0,1],range(3),[0,1,32,33,48,87],[0,1])]
        specs += [dict(char=1,variant=v,offset=o,mm=mm,tier=t,engine=8)
                  for v,o,mm,t in itertools.product([0,1],[0,25,64,65,237],[0,1,2,8],[0,2])]
        specs += [dict(char=1,variant=v,engine=8,**{n:z})for v,n,z in itertools.product([0,1],['star','guest','hurt'],[1,4,255])]
        for v,m,t,flag in itertools.product([0,1],[0,1],range(3),range(64)):
            status=0x30|sum(1<<bit for j,bit in enumerate([0,1,2,3,6,7])if flag>>j&1)
            specs.append(dict(char=1,variant=v,mode=m,tier=t,engine=8,charge=1,charging=1,flags=status))
        for spec in specs:
            settings={k:v for k,v in spec.items()if k not in['mode','mm','hurt','flags']}
            qs=[configured(b,**settings)for b in bs]
            for q in qs:q.put(CrossoverBehaviorVersion=spec.get('mode',1),MmLastPalette=spec.get('mm',0),GuestHurtTicks=spec.get('hurt',0))
            cpus=[invoke(q,'X5GetPlayerColors',spec.get('flags',0x30))for q in qs]
            assert[(c.a,c.x,c.y,c.p,c.sp)for c in cpus][0]==[(c.a,c.x,c.y,c.p,c.sp)for c in cpus][1],('producerABI',spec)
            final=qs[1].get('VRAM_Buffer1_Offset')
            expected=spec['char']==1 and not spec.get('selected',0)and not spec.get('guest',0)and not spec.get('star',0)and spec.get('charge',0)<33 and 19<=final<84
            want=2 if spec.get('tier',0)==2 else 1
            assert qs[1].get('MmLastPalette')==(want if expected else qs[0].get('MmLastPalette'))
            changed=diffs(qs);mm=address(bs[1],'MmLastPalette')
            assert changed==([mm]if expected and qs[0].get('MmLastPalette')!=want else[]),('producerRAM',spec,changed)
            old=[(at,v)for at,v in qs[0].m.writes if not 0x100<=at<0x200]
            new=[(at,v)for at,v in qs[1].m.writes if not 0x100<=at<0x200 and not(expected and at==mm)]
            assert old==new,('orderedproducerwrites',spec)
            assert qs[0].m.banks==qs[1].m.banks and qs[0].m[0x1fe:0x200]==qs[1].m[0x1fe:0x200]
            direct.append(dict(spec=spec,cache_published=expected,producer_delta=cpus[1].processorCycles-cpus[0].processorCycles))
        # Real complete palette+graphics consumers, with the actual native HUD
        # packet that precedes the failed378 refresh. No queue compaction.
        for variant,mode,tier,charge in itertools.product([0,1],[0,1],range(3),[0,1,32]):
            qs=[];detail=[]
            for b in bs:
                q=configured(b,1,variant=variant,engine=8,tier=tier,charge=charge,charging=1,cache=0)
                q.put(CrossoverBehaviorVersion=mode,InvDirty=1,DisableScreenFlag=0,GuestHurtTicks=0)
                clocks=[]
                for name in['InventoryHud','SpecialPalette','PlayerGfxHandler']:
                    cpu=invoke(q,name);clocks.append(dict(name=name,cycles=cpu.processorCycles,regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp]))
                size=q.get('VRAM_Buffer1_Offset');packet=list(q.m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+size+1])
                qs.append(q);detail.append(dict(packet=packet,packet_bytes=size,clocks=clocks,MmPaletteIndex=q.get('MmPaletteIndex'),MmLastPalette=q.get('MmLastPalette')))
            assert detail[0]['packet_bytes']==53 and detail[1]['packet_bytes']==47
            assert detail[0]['packet'][:47]==detail[1]['packet'][:47] and detail[1]['packet'][47]==0
            assert detail[0]['packet'][47:]==[63,17,3,*detail[0]['packet'][44:47],0]
            # FullPlayerGfxHandler AXYP can expose its private skipped-queue X;
            # bind its actual return before the separate real continuation test.
            assert detail[0]['clocks'][-1]['regs'][0]==detail[1]['clocks'][-1]['regs'][0]
            assert qs[0].get('MmLastPalette')==qs[1].get('MmLastPalette')
            assert detail[0]['MmPaletteIndex']==(2 if tier==2 else 0)
            assert detail[1]['MmPaletteIndex']==(1 if tier==2 else 0)
            for q in qs:nmi_seed(q)
            outs=[nmi_run(b,q,stall=0)for b,q in zip(bs,qs)]
            for k in['regs','banks','serial','reads']:assert outs[0][k]==outs[1][k],(k,variant,mode,tier,charge)
            assert palette(outs[0]['writes'])==palette(outs[1]['writes'])
            flows.append(dict(variant=variant,mode=mode,tier=tier,charge=charge,details=detail,
                whole_NMI_old=outs[0]['cycles'],whole_NMI_new=outs[1]['cycles'],NMI_delta=outs[1]['cycles']-outs[0]['cycles'],
                final_PPU_values_exact=True,source_MmPaletteIndex_tier2_dead_result_delta=[2,1]if tier==2 else None))
        put(a.output/'direct.json',direct);put(a.output/'flows.json',flows)
        put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,
            baseline_ROM_sha256=sha(P/'candidate.nes'),candidate_ROM_sha256=sha(C/'candidate.nes'),
            full_public_producer_cases=len(direct),all64physicalflagpatterns_EasyHard_Proto_tiers=True,
            full_producer_AXYP_SP_livecallerstack_application_RAM_banks_orderedwrites_exact_except_MmLastPalette=True,
            whole_actual_HUD_SpecialPalette_PlayerGfx_and_NMI_cases=len(flows),
            NMI_deltas=sorted(set(x['NMI_delta']for x in flows)),
            producer_delta=[min(x['producer_delta']for x in direct),max(x['producer_delta']for x in direct)],
            final_completeNMI_regs_banks_input_reads_and_PPU_values_exact=True,
            exact_scoped_dead_MmPaletteIndex_difference='For tier2 firstskippedqueue finalindex1vsoldappend2; nextcall earlySTY overwrites it before every source read. Separate caller/reader proof required; no broad RAM mask.',
            direct_sha256=sha(a.output/'direct.json'),flows_sha256=sha(a.output/'flows.json'),tool_sha256=sha(__file__),
            limits='Source configured producers/graphics and completeNMI, not fullMain/native recovery. Intentional6-byte redundantqueue removal changes deadqueue contents/offset and parserpointer; no hidden ordered-APU/channel/state relaxation. IRQ/lifecycle/realcaller/ordinary controls separate.'))
        print((a.output/'proof.json').read_text())
    except BaseException as e:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(e),traceback=traceback.format_exc(),direct_completed=len(direct),flows_completed=len(flows)))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
