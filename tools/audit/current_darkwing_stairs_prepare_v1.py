"""One source-controlled stair/overhead input successor and exactee ready."""
from pathlib import Path
from argparse import Namespace
import csv,json,re
from current_darkwing_arrow_route_source_v1 import scene,world,block
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import prepare,linked,lua,ROOT,sha,png
ROM=ROOT/'build/roster-20261028-fixes.nes'
EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
POLICY=ROOT/'tools/playthroughs/current_roster_darkwing_stairs_v8.lua'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
SOLID=lambda t:t not in[0,35,38,194,195]
STAIRS=[dict(begin=2080,peak=2192,edge=2208,far=2240,finish=2304),dict(begin=2336,peak=2432,edge=2448,far=2480,finish=2544)]

def compiled_map(b):
 q=Arena(b,12);q.put(DarkwingVariant=1,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0);q.invoke('GetAreaDataAddrs')
 assert q.get('AreaDataLow')+256*q.get('AreaDataHigh')==address(b,'L_GroundArea6')+2
 q.array('AreaObjectLength',[255]*3);columns={}
 for col in range(162):
  q.put(CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32);q.invoke('AreaParserCore')
  columns[col]=[q.get('Block_Buffer_1',(col%32//16)*208+row*16+col%16)for row in range(13)]
 for s in STAIRS:
  assert columns[s['peak']//16][7]==columns[s['far']//16][7]==97 and not SOLID(columns[s['edge']//16][7])
 return columns

def source(b,cols,mode):
 q=scene(b);q.put(CrossoverBehaviorVersion=mode,Player_X_Position=32,Player_PageLoc=8,MmOldX=32,Player_Y_Position=176,ScrollLock=1)
 # Environment: native parser-produced logical cells for pages8/9, initial
 # player2080/176. No inventory, acquired resources or private motion seeds.
 q.array('Block_Buffer_1',[0]*416)
 for col in range(128,160):
  for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 phase='climb';which=0;rows=[];landings=[];jumps=[]
 for tick in range(700):
  x,y=world(q),q.get('Player_Y_Position');ground=q.get('Player_State')==0;prev=q.get('DwPrevious')
  if which<2 and x>=STAIRS[which]['finish']:which+=1;phase='climb'
  bits=1
  if which<2 and x>=STAIRS[which]['begin']:
   s=STAIRS[which]
   if phase=='climb-air'and ground:phase='climb'
   if phase in['climb','climb-air']and x>=s['peak']and y+32<=144:phase='land'
   if phase=='land':
    bits=1 if x<s['peak']+2 else 2 if x>s['peak']+6 else 0
    if ground and y+32<=144 and not prev&128:
     landings.append(dict(which=which,x=x,y=y,previous=prev,update=tick));phase='cross';bits=129
   elif phase=='cross':
    if ground and x>=s['far']-8:phase='walkout'
    bits=129
   elif phase=='walkout':bits=1
   elif phase=='climb-air':bits=129
   elif ground and(SOLID(block(q,x+24,y+8))or SOLID(block(q,x+24,y+24)))and not prev&128:phase='climb-air';bits=129
  cam=max(1968,x-112);q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
  oldstate=q.get('Player_State');q.put(SavedJoypadBits=bits);q.invoke('GameLoop')
  row=dict(update=tick,which=which,phase=phase,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),buttons=bits,previous=q.get('DwPrevious'),fresh=q.get('ScFresh'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor'));rows.append(row)
  if oldstate==0 and row['state']==1 and q.get('Player_Y_Speed')>=128:jumps.append(row)
  assert q.get('GameEngineSubroutine')==8 and q.get('MmDeathFlag')==0,('Real source death/transition',row)
  ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
  if world(q)>=2550 and q.get('Player_State')==0:break
 assert world(q)>=2550 and len(landings)==2,('Actual stair landing/crossing',landings,rows[-8:])
 assert all(s['peak']<=r['x']<=s['peak']+6 and r['y']==112 and not r['previous']&128 for s,r in zip(STAIRS,landings))
 assert all(r['gas']==r['adaptor']==0 for r in rows)
 return dict(mode=mode,updates=len(rows),landings=landings,jumps=jumps,rows=rows)

def overhead(b,cols,mode):
 q=scene(b);q.put(CrossoverBehaviorVersion=mode,Player_X_Position=218,Player_PageLoc=5,MmOldX=218,Player_Y_Position=176,ScreenLeft_X_Pos=106,ScreenLeft_PageLoc=5,ScreenRight_X_Pos=105,ScreenRight_PageLoc=6)
 q.array('Block_Buffer_1',[0]*416)
 for col in range(80,112):
  for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 x,y=world(q),q.get('Player_Y_Position');head=any(SOLID(block(q,x+dx,y-20))for dx in[16,32]);body=any(SOLID(block(q,x+dx,y+dy))for dx in[16,32]for dy in[8,24]);assert head and not body
 rows=[]
 for tick in range(40):
  q.put(SavedJoypadBits=1);q.invoke('GameLoop');rows.append(dict(update=tick,x=world(q),y=q.get('Player_Y_Position'),gas=q.get('DwGas'),adaptor=q.get('DwAdaptor')))
  ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
 assert world(q)>1536 and all(r['y']==176 and r['gas']==r['adaptor']==0 for r in rows)
 return dict(mode=mode,head_height_only=True,forward_body_clear=True,rows=rows,limits='Native v7 really had earnedgas4. This source walk starts cold0; it proves the compiled overhead permits Right, not a reenactment of unlogged native actor/physics RAM or resource state.')

def main():
 assert sha(ROM)==EXPECTED;oldrom=ROOT/'build/darkwing_hang_floor.nes';assert sha(oldrom)=='3e5ee17fb7cc0413df4b758c94499ace1f33d8b66dd519fcdb92959e79b2ac1d'
 assert ROM.read_bytes()[16+67*8192:16+68*8192]==oldrom.read_bytes()[16+67*8192:16+68*8192]
 b=scoped_load(ROM);cols=compiled_map(b);sources=[source(b,cols,m)for m in[0,1]];heads=[overhead(b,cols,m)for m in[0,1]]
 parent=ROOT/'build/verification/compact-3e5e-darkwing-air-arrow-v7';rp=parent/'ready.json';old=json.loads(rp.read_text());assert all(sha(Path(p))==v for p,v in old['bindings'].items())
 rows=list(csv.DictReader((parent/'trace.csv').open()));r=lambda f:next(q for q in rows if int(q['frame'])==f)
 assert(r(3097)['x'],r(3097)['y'],r(3097)['state'])==('2152','144','0')and(r(3156)['x'],r(3156)['y'])==('2225','176')
 proof=ROOT/'build/darkwing_stairs_source_v1.json';assert not proof.exists()
 put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,same_3e5e_bank67=True,source_cases=sources,overhead_cases=heads,
  genuine_parser_columns={str(col):value for col,value in cols.items()if 90<=col<=96 or 130<=col<=160},
  scope='Actual compiled GetAreaDataAddrs(1-1 pointer25)/AreaParserCore-produced cells; typed initial player/camera/cold inventory/no enemy stream, then inputs only apart from following camera/actual VRAM consumer. Same source body/stair collision, not exact unlogged native RAM, PPU, Lua polling or fullroute proof.',
  preserved_native_false=dict(result_sha256=sha(parent/'result.json'),lower_landing=r(3097),old_top_pass=r(3129),first_bottom_landing=r(3156)),
  bindings={str(p):sha(p)for p in[Path(__file__),POLICY,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'src/level_tiles.s',rp,parent/'trace.csv',parent/'inputs.csv',parent/'result.json',ROOT/'tools/audit/current_darkwing_arrow_route_source_v1.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']}))
 out=ROOT/'build/verification/compact-ee1152-darkwing-stairs-v8';prepare(Namespace(identity='darkwing',mode='easy',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=POLICY,replay=None))
 ready=out/'ready.json';z=json.loads(ready.read_text());run=out/'run.lua';observer=ROOT/'tools/audit/current_darkwing_resource_observer_v2.lua';cfg=old['passive_darkwing_resources']['config'];raw,syms,addr,loc,hook=linked(ROM)
 for n,v in cfg['ram'].items():assert addr(n)==v
 for n,h in cfg['hooks'].items():assert hook(h['name'])==h
 insertion='ROSTER_CONFIG.bass_close=dofile('+lua(observer.as_posix())+')(ROSTER_CONFIG.prefix,'+lua(cfg)+')\n';anchor='dofile('+lua((ROOT/'tools/audit/current_roster_compact_11_v1.lua').as_posix())+')\n';text=run.read_text();assert text.count(anchor)==1;altered=text.replace(anchor,insertion+anchor);assert altered.replace(insertion,'',1)==text;run.write_text(altered,newline='\n')
 for n in['character','menu_index','variant_symbol','variant','mode_value','limit','capture_bytes','navigation','marker_names','smc_fields','dma_store_return','hooks']:assert z['config'][n]==old['config'][n],n
 for p in[Path(__file__),POLICY,proof,rp,parent/'result.json',parent/'trace.csv',parent/'darkwing-resources.csv',observer,run]+list(parent.glob('*.log')):z['bindings'][str(p.resolve())]=sha(p)
 command=out/'command.json';put(command,z['command']);z['bindings'][str(command.resolve())]=sha(command)
 z.update(native_run=False,native_clear_or_timing_pass=False,input_only=True,source_proof_sha256=sha(proof),original_v7_FALSE_preserved=True,passive_darkwing_resources=dict(ROM_sha256=EXPECTED,config=cfg,observer_literal=True,actual_RAM_and_hook_bytes_verified=True),scope='Full1-1/controlled1-2 strict unchanged route/hardware/caps. Input-only stair landing and head-only falsewall filter over immutablev7. Source cases are finite CPU evidence, not a native clear or authentic-world-everypixel claim.')
 put(ready,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items());print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),source_proof=str(proof),source_sha256=sha(proof),source_stair_calls=[s['updates']for s in sources],command=str(command)),indent=2))

if __name__=='__main__':main()
