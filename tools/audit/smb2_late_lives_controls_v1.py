"""Actual pending-ROM/lives-text overwrite regression and repaired late consumer."""
from pathlib import Path
import copy,hashlib,importlib.util,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
O=R/'build/smb2-late-lives-controls-v1';P=R/'build/arthur-goku-smb2-palette-v1/joint';J=R/'build/smb2-late-lives-palette-v4/joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('one_late_status_source_factory',R/'build/smb2-natural-current-audio-v20/controls.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A);C=A.C;M=A.M
BODY=[[1,22,39],[1,42,54],[1,48,39],[6,37,54]]
Base=C.Bus
class TraceBus(Base):
 def __setitem__(self,at,v):
  if isinstance(at,int)and at==0x4014 and self.get('OperMode')==1 and self.get('ScreenRoutineTask')==7:
   self.livesDMA.append(dict(P0=list(self.vram[0x3f11:0x3f14]),BG=self.vram[0x3f00],offset=self.get('VRAM_Buffer1_Offset'),ack=self.get('S2PaletteAck'),CPU_PC=self.pc))
  if isinstance(at,int)and at==self.lab['VRAM_Buffer1'] and self.get('ScreenRoutineTask')==6:
   self.overwrites.append(dict(PC=self.pc,before=self.ram[at],value=v,offset=self.get('VRAM_Buffer1_Offset'),ack=self.get('S2PaletteAck')))
  super().__setitem__(at,v)
def seed(j,v=0,mode=0):
 m=M.fresh(v,mode);old=C.O;C.O=j
 try:b=C.Bus()
 finally:C.O=old
 m.bundle=b.bundle;m.ROM_banks=b.ROM_banks;m.lab=b.lab;m.__class__=TraceBus;m.livesDMA=[];m.overwrites=[]
 C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
 A.interrupt(m,0);return m

def hits(m,z,n):return sum(pc==m.lab[n]and pc>=32768 and tags[(pc-32768)//8192]==m.bank(n)|128 for tags,pc in z['trace'])
def cold(j,v,mode,finish=True):
 m=seed(j,v,mode);M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',A=0);paired=False;seen=False;record={}
 for age in range(1500):
  A.interrupt(m,0);z=C.invoke(m,'GameLoop')
  if not paired and m.get('OperMode_Task')==1 and m.get('ScreenRoutineTask')==1 and m.get('VRAM_Buffer_AddrCtrl')==3:
   before=dict(published=m.get('VRAM_Buffer_AddrCtrl'),ack=m.get('S2PaletteAck'),task=m.get('ScreenRoutineTask'));zz=C.invoke(m,'GameLoop');assert hits(m,zz,'SetupIntermediate')==1 and hits(m,zz,'S2MainPalette')==1 and m.get('S2PaletteAck')==255
   record['actual_InitScreen_then_SetupIntermediate_before_same_NMI']=dict(before=before,after=dict(published=m.get('VRAM_Buffer_AddrCtrl'),ack=m.get('S2PaletteAck'),offset=m.get('VRAM_Buffer1_Offset'),task=m.get('ScreenRoutineTask')));paired=True
  if hits(m,z,'DisplayIntermediate'):
   at=m.lab['VRAM_Buffer1'];record['after_actual_native_lives_text']=dict(offset=m.get('VRAM_Buffer1_Offset'),ack=m.get('S2PaletteAck'),buffer=list(m.ram[at:at+45]),overwrites=m.overwrites[:]);seen=True
   A.interrupt(m,0);assert m.livesDMA;record['actual_first_lives_DMA']=m.livesDMA[0]
   if not finish:break
   assert m.livesDMA[0]['P0']==BODY[v]and m.livesDMA[0]['BG']==15,(v,mode,m.livesDMA[0])
  if finish and m.get('OperMode_Task')==3 and m.get('GameEngineSubroutine')==8:
   A.interrupt(m,0);assert m.vram[0x3f00]==34;record['entered_BG']=m.vram[0x3f00];record['Main']=[]
   for tick in range(8):
    A.interrupt(m,1 if tick>2 else 0);z=C.invoke(m,'GameLoop');assert m.vram[0x3f00]==34;record['Main'].append(dict(CPU=z['CPU'],x=m.get('Player_X_Position'),y=m.get('Player_Y_Position')))
   break
 else:raise AssertionError('actual cold bound')
 assert paired and seen;return m,record

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,checks={});ck=q['checks']
 try:
  assert sha(J/'candidate.nes')=='6c6ad55fb77b3ad1741440557541342a2829c971f65e2be92f492ec741ff88fe'
  old,negative=cold(P,0,0,False);assert negative['actual_first_lives_DMA']['P0']==[22,39,24]and negative['after_actual_native_lives_text']['ack']==0;ck['reproduced_native_3721_pending_ROM3_then_text_overwrite']=negative
  rows=[];bases=[]
  for var,mode in itertools.product(range(4),range(2)):
   m,z=cold(J,var,mode);rows.append(dict(var=var,mode=mode,**z))
   if mode==0:bases.append(m)
  ck['all8_actual_pendingROM3_lives_entrance_64Main']=rows
  # Actual old/new service30 all64flags: A0 old name+C output exact;
  # A1 invalidY and all other A remain application/register/map exact.
  abi=[]
  for sourceA,Y,flags in itertools.product([0,1,2,255],[0,29,31,255],range(64)):
   p=(flags&3)|((flags&4)<<1)|((flags&8)<<3)|((flags&16)<<3)|((flags&32)<<2)|0x30;pair=[]
   for j in[P,J]:
    m=seed(j);M.put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0);z=C.invoke(m,'S2MenuStatus',A=sourceA,X=0x57,Y=Y,P=p)
    pair.append((z['registers'],bytes(m.ram[:256]),bytes(m.ram[0x300:0x800]),m.tags[:],bytes(m.ram[0x15a:0x17b])))
   assert pair[0]==pair[1],(sourceA,Y,flags,pair[0][0],pair[1][0]);abi.append([sourceA,Y,flags])
  ck['original_nonlives_service30_full64flag_ABI']=dict(cases=len(abi))
  # Actual A1/Y30 callback appends to the genuine native lives message,
  # preserves original R0..7/BGctrl/AXYP/C/all33SMC; published rejection stays
  # invalid and a later authentic callback retries a whole packet.
  rows=[]
  for var,flags,published in itertools.product(range(4),range(64),[0,3]):
   m=seed(J,var);M.put(m,OperMode=1,BackgroundColorCtrl=0,VRAM_Buffer_AddrCtrl=published,VRAM_Buffer1_Offset=83,S2PaletteAck=0)
   at=m.lab['VRAM_Buffer1'];m.ram[at:at+30]=bytes(range(30));m.ram[at+30]=0;m.ram[at+84]=0xa6
   for i in range(8):m.ram[m.lab['R0']+i]=(i*17+31)&255
   before=bytes(m.ram[m.lab['R0']:m.lab['R0']+8]);maps=m.tags[:];smc=bytes(m.ram[0x15a:0x17b]);p=(flags&3)|((flags&4)<<1)|((flags&8)<<3)|((flags&16)<<3)|((flags&32)<<2)|0x30;z=C.invoke(m,'S2MenuStatus',A=1,X=0x57,Y=30,P=p)
   assert z['registers']==dict(A=1,X=0x57,Y=30,P=p)and bytes(m.ram[m.lab['R0']:m.lab['R0']+8])==before and m.tags==maps and m.get('BackgroundColorCtrl')==0 and m.ram[at+84]==0xa6
   assert bytes(m.ram[at:at+30])==bytes(range(30))
   if published:assert m.get('S2PaletteAck')==255 and m.get('VRAM_Buffer1_Offset')==30
   else:assert list(m.ram[at+30:at+38])==[63,16,4,15]+BODY[var]+[0]and m.get('VRAM_Buffer1_Offset')==37 and m.get('S2PaletteAck')==[0,3,2,1][var]
   rows.append([var,flags,published,z['CPU']])
  ck['all512_late_fullqueue_reclaim_published_retry_ABI']=dict(cases=len(rows),rows=rows)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  paths={Path(__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',R/'build/smb2-late-lives-palette-v4/source-proof.json',R/'build/smb2-lives-palette-diagnostic-v1/class0/capture/palette-write-order.csv',R/'build/smb2-lives-palette-diagnostic-v1/class0/ready.json'}
  for mod in list(sys.modules.values()):
   f=getattr(mod,'__file__',None)
   if f and Path(f).resolve().is_relative_to(R/'tools'):paths.add(Path(f).resolve())
  paths|={Path(A.__file__),Path(M.__file__),Path(C.__file__)};q['bindings']={str(p.resolve()):sha(p)for p in paths if p.is_file()};out=O/'controls.json';out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),path=str(out),sha256=sha(out))),flush=True)
if __name__=='__main__':main()
