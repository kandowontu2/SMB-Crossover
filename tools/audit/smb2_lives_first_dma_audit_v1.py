"""Retain first actual cold lives-DMA palette/queue order on old/new source CPU."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
O=R/'build/smb2-lives-first-dma-audit-v1';assert not O.exists();O.mkdir()
s=importlib.util.spec_from_file_location('one_lives_dma_factory',R/'build/smb2-natural-current-audio-v20/controls.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A);C=A.C;M=A.M
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
Base=C.Bus
class TraceBus(Base):
 def __setitem__(self,a,v):
  if isinstance(a,int)and a==0x4014 and self.get('OperMode')==1 and self.get('ScreenRoutineTask')==7:
   at=self.lab['VRAM_Buffer1'];self.dmas.append(dict(phase=self.phase,PC=self.pc,P0=list(self.vram[0x3f11:0x3f14]),BG=self.vram[0x3f00],task=self.get('ScreenRoutineTask'),disabled=self.get('DisableScreenFlag'),mask=self.ppu_mask,source=v,buffer_offset=self.get('VRAM_Buffer1_Offset'),buffer=list(self.ram[at:at+84]),published=self.get('VRAM_Buffer_AddrCtrl'),PPU_writes=self.palette_writes[-40:]))
  super().__setitem__(a,v)
for dirname in['functional-roster-coherent62-v4','arthur-goku-smb2-palette-v1']:
 J=R/'build'/dirname/'joint';m=M.fresh(0,0);old=C.O;C.O=J
 try:b=C.Bus()
 finally:C.O=old
 m.bundle=b.bundle;m.ROM_banks=b.ROM_banks;m.lab=b.lab;m.__class__=TraceBus;m.dmas=[];m.phase='menu'
 C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
 A.interrupt(m,0);M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',A=0)
 for age in range(80):
  m.phase='NMI-'+str(age);A.interrupt(m,0);m.phase='Main-'+str(age);C.invoke(m,'GameLoop')
  if len(m.dmas)>=3:break
 rows.append(dict(candidate=sha(J/'candidate.nes'),first_lives_dmas=m.dmas,actual_palette_end=list(m.vram[0x3f10:0x3f14])))
p=O/'audit.json';p.write_text(json.dumps(dict(source_CPU_only=True,rows=rows,bindings={str(Path(__file__).resolve()):sha(__file__),str(Path(A.__file__)):sha(A.__file__)}),indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(path=str(p),sha256=sha(p),first_P0=[r['first_lives_dmas'][0]['P0']for r in rows])),flush=True)
