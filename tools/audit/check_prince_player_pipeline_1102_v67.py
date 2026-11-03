"""Actual full PlayerCtrlRoutine terrain/query and source-control CPU episodes."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_native_manifest_1102_v65 as M
import check_prince_successor_services_1102_v27 as S
import check_prince_native_link_1102_v43 as V
N,O=V.N,M.O;address,location=V.H.W.address,V.H.W.location


def loaded():
 _,b,_,_=M.bundle();N.Bus=V.ControllerBus;m=N.fresh(b)
 for k in [2,3]:m.ram[k][:]=bytes([0x9d])*8192;m.ram[k][0x1fe0:0x1ff0]=bytes(16)
 m.raw_page(2,2);N.put(m,CurrentBankC=2,SelectedCharacter=38,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,FamilyMainCommit=1,ReloadCHRBank=0,NumberofLives=2)
 m.ppuctrl=160;m[0x2001]=0;assert S.invoke(m,193,0xae00)['regs'][3]&1
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
 return b,m,json.loads((O/'native-labels-v49.json').read_text())


def terrain(m,fn):
 for page in range(2):
  at=address(m.bundle,'Block_Buffer_1'if page==0 else'Block_Buffer_2')
  for row in range(13):
   for col in range(16):m[at+row*16+col]=fn(page*256+16*col,32+16*row)


def main():
 b,seed,lab=loaded();actual=N.NesMPU;counts=Counter();tags=Counter();points={}
 for name in ['PlayerBGCollision','BlockBufferColli_Head','BlockBufferColli_Side','KillPlayer']:
  pc=address(b,name);points[pc,((location(b,name)-16)//8192)|128]=name
 points[lab['PpNativeTick'],2]='PpNativeTick';points[lab['PpNativeRoute'],2]='PpNativeRoute'
 class Trace(actual):
  def step(self):
   if self.pc>=0x8000:
    name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
    if name:
     counts[name]+=1
     if name=='PpNativeRoute':tags[self.memory.ram[2][0x9e]]+=1
   return super().step()
 N.NesMPU=Trace;episodes=[]
 try:
  for scenario in ['flat-walk','flat-up','wall-up']:
   m=N.fork(seed);terrain(m,lambda x,y:0x54 if y>=208 or scenario=='wall-up'and 128<=x<160 and y>=176 else 0);rows=[];native_min=256;maximum=48;prior=dict(counts);tagprior=dict(tags);minimum=224;cost=[]
   for epoch in range(320):
    x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');pad=1 if scenario=='flat-walk'else 8 if scenario=='flat-up'and 16<=epoch<120 else 0
    if scenario=='wall-up':pad=1 if x<104 else 8
    N.put(m,FrameCounter=epoch&255,SavedJoypad1Bits=pad,SavedJoypadBits=pad);out=N.invoke(m,'PlayerCtrlRoutine',a=83,x=0,y=0,p=0x21);minimum=min(minimum,out['minimum_SP']);cost.append(out['CPU']);y=N.get(m,'Player_Y_Position');native_min=min(native_min,y);maximum=max(maximum,N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))
    if epoch%8==0:rows.append(dict(epoch=epoch,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=y,yHigh=N.get(m,'Player_Y_HighPos'),sourceY=m.ram[2][0x611],action=m.ram[2][0x616],pose=m.ram[2][0x617],mode=m.ram[2][0x618],foot=int.from_bytes(m.ram[2][0x84:0x86],'little'),speedY=N.get(m,'Player_Y_Speed'),engine=N.get(m,'GameEngineSubroutine')))
    if N.get(m,'GameEngineSubroutine')!=8:break
   events={k:v-prior.get(k,0)for k,v in counts.items()if v!=prior.get(k,0)};tagdelta={str(k):v-tagprior.get(k,0)for k,v in tags.items()if v!=tagprior.get(k,0)}
   episodes.append(dict(scenario=scenario,updates=epoch+1,max_native_X=maximum,min_native_Y=native_min,final_engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),sourceHP=m.ram[2][0x6cf],source_phase=m.ram[2][0xa6],actual_calls=events,actual_public_tags=tagdelta,minimum_SP=minimum,CPU=[min(cost),max(cost)],trace=rows))
 finally:N.NesMPU=actual
 passed=episodes[0]['max_native_X']>150 and all(e['final_engine']==8 and e['lives']==2 and e['sourceHP']==5 for e in episodes)and episodes[1]['min_native_Y']<176 and all(e['actual_calls'].get('PpNativeTick')==e['updates']for e in episodes)
 q=dict(passed=passed,CPU_only=True,ROM_written=False,native_emulator=False,base_SHA256=M.PIN,memory_SHA256=M.sha(b['raw']),episodes=episodes,scope='Actual complete native PlayerCtrlRoutine with authentic current private source owner and explicit native metatile fixtures. Source controls use genuine Up and Right inputs. Full actual native BG/head/side callback counts and source/native trajectories recorded. This is neither parsed1-1 nor native emulator/helper crossing or full life/respawn claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-manifest-v65.json',O/'native-ingress-CPU-v66.json']})
 (O/'player-pipeline-CPU-v67.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['episodes','bindings']}));print(json.dumps([{k:v for k,v in e.items()if k!='trace'}for e in episodes]));assert passed,'Actual player pipeline needs source diagnosis; negative retained.'


if __name__=='__main__':main()
