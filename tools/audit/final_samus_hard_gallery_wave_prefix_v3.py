"""Finite compiled full-GameLoop Wave spawn/first-Move source diagnosis."""
from pathlib import Path
import argparse,hashlib,json,sys
import final_samus_hard_gallery_source_v1 as source
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA,TraceArena
from final_samus_hard_gallery_pool_prepare_v1 import setups
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 native=D/'current3b112-samus-hard-freeze-clock-ready-v1/native';b=scoped_load(native/'candidate.nes');assert sha(native/'candidate.nes')==SHA;cfg=json.loads((native/'config.json').read_text());sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 rows,_=setups(LuaRuntime,(native/'run.lua').read_text(),cfg,b['raw']);active=None
 wanted={n:(address(b,n),(location(b,n)-16)//8192)for n in['PlayerCtrlRoutine','SamusWeapons::Spawn','SamusMuzzle','SamusWeapons::Move','SamusWaveWorldX','SamusWaveWorldPage','MegaManWeapons::Blocks']}
 for n in['GameLoop',*[n for n in wanted if n!='SamusWaveWorldPage']]:
  if n not in source.OWNER_NAMES:source.OWNER_NAMES.append(n)
 class Spy(NesMPU):
  def step(c):
   q=active;bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   def fields():
    i=q.get('SmSlot');return dict(player=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),playerY=q.get('Player_Y_Position'),slot=i,center=q.get('SmShotCenter',i),shotX=q.get('SmShotX',i)+256*q.get('SmShotPage',i),age=q.get('SmShotAge',i),type=q.get('SmShotType',i),dir=q.get('SmShotDir',i),muzzle=q.get('SmTempX')+256*q.get('SmTempPage'),pol=q.get('SmShotPolarity',i))
   for z in list(q.pending_trace):
    if(c.pc,bank,c.sp)==tuple(z['return']):z['after']=fields();z['returned']=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p);q.pending_trace.remove(z)
   for name,pair in wanted.items():
    if(c.pc,bank)!=pair:continue
    # The fixed-page tail is JMP-entered with the new-low-X PHA payload
    # above the genuine JSR return. It consumes that payload before RTS.
    extra=1 if name=='SamusWaveWorldPage'else 0
    ret=(q.m[0x100+((c.sp+1+extra)&255)]+256*q.m[0x100+((c.sp+2+extra)&255)]+1)&65535;rb=q.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1
    z=dict(owner=name,step=q.step_index,entry=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p),before=fields(),extra_stack_payload=extra,return_=[ret,rb,(c.sp+2+extra)&255]);z['return']=z.pop('return_');q.prefix.append(z);q.pending_trace.append(z)
   return super().step()
 saved=source.NesMPU;source.NesMPU=Spy;results=[]
 try:
  for task in[1,2]:
   seed=next(z for z in rows if z['case']==6 and z['task']==task)
   for variant in['original','block-above-player']:
    q=TraceArena(b);active=q;q.pending_trace=[];q.prefix=[];q.step_index=0
    for addr,v in seed['RAM'].items():q.m[addr]=v
    q.put(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,AreaType=1,DisableScreenFlag=0,GameTimerCtrlTimer=24,Player_CollisionBits=255)
    q.array('GameTimerDisplay',[3,4,6])
    if variant=='block-above-player':q.set('Block_Buffer_1',0,9*16+15);q.set('Block_Buffer_1',0xc1,7*16+15)
    ticks=[]
    for step in range(8 if variant=='original'else 65):
     q.step_index=step;age=max(0,step-1);buttons=(8 if 4<=age<9 else 0)|(64 if 5<=age<8 else 0);q.put(SavedJoypadBits=buttons,SavedJoypad1Bits=buttons)
     q.invoke('GameLoop');ticks.append(dict(step=step,controller_age=age,buttons=buttons,player=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),playerY=q.get('Player_Y_Position'),state=q.get('Player_State'),center=q.get('SmShotCenter',2),x=q.get('SmShotX',2)+256*q.get('SmShotPage',2),type=q.get('SmShotType',2)))
     if variant=='original'and any(z['owner']=='SamusWeapons::Move'for z in q.prefix):break
     if variant!='original'and step>6 and q.get('SmShotType',2)==0:break
    moves=[z for z in q.prefix if z['owner']=='SamusWeapons::Move'];assert moves,(task,variant,ticks)
    center=cfg['cases'][5]['tasks'][task-1]['center'];crossings=0
    if variant!='original':
     assert all(z['player']==(244 if task==1 else 252)for z in ticks)
     for z in moves:
      if z['after']['type']!=3:continue
      off=cfg['wave'][z['before']['age']-1];off=off-256 if off>=128 else off
      if z['before']['pol']==0:off=-off
      assert z['before']['center']==center%256 and z['after']['shotX']==center+off
      crossings+=z['before']['shotX']//256!=z['after']['shotX']//256
     assert crossings>0 and q.get('SmShotType',2)==0 and not any(z['owner']=='MegaManWeapons::Blocks'for z in q.prefix)
    results.append(dict(task=task,face=seed['face'],variant=variant,planned_center=center,page_crossings=crossings,ticks=ticks,prefix=q.prefix,calls=q.calls))
 finally:source.NesMPU=saved
 legality=[]
 for seed in rows:
  if seed['case']not in[7,8]:continue
  m=seed['RAM'];block=cfg['ram']['Block_Buffer_1'];x=m[cfg['ram']['Player_X_Position']];y=m[cfg['ram']['Player_Y_Position']]
  cells=[m[block+row*16+col]for row in range((y-32)//16,(y+31-32)//16+1)for col in range(x//16,(x+13)//16+1)]
  assert not any(cells)
  legality.append(dict(case=seed['case'],task=seed['task'],kind=seed['kind'],player_solid_overlap=False,solid_cells=cells,intentional_hazard_contact=seed['kind']in['firebar','firebar-no-varia','ordinary-hurt'],Screw_target='Later aligned native actor/body contact, not a solid block overlap'if seed['case']==8 else None))
 put(a.output/'proof.json',dict(passed=True,source_only=True,ROM_sha256=SHA,results=results,future_stage_legality=legality,native_operand_dump=False,scope='Compiled complete GameLoop with literal declared Lua setup and source-level1-1 mode defaults; PPU/NMI not emulated. Legal row7 geometry preserves intended center and complete source world positions/page crossings/natural expiry/no normal block queries. Prior original row9 geometry reproduces native signature but does not backfill missing native position dumps.'));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),summary=[dict(task=q['task'],variant=q['variant'],planned=q['planned_center'],page_crossings=q['page_crossings'],first_move=next(z for z in q['prefix']if z['owner']=='SamusWeapons::Move')['before'])for q in results],future_stage_legality=legality),indent=2))
if __name__=='__main__':main()
