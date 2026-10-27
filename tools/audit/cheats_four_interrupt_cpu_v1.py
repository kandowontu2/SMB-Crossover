"""Finite source-CPU IRQ/NMI ownership controls for cold Cheats helpers.
No PPU clock, DMC fetch/waveform or native hardware qualification.
"""
from pathlib import Path
import argparse,sys,json,hashlib,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
b=scoped_load(a.candidate);records=[];seen=set();irq_count=nmi_count=masked=0;minsp=255
names=['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC']
smc=[]
for n in names:
 z=address(b,n)+1;smc.append(z)
 if n=='FarcallJmpTarget_SMC':smc.append(z+1)

def put(n,v):
 raw=(json.dumps(v,indent=2)+'\n').encode();assert len(raw)<125000
 (a.output/n).write_bytes(raw)
def snapshot(q,c):return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,bytes(q.m[:8]),bytes(q.m[z]for z in smc),q.get('CurrentBank'),q.get('CurrentBankC'))
def run(name,char,variant_name=None,variant=0,kind='normal'):
 global irq_count,nmi_count,masked,minsp
 q=Arena(b,char);q.put(OperMode_Task=3,GameEngineSubroutine=8,AreaType=1,PlayerStatus=1,Player_State=2,Player_Y_HighPos=1,Player_Y_Position=237,Player_Y_Speed=5,NmiDisable=255,DisableScreenFlag=1,SavedJoypadBits=128,PreviousA_B_Buttons=0)
 if variant_name:q.set(variant_name,variant)
 if kind=='queue':q.put(CrossoverOptionsFocus=5,CheatInvincible=31)
 s=b['syms'][name];g=b['segs'][s['seg']];bank=(int(g['ooffs'],0)-16)//8192;pc=address(b,name);window=(pc-0x8000)//8192;q.m.page(window,bank)
 if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff);steps=0;entry=irq_count+nmi_count;local_min=255
 while c.pc!=0x5b00:
  steps+=1;assert steps<100000,(name,'foreground timeout',hex(c.pc))
  physical=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
  key=(physical,c.pc)
  if physical==63 and key not in seen:
   seen.add(key)
   for which in ['irq','nmi']:
    if which=='irq'and c.p&4:masked+=1;continue
    before=snapshot(q,c);oldbanks=list(q.m.banks);mark=len(q.m.writes)
    if which=='irq':q.m[0x5204]=128;c.irq();irq_count+=1
    else:c.nmi();nmi_count+=1
    for j in range(30000):
     local_min=min(local_min,c.sp);minsp=min(minsp,c.sp)
     if c.pc==before[0]and c.sp==before[5]:break
     c.step()
    else:raise AssertionError((name,which,'interrupt timeout',hex(c.pc),c.sp))
    assert snapshot(q,c)==before,(name,which,hex(before[0]),'AXYP/SP/R0..7/fiveSMC/shadow mismatch',before,snapshot(q,c))
    expected=[oldbanks[0],before[-2]&127,before[-1]&127,oldbanks[3]]
    assert q.m.banks==expected,(name,which,hex(before[0]),oldbanks,q.m.banks,expected)
    if which=='nmi':assert not any(at in[0x2006,0x2007]for at,v in q.m.writes[mark:]),'screen-off lag NMI touched PPU address/data'
  c.step();local_min=min(local_min,c.sp);minsp=min(minsp,c.sp)
 assert c.sp==0xfd,(name,c.sp)
 records.append(dict(name=name,char=char,variant=variant,foreground_steps=steps,interrupts_added=irq_count+nmi_count-entry,min_SP=local_min))
try:
 for case in [('CheatsSixInput',0,None,0,'queue'),('CheatsSixQueue',0,None,0,'queue'),('CheatsSixPage',0,None,0,'page'),('CheatsAirJump',19,None,0,'normal'),('CheatsWrapPlayer',0,None,0,'normal'),('CheatsFullPower',1,None,0,'normal'),('CheatsFullPower',18,'VvVariant',2,'normal')]:run(*case)
 put('proof.json',dict(passed=True,source_CPU_only=True,ROM=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),cases=records,unique_new_helper_boundaries=len(seen),actual_IRQs=irq_count,actual_lag_screen_off_NMIs=nmi_count,IRQ_masked_page_boundaries=masked,minimum_SP=minsp,AXYP_SP_R0_R7_fiveSMC_and_shadow_exact=True,hardware_A_C_restore_to_committed_shadow=True,screen_off_lag_NMI_PPUDATA_PPUADDR_untouched=True,limits='Finite source execution in Memory model; no NMI/PPU timing, sprite/OAM hardware, real DMC requests/fetches, waveform or campaign. E125 mirror byte layout is separately bound, not an active-DMC interrupt test.'))
 print(json.dumps({'passed':True,'boundaries':len(seen),'IRQs':irq_count,'NMIs':nmi_count,'min_SP':minsp}))
except Exception as e:
 put('failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),cases=records,unique_boundaries=len(seen),IRQs=irq_count,NMIs=nmi_count));raise
