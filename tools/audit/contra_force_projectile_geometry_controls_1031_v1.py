"""Original-allocated CF shots against explicit native-target edge fixtures."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
import contra_force_weapon_probe_v1 as W
P=R/'build/contra-force-projectile-contact-1031-v3';O=R/'build/contra-force-projectile-geometry-controls-1031-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,edges=[],exclusions=[])
 try:
  A.K=P/'kernel';A.bind(P);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  bases=[]
  for cls in range(4):
   for face,pad in [('right',1),('left',2)]:
    original=W.machine(cls,0);W.T.step(original,pad)
    for _ in range(4):W.T.step(original,4)
    W.T.step(original,68);W.T.call(original,0x8132)
    base=V.scene(cls,shot=False,world=False);T.put(base,CurrentBank=3,CurrentBankC=2,ObjectOffset=5);base[0x5115]=3;base[0x5116]=2
    base.ram[2][0x300:0x4e0]=bytes(original.memory[0x600:0x7e0]);base.ram[2][0x2fc]=10;base.ram[2][0x53]=10;base.ram[2][0x36]=13
    for i in range(6):base[T.address(T.B,'Enemy_Flag')+i]=0
    T.put(base,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,Enemy_Y_Position=176,Enemy_BoundBoxCtrl=9)
    for i in range(8):base[3+i]=17*(i+1)
    base.writes.clear();base.ram_writes.clear();base.ppu_log.clear();base.executed_guest.clear();bases.append((cls,face,base))
  def invoke(m):
   before=bytes(m[3:11]);maps=m.rawtags[:];r=T.finish(m,C.start(m,Q.L['CfHostShotContacts'],3,a=87,x=10,y=3,p=0x79))
   assert bytes(m[3:11])==before and T.get(m,'ObjectOffset')==5 and m.rawtags==maps and r['AXYP'][1]==10
   return bool(T.get(m,'Enemy_State')&32),r
  for cls,face,base in bases:
   for camera,sx in[(0,128),(240,32),(256,16)]:
    for dx in[-6,-5,0,21,22]:
     for dy in[0,1,8,31,32]:
      m=C.clone(base);ex=camera+sx-dx;T.put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,Enemy_X_Position=ex&255,Enemy_PageLoc=ex>>8)
      m.ram[2][0x34e+10]=sx;m.ram[2][0x368+10]=176+dy
      got,r=invoke(m);expected=(-6<dx<=21 and 0<dy<=31)
      assert got==expected,(cls,face,camera,dx,dy,got,r)
      if got:assert T.get(m,'FloateyNum_Control')==1 and m.ram[2][0x382+10]==6,'Real native score/source impact action'
      else:assert m.ram[2][0x382+10]==1,'Miss must preserve genuine active bullet'
      d['edges'].append(dict(variant=cls,facing=face,camera=camera,dx=dx,dy=dy,hit=got,CPU=r['CPU']))
  cls,face,base=bases[0]
  cases=[('inactive',None,(0x382+10,0)),('offscreen',None,(0x300+10,0x80)),('not_shot',None,(0x334+10,0)),('radius0',None,(0x420+10,0)),('bad_radius',None,(0x420+10,29))]
  cases +=[(f'nativeID{i}',dict(Enemy_ID=i),None)for i in[2,4,8,9,12,19,21,46]]
  cases +=[('erased',dict(Enemy_Flag=0),None),('duplicate',dict(Enemy_Flag=128),None),('defeated',dict(Enemy_State=32),None),('squished',dict(Enemy_State=2),None),('wrongYpage',dict(Enemy_Y_HighPos=2),None)]
  for name,fields,source in cases:
   m=C.clone(base);T.put(m,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Enemy_X_Position=128,Enemy_PageLoc=0)
   m.ram[2][0x34e+10]=128;m.ram[2][0x368+10]=193
   if fields:T.put(m,**fields)
   if source:m.ram[2][source[0]]=source[1]
   state=T.get(m,'Enemy_State');kind=m.ram[2][0x382+10];got,r=invoke(m)
   assert T.get(m,'Enemy_State')==state and m.ram[2][0x382+10]==kind,(name,r)
   d['exclusions'].append(dict(case=name,native_state_unchanged=state,original_shot_kind=kind))
  # Same genuine standing muzzle against static tall ordinary native body.
  m=C.clone(base);T.put(m,Enemy_ID=0,Enemy_State=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Enemy_X_Position=128,Enemy_PageLoc=0,Enemy_Y_Position=184)
  m.ram[2][0x34e+10]=128;m.ram[2][0x368+10]=184
  hit,r=invoke(m);assert hit
  d.update(passed=True,all4classes_bothfacings_pageedges=len(d['edges']),stale_native_hazard_exclusions=len(d['exclusions']),standing_tall_target=dict(muzzleY=184,target_Y=184,raw_top=0,native_defeat=True,synthetic_target_fixture=True),scope='Original donor input/weapon allocator creates all shot actor fields. Native geometry, camera/page and target actors are explicit staged leaf inputs; no earned/native-controller/level claim for these cases. Separate natural4 source histories prove earned right-facing native defeats. Player/stomp boxes untouched.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(A.__file__),Path(W.__file__),Path(W.T.__file__),P/'source-stage.json',P/'kernel/runtime.lbl'];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],edges=len(d['edges']),exclusions=len(d['exclusions']),error=d.get('error'))),flush=True)
if __name__=='__main__':main()
