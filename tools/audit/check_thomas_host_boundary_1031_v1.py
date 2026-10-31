"""Finite real a126 native-query/combat/progression ABI controls, no emulator."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import thomas_original_cpu_1031_v1 as T
import check_thomas_actual_host_vectors_1031_v1 as A
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
P=R/'build/thomas-host-boundary-1031-v2';J=A.J;O=R/'build/thomas-host-boundary-controls-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
FLAGS=[L.flags(i)for i in range(64)]

def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,actual_host_ROM_unchanged=True)
 try:
  stage=json.loads((P/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(J/'candidate.nes');s=T.labels(P/'component.lbl');image=(P/'component.bin').read_bytes()
  def make():
   m=L.make(b,SelectedCharacter=10,FmAlts=64,CurrentPlayer=0,Player_Rel_XPos=120,Player_Rel_YPos=160)
   m.__class__=A.HostMemory;m.ram[3][:]=image;m.ram[2][:]=bytes(8192);m.raw_page(1,3);m.raw_page(2,2)
   H.put(m,CurrentBank=3,CurrentBankC=2);m.observe(s);m.writes.clear();m.ram_writes.clear();return m
  def fork(m):z=L.fork(m);z.__class__=A.HostMemory;return z
  def run(m,name,a=0x59,x=7,y=0x83,p=0x30,hook=None):
   c=A.CPU(memory=m,pc=s[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5aff);low=c.sp;pcs=[]
   for i in range(50000):
    if c.pc==0x5b00:break
    if hook:hook(m,c,i)
    pcs.append((c.pc,m.rawtags[:]))
    low=min(low,c.sp);assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags);c.step()
   else:raise AssertionError(('bounded adapter',name,hex(c.pc)))
   assert c.sp==224 and m.rawtags[1:3]==[3,2],(name,'maps/SP',c.sp,m.rawtags)
   return c,pcs,low
  def preserved(c,a=0x59,x=7,y=0x83,p=0x30):assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,y,p,224),('caller',c.a,c.x,c.y,c.p,c.sp,a,x,y,p)
  def cold(m,player=0):
   c,_,_=run(m,'ThomasHostCold',a=0,x=player,y=0);preserved(c,0,player,0,0x30)
  def read(m,name,count=1):at=s[name];return bytes(m[at:at+count])
  frames=0;body=0;anchor=0
  policies=[('walk',[1]*24),('reverse',[1]*12+[2]*12),('jump',[8]*3+[0]*36),('punch',[0]*2+[64]*6+[0]*24),('kick',[0]*2+[128]*6+[0]*24),('crouch',[4]*3+[68]*6+[4]*12)]
  for player,(name,policy)in itertools.product(range(2),policies):
   m=make();H.put(m,CurrentPlayer=player);cold(m,player);epoch=0
   for index,pad in enumerate(policy):
    epoch=(epoch+1)&255;ref=fork(m)
    # Independently replay the exact corrected original worker, with only the
    # declared source-native center import performed by the host boundary.
    ref[0xc0d4]=(H.get(ref,'Player_X_Position')+8)&255
    ref[0xc0e5]=(H.get(ref,'Player_PageLoc')+int(H.get(ref,'Player_X_Position')>=248))&255
    ref[0xc094]=(H.get(ref,'Player_Rel_XPos')+8)&255
    c,_,_=run(ref,'ThomasC2AcceptedFrame',pad,1,epoch,FLAGS[index%64]);preserved(c,pad,1,epoch,FLAGS[index%64])
    oldy=H.get(m,'Player_Y_Position');c,_,_=run(m,'ThomasHostFrame',pad,1,epoch,FLAGS[index%64]);preserved(c,pad,1,epoch,FLAGS[index%64])
    assert m.ram[2][:0x818]==ref.ram[2][:0x818],('accepted original state',player,name,index)
    assert m.logical==ref.logical
    gx=int.from_bytes(read(m,'ThHostGround',2),'little');delta=m[0xc0b6]-135
    pos=(gx+delta)&65535
    assert H.get(m,'Player_Y_Position')==pos&255 and H.get(m,'Player_Y_HighPos')==pos>>8
    assert H.get(m,'Player_Y_Speed')==(pos-oldy)&255
    assert H.get(m,'Player_X_Position')==(m[0xc0d4]-8)&255
    assert H.get(m,'PlayerFacingDir')==(1 if m[0xc069]&1 else 2)
    before=bytes(m[3:11]);c,_,_=run(m,'ThomasHostBody',p=FLAGS[index%64]);preserved(c,p=FLAGS[index%64]);assert bytes(m[3:11])==before
    original=T.machine();original.memory[0x94]=m[0xc094];original.memory[0x69]=m[0xc069];original.memory[0x68]=m[0xc068]
    T.run(original,0xc0b6,x=0);expected=bytes((original.memory[i]+((gx-157)&255 if i in[1,3]else 0))&255 for i in range(4))
    assert read(m,'ThHostBodyRect',4)==expected,(name,index,'original body',read(m,'ThHostBodyRect',4),expected)
    assert bytes(m[address(b,'BoundingBox_UL_Corner'):address(b,'BoundingBox_UL_Corner')+4])==expected
    c,_,_=run(m,'ThomasHostRenderAnchor');preserved(c)
    assert int.from_bytes(read(m,'ThHostArtOrigin',2),'little')==(gx-304)&65535
    # The scripts bake their own jump. Anchor is independent of currentB6.
    # Its one displacement in host position is canceled before canvas drawing.
    assert (pos-48-delta-256)&65535==int.from_bytes(read(m,'ThHostArtOrigin',2),'little')
    anchor+=1;body+=1;frames+=1
   # Genuine post-terrain bridge imports the host correction; it cannot
   # manufacture a metatile or choose a second velocity/integration step.
   H.put(m,Player_X_Position=73,Player_PageLoc=1,Player_Y_Position=144,Player_Y_HighPos=1)
   c,_,_=run(m,'ThomasHostAfterTerrain');preserved(c)
   assert m[0xc0d4]==81 and m[0xc0e5]==1
   assert int.from_bytes(read(m,'ThHostGround',2),'little')==(400-(m[0xc0b6]-135))&65535
  print('Thomas accepted movement/body/one-anchor source boundary PASS',flush=True)
  queries=0
  for entry,target,profile,p in itertools.product(['ThomasHostFeet','ThomasHostHead','ThomasHostSide'],[0],range(7),FLAGS):
   target={'ThomasHostFeet':'BlockBufferColli_Feet','ThomasHostHead':'BlockBufferColli_Head','ThomasHostSide':'BlockBufferColli_Side'}[entry]
   m=make()
   for at in range(address(b,'Block_Buffer_1'),address(b,'Block_Buffer_1')+416):m[at]=(at*13+71)&255
   r=fork(m);before=bytes(m.ram[2]);c,_,_=run(m,entry,a=0x59,x=7,y=profile,p=p)
   z,_=H.invoke(r,target,a=0x59,x=7,y=profile,p=p)
   assert(c.a,c.x,c.y,c.p,c.sp)==(z.a,z.x,z.y,z.p,z.sp),(entry,profile,p)
   assert bytes(m[3:11])==bytes(r[3:11]) and bytes(m.ram[2])==before
   queries+=1
  print('Thomas genuine native head/feet/side allflags ABI PASS',flush=True)
  # Earn the original melee window through source input. Targets are explicit
  # unit-test native actors, never described as a played level encounter.
  m=make();cold(m);earned=0;hit_calls=0
  for i,pad in enumerate([0,0]+[64]*6+[0]*32):
   run(m,'ThomasHostFrame',pad,1,i+1)
   if not m[s['ThAttackEnabled']]:continue
   earned+=1;rect=bytearray(read(m,'ThAttackRect',4));off=(int.from_bytes(read(m,'ThHostGround',2),'little')-157)&255
   rect[1]=(rect[1]+off)&255;rect[3]=(rect[3]+off)&255
   H.put(m,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,EnemyOffscrBitsMasked=0,Enemy_Y_HighPos=1)
   m[address(b,'BoundingBox_UL_Corner')+4:address(b,'BoundingBox_UL_Corner')+8]=rect
   H.put(m,Enemy_X_Position=H.get(m,'Player_X_Position'),Enemy_PageLoc=0,Enemy_Y_Position=160)
   visits=[];run(m,'ThomasHostWeapons',hook=lambda mem,c,n:visits.append(c.pc)if c.pc==address(b,'HandleEnemyFBallCol')else None)
   assert visits and H.get(m,'Enemy_State')&32,('earned melee failed actual native defeat',i,rect,visits)
   hit_calls+=len(visits);before=H.get(m,'Enemy_State');again=[]
   run(m,'ThomasHostWeapons',hook=lambda mem,c,n:again.append(c.pc)if c.pc==address(b,'HandleEnemyFBallCol')else None)
   assert not again and H.get(m,'Enemy_State')==before,'Duplicate epoch hit twice'
   break
  assert earned and hit_calls==1
  print('Thomas earned original punch -> native enemy defeat once PASS',flush=True)
  damage=0
  for hp,amount,p in itertools.product([0,1,2,48],[0,1,2,49],FLAGS):
   m=make();cold(m);m[0xc4a6]=hp;r=T.machine()
   # Original function sees precisely the current canonical source state.
   list.__setitem__(r.memory,slice(0,2048),m.ram[2][:2048]);r.memory[0x37a]=amount
   T.run(r,0xc462,a=amount,x=6,p=p)
   c,_,_=run(m,'ThomasHostDamage',amount,7,0x83,p);preserved(c,amount,7,0x83,p)
   for at in [0x4a6,0x4c6,0x68,0x21,0x37a,0x52,0xfd,0xfe,0xff]:assert m[0xc000+at]==r.memory[at],('native health math',hp,amount,p,hex(at),m[0xc000+at],r.memory[at])
   damage+=1
  print('Thomas genuine player damage allflags/underflow PASS',flush=True)
  # Existing native item implementation is the sole progression owner.
  pickups=0
  for kind,p in itertools.product(range(4),FLAGS[::8]):
   m=make();cold(m);H.put(m,PowerUpType=kind,Enemy_State=128,PlayerStatus=0,PlayerSize=1,ObjectOffset=0)
   ref=fork(m);z,_=H.invoke(ref,'MarioSourcePowerupCollision',a=0x59,x=0,y=0x83,p=p)
   c,_,_=run(m,'ThomasHostPickup',a=0x59,x=0,y=0x83,p=p)
   assert(c.a,c.x,c.y,c.p,c.sp)==(z.a,z.x,z.y,z.p,z.sp),(kind,p,'item ABI')
   for name in ['PlayerStatus','PlayerSize','GameEngineSubroutine','NumberofLives','Square2SoundQueue','Enemy_State']:
    assert H.get(m,name)==H.get(ref,name),(kind,p,name)
   assert bytes(m.ram[2])==bytes(ref.ram[2]);pickups+=1
  # Real vectors at native query, owned body/scratch and actual SFC instructions.
  vectors=[]
  for name in ['ThomasHostBody','ThomasHostQueries','ThomasHostWeapons']:
   seed=make();cold(seed);base=fork(seed);_,pcs,_=run(base,name)
   cuts={0,len(pcs)-2};cuts.update(range(0,len(pcs),max(1,len(pcs)//14)))
   for cut,(lag,kind)in itertools.product(sorted(cuts),[(0,'NMI'),(255,'NMI'),(255,'IRQ')]):
    m=fork(seed);H.put(m,NmiDisable=lag);receipts=[]
    def hook(mem,c,i):
     if i==cut:receipts.append(V.interrupt(mem,c,kind))
    c,_,_=run(m,name,hook=hook);preserved(c)
    assert bytes(m.ram[2])==bytes(base.ram[2]) and bytes(m[3:11])==bytes(base[3:11])
    vectors.append(dict(entry=name,cut=cut,**receipts[0]))
  q.update(passed=True,accepted_original_boundary_pairs=frames,original_body_pairs=body,single_B6_canvas_anchor_pairs=anchor,
   native_head_feet_side_allflags_pairs=queries,earned_source_punch_native_enemy_defeats=hit_calls,duplicate_attack_inert=True,
   original_native_player_health_pairs=damage,native_powerup_pairs=pickups,actual_vector_cases=len(vectors),vectors=vectors,
   limits=['Terrain-query and post-contact API only; full natural Thomas world/head/feet row integration remains unhooked',
    'No fall/ceiling/source-air cancellation integration claim','No renderer/audio/physical loader or playable readiness claim'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in [Path(__file__),Path(A.__file__),Path(L.__file__),Path(H.__file__),Path(V.__file__),P/'source-stage.json',P/'component.bin',P/'component.lbl',J/'candidate.nes',R/'tools/audit/verify_native_relocation.py']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','vectors','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
