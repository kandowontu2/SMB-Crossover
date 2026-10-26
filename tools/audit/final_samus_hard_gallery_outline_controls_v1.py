"""Complete compiled Samus draw/outline ownership controls; no native launch."""
from pathlib import Path
import argparse,hashlib,json
import final_samus_hard_gallery_source_v1 as source
from final_samus_hard_gallery_source_v1 import SHA,PARENT,ROOT,D,TraceArena
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def controls(b,registry):
 rows=[];active=None
 pcs={n:(address(b,n),(location(b,n)-16)//8192)for n in ['DrawMetasprite','PlayerRemoveOutlines','MetaspriteRenderLoop']}
 for n in pcs:
  if n not in source.OWNER_NAMES:source.OWNER_NAMES.append(n)
 class Spy(NesMPU):
  def step(c):
   q=active;bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   def ptr():return q.get('R0')+256*q.get('R1')
   def endpoint():
    ret=(q.m[0x100+((c.sp+1)&255)]+256*q.m[0x100+((c.sp+2)&255)]+1)&65535
    return(ret,q.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1,(c.sp+2)&255)
   def readrecord(p):
    n=q.m[p];assert n%4==0 and n<=128
    return[q.m[p+i]for i in range(n+1)]
   here=(c.pc,bank,c.sp)
   if q.filter_pending and here==q.filter_pending['endpoint']:
    z=q.filter_pending;z['returned']=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p,pointer=ptr(),C_bank=q.m.banks[2]);z['bytes']=readrecord(ptr());assert z['returned']['C_bank']==z['source_bank']
    parts=[]
    for i in range(1,len(z['source_bytes']),4):
     if not(z['source_bytes'][i+1]&4):parts+=z['source_bytes'][i:i+4]
    assert z['bytes']==[len(parts)]+parts
    assert ptr()-address(b,'OutlinePoseBuffer')in[0,32,64,96]
    q.filters.append(z);q.filter_pending=None
   if q.body_end and here==q.body_end:q.body_end=None
   if(c.pc,bank)==pcs['DrawMetasprite']and c.y==0:q.body_end=endpoint()
   if(c.pc,bank)==pcs['PlayerRemoveOutlines']and q.body_end:
    key=str(q.m.banks[2])+':'+str(ptr());original=registry[key];assert readrecord(ptr())==original['bytes']
    q.filter_pending=dict(entry=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p),endpoint=endpoint(),source_pointer=ptr(),source_bank=q.m.banks[2],source_bytes=original['bytes'])
   if(c.pc,bank)==pcs['MetaspriteRenderLoop']and q.body_end:
    z=dict(pointer=ptr(),bank=q.m.banks[2],a=c.a,x=c.x,y=c.y,p=c.p,sp=c.sp,bytes=readrecord(ptr()))
    if q.get('PlayerOutlinesOff'):
     assert q.filters and q.filters[-1]['returned']['pointer']==ptr()and z['bytes']==q.filters[-1]['bytes']
    else:assert z['bytes']==registry[str(z['bank'])+':'+str(ptr())]['bytes']
    q.body_draws.append(z)
   return super().step()
 saved=source.NesMPU;source.NesMPU=Spy
 try:
  # Classic tiers plus current Hard starting/Long/Varia presentation. These are
  # explicit CPU setup cells, not additional native difficulty coverage.
  for mode,power,owned in[(0,0,0),(0,1,0),(0,2,0),(1,0,0),(1,1,129),(1,1,161)]:
   for face in[1,2]:
    for pose in['standing','crouch','Morph','spin']:
     for off in[0,1]:
      q=TraceArena(b);active=q;q.filters=[];q.filter_pending=None;q.body_end=None;q.body_draws=[]
      q.put(CrossoverBehaviorVersion=mode,PlayerStatus=power,PlayerFacingDir=face,PlayerOutlinesOff=off,SmJumpStartY=200)
      q.set('InvOwnedLo',owned,2)
      if pose=='crouch':q.put(SmCrouch=1)
      if pose=='Morph':q.put(SmBall=1)
      if pose=='spin':q.put(Player_State=1,SmFlip=1,Player_Y_Position=150)
      q.invoke('PlayerGfxHandler');actual_pose=q.get('SmPose');q.invoke('DrawAllMetasprites')
      assert len(q.body_draws)==1 and len(q.filters)==off and q.filter_pending is None and q.body_end is None
      entry_names={x['owner']for c in q.calls for x in c['entries']}
      assert {'DrawMetasprite','MetaspriteRenderLoop'}<=entry_names
      assert('PlayerRemoveOutlines'in entry_names)==bool(off)
      for call in q.calls:assert call['returned']['sp']==253
      rows.append(dict(mode=mode,power=power,owned=owned,face=face,pose=pose,actual_pose=actual_pose,outlines_off=off,body=q.body_draws[0],filters=q.filters,calls=q.calls))
 finally:source.NesMPU=saved
 assert len(rows)==96
 return dict(passed=True,source_only=True,ROM_sha256=SHA,complete_caller_cases=len(rows),filtered_cases=sum(bool(z['filters'])for z in rows),cases=rows,limits='Actual complete PlayerGfxHandler and DrawAllMetasprites callers, including source filter/caches and farcall return PC/SP/bank. CPU states are synthetic legal presentation cells, not native acquisitions or visual verdicts.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--config',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
 cfg=json.loads(a.config.read_text());z=controls(b,cfg['body_records']);put(a.output/'proof.json',z);print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),cases=z['complete_caller_cases'],filtered=z['filtered_cases'])))

if __name__=='__main__':main()
