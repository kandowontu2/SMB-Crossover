"""Actual caller/parser/OAM and vector proof for BT's late-color/body repair."""
from pathlib import Path
import argparse, collections, itertools, json, sys, traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_joint_cold_controls_v1 as T
import battletoads_current_loader_controls_v1 as L
H=T.H;address=L.address
J=R/'build/bt-lives-body-source-v7/joint';P=R/'build/bt-lives-body-source-v5/joint'
O=R/'build/bt-lives-body-controls-v3'
SHA='b356ae88e13ff319dc863ddc59df02edca879aeafc923e0d815c641830b3de91'

def bound():
 d=json.loads((J.parent/'source-stage.json').read_text());assert d['candidate']==L.sha(J/'candidate.nes')==SHA
 for n,h in d['bindings'].items():assert L.sha(n)==h,n
 H.O=J
 return len(d['bindings'])

def seed(b,v):
 m=L.make(b,FmGroups=v<<5,CurrentPlayer=0);L.call(m,'BtAcquire');assert T.T.get(m,'BtHostReady')==1
 H.put(m,ScreenRoutineTask=0,Mirror_PPUMASK=0,DisableScreenFlag=1)
 T.invoke(m,'InitScreen');T.C.A.consume(m)
 assert m.vram[0x3f04]==m.vram[0x3f14]==15
 return m

def callers():
 bs=[H.C.qualified(p/'candidate.nes')for p in[P,J]];pairs=0;edges=[]
 for variant in [0,1]:
  seeds=[seed(b,variant)for b in bs]
  for player,players,message,f in itertools.product(range(2),range(2),[0,1,2,3,4],range(64)):
   mm=[];cc=[]
   for s in seeds:
    m=L.fork(s);H.put(m,CurrentPlayer=player,NumberOfPlayers=players,VRAM_Buffer1_Offset=0,WorldNumber=0,LevelNumber=0,NumberofLives=2)
    c,_=L.call(m,'WriteGameText',a=message,x=91,y=37,p=L.flags(f));mm.append(m);cc.append(c)
   assert[(c.a,c.x,c.y,c.p,c.sp)for c in cc][0]==[(c.a,c.x,c.y,c.p,c.sp)for c in cc][1],('real native returned AXYP/SP',variant,player,players,message,f)
   at=address(bs[1],'VRAM_Buffer1')
   if message==1:
    assert bytes(mm[0][at:at+30])==bytes(mm[1][at:at+30]),'native30-byte lives packet changed'
    wanted=bytes([63,17,7])+bytes([15,10,26]if variant==0 else[15,23,39])+bytes([15,24,40,32,0])
    assert bytes(mm[1][at+30:at+41])==wanted
    assert H.get(mm[1],'VRAM_Buffer1_Offset')==40
    if f==0:
     before=list(mm[1].vram[0x3f11:0x3f18]);r=T.C.A.consume(mm[1])
     assert list(mm[1].vram[0x3f11:0x3f14])==list(wanted[3:6])
     assert list(mm[1].vram[0x3f15:0x3f18])==[24,40,32]
     edges.append(dict(variant=variant,player=player,NumberOfPlayers=players,before=before,after=list(mm[1].vram[0x3f11:0x3f18]),NMI=r))
   else:
    assert bytes(mm[0][at:at+128])==bytes(mm[1][at:at+128]),('unrelated text changed',message)
   assert [bytes(x)for x in mm[0].ram[:3]]==[bytes(x)for x in mm[1].ram[:3]]
   assert mm[0].rawtags==mm[1].rawtags
   pairs+=1
 # Probe the exact typed continuation guard, not an unbounded queue context.
 rejected=0;b=bs[1]
 for a,y in [(1,0),(1,29),(1,31),(2,30),(3,30),(4,30),(255,30)]:
  m=seed(b,0);H.put(m,VRAM_Buffer1_Offset=0);at=address(b,'VRAM_Buffer1');before=bytes(m[at:at+128])
  c,_=T.T.row(m,30,a=a,y=y)
  assert bytes(m[at:at+128])==before and H.get(m,'VRAM_Buffer1_Offset')==0
  rejected+=1
 return dict(passed=True,actual_WriteGameText_pairs=pairs,complete_native_AXYP_SP_exact=True,native30byte_lives_packet_exact=True,
   typed_black_lives_11byte_packet_at30=True,transparent3F14_native0F_preserved=True,full_normal_NMI_body_roles=edges,other_typed_contexts_unchanged=rejected,
   retained_P2_cosmetic='Native CheckPlayerName still writes LUIGI over first5 header bytes in a two-player P2 A0 call.')

def natural():
 b=H.C.qualified(J/'candidate.nes');rows=[]
 T.ROM+=['WriteGameText','SetupIntermediate','DisplayIntermediate'];T.RAM+=['BtStatusName']
 for player,variant in itertools.product(range(2),range(2)):
  m=T.C.fresh(b,0);H.put(m,CurrentPlayer=player,CrossoverMenuIndex=23,FmGroups=variant<<5,SelectedCharacter=0,CrossoverMenuState=2)
  before=bytes(m.ram[3]);cold=[]
  for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
   cold.append(T.invoke(m,n));assert H.get(m,'SelectedCharacter')==33 and bytes(m.ram[3])==before and m.ppu_reads==0
  assert H.get(m,'CurrentOAMOffset')==32 and cold[-1]['counts'].get('BtColdPortrait')==1
  H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
  start=T.invoke(m,'CrossoverMenuInput');a,x,y,p=start['AXYP_SP'][:4]
  T.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=a,x=x,y=y,p=p);T.invoke(m,'PauseRoutine',a=0)
  assert H.get(m,'FmGroups')==variant<<5
  stages=[];seen_lives=False
  for age in range(600):
   if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
   H.put(m,SavedJoypad1Bits=0,SavedJoypad2Bits=0,SavedJoypadBits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
   z=T.invoke(m,'GameLoop');nmi=T.C.A.consume(m)
   if z['counts'].get('DisplayIntermediate'):
    assert H.get(m,'CurrentOAMOffset')==32
    assert list(m.vram[0x3f11:0x3f14])==([15,10,26]if variant==0 else[15,23,39])
    assert list(m.vram[0x3f15:0x3f18])==[24,40,32];seen_lives=True
   stages.append(dict(age=age,counts=z['counts'],NMI=nmi))
  else:raise AssertionError('native parser bound')
  assert seen_lives and m.ppu_reads==16400 and T.T.get(m,'BtHostReady')==1
  frames=[]
  for age in range(40):
   keys=1|(128 if 4<=age<12 else 0)|(64 if 16<=age<24 else 0)
   H.put(m,SavedJoypad1Bits=keys if player==0 else 0,SavedJoypad2Bits=keys if player==1 else 0,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
   clock=T.T.get(m,'BtSrc_FrameCounter');z=T.invoke(m,'GameLoop')
   for n in ['BtMovement','BtCoreStep','BtPhysicsStep','BtGraphics','BtDraw','PlayerBGCollision']:assert z['counts'].get(n)==1,(player,variant,age,n,z['counts'])
   assert z['source_clock']==(clock+1)&255 and z['HP']>0 and not H.get(m,'MmDeathFlag')
   visible=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240 and m[513+i]<64]
   assert len(visible)>=6,('actual source body absent',player,variant,age,visible)
   assert T.T.get(m,'BtRenderBuffer')>=24
   nmi=T.C.A.consume(m)
   assert T.T.get(m,'BtSrc_FrameCounter')==z['source_clock']
   assert 915<=m.chr_latches[0]<919
   frames.append(dict(age=age,input=keys,Main=z,body_OAM=visible,physicalCHR=m.chr_latches[0],NMI=nmi))
  assert max(e['Main']['X']for e in frames)>min(e['Main']['X']for e in frames)
  assert min(e['Main']['Y']for e in frames)<160
  rows.append(dict(player=player,variant=variant,cold=cold,Start=start,parser=stages,frames=frames))
  print('actual natural menu/parser/visible Main PASS',player,variant,flush=True)
 return dict(passed=True,cohorts=4,real_Main_updates=160,no_ready_cache_support_HP_preload=True,sourceGraphics_andDraw_once_per_Main=True,rows=rows)

def pixels():
 import battletoads_native_adapter_controls_v2 as V
 source=Path(V.__file__).read_text(encoding='utf-8')
 source=source.replace('T.row(m,26)',"T.direct(m,'BtColors')")
 source=source.replace("assert m.rawtags[2]==0xa2 and T.H.get(m,'CurrentBankC')==0xa2","assert m.rawtags[2]==3 and T.H.get(m,'CurrentBankC')==3")
 source=source.replace("T.address(b,'QwEmpty34')","T.address(b,'BtEmpty')+8192")
 ns={'__file__':V.__file__,'__name__':'actual_BT_new_C3_pixel_contract'}
 exec(compile(source,V.__file__,'exec'),ns)
 return dict(passed=True,result=ns['render'](H.C.qualified(J/'candidate.nes')),typed_changes='Graphics/Draw publish own C3 empty descriptor before native post-shot reservation; colors compared through genuine own BtColors, not cold ROM26 with its area-backdrop packet.')

def foreign():
 import cf_bt_shared_foreign_main_v1 as F
 F.J=J;F.P=P;F.O=O/'foreign-main';F.main()
 return json.loads((F.O/'controls.json').read_text())

def vectors():
 b=H.C.qualified(J/'candidate.nes');warm=seed(b,0);rows=[]
 for slot,a,y in [(30,1,30),(2,85,91)]:
  initial=L.fork(warm);H.put(initial,NmiDisable=255,GuestAudioCharacter=22,Square1SoundQueue=4,Square2SoundQueue=8,CurrentOAMOffset=0,VRAM_Buffer1_Offset=30,OperMode=0)
  if slot==2:T.T.put(initial,'BtSrc_player1_obj_wanted_frame',1)
  def begin(m):
   c=H.start(m,'BtServiceVeneers',a=a,y=y,p=48);at=address(b,'BtServiceVeneers')+3*slot
   m[address(b,'FarcallJmpTarget_SMC')+1]=at&255;m[address(b,'FarcallJmpTarget_SMC')+2]=at>>8;return c
  m=L.fork(initial);cuts=[];seen=set()
  def trace(mm,c,step):
   tag=mm.rawtags[(c.pc-32768)//8192]if c.pc>=32768 else-1
   own=(tag==3 and (address(b,'BtGraphics')<=c.pc<address(b,'BtEmpty')or address(b,'BtStatusName')<=c.pc<address(b,'BtStatusNames')))
   if own and(tag,c.pc)not in seen:seen.add((tag,c.pc));cuts.append((step,c.pc,bool(c.p&4)))
  H.finish(m,begin(m),trace)
  assert cuts
  for step,pc,masked in cuts:
   for kind in ['NMI']+([]if masked else['IRQ']):
    m=L.fork(initial);proof=[]
    def inject(mm,c,tick):
     if tick==step:
      assert c.pc==pc;proof.append(L.V.interrupt(mm,c,kind))
    c,lo=H.finish(m,begin(m),inject);assert len(proof)==1 and c.sp==224
    rows.append(dict(slot=slot,PC=pc,**proof[0]))
  for pause in [0,1]:
   m=L.fork(initial);c,_=H.finish(m,begin(m));H.put(m,NmiDisable=0,GamePauseStatus=pause)
   rows.append(dict(slot=slot,completed=True,pause=pause,**L.V.interrupt(m,c,'NMI')))
 return dict(passed=True,cases=len(rows),all33SMC_AXYP_SP_livepage1_rawmaps_exact=True,rows=rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',choices=['callers','natural','pixels','foreign','vectors'],required=True);a=ap.parse_args()
 O.mkdir(exist_ok=True);out=O/(a.check+'-controls.json');assert not out.exists();q=dict(passed=False,native=False,candidate=SHA,check=a.check)
 try:q.update(source_bindings_verified=bound(),result=globals()[a.check](),passed=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(T.__file__),Path(L.__file__),J.parent/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in q.items()if k not in['result','bindings']}),flush=True)
 if q['passed']:print(json.dumps({k:v for k,v in q['result'].items()if k not in['rows','cohorts','bindings','result']}),flush=True)
 assert q['passed'],q.get('error')
if __name__=='__main__':main()
