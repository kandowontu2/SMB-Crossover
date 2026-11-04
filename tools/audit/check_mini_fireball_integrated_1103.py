"""Actual native callers for the isolated Mini fireball integration."""
from pathlib import Path
import argparse,hashlib,json,re
from prepare_mini_mario_native_power_1103_v56 import N,address,bundle

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rom',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--enemy-only',action='store_true');ap.add_argument('--roll-only',action='store_true')
 a=ap.parse_args();o=a.output;o.mkdir(exist_ok=True)
 raw=a.rom.read_bytes();b=bundle(raw)
 if a.roll_only:
  refpath=Path(__file__).resolve().parents[2]/'build/mini-idle-constants-1103/mini-idle-fast.nes'
  ref=bundle(refpath.read_bytes());checks=[]
  for active in [0,1,3]:
   machines=[];outcomes=[]
   for image in [ref,b]:
    m=N.fresh(image)
    N.put(m,SelectedCharacter=address(image,'CHARACTER_BASS'),RlVariant=1,GameEngineSubroutine=8,TimerControl=0,MmDeathFlag=0,ObjectOffset=3,SavedJoypadBits=0,Player_X_Position=80,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,AreaType=1)
    N.invoke(m,'RlEnsure')
    N.put(m,RlFresh=0)
    for i in range(active):
     for name,value in [('MmBulletType',1),('MmBulletX',140+i*20),('MmBulletY',160),('MmBulletPage',0),('MmBulletAge',0)]:m[address(image,name)+i]=value
    out=N.invoke(m,'RlWeapons',a=89,x=7,y=91,p=0x61)
    outcomes.append(out);machines.append(m)
   assert [(q['A'],q['X'],q['Y'],q['P'])for q in outcomes][0]==[(q['A'],q['X'],q['Y'],q['P'])for q in outcomes][1],outcomes
   assert machines[0][0:0x8000]==machines[1][0:0x8000],active
   assert all(x==y for x,y in zip(machines[0].ram,machines[1].ram)),active
   assert machines[0].rawtags==machines[1].rawtags
   checks.append(dict(active_native_bullets=active,actual_RlWeapons_complete=True,AXYP_full_native_RAM_overlay_and_maps_exact=True,cycles=[q['CPU']for q in outcomes]))
  receipt=dict(passed=True,ROM_SHA256=hashlib.sha256(raw).hexdigest(),reference_ROM_SHA256=hashlib.sha256(ref['raw']).hexdigest(),protective_JMP='B53A JMP B54C',cases=checks,scope='Actual native Roll whole weapon loop, empty/one/three typed CPU bullets. Compare against pre-f552 safe Roll continuation; no PC interception or ROM output.')
  (o/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
 def machine():
  m=N.fresh(b)
  N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
  N.invoke(m,'MiniScene')
  N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8,PlayerStatus=0,PlayerSize=1,Player_X_Position=80,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerFacingDir=1,FrameCounter=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,TimerControl=0,GameTimerDisplay=4,AreaType=1)
  for n in ['Block_Buffer_1','Block_Buffer_2']:
   at=address(b,n);m[at:at+208]=[0]*176+[0x54]*32
  N.invoke(m,'GameCoreRoutine',x=0,y=0)
  return m
 seed=machine();rows=[]
 if a.enemy_only:
  m=N.fork(seed);N.put(m,PlayerStatus=2,PlayerFacingDir=1)
  px=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');ex=px+24
  # EnemyLanding stores low-nibble8, and ChkUnderEnemy uses Y+24: floor208
  # therefore means nativeY184. Its actual16px displayed body starts192.
  for name,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=ex&255,Enemy_PageLoc=ex>>8,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_X_Speed=248,Enemy_Y_Speed=0,Enemy_MovingDir=2,Enemy_BoundBoxCtrl=9).items():m[address(b,name)]=value
  before=list(m[address(b,'Player1ScoreDisplay'):address(b,'Player1ScoreDisplay')+6]);trace=[];hit=None
  N.put(m,ObjectOffset=0)
  floor=N.invoke(m,'ChkUnderEnemy',x=0)
  assert floor['A']==0x54,('Enemy native floor fixture',floor,m[3:11],hex(address(b,'Block_Buffer_1')),hex(address(b,'Block_Buffer_2')))
  for tick in range(40):
   buttons=64 if tick==3 else 0
   N.put(m,FrameCounter=32+tick,SavedJoypadBits=buttons,SavedJoypad1Bits=buttons,A_B_Buttons=buttons&192,PreviousA_B_Buttons=64 if tick==4 else 0,Left_Right_Buttons=buttons&3,Up_Down_Buttons=0)
   N.invoke(m,'GameCoreRoutine',x=0,y=0)
   row=dict(tick=tick,playerY=N.get(m,'Player_Y_Position'),enemyY=N.get(m,'Enemy_Y_Position'),enemyState=N.get(m,'Enemy_State'),fireState=N.get(m,'Fireball_State'),fireX=N.get(m,'Fireball_X_Position'),fireY=N.get(m,'Fireball_Y_Position'),sfx=N.get(m,'Square1SoundQueue'),floatey=N.get(m,'FloateyNum_Control'),bbox=list(m[address(b,'BoundingBox_UL_Corner')+4:address(b,'BoundingBox_UL_Corner')+8]),shotbox=list(m[0x674:0x678]))
   trace.append(row)
   if row['enemyState']&32:
    assert row['sfx']==address(b,'Sfx_EnemySmack') and row['floatey']==1,row
    assert row['fireState']&128,row
    hit=row;break
  assert hit,trace
  receipt=dict(passed=True,ROM_SHA256=hashlib.sha256(raw).hexdigest(),actual_full_GameCoreRoutine=True,native_fireball_Goomba_defeat=hit,trace=trace,score_event='Actual SetupFloateyNumber control1 awards100 points for Goomba; native smack SFX asserted.',scope='Explicit CPU scene; Goomba native184/displayed192 on208floor; initial horizontal gap24. Three real warm updates compute native bbox, then one real fresh B. No PC interception, outcome seeding, ROM output or Mesen claim.')
  (o/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
 for facing in [1,2]:
  for up in [0,8]:
   m=N.fork(seed)
   N.put(m,PlayerStatus=2,PlayerFacingDir=facing,A_B_Buttons=64,PreviousA_B_Buttons=0,SavedJoypadBits=64|up,FrameCounter=8)
   N.invoke(m,'ProcFireball_Bubble',a=0xa5,x=7,y=91,p=0xe1)
   vals={n:N.get(m,n)for n in ['Fireball_State','Fireball_X_Position','Fireball_PageLoc','Fireball_Y_Position','Fireball_Y_HighPos','Fireball_X_Speed','Fireball_Y_Speed','Fireball_BoundBoxCtrl','FireballMetasprite']}
   assert vals['Fireball_State']==1 and vals['Fireball_BoundBoxCtrl']==8 and vals['FireballMetasprite']==0,vals
   assert vals['Fireball_X_Speed']==(32 if facing==1 else 224),vals
   base_x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
   shot_x=vals['Fireball_X_Position']+256*vals['Fireball_PageLoc']
   assert shot_x==base_x+(4 if facing==1 else-8),(base_x,shot_x,vals)
   # A released edge permits slot1 while slot0 continues genuine physics.
   N.put(m,A_B_Buttons=0,PreviousA_B_Buttons=64,FrameCounter=9)
   N.invoke(m,'ProcFireball_Bubble')
   N.put(m,A_B_Buttons=64,PreviousA_B_Buttons=0,FrameCounter=10)
   N.invoke(m,'ProcFireball_Bubble')
   assert [N.get(m,'Fireball_State',i)for i in [0,1]]==[1,1]
   assert [N.get(m,'Fireball_BoundBoxCtrl',i)for i in [0,1]]==[8,8]
   assert [N.get(m,'Fireball_X_Speed',i)for i in [0,1]]==[32 if facing==1 else 224]*2
   # Third fresh edge is refused while both actors are busy. Neither X is
   # reinitialized, and held B continues motion without automatic refiring.
   for epoch,buttons,old in [(11,0,64),(12,64,0),(13,64,64),(14,64,64)]:
    before=[N.get(m,'Fireball_X_Position',i)for i in [0,1]]
    N.put(m,A_B_Buttons=buttons,PreviousA_B_Buttons=old,FrameCounter=epoch,Square1SoundQueue=0)
    N.invoke(m,'ProcFireball_Bubble')
    assert [N.get(m,'Fireball_State',i)for i in [0,1]]==[1,1]
    assert [N.get(m,'Fireball_X_Position',i)for i in [0,1]]==[(v+(2 if facing==1 else-2))&255 for v in before]
    assert N.get(m,'Square1SoundQueue')!=0x20
   # Full draw executes both through the universal body-return wrapper.
   N.invoke(m,'DrawAllMetasprites',a=0,x=0,y=0)
   records=[list(m[at:at+4])for at in range(0x200,0x300,4)if m[at]<240 and m[at+1]==0x6f]
   assert len(records)==2,records
   assert N.get(m,'CurrentCHRBank',5)==199 and m[0x73e5]==0x83
   assert all(v[2]==2 for v in records)
   only_second=N.fork(m)
   N.put(only_second,PlayerStatus=0,Fireball_State=0,FireballMetasprite=0,A_B_Buttons=0,PreviousA_B_Buttons=64)
   N.invoke(only_second,'ProcFireball_Bubble')
   assert [N.get(only_second,'Fireball_State',i)for i in [0,1]]==[0,0]
   N.put(m,PlayerStatus=0,A_B_Buttons=0,PreviousA_B_Buttons=64)
   N.invoke(m,'ProcFireball_Bubble')
   assert [N.get(m,'Fireball_State',i)for i in [0,1]]==[0,0]
   assert [N.get(m,'FireballMetasprite',i)for i in [0,1]]==[0,0]
   rows.append(dict(facing=facing,up=bool(up),first=vals,OAM=records,two_active=True,third_fresh_edge_and_hold_refused=True,power_loss_clears_both=True,only_second_active_power_loss_clears=True))
 # Actual renderer code: slot clipping and OAM allocation are independent.
 labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(a.rom.parent/'render.lbl').read_text(),re.M)}
 b['segs']['fire89']=dict(start=str(0xa000),ooffs=str(16+89*8192))
 b['syms']['MiniFireballDraw']=dict(val=str(labels['MiniFireballDraw']),seg='fire89')
 clip_rows=[]
 for clipped in [None,0,1,'both','vertical']:
  m=N.fork(seed);m[0x200:0x300]=[248,0,0,0]*64
  N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=12)
  for i in [0,1]:
   for name,value in [('Fireball_State',1),('Fireball_X_Position',80+i*20),('Fireball_PageLoc',0),('Fireball_Y_Position',196)]:m[address(b,name)+i]=value
  if clipped in [0,1]:m[address(b,'Fireball_X_Position')+clipped]=250
  if clipped=='both':m[address(b,'Fireball_Y_Position'):address(b,'Fireball_Y_Position')+2]=[240,240]
  if clipped=='vertical':m[address(b,'Fireball_Y_Position')]=240
  N.invoke(m,'MiniFireballDraw',a=0,x=0,y=0)
  expected=2 if clipped is None else 0 if clipped=='both' else 1
  recs=[(at,list(m[at:at+4]))for at in range(0x200,0x300,4)if m[at]<240 and m[at+1]==0x6f]
  assert len(recs)==expected and N.get(m,'CurrentOAMOffset')==expected*4,(clipped,recs)
  assert [at for at,v in recs]==[0x20c+i*4 for i in range(expected)]
  clip_rows.append(dict(clipped=clipped,visible=expected,records=recs))
 # The actual constructor's redirected MiniInit clears both native slots,
 # including stale state after a foreign roster profile.
 m=N.fork(seed)
 for name in ['Fireball_State','FireballMetasprite']:
  at=address(b,name);m[at:at+2]=[129,130]
 # Row36 re-enters the true native Mini scene constructor through its
 # authenticated public service. NrReset owns scene, rather than direct RAM.
 N.put(m,DisableScreenFlag=1,Mirror_PPUMASK=0)
 N.invoke(m,'GmFreshGate')
 for name in ['Fireball_State','FireballMetasprite']:
  at=address(b,name);assert m[at:at+2]==[0,0],(name,m[at:at+2])
 receipt=dict(passed=True,ROM_SHA256=hashlib.sha256(raw).hexdigest(),native_Mesen_run=False,actual_native_ProcFireball_Bubble_and_DrawAll=rows,independent_clipping_and_rotated_OAM=clip_rows,fresh_scene_clears_both_slots=True,
  scope='Actual compiled CPU/native actor and renderer callers. Status2 is an explicit CPU fixture, not an earned flower. No PPU deadline or physical native acceptance claim.')
 (o/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
