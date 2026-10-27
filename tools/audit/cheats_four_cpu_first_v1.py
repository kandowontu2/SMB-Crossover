"""Private source-only four Cheats first assembled controls; no Mesen/PPU claim."""
from pathlib import Path
import sys,json,itertools,hashlib,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
D=Path(r'C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'current3b-cheats-four-draft-v5';O=P/'cpu-first-v1';O.mkdir(exist_ok=False)
def put(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n',newline='\n')
b=scoped_load(P/'candidate.nes');rows=[]
try:
 for flags,inj in itertools.product(range(32),[0,1,2,127,128,255]):
  q=Arena(b,0);q.put(CheatInvincible=flags,InjuryTimer=inj);c,t=q.invoke('CheatsInjuryTimer',a=27,x=42,y=89)
  assert c.a==(inj|(flags&1))and c.x==42 and c.y==89
  rows.append(dict(flags=flags,injury=inj,cycles=c.processorCycles))
 put('injury.json',dict(passed=True,cases=rows))
 rows=[]
 for flags,focus,bits in itertools.product(range(32),range(6),[4,8,128,64,16,1,2,32,0]):
  q=Arena(b,0);q.put(CheatInvincible=flags,CrossoverOptionsFocus=focus,CrossoverMenuPressed=bits,CheatStartLevel=0x20|11)
  c,t=q.invoke('CheatsSixInput');f=q.get('CrossoverOptionsFocus');v=q.get('CheatInvincible');lv=q.get('CheatStartLevel')
  if bits==64:assert q.get('CrossoverMenuState')==3 and f==2 and v==flags and lv==43
  elif bits in [4,8]:assert f==(focus+(1 if bits==4 else -1))%6 and v==flags
  elif bits in [128,16,1,2,32]:
   assert f==focus
   if focus==1:assert v==flags and lv==32|((11+(-1 if bits==2 else 1))&31)
   else:assert v==flags^[1,0,2,4,8,16][focus]and lv==43
  else:assert f==focus and v==flags and lv==43
  assert q.get('VRAM_Buffer1_Offset')in[0,44]
  rows.append([flags,focus,bits])
 put('menu-input.json',dict(passed=True,cases=len(rows),inputs=rows))
 rows=[]
 for flags,level,focus in itertools.product(range(32),[0,3,4,15,28,31],range(6)):
  q=Arena(b,0);q.put(CheatInvincible=flags,CheatStartLevel=level,CrossoverOptionsFocus=focus)
  c,t=q.invoke('CheatsSixQueue');a=address(b,'VRAM_Buffer1');raw=bytes(q.m[a:a+45]);assert q.get('VRAM_Buffer1_Offset')==44 and raw[44]==0
  for i,at in enumerate([0x2125,0x2165,0x21a5,0x21e5,0x2225,0x2265]):
   x=i*6;assert int.from_bytes(raw[x:x+2],'big')==at+17 and raw[x+2]==3
   expected=bytes([level//4+1,0x28,level%4+1])if i==1 else bytes([24,23,36])if flags&[1,0,2,4,8,16][i]else bytes([24,15,15])
   # Character map digittiles0..9, O=$18 N=$17 F=$0F -= $28.
   assert raw[x+3:x+6]==expected,(flags,level,focus,i,raw[x+3:x+6].hex(),expected.hex())
  assert raw[36:40]==bytes([0x21,0x23,0xcb,0x24])
  rows.append([flags,level,focus])
 put('menu-queue.json',dict(passed=True,cases=len(rows),VRAM_command_bytes=44,terminator_byte=1))
 rows=[]
 for char,variants in [(0,[0]),(1,[0,1]),(2,[0]),(3,[0,1]),(4,[0,1]),(5,[0,1,2,3]),(6,[0]),(7,[0]),(8,[0]),(9,[0,1]),(10,[0]),(11,[0]),(12,[0,1]),(13,[0,1]),(14,[0,1]),(15,[0]),(16,[0]),(17,[0,1]),(18,[0,1,2,3]),(19,[0,1,2,3])]:
  for mode,variant in itertools.product([0,1],variants):
   q=Arena(b,char);q.put(OperMode_Task=3,PlayerStatus=0,CrossoverBehaviorVersion=mode,VvAlive=1)
   for n in ['ProtoVariant','BillVariant','Z2Variant','Cv3Variant','RlVariant','DarkwingVariant','KbVariant','CdVariant','M3Variant','VvVariant','TnVariant']:
    if n in b['syms']:q.set(n,0)
   n={1:'ProtoVariant',3:'BillVariant',4:'Z2Variant',5:'Cv3Variant',9:'RlVariant',12:'DarkwingVariant',13:'KbVariant',14:'CdVariant',17:'M3Variant',18:'VvVariant',19:'TnVariant'}.get(char)
   if n:q.set(n,variant)
   cycles=[]
   for tick in range(18):
    q.set('GameEngineSubroutine',8);q.set('GuestPowerupActive',0)
    c,t=q.invoke('CheatsFullPower');cycles.append(c.processorCycles)
    if q.get('GuestPowerupActive'):q.set('PlayerStatus',q.get('GuestPowerupTarget'))
   row=dict(char=char,mode=mode,variant=variant,cycles=cycles,status=q.get('PlayerStatus'))
   if char<12:row.update(lo=q.get('InvOwnedLo',char),hi=q.get('InvOwnedHi',char),selected=q.get('InvSelected',char))
   if char==18:row.update(speed=q.get('VvSpeed'),gun=q.get('VvGun'),options=q.get('VvOptions'),shield=q.get('VvShield'))
   rows.append(row)
 put('full-power-smoke.json',dict(passed=True,cases=rows,limits='Actual helper/real grant and gear APIs; transformed state advance emulated only between calls, not native animation qualification. Expected per-owner assertions still required.'))
 put('proof.json',dict(passed=True,ROM=hashlib.sha256((P/'candidate.nes').read_bytes()).hexdigest()))
 print(json.dumps({'passed':True,'full_power_cases':len(rows)}))
except Exception as e:
 put('failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),last_rows=rows[-3:]));raise
