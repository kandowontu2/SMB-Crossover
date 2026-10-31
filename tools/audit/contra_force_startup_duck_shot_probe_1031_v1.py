"""Real CF cold menu/parser/Main scroll+enemy proof; source CPU, never Mesen."""
from pathlib import Path
import argparse,collections,hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_menu_cold_parser_1031_v1 as M
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P,C,H=M.P,M.C,M.H
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--kernel',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True);ap.add_argument('--variants',type=int,nargs='+',default=[0]);ap.add_argument('--expect-scroll',action='store_true')
 a=ap.parse_args();J=a.joint.resolve();K=a.kernel.resolve();O=a.output.resolve();assert not O.exists();O.mkdir()
 P.J=H.O=J;P.L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
 b=qualified(J/'candidate.nes');rows=[];q=dict(passed=False,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'),cohorts=rows)
 original=H.finish;current=None
 names=['ScrollHandler','ScrollScreen','InitScrlAmt','AreaParserTaskHandler','EnemiesAndLoopsCore','ProcessEnemyData']
 points={(address(b,n),(location(b,n)-16)//8192|128):n for n in names}
 points[(P.L['CfSourceImpact'],3)]='CfSourceImpact'
 fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_State','Player_Pos_ForScroll','Player_Rel_XPos','Player_X_Scroll','Player_X_Speed','Player_XSpeedAbsolute','SideCollisionTimer','ScrollLock','ScrollAmount','ScreenLeft_X_Pos','ScreenLeft_PageLoc','ScrollThirtyTwo','AreaParserTaskNum','AreaPointer','EnemyDataOffset']
 def read(m):return{n:H.get(m,n)for n in fields}
 def finish(m,c,hook=None):
  def audit(mem,cpu,step):
   if current is not None and cpu.pc>=0x8000:
    n=points.get((cpu.pc,mem.rawtags[(cpu.pc-0x8000)//8192]))
    if n:
     current['calls'][n]+=1
     if n in('ScrollHandler','ScrollScreen','InitScrlAmt'):
      current['events'].append(dict(point=n,**read(mem)))
   if hook:hook(mem,cpu,step)
  return original(m,c,audit)
 H.finish=finish
 try:
  for v in a.variants:
   m=C.fresh(b,0);before=bytes(m[:0x800]);H.put(m,Player_Pos_ForScroll=0)
   corrected=bytes(m[:0x800]);changed=[i for i,(x,y)in enumerate(zip(before,corrected))if x!=y]
   assert changed==[address(b,'Player_Pos_ForScroll')]and before[changed[0]]==96 and corrected[changed[0]]==0
   # Only this nativeAllZeros field changes before menu; no guest state projection.
   H.put(m,CrossoverMenuIndex=30,FmGroups=v<<3,FmAlts=0,CrossoverMenuState=2,SelectedCharacter=0)
   for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:P.invoke(m,n)
   H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0);s=P.invoke(m,'CrossoverMenuInput')
   P.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['AXYP'][0],x=s['AXYP'][1],y=s['AXYP'][2],p=s['AXYP'][3]);P.invoke(m,'PauseRoutine',a=0)
   for setup in range(600):
    if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
    H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
    P.invoke(m,'GameLoop');C.A.consume(m)
   else:raise AssertionError('Cold native parser timeout')
   cohort=dict(variant=v,setup_Main=setup,initial=read(m),initial_area_data=H.get(m,'AreaDataLow')+256*H.get(m,'AreaDataHigh'),initial_enemy_data=H.get(m,'EnemyDataLow')+256*H.get(m,'EnemyDataHigh'),frames=[]);rows.append(cohort)
   bp=address(b,'Block_Buffer_1');initial=bytes(m[bp:bp+416]);life=H.get(m,'NumberofLives')
   duck_since=None
   for age in range(420 if a.expect_scroll else 240):
    current=dict(age=age,calls=collections.Counter(),events=[])
    # Only ordinary real controller bytes change after the actual cold Start.
    keys=1
    if a.expect_scroll and H.get(m,'Player_State')==0:
     player=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')
     for i in range(6):
      if 0<m[address(b,'Enemy_Flag')+i]<128 and m[address(b,'Enemy_ID')+i]<21 and not m[address(b,'Enemy_State')+i]&32:
       ex=m[address(b,'Enemy_X_Position')+i]+256*m[address(b,'Enemy_PageLoc')+i]
       if 18<ex-player<100 and abs(m[address(b,'Enemy_Y_Position')+i]-H.get(m,'Player_Y_Position'))<36:
        if duck_since is None:duck_since=age
        keys=4|(64 if(age-duck_since)%8<2 else 0)
    current['input']=keys
    H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
    result=P.invoke(m,'GameLoop');C.A.consume(m)
    current.update(end=read(m),Main_CPU=result['CPU'],minimum_SP=result['minimum_SP'],
      enemies=[dict(slot=i,id=m[address(b,'Enemy_ID')+i],flag=m[address(b,'Enemy_Flag')+i],x=m[address(b,'Enemy_X_Position')+i]+256*m[address(b,'Enemy_PageLoc')+i],y=m[address(b,'Enemy_Y_Position')+i])for i in range(6)if m[address(b,'Enemy_Flag')+i]],
      block_buffer_changed=bytes(m[bp:bp+416])!=initial)
    current['source_body']={n:m.ram[2][at]for n,at in{'anchorX':0x34e,'anchorY':0x368,'input':0x4aa,'action':0x300,'type':0x334,'frame':0x31a}.items()}
    current['source_shots']=[dict(slot=i,active=m.ram[2][0x382+i],type=m.ram[2][0x334+i],action=m.ram[2][0x300+i],x=m.ram[2][0x34e+i]+256*H.get(m,'ScreenLeft_PageLoc')+H.get(m,'ScreenLeft_X_Pos'),y=m.ram[2][0x368+i])for i in range(10,22)if m.ram[2][0x382+i]]
    current['native_boxes']=[dict(slot=i,id=m[address(b,'Enemy_ID')+i],control=m[address(b,'Enemy_BoundBoxCtrl')+i],state=m[address(b,'Enemy_State')+i],offsets=list(m[address(b,'BoundBoxCtrlData')+4*m[address(b,'Enemy_BoundBoxCtrl')+i]:address(b,'BoundBoxCtrlData')+4*m[address(b,'Enemy_BoundBoxCtrl')+i]+4]))for i in range(6)if m[address(b,'Enemy_Flag')+i]]
    cohort['frames'].append(current)
    assert H.get(m,'NumberofLives')==life and H.get(m,'GameEngineSubroutine')!=11,'Early native contact/death'
    x=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc');camera=H.get(m,'ScreenLeft_X_Pos')+256*H.get(m,'ScreenLeft_PageLoc')
    if a.expect_scroll and x>=352 and camera>=256 and any(r['enemies']for r in cohort['frames'])and current['block_buffer_changed']:break
   cohort.update(final_X=x,final_camera=camera,actual_enemy_spawn=any(r['enemies']for r in cohort['frames']),native_terrain_advanced=any(r['block_buffer_changed']for r in cohort['frames']))
   if a.expect_scroll:assert x>=352 and camera>=256 and cohort['actual_enemy_spawn']and cohort['native_terrain_advanced'],cohort
   else:assert x==239 and camera==0 and not cohort['actual_enemy_spawn']and not cohort['native_terrain_advanced'],cohort
   current=None
  q.update(passed=True,expected_scroll=a.expect_scroll,scope='Actual cold menu/Start/native parser/Main+normalNMI source executions with only held Right. No guest-state/load/position/camera/terrain/enemy seeds; source CPU model, no new native result. Native Player_Pos_ForScroll starts at real AllZeros0 before menu; inherited seeded96 factory is explicitly corrected, not camera/guest outcome seeded.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 finally:H.finish=original
 refs=[Path(__file__),Path(M.__file__),Path(P.__file__),Path(C.__file__),Path(H.__file__),J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',K/'runtime.lbl',J.parent/'source-stage.json',R/'build/contra-force-11-native-1031-v5/burns/capture/result.json',R/'build/contra-force-11-native-1031-v5/burns/capture/trace.csv']
 q['bindings']={str(p.resolve()):sha(p)for p in refs}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(path=str(O/'controls.json'),sha256=sha(O/'controls.json'),passed=q['passed'],summary=[{k:v for k,v in c.items()if k!='frames'}for c in rows],error=q.get('error')),indent=2),flush=True);assert q['passed']
if __name__=='__main__':main()
