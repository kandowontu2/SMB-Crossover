"""Compact actual-CPU default-ABI/timer controls; no native or capture output."""
from pathlib import Path
import sys,json,argparse,itertools,traceback,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from mario_luigi731_coefficients_v1 import make
from check_tmnt_render_oa import address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();O=a.output;O.mkdir(exist_ok=False,parents=True)
files=0;total=0
def put(n,v):
 global files,total
 raw=(json.dumps(v,indent=2)+'\n').encode();files+=1;total+=len(raw);assert files<=12 and total<=750000
 (O/n).write_bytes(raw)
b=scoped_load(a.candidate);old=scoped_load(a.baseline)
V={1:('ProtoVariant',2),3:('BillVariant',2),4:('Z2Variant',2),5:('Cv3Variant',4),9:('RlVariant',2),12:('DarkwingVariant',2),13:('KbVariant',2),14:('CdVariant',2),17:('M3Variant',2),18:('VvVariant',4),19:('TnVariant',4)}
def fresh(bundle,ch,mode,v):
 q=make(bundle,ch,mode);q.put(OperMode_Task=3,Player_Rel_XPos=96,Player_Pos_ForScroll=96,ScreenRight_PageLoc=1,ScreenRight_X_Pos=255,ScrollLock=1,NmiDisable=255)
 for n,z in V.values():q.set(n,0)
 if ch in V:q.set(V[ch][0],v)
 if ch==8:q.set('MarioSourceActive',1)
 for i in range(416):q.set('Block_Buffer_1',0x54 if i%208>=0xb0 else 0,i)
 return q
def step(q,bits):
 q.set('SavedJoypadBits',bits);c,_=q.invoke('PlayerCtrlRoutine');q.set('PreviousA_B_Buttons',bits&192);q.set('FrameCounter',(q.get('FrameCounter')+1)&255);return c
def state(q,c):return c.a,c.x,c.y,c.p,c.sp,bytes(q.m[:256])+bytes(q.m[512:32768]),q.m.banks
rows=[]
try:
 # Every preexisting source-qualified symbol is retained except explicit
 # removed private old menu labels and the genuine moved4B stomp policy.
 x,y=qualified(a.baseline),qualified(a.candidate);diff={str(k):[v,y.get(k)]for k,v in x.items()if y.get(k)!=v}
 allowed={str(('GuestWaterStompPolicy',)),str(('GuestGameRoutinesBridge','Run')),str(('_FARCALL_COUNT',))}
 for k in diff:
  assert k in allowed or k.startswith("('CheatsMenuInput',")or k.startswith("('QueueCheats',")or k.startswith("('CheatsPatchPage',"),k
 assert len(diff)==16,diff
 assert address(b,'GuestWaterStompPolicy')==0x8d2b
 assert old['raw'][:16]==b['raw'][:16]and old['raw'][16+128*8192:]==b['raw'][16+128*8192:]
 banks=[dict(bank=i,bytes=sum(x!=y for x,y in zip(old['raw'][16+i*8192:16+(i+1)*8192],b['raw'][16+i*8192:16+(i+1)*8192])))for i in range(128)if old['raw'][16+i*8192:16+(i+1)*8192]!=b['raw'][16+i*8192:16+(i+1)*8192]]
 assert [r['bank']for r in banks]==[20,63,77,125,126,127]
 put('layout-symbols.json',dict(passed=True,retained_qualified_symbols=len(x)-len(diff),legitimate_symbol_changes=diff,changed_banks=banks,new_RAM_bytes=0,header_CHR_exact=True,genuine_policy_relocation=True))
 for ch in range(20):
  for mode,v,bits in itertools.product([0,1],range(V.get(ch,('',1))[1]),[0,1,129]):
   qs=[fresh(z,ch,mode,v)for z in [old,b]]
   for q in qs:
    for i in range(12):step(q,0)
    q.put(CheatInvincible=0,SavedJoypadBits=bits)
   cp=[q.invoke('GuestGameRoutinesBridge')[0]for q in qs]
   assert state(qs[0],cp[0])==state(qs[1],cp[1]),(ch,mode,v,bits,'ABI/RAM/bank mismatch')
   d=cp[1].processorCycles-cp[0].processorCycles
   assert d==4,(ch,mode,v,bits,d)
   rows.append([ch,mode,v,bits,cp[0].processorCycles,d])
 put('default-off-real-wrapper.json',dict(passed=True,cases=len(rows),rows=rows,actual_entry='GuestGameRoutinesBridge',all_AXYP_SP_RAM_except_stack_and_final_banks_exact=True,cycles_added_each=4,limits='Source CPU legal synthetic floor arenas; no native frame/cadence claim.'))
 rows=[]
 q=Arena(b,0);q.m.page(0,126)
 pc=address(b,'CheatsInjuryTimer')
 for flags,inj,pv in itertools.product(range(32),range(256),[0x20,0x21,0x24,0x28,0x60,0xa0,0xe9,0x6d]):
  q.put(CheatInvincible=flags,InjuryTimer=inj);c=NesMPU(memory=q.m,pc=pc);c.a=27;c.x=42;c.y=89;c.p=pv;c.sp=0xfd;c.stPushWord(0x5aff)
  for i in range(12):
   if c.pc==0x5b00:break
   c.step()
  assert c.pc==0x5b00 and c.sp==0xfd
  val=inj|(flags&1)
  assert c.a==val and c.x==42 and c.y==89 and(c.p&0x4d)==(pv&0x4d)
  assert bool(c.p&0x80)==bool(val&128)and bool(c.p&2)==(val==0)
  if inj in [0,255]and flags in [0,1,31]:rows.append([flags,inj,pv,c.processorCycles])
 put('injury-full-domain.json',dict(passed=True,cases=32*256*8,all_input_CVDI_preserved=True,sampled_cycles=rows))
 # Observe the real bridge's prelude at genuine GameRoutines entry; execute
 # actual native countdown separately. Main/NMI scheduling is not modeled.
 def pre(q):
  s=b['syms']['GuestGameRoutinesBridge'];q.m.page(3,127);c=NesMPU(memory=q.m,pc=address(b,'GuestGameRoutinesBridge'));c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff)
  for i in range(30000):
   if c.pc==address(b,'GameRoutines')and q.m.banks[1]==1:return c
   c.step()
  raise AssertionError('prelude timeout')
 rows=[]
 for flag,digits in itertools.product([0,8],[[0,0,0],[1,0,0],[1,1,1],[4,0,0]]):
  q=fresh(b,0,0,0);q.put(CheatInvincible=flag,GameTimerCtrlTimer=0)
  q.array('GameTimerDisplay',digits);pre(q);ctrl=q.get('GameTimerCtrlTimer');q.invoke('RunGameTimer');got=[q.get('GameTimerDisplay',i)for i in range(3)]
  if flag:assert ctrl==2 and got==digits and q.get('GameEngineSubroutine')==8 and q.get('EventMusicQueue')==0
  else:assert ctrl==0 and(got!=digits or digits==[0,0,0])
  rows.append(dict(flag=flag,digits=digits,pre_ctrl=ctrl,after_digits=got,engine=q.get('GameEngineSubroutine')))
 put('actual-native-timer.json',dict(passed=True,cases=rows,scope='Genuine bridge prelude + real RunGameTimer, separated CPU calls; no NMI clock/cadence.'))
 put('proof.json',dict(passed=True,source_CPU_only=True,ROM=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),output_files=files+1,output_bytes_before_receipt=total))
 print(json.dumps({'passed':True,'wrapper_cases':222,'injury_cases':65536,'timer_cases':8}))
except Exception as e:
 put('failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),last_rows=rows[-3:]));raise
