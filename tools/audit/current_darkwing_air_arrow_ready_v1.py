"""Prepare one3e5e controller-only route; no native or game modifications."""
from pathlib import Path
from argparse import Namespace
import json,re
from current_darkwing_air_arrow_prepare_v1 import Controller,campaign,ROM,EXPECTED,POLICY,put
from current_darkwing_arrow_route_source_v1 import scene,world
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_roster_compact_11_v1 import prepare,linked,lua,ROOT,sha

class AtWall(Controller):
 def __init__(self,top,wall):super().__init__(top);self.wall=wall
 def stable(self,q):
  if self.slot is None:return False
  i=self.slot;a=q.get('RgShotImpact',i)-1;sx=q.get('RgShotX',i)+256*q.get('RgShotPage',i)
  return(q.get('RgShotType',i)==6 and q.get('RgShotDir',i)==1 and q.get('SsMode',i)==0 and 0<=a<6
   and q.get('Enemy_Flag',a)==1 and q.get('Enemy_ID',a)==38 and q.get('Enemy_State',a)==32|i
   and self.wall<=sx+12<self.wall+32 and q.get('Enemy_X_Position',a)+256*q.get('Enemy_PageLoc',a)==sx-12
   and q.get('Enemy_Y_Position',a)==q.get('RgShotY',i)and q.get('RgShotY',i)<=self.top+20)

def pair(b,mode):
 q=scene(b);q.set('CrossoverBehaviorVersion',mode)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 for y in range(128,208,16):
  for x in[912,928]:q.set('Block_Buffer_1',(16 if x==912 else 17)if y==128 else(20 if x==912 else 21),x//256%2*208+(y-32)//16*16+x%256//16)
 ctrl=AtWall(144,736);stage='first';rows=[];events=[];tick=0;original=NesMPU.step
 names=['DwRecovery::Spawn','DwGiveItem','DwShotInit','DwAttachArrow']
 lookup={(address(b,n),(location(b,n)-16)//8192):n for n in names}
 def step(cpu):
  k=q.m.banks[(cpu.pc-32768)//8192]if cpu.pc>=32768 else-1;n=lookup.get((cpu.pc,k))
  if n:events.append(dict(update=tick,owner=n,pc=cpu.pc,bank=k,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),gas=q.get('DwGas'),mode=q.get('DwMode')))
  original(cpu)
 NesMPU.step=step
 try:
  for tick in range(400):
   # Following viewport is the disclosed CPU environment, never a rewrite of
   # a player/resource/consumer/Arrow or collision result.
   cam=max(632,world(q)-112);q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
   if stage=='first'and world(q)>=776:stage='basic-release'
   if stage=='basic-release':
    bits=1
    if q.get('DwMode')==0:stage='walk'
    elif not q.get('DwPrevious')&32:stage='basic-press';bits=33
   elif stage=='basic-press':
    bits=33
    if q.get('DwMode')==0:stage='walk';bits=1
   elif stage=='walk':
    bits=1
    if world(q)>=897 and q.get('Player_State')==0 and q.get('Player_X_Speed')==0:ctrl=AtWall(128,912);stage='second';bits=ctrl.buttons(q)
   else:bits=ctrl.buttons(q)
   q.put(SavedJoypadBits=bits);q.invoke('GameLoop')
   rows.append(dict(update=tick,stage=stage,phase=ctrl.phase,buttons=bits,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),previous=q.get('DwPrevious'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'),mode=q.get('DwMode'),hang=q.get('DwHang')))
   assert q.get('GameEngineSubroutine')==8 and q.get('MmDeathFlag')==0
   ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
   if world(q)>976 and q.get('Player_State')==0:break
 finally:NesMPU.step=original
 assert world(q)>976,('Two genuine Arrow crossings',rows[-8:])
 assert q.get('DwGas')==4 and q.get('DwAdaptor')==2
 assert sum(e['owner']=='DwRecovery::Spawn'for e in events)==1 and sum(e['owner']=='DwGiveItem'for e in events)==1
 shots=[e for e in events if e['owner']=='DwShotInit'];assert len(shots)==2 and all(e['state']!=0 for e in shots)
 assert any(r['stage']=='first'and r['hang']>=128 for r in rows)and any(r['stage']=='second'and r['hang']>=128 for r in rows)
 return dict(mode=mode,updates=len(rows),events=events,rows=rows,ending_gas=q.get('DwGas'),source_clock_note='GameLoop plus actual SamusFreezeUpdateScreen consumer; no actual PPU/NMI deadline/physical DMA model.')

def main():
 assert sha(ROM)==EXPECTED;sourceproof=ROOT/'build/darkwing_air_arrow_source_v1.json';s=json.loads(sourceproof.read_text());assert s['passed']and all(sha(Path(p))==v for p,v in s['bindings'].items())
 assert POLICY.is_file()and not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(',POLICY.read_text())
 b=scoped_load(ROM);paired=[pair(b,m)for m in[0,1]]
 pairedpath=ROOT/'build/darkwing_air_arrow_pair_source_v1.json';assert not pairedpath.exists()
 put(pairedpath,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,cases=paired,
  scope='Same earned inventory across typed64px then80px pipe. One actual recovery/physical grant10 gas, two airborne Arrow spends to7 then4, both real attached actor/hang/freshA/native platform landings. Input-only after initial typed terrain/player/cold inventory, except disclosed following viewport and VRAM-consumer environment. No native exact map reconstruction or fullclear assertion.',
  bindings={str(p):sha(p)for p in[Path(__file__),POLICY,sourceproof,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/audit/current_darkwing_air_arrow_prepare_v1.py']}))
 parent=ROOT/'build/verification/compact-3e5e-darkwing-hang-floor-v1';rp=parent/'ready.json';old=json.loads(rp.read_text())
 assert old['ROM_sha256']==EXPECTED and old['config']['policy'].endswith('current_roster_darkwing_gap_v6.lua')
 out=ROOT/'build/verification/compact-3e5e-darkwing-air-arrow-v7'
 prepare(Namespace(identity='darkwing',mode='easy',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=POLICY,replay=None))
 ready=out/'ready.json';z=json.loads(ready.read_text());run=out/'run.lua'
 observer=ROOT/'tools/audit/current_darkwing_resource_observer_v2.lua';cfg=old['passive_darkwing_resources']['config'];raw,syms,addr,loc,hook=linked(ROM)
 for n,v in cfg['ram'].items():assert addr(n)==v,('Real passive RAM owner',n)
 for n,h in cfg['hooks'].items():assert hook(h['name'])==h,('Real passive code owner',n)
 insertion='ROSTER_CONFIG.bass_close=dofile('+lua(observer.as_posix())+')(ROSTER_CONFIG.prefix,'+lua(cfg)+')\n'
 anchor='dofile('+lua((ROOT/'tools/audit/current_roster_compact_11_v1.lua').as_posix())+')\n';text=run.read_text();assert text.count(anchor)==1
 altered=text.replace(anchor,insertion+anchor);assert altered.replace(insertion,'',1)==text;run.write_text(altered,newline='\n')
 for n in['character','menu_index','variant_symbol','variant','mode_value','limit','capture_bytes','navigation','marker_names','smc_fields','dma_store_return','hooks']:
  assert z['config'][n]==old['config'][n],n
 assert z['config']['policy']==str(POLICY.resolve()).replace('\\','/')
 paths=[Path(__file__),POLICY,sourceproof,pairedpath,rp,parent/'result.json',parent/'darkwing-resources.csv',observer,run]
 paths+=list(parent.glob('*.log'))
 for p in paths:z['bindings'][str(p.resolve())]=sha(p)
 command=out/'command.json';put(command,z['command']);z['bindings'][str(command.resolve())]=sha(command)
 z.update(native_run=False,native_clear_or_timing_pass=False,input_only=True,source_cases=4,source_pair_cases=2,
  source_handoff=dict(single_source_sha256=sha(sourceproof),paired_source_sha256=sha(pairedpath),Lua_VM_executed=False),
  original_native_FALSE_preserved=True,passive_darkwing_resources=dict(ROM_sha256=EXPECTED,config=cfg,observer_literal=True,actual_RAM_and_hook_bytes_verified=True),
  controller_change='Only local typed64/80px pipe handling: genuine takeoff, B at live top-derived airborne height, exact new local stable Arrow/actor/hang ownership, acknowledged freshA jump, then default mode. Delegates unchanged gap_v6/arrow_v5 route elsewhere without advancing their Lua phases during this override.',
  limits='Source mirrors, not executed Lua/native/actual poll replay or full1-1 proof. Stable local source-owned Arrow required; globally valid/falling/released arrows do not establish a step. Unknown terrain/enemy/PPU/cadence outcomes keep all original finite/current native assertions. No game/default/settings/native changes.')
 put(ready,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items())
 print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),pair_source_sha256=sha(pairedpath),command=str(command)),indent=2))

if __name__=='__main__':main()
