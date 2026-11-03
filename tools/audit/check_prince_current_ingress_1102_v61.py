"""Proposed current headers plus actual native pickup/body callback ingresses."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_collision_manifest_1102_v59 as M
import check_prince_successor_services_1102_v27 as S
import check_prince_collision_services_1102_v56 as V
N,O=V.N,V.O;address,location=V.address,V.location


def main():
 base,new,_,details=M.bundle();N.Bus=V.V.ControllerBus
 labels=json.loads((O/'native-labels-v49.json').read_text());cookie=bytes.fromhex(details['cookie']);bad=helpers=0
 seed=N.fresh(new)
 for k in [2,3]:seed.ram[k][:]=bytes([0x73])*8192;seed.ram[k][0x1fe0:0x1ff0]=cookie
 N.put(seed,SelectedCharacter=38,NmiDisable=1)
 for bank in [2,3]:
  for byte in range(16):
   n=N.fork(seed);n.ram[bank][0x1fe0+byte]^=1;before=[bytes(x)for x in n.ram];out=S.invoke(n,193,0xb08c);assert not out['regs'][3]&1 and before==[bytes(x)for x in n.ram];bad+=1
 ownerlab=V.H.P.T.labels(O/'collision-owner-v59.lbl')
 for char in range(256):
  for owner in [37,38,39]:
   n=N.fork(seed);N.put(n,SelectedCharacter=char);off=0x1003 if owner==39 else 0xff3 if owner==37 else ownerlab['PrCookie']-0xa000;expect=new['raw'][16+65*8192+off:16+65*8192+off+16]
   for k in [2,3]:n.ram[k][0x1fe0:0x1ff0]=expect
   state=[bytes(x)for x in n.ram];out=S.invoke(n,193,0xaef3);assert bool(out['regs'][3]&1)==(char==owner)and state==[bytes(x)for x in n.ram];helpers+=1
 # One actual resident cold call supplies the initialized native fixture;
 # callbacks and private leaves are never substituted with RTS/test stubs.
 m=N.fresh(new)
 for k in [2,3]:m.ram[k][:]=bytes([0x9d])*8192;m.ram[k][0x1fe0:0x1ff0]=bytes(16)
 m.raw_page(2,2);N.put(m,CurrentBankC=2,SelectedCharacter=38,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,FamilyMainCommit=1,ReloadCHRBank=0,NumberofLives=2)
 m.ppuctrl=160;m[0x2001]=0;assert S.invoke(m,193,0xae00)['regs'][3]&1
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
 actual=N.NesMPU;calls=Counter();points={};far_trace=[]
 for name in ['NrPickupCollision','JnCollisionDispatch','M3PickupCollision','HuMature','NrPickup','JnPickupDispatch','M3CollectPickup','HuPickup','HandlePowerUpCollision','GuestBodyContactBridge','HuBody','HuFullBox']:
  pc=address(new,name);points[pc,((location(new,name)-16)//8192)|128]=name
 for name in ['PpNativeRoute','PpNativePickup','PpNativeContact']:
  pc=labels[name];points[pc,2 if pc>=0xc000 else 3]=name
 class Trace(actual):
  def step(self):
   if self.pc==address(new,'FarCallCommon')and len(far_trace)<60:far_trace.append(dict(bank=self.a,target=N.get(self.memory,'FarcallJmpTarget_SMC',1)+256*N.get(self.memory,'FarcallJmpTarget_SMC',2),selected=N.get(self.memory,'SelectedCharacter')))
   if self.pc>=0x8000:
    name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
    if name:calls[name]+=1
   return super().step()
 N.NesMPU=Trace;episodes=[]
 try:
  N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21);assert bytes(m[address(new,'BoundingBox_UL_XPos'):address(new,'BoundingBox_UL_XPos')+4])==bytes([48,176,64,208])
  for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])
  native_seed=N.fork(m)
  for kind in range(4):
   n=N.fork(native_seed);n.ram[2][0x6cf]=4;slot=5;N.put(n,ObjectOffset=slot)
   for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=183,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():n[address(new,field)+slot]=value
   before=dict(calls);far_trace.clear();out=N.invoke(n,'PowerUpObjHandler',a=83,x=slot,y=0,p=0x21);delta={k:v-before.get(k,0)for k,v in calls.items()if v!=before.get(k,0)}
   if not all(delta.get(k,0)>0 for k in ['NrPickupCollision','HuMature','HandlePowerUpCollision','NrPickup','HuPickup','PpNativePickup']):
    (O/'current-ingress-negative-v61.json').write_text(json.dumps(dict(qualified=False,base_SHA256=M.PIN,successor_memory_SHA256=M.sha(new['raw']),kind=kind,actual_calls=delta,far_trace=far_trace,sourceHP=n.ram[2][0x6cf],sourceSword=n.ram[2][0x6ee],native_item_flag=n[address(new,'Enemy_Flag')+slot],native_engine=N.get(n,'GameEngineSubroutine')),indent=2)+'\n')
   assert all(delta.get(k,0)>0 for k in ['NrPickupCollision','HuMature','HandlePowerUpCollision','NrPickup','HuPickup','PpNativePickup']),(kind,delta,out,bytes(n[address(new,'BoundingBox_UL_XPos'):address(new,'BoundingBox_UL_XPos')+28]).hex())
   assert not n[address(new,'Enemy_Flag')+slot]and N.get(n,'NumberofLives')==2
   if kind==0:assert n.ram[2][0x6cf]==5
   elif kind==1:assert n.ram[2][0x6ee]==1 and n.ram[2][0x616]==91
   elif kind==2:assert N.get(n,'StarInvincibleTimer')==35
   else:assert n[address(new,'FloateyNum_Control')+slot]==11
   episodes.append(dict(kind=kind,CPU=out['CPU'],minimum_SP=out['minimum_SP'],actual_ingress_calls=delta))
 finally:N.NesMPU=actual
 q=dict(passed=True,private_proposal_only=True,new_execution_granted=False,ROM_written=False,native_emulator=False,base_SHA256=M.PIN,successor_memory_SHA256=M.sha(new['raw']),Prince_bad_header_byte_rejections=bad,raw256_three_cookie_selector_cases=helpers,actual_HuFullBox=True,actual_PowerUpObjHandler_pickup_episodes=episodes,scope='Current proposed source image executes complete resident cold to native initialized fixture, real HuFullBox, then genuine native PowerUpObjHandler→NrPickupCollision/HuMature→native overlap→NrPickup/HuPickup→source-native collector for all4types. Explicit CPU actors only, no emulator RAM seeds/native-play claim. Exact new cookie rejects before private tag write and bounded selector is closed for all raw256. Foreign full-row proof reused from unchanged shared gates plus exact Sunny disjoint rebase. New execution lifetimes remain ungranted.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),M.BASE,O/'collision-manifest-v59.json',O/'collision-shared-CPU-v60.json',O/'collision-services-CPU-v56.json',O/'current-foreign-CPU-v52.json']})
 (O/'current-ingress-CPU-v61.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
