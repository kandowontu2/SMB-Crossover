"""Replay literal static Lua observer on actual assembled RemainingDraw calls."""
from pathlib import Path
import argparse,json,sys
from final_bill_lance_hard_gallery_source_v1 import PARENT,SHA,D,ROOT,sha,put,OWNER_NAMES,EXTRA_OWNERS
from final_bill_lance_hard_gallery_source_v2 import BillArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA and ready['observer_version']==2
 b=scoped_load(PARENT/'candidate.nes');sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
 for n in EXTRA_OWNERS:
  if n in b['syms']and n not in OWNER_NAMES:OWNER_NAMES.append(n)
 rows=[];original_step=NesMPU.step
 for variant in [0,1]:
  profile=ready['profiles'][variant];path=Path(profile['output']);cfg=json.loads((path/'config.json').read_text());script=(path/'run.lua').read_text()
  assert sha(path/'run.lua')==profile['script_sha256']
  for item,case in [(2,4),(3,5)]:
   for face in [1,2]:
    for mixed in [False,True]:
     q=BillArena(b,variant);q.put(PlayerFacingDir=face,Player_MovingDir=face);q.grant(item);q.buttons(64)
     q.invoke('RosterDrawShots');assert q.get('RgSlot')==0 and q.get('RgShotType',0)==0
     if mixed:
      for n,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('Enemy_X_Position',200),('Enemy_PageLoc',0),('Enemy_Y_Position',160),('Enemy_Y_HighPos',1),('InvPickupOwner',3),('InvPickup',4)]:q.set(n,v,5)
     rt=LuaRuntime(unpack_returned_tuples=True)
     rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPrgRom=6;emu.write=function()error("Observer must never write game state in draw controls")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end')
     rt.execute(script+f"\nentered=true;done=false;phase='run';wall=500;updates=1;current={{q=C.cases[{case}],stage={{draws=0}}}}\nMODEL_RESULT=function()return current.stage.draws,drawScope~=nil end\n")
     rt.globals().PY_READ=lambda at,kind:q.m[at] if kind==1 else b['raw'][16+at]if kind==6 else 0
     rt.globals().PY_BANK=lambda at:q.m.banks[(at-32768)//8192]*8192+(at&8191)if at>=32768 else at
     rt.execute('emu.read=function(a,k)return PY_READ(a,k)end;emu.convertAddress=function(a)return{address=PY_BANK(a)}end;emu.addMemoryCallback=function()error("No runtime registration")end;emu.removeMemoryCallback=function()error("No runtime removal")end')
     callbacks=[v for _,v in rt.globals().callbacks.items()];assert int(callbacks[-1]['lo'])==0 and int(callbacks[-1]['hi'])==65535
     events=[];pending=[];active=False;cpu=None
     points={address(b,n):n for n in ['RemainingDraw','RemainingDraw::ArtPointer','MetaspriteRenderLoop']}
     def stamp(c):
      return dict(pc=c.pc,bank=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else -1,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p,index=q.get('AvDrawIndex'),AvSlot=q.get('AvSlot'),RgSlot=q.get('RgSlot'),ptr=q.get('R0')+256*q.get('R1'))
     def step(c):
      nonlocal cpu
      if not active:return original_step(c)
      cpu=c
      s=rt.globals().state
      for k,v in {'cpu.pc':c.pc,'cpu.sp':c.sp,'cpu.a':c.a,'cpu.x':c.x,'cpu.y':c.y,'cpu.p':c.p,'cpu.ps':c.p,'cpu.cycleCount':c.processorCycles}.items():s[k]=v
      for x in list(pending):
       if (c.pc,q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else -1,c.sp)==x['return']:
        events.append(dict(kind='ArtPointer-return',**stamp(c),accepted=bool(c.p&1),source_owner=x['owner']));pending.remove(x)
      if c.pc in points:
       name=points[c.pc]
       expected=(location(b,name)-16)//8192
       if q.m.banks[(c.pc-32768)//8192]==expected:
        row=dict(kind=name,**stamp(c));events.append(row)
        if name=='RemainingDraw::ArtPointer':
         ret=(q.m[256+((c.sp+1)&255)]+256*q.m[256+((c.sp+2)&255)]+1)&65535
         rb=q.m.banks[(ret-32768)//8192]
         pending.append(dict(return_ignored=None,**{'return':(ret,rb,(c.sp+2)&255)},owner=dict(index=q.get('AvDrawIndex'),slot=q.get('AvSlot'))))
      for cb in callbacks:
       if int(cb['kind'])==2 and int(cb['lo'])<=c.pc<=int(cb['hi']):cb['fn'](c.pc)
      return original_step(c)
     NesMPU.step=step
     turns=[]
     try:
      for turn in range(4):
       before=rt.globals().MODEL_RESULT()[0];active=True;c,_=q.invoke('RemainingDraw');active=False
       drawn,leak=rt.globals().MODEL_RESULT();assert not leak,'Qualified draw admission must clear at actual render return/nonshot pointer'
       turns.append(dict(turn=turn,actual_draws=drawn-before,cycles=c.processorCycles,scope_leaked=leak,final_Cbank=q.m.banks[2]))
     finally:active=False;NesMPU.step=original_step
     renderer=[z for z in events if z['kind']=='MetaspriteRenderLoop'];pointers=[z for z in events if z['kind']=='ArtPointer-return']
     actualshots=[z for z in renderer if z['index']<10 and q.get('RgShotType',z['AvSlot'])==(42 if item==2 else 43)]
     rejected=[z for z in pointers if z['source_owner']['index']<10 and not z['accepted']]
     nonshots=[z for z in renderer if z['index']>=10]
     total=rt.globals().MODEL_RESULT()[0]
     assert total==len(actualshots)>0 and rejected and nonshots,(variant,item,face,mixed,total,len(actualshots),len(rejected),len(nonshots))
     assert all(z['RgSlot']==0 and z['AvSlot']!=0 for z in actualshots)
     rows.append(dict(variant=variant,item=item,face=face,mixed_world_pickup=mixed,actual_compiled_remaining_calls=4,turns=turns,
         admitted_advanced_draws=total,actual_advanced_render_entries=len(actualshots),actual_CHR_rejected_shot_pointers=len(rejected),actual_nonshot_render_entries=len(nonshots),events=events,
         contract='Literal generated v2 observer driven by actual compiled CPU entry/return state. No game instructions, pointers, source records or carry results stubbed; no NMI/PPU/native claim.'))
 put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,cases=len(rows),complete_RemainingDraw_calls=4*len(rows),rows=rows,
     observer_replayed_literal=True,legacy_stale_RgSlot_produced_by_complete_RosterDrawShots=True,
     every_accepted_advanced_entry_counted=True,real_nonshot_and_CHR_rejection_not_counted=True,
     all_four_full_returns_scope_clear=True,checker_sha256=sha(__file__),bindings={str(f):sha(f)for f in [Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua']}))
 print(json.dumps(dict(passed=True,cases=len(rows),actual_compiled_calls=4*len(rows),proof_sha256=sha(a.output/'proof.json'))))


if __name__=='__main__':main()
