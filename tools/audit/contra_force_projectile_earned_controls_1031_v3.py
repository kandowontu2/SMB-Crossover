"""Natural source cold controller histories earning a real CF-shot native defeat."""
from pathlib import Path
import collections,hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_menu_cold_parser_1031_v1 as M
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P,C,H=M.P,M.C,M.H
B=R/'build/contra-force-projectile-contact-1031-v3';J=B/'joint';K=B/'kernel';O=R/'build/contra-force-projectile-earned-controls-1031-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();P.J=H.O=J;P.L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
 b=qualified(J/'candidate.nes');d=dict(passed=False,source_CPU=True,native=False,rows=[]);original=H.finish;current=None
 pts={(address(b,n),(location(b,n)-16)//8192|128):n for n in ['ShellOrBlockDefeat','SetupFloateyNumber']};pts[(P.L['CfSourceImpact'],3)]='CfSourceImpact'
 def enemy(m):
  return[dict(slot=i,id=m[address(b,'Enemy_ID')+i],flag=m[address(b,'Enemy_Flag')+i],state=m[address(b,'Enemy_State')+i],x=m[address(b,'Enemy_X_Position')+i]+256*m[address(b,'Enemy_PageLoc')+i],y=m[address(b,'Enemy_Y_Position')+i])for i in range(6)if 0<m[address(b,'Enemy_Flag')+i]<128]
 def finish(m,c,hook=None):
  def audit(mem,cpu,step):
   if current is not None and cpu.pc>=0x8000:
    name=pts.get((cpu.pc,mem.rawtags[(cpu.pc-0x8000)//8192]))
    if name:
     current['calls'][name]+=1
     if name=='CfSourceImpact':
      i=mem.ram[2][0x2fc];e=H.get(mem,'ObjectOffset')
      current['impact']=dict(slot=i,kind=mem.ram[2][0x382+i],radius_index=mem.ram[2][0x420+i],x=mem.ram[2][0x34e+i]+H.get(mem,'ScreenLeft_X_Pos')+256*H.get(mem,'ScreenLeft_PageLoc'),y=mem.ram[2][0x368+i],enemy_slot=e,enemy_id=mem[address(b,'Enemy_ID')+e],enemy_state=mem[address(b,'Enemy_State')+e],native_score=mem[address(b,'FloateyNum_Control')+e],native_sound=H.get(mem,'Square1SoundQueue'))
   if hook:hook(mem,cpu,step)
  return original(m,c,audit)
 H.finish=finish
 try:
  for v in range(4):
   for face in ['right','left']:
    m=C.fresh(b,0);before=bytes(m[:0x800]);H.put(m,Player_Pos_ForScroll=0);assert[i for i,(a,z)in enumerate(zip(before,bytes(m[:0x800])))if a!=z]==[address(b,'Player_Pos_ForScroll')]
    H.put(m,CrossoverMenuIndex=30,FmGroups=v<<3,FmAlts=0,CrossoverMenuState=2,SelectedCharacter=0)
    for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:P.invoke(m,n)
    H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0);s=P.invoke(m,'CrossoverMenuInput')
    P.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['AXYP'][0],x=s['AXYP'][1],y=s['AXYP'][2],p=s['AXYP'][3]);P.invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
     if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
     H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255);P.invoke(m,'GameLoop');C.A.consume(m)
    else:raise AssertionError('Natural cold parser timeout')
    row=dict(variant=v,facing=face,setup_Main=setup,frames=[]);d['rows'].append(row);life=H.get(m,'NumberofLives');phase='approach';since=0;jump_since=None;crossed=False;air=False
    for age in range(650):
     x=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc');foes=[e for e in enemy(m)if e['id']==6 and not e['state']&32]
     e=foes[0]if foes else None;ground=H.get(m,'Player_State')==0
     if phase=='approach'and e and 18<e['x']-x<(100 if face=='right'else 72)and ground:
      phase='shoot'if face=='right'else'jump';since=age;jump_since=age if face=='left'else None
     if phase=='jump':
      air|=not ground
      if e and x-e['x']>=24:crossed=True
      keys=(0 if crossed else 1)|(128 if age-jump_since<44 else 0)
      if air and ground:
       phase='turn'if crossed else 'release';since=age;keys=2 if crossed else 1
     elif phase=='release':
      keys=1
      if age-since>=4:phase='approach'
     elif phase=='turn':phase='shoot';since=age;keys=4
     elif phase=='shoot':
      settle=0 if v==2 else 4;keys=4|(64 if age-since>=settle and(age-since-settle)%8<2 else 0)
     else:keys=1
     current=dict(age=age,phase=phase,input=keys,calls=collections.Counter(),before_enemy=e)
     H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
     z=P.invoke(m,'GameLoop');C.A.consume(m)
     current.update(x=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),y=H.get(m,'Player_Y_Position'),camera=H.get(m,'ScreenLeft_X_Pos')+256*H.get(m,'ScreenLeft_PageLoc'),body={n:m.ram[2][p]for n,p in dict(Y=0x368,input=0x4aa,frame=0x31a).items()},shots=[dict(slot=i,kind=m.ram[2][0x382+i],x=m.ram[2][0x34e+i],y=m.ram[2][0x368+i],radius=m.ram[2][0x420+i])for i in range(10,22)if m.ram[2][0x382+i]],enemies=enemy(m),CPU=z['CPU'],minimum_SP=z['minimum_SP'])
     row['frames'].append(current)
     assert H.get(m,'NumberofLives')==life and H.get(m,'GameEngineSubroutine')!=11,('Natural contact/death',v,face,age)
     if 'impact'in current:
      hit=current['impact'];assert current['calls']['ShellOrBlockDefeat']==1 and current['calls']['SetupFloateyNumber']>=1
      assert hit['enemy_id']==6 and hit['enemy_state']&32 and hit['native_score']==1 and hit['native_sound']==address(b,'Sfx_EnemySmack')
      assert hit['radius_index']==6 and hit['kind']!=0
      row['earned']=dict(age=age,impact=hit,genuine_jump_over_enemy=air if face=='left'else False);break
    else:raise AssertionError(('No earned original shot defeat',v,face))
    current=None
  d.update(passed=True,natural_earned_defeats=len(d['rows']),all4classes_bothfacings=True,original_source_controls_art_anchors=True,source_CPU_only=True,scope='Genuine cold menu/Start/parser and controller-held-byte Main histories, native normalNMI consumers. No CF cache/shot/enemy/position/outcome preload after cold. Iron uses authentic freshDown+B startup; others settleDown4 then freshB2/6. Left-facing histories jump over the genuine spawned Goomba then turn/fire. Not a native/standing-Goomba/whole1-1 claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  H.finish=original;refs=[Path(__file__),Path(M.__file__),Path(P.__file__),Path(C.__file__),Path(H.__file__),B/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',K/'runtime.lbl']
  d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],rows=[{k:v for k,v in r.items()if k!='frames'}for r in d['rows']],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
