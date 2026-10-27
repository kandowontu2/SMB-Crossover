"""Compact source-CPU page, legal carried-choice, persistence and gate controls.
No native PPU/DMA, animation, timing, controller-route or audio-fidelity claim.
"""
from pathlib import Path
import sys,json,argparse,hashlib,itertools,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
b=scoped_load(a.candidate);records=[]
def put(n,v):
 raw=(json.dumps(v,indent=2)+'\n').encode();assert len(raw)<160000
 (a.output/n).write_bytes(raw)
def cpu_call(q,name,pv=0x30):
 s=b['syms'][name];g=b['segs'][s['seg']];bank=(int(g['ooffs'],0)-16)//8192;pc=address(b,name);w=(pc-0x8000)//8192;q.m.page(w,bank)
 if w in[1,2]:q.set('CurrentBank'if w==1 else'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.p=pv;c.sp=0xfd;c.stPushWord(0x5aff);q.m.writes=[];bus=[]
 for i in range(100000):
  if c.pc==0x5b00:assert c.sp==0xfd;return c,bus
  at=c.pc;mark=len(q.m.writes);oldp=c.p;c.step()
  bus.extend([dict(PC=at,address=x,value=y,P=oldp)for x,y in q.m.writes[mark:]if x in[0x2006,0x2007]])
 raise AssertionError(('timeout',name,hex(c.pc)))
try:
 # Compare the complete direct PPU address/data store stream, including the
 # parent AUDIO TEST row22 blank and independent B-back row23. CPU bus only.
 def tiles(text):return bytes(36 if x==' 'else 40 if x=='-'else ord(x)-ord('A')+10 for x in text)
 labels=['INVINCIBLE            ','START LEVEL           ','MID-AIR JUMPS         ','SCREEN WRAP           ','FREEZE TIMER          ','FULL POWER            ']
 def seq(at,data):return[(0x2006,at>>8),(0x2006,at&255)]+[(0x2007,z)for z in data]
 expected=seq(0x20cb,tiles('CHEATS '))+seq(0x2100,[36]*608)
 for at,text in zip([0x2125,0x2165,0x21a5,0x21e5,0x2225,0x2265],labels):expected+=seq(at,tiles(text))
 expected+=seq(0x22ea,tiles('B - BACK'))
 for pv in[0x20,0x21,0x24,0x28,0x60,0xa0,0xe9,0x6d]:
  q=Arena(b,0);q.put(DisableScreenFlag=1,NmiDisable=255);c,bus=cpu_call(q,'CheatsSixPage',pv)
  assert [(r['address'],r['value'])for r in bus]==expected
  assert all(r['P']&4 for r in bus) and c.p&0xcf==pv&0xcf
  records.append(dict(input_P=pv,cycles=c.processorCycles,PPUADDR_stores=sum(x==0x2006 for x,y in expected),PPUDATA_stores=sum(x==0x2007 for x,y in expected)))
 put('page.json',dict(passed=True,cases=records,entire_ordered_bus_exact=True,rows8_through26_cleared=True,row22_parent_text_removed=True,own_back_row23=True,IRQ_masked_for_every_direct_store=True,limits='Expected forced blank is a caller precondition; model has no real PPU clock/address-latch/DMA/enable timing.'))
 # Legal exclusive guns and selection must survive grants of compatible gear.
 records=[]
 for ch,mask,ids in[(2,0x18,[3,4]),(3,0x3c,[2,3,4,5]),(5,0x7c,[2,3,4,5,6]),(10,0x3e,[1,2,3,4,5])]:
  for item in ids:
   q=Arena(b,ch);q.put(OperMode_Task=3,PlayerStatus=1);q.set('InvOwnedLo',1|(1<<item),ch);q.set('InvSelected',item,ch)
   q.invoke('CheatsFullPower');assert q.get('InvOwnedLo',ch)&mask==1<<item and q.get('InvSelected',ch)==item,(ch,item,q.get('InvOwnedLo',ch),q.get('InvSelected',ch))
   q.set('InvDirty',0);q.set('Square2SoundQueue',0);c,_=q.invoke('CheatsFullPower');assert q.get('InvDirty')==0 and q.get('InvSelected',ch)==item
   records.append(dict(char=ch,retained_item=item,exclusive_owned=q.get('InvOwnedLo',ch)&mask,steady_cycles=c.processorCycles))
 # This copy is intentionally a source maximum table, not an invented pool.
 assert b['raw'][location(b,'CheatsInventoryMax::AmmoMax'):location(b,'CheatsInventoryMax::AmmoMax')+192]==b['raw'][location(b,'InvMaxAmmo'):location(b,'InvMaxAmmo')+192]
 put('exclusive-inventory.json',dict(passed=True,cases=records,all192_source_max_ammo_bytes_exact=True,no_repeated_dirty_on_already_full=True))
 records=[]
 for variant in[1,2,3]:
  for carried in([0,1,2,3]if variant<3 else[0]):
   q=Arena(b,5);q.put(Cv3Variant=variant);q.set('Cv3Subweapon',carried,variant-1);q.invoke('CheatsFullPower');got=q.get('Cv3Subweapon',variant-1)
   assert got==(carried or (1 if variant<3 else 0))
   records.append(dict(char='CV3',variant=variant,prior=carried,after=got))
 for carried in range(4):
  q=Arena(b,12);q.put(DarkwingVariant=1,DwAdaptor=carried);q.invoke('CheatsFullPower');got=q.get('DwAdaptor');assert got==(carried or 2)
  assert q.get('DwHealth')==4 and q.get('DwGas')==99
  q.set('Square2SoundQueue',0);q.invoke('CheatsFullPower');assert q.get('Square2SoundQueue')==0
  records.append(dict(char='Darkwing',prior=carried,after=got))
 for form in range(2,8):
  q=Arena(b,17);q.set('M3Form',form);q.invoke('CheatsFullPower');assert q.get('M3Form')==form
  records.append(dict(char='SMB3',retained_form=form))
 put('native-carried-choice.json',dict(passed=True,cases=records,limits='Initialized source helper semantics; subsequent actual gameplay/native visual checks remain required.'))
 records=[]
 for flags in range(32):
  q=Arena(b,0);q.put(CheatInvincible=flags,CheatStartLevel=43);q.invoke('CrossoverInit');assert q.get('CheatInvincible')==q.get('CheatStartLevel')==0
  for ch in[0,1,3,8,17,19]:
   q=Arena(b,ch);q.put(CheatInvincible=flags,CheatStartLevel=43);q.invoke('MegaManResetArea');assert q.get('CheatInvincible')==flags and q.get('CheatStartLevel')==43
  records.append(dict(prior_flags=flags,reset_default=0,area_reset_owners=[0,1,3,8,17,19]))
 put('persistent-flags.json',dict(passed=True,actual_power_reset_calls=32,actual_area_reset_calls=192,cases=records,new_persistent_bytes=0))
 records=[]
 for op,task,engine,pause in itertools.product([0,1,2],[0,3],[8,9,11],[0,1]):
  q=Arena(b,0);q.put(OperMode=op,OperMode_Task=task,GameEngineSubroutine=engine,GamePauseStatus=pause);c,_=q.invoke('CheatsActive');expected=(op==1 and task==3 and engine==8 and pause==0)
  assert bool(c.p&1)==expected
  records.append([op,task,engine,pause,expected])
 put('active-gate.json',dict(passed=True,cases=records,limits='Actual compiled admission helper; transition/render/menu parent composition still required.'))
 put('proof.json',dict(passed=True,ROM=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),source_CPU_only=True,output_files=6))
 print(json.dumps(dict(passed=True)))
except Exception as e:
 put('failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),last_rows=records[-3:]));raise
