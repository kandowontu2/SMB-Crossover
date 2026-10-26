"""Full compiled GameLoop/Samus draw wrapper and final OAM owner controls."""
from pathlib import Path
import argparse,hashlib,json,sys
import final_samus_hard_gallery_source_v1 as source
from final_samus_hard_gallery_source_v1 import D,SHA,TraceArena
from final_samus_hard_gallery_pool_prepare_v1 import setups
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def controls(b,seeds):
 active=None;names=['GameLoop','PlayerGfxHandler','SamusFreezeDrawAll','DrawAllMetasprites','DrawMetasprite','MetaspriteRenderLoop','SamusFreezeRenderFinish'];pcs={n:(address(b,n),(location(b,n)-16)//8192)for n in names}
 for n in names:
  if n not in source.OWNER_NAMES:source.OWNER_NAMES.append(n)
 class Spy(NesMPU):
  def step(c):
   q=active;bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;here=(c.pc,bank,c.sp)
   def endpoint():
    ret=(q.m[256+((c.sp+1)&255)]+256*q.m[256+((c.sp+2)&255)]+1)&65535;rb=q.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1;return(ret,rb,(c.sp+2)&255)
   def oam():return[q.m[512+i]for i in range(256)]
   scope=q.scope
   if scope and here==scope['inner_endpoint']:
    assert not scope.get('inner_completed');scope['inner_completed']=True;scope['inner_source']=oam();scope['body']=q.body;scope['inner_return']=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p)
   if scope and here==scope['outer_endpoint']:
    assert scope.get('inner_completed') and q.get('GuestOamRotationActive')==0
    scope['source']=oam();scope['outer_return']=dict(pc=c.pc,bank=bank,native_helper_bank=bank if c.pc>=0x8000 else 0,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p);scope['post_finish_OAM_changes']=[i for i,(x,y)in enumerate(zip(scope['inner_source'],scope['source']))if x!=y];q.completed.append(scope);q.scope=None
   if q.body_endpoint and here==q.body_endpoint:q.body_endpoint=None
   if(c.pc,bank)==pcs['SamusFreezeDrawAll']:
    assert q.scope is None;q.scope=dict(entry=dict(pc=c.pc,bank=bank,sp=c.sp),outer_endpoint=endpoint(),inner_endpoint=None,postFinish=q.get('SmFreezeRenderState')!=0,body=None)
   if(c.pc,bank)==pcs['DrawAllMetasprites']:
    assert q.scope is not None;q.body=None;q.scope['inner_endpoint']=endpoint();q.scope['inner_entry']=dict(pc=c.pc,bank=bank,sp=c.sp)
   if(c.pc,bank)==pcs['DrawMetasprite']and c.y==0:q.body_endpoint=endpoint()
   if(c.pc,bank)==pcs['MetaspriteRenderLoop']and q.body_endpoint:
    ptr=q.get('R0')+256*q.get('R1');cb=q.m.banks[2];length=q.m[ptr];assert length%4==0 and length<=128
    q.body=dict(pointer=ptr,bank=cb,bytes=[q.m[ptr+i]for i in range(length+1)],pose=q.get('SmPose'),logical=q.get('SmChrBank'))
   if(c.pc,bank)==pcs['SamusFreezeRenderFinish']:
    assert q.scope and q.scope.get('inner_completed') and q.scope['postFinish'];q.scope['finish_entry']=dict(pc=c.pc,bank=bank,sp=c.sp)
   return super().step()
 saved=source.NesMPU;source.NesMPU=Spy;rows=[]
 try:
  plans=[(owned,face,'standing')for owned in[0,129,131,133,137,145,161,193]for face in[1,2]]+[(owned,face,pose)for owned,pose in[(129,'crouch'),(131,'Morph'),(193,'spin')]for face in[1,2]]
  for owned,face,pose in plans:
   seed=next(z for z in seeds if z['RAM'].get(address(b,'InvOwnedLo')+2)==owned)
   for freeze in[0,1]:
    q=TraceArena(b);active=q;q.scope=None;q.completed=[];q.body={'stale_prior_body':True};q.body_endpoint=None
    for at,v in seed['RAM'].items():q.m[at]=v
    q.put(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,AreaType=1,DisableScreenFlag=0,GameTimerCtrlTimer=24,Player_CollisionBits=255,PlayerOutlinesOff=1,PlayerFacingDir=face,Player_MovingDir=face,SmFreezeRenderState=freeze,SavedJoypadBits=0,SavedJoypad1Bits=0)
    q.array('GameTimerDisplay',[3,4,6])
    if pose=='crouch':q.put(SmCrouch=1,SavedJoypadBits=4,SavedJoypad1Bits=4)
    if pose=='Morph':q.put(SmBall=1)
    if pose=='spin':q.put(Player_State=1,SmFlip=1,Player_Y_Position=150,SmJumpStartY=200)
    if freeze:
     q.put(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=168,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1,EnemyMetasprite=103,AvFrozen=104,AvFrozenHi=1,RgEnemyStun=255,LsrFrozenPose=103)
    for repeat in range(2):
     # The selected source branch is explicit CPU setup, not native coverage.
     q.put(SmFreezeRenderState=freeze);q.invoke('GameLoop')
     assert q.scope is None and len(q.completed)==repeat+1
    assert all(z['body']and 'stale_prior_body'not in z['body']and z['postFinish']==bool(freeze)and bool(z.get('finish_entry'))==bool(freeze)for z in q.completed)
    rows.append(dict(owned=owned,face=face,pose=pose,freeze=freeze,calls=q.calls,completed=q.completed))
 finally:source.NesMPU=saved
 assert len(rows)==44 and sum(bool(z['post_finish_OAM_changes'])for q in rows for z in q['completed'])>0
 return dict(passed=True,source_only=True,ROM_sha256=SHA,complete_GameLoop_cells=44,actual_wrapper_returns=88,rows=rows,limits='Full compiled GameLoop and genuine existing wrapper/inner/OAMClear/Finish return PC/SP/bank, uncached then repeat. Explicit CPU scene/presentation/Freeze-state setup; no native or NMI/PPU verdict. NMI interruption/physical epoch sequencing are separate Lua models.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);n=D/'current3b112-samus-hard-wave-ready-v1/native';b=scoped_load(n/'candidate.nes');assert sha(n/'candidate.nes')==SHA;sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 cfg=json.loads((n/'config.json').read_text());seeds,_=setups(LuaRuntime,(n/'run.lua').read_text(),cfg,b['raw']);z=controls(b,seeds);(a.output/'proof.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),cells=z['complete_GameLoop_cells'],returns=z['actual_wrapper_returns'],changed_finish=sum(bool(z['post_finish_OAM_changes'])for q in z['rows']for z in q['completed'])),indent=2))
if __name__=='__main__':main()
