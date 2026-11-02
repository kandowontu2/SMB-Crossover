"""In-memory real1966 native binding, original source roots, compiled lifecycle."""
from pathlib import Path
import hashlib,json
import prince_host_world_compiled_1102_v8 as C
import compile_prince_host_lifecycle_1102_v12 as L
W=C.W;P,O=C.P,C.O
BASE,PIN=L.BASE,L.PIN
W.BASE=BASE;W.PIN=PIN


class World(C.World):
 def __init__(self,b=None,x=48,y=176):
  super().__init__(b,x=x,y=y)
  self.worldlab=P.T.labels(O/'host-life-v12.lbl');self.lab.update(self.worldlab)
  coords=P.T.labels(O/'world-coordinates-v7.lbl');self.s[:]=bytes(8192)
  blob=(O/'world-coordinates-v7.bin').read_bytes();self.s[0x100:0x200]=blob[:256];self.s[0x235:0x235+len(blob)-256]=blob[256:]
  self.m.ram[3][:]=bytes(8192);self.loadcode(0xa000,(O/'contact-core.bin').read_bytes());self.loadcode(0xb310,(O/'contact-point.bin').read_bytes());self.loadcode(0xbbc1,(O/'host-render-v11.bin').read_bytes())
  blob=(O/'host-life-v12.bin').read_bytes();layout=json.loads((O/'host-life-layout-v12.json').read_text())
  for q in layout['regions']:
   at,end=q['half_open'];self.loadcode(at,blob[q['source_file_offset']:q['source_file_offset']+end-at])
  meta=(O/'prince-pose-packets-v11.bin').read_bytes();self.s[0x800:0x800+len(meta)]=meta
  base_lab=P.T.labels(O/'contact-core.lbl')
  self.callbacks={base_lab[n]:(n,k[0],int(k[1],16))for n,k in self.recovery['declared_original_environment_boundaries'].items()}
  targets={**{n:a for n,a in coords.items()if n in self.recovery['declared_original_environment_boundaries']},**{n:a for n,a in self.worldlab.items()if n in self.recovery['declared_original_environment_boundaries']}}
  targets['PpWorldContext']=self.worldlab['PpWorldSourceContext'];targets['PpWorldColumn']=self.worldlab['PpWorldSourceColumn']
  for n in ['PpWorldGateState','PpWorldGateSupport','PpWorldGateHeight']:targets[n]=self.worldlab['PpWorldGateEmpty']
  self.map()
  for tag,v in self.recovery['instructions'].items():
   if v['mn']not in ['JSR','JMP']:continue
   bank,pc=tag.split(':');at=self.lab[f'PpN_{bank}_{pc}'];old=self.m[at+1]|self.m[at+2]<<8;n=self.callbacks.get(old,(None,))[0]
   if n in targets:self.m[at+1]=targets[n]&255;self.m[at+2]=targets[n]>>8
  self.callbacks={a:v for a,v in self.callbacks.items()if v[0]not in targets}
  W.N.put(self.m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1,GameEngineSubroutine=8,SelectedCharacter=38)
  self.rootcounts={};self.cost=[];self.source('PpHostInit')
 def source(self,name):
  # Reuse bounded original-audio fixture boundaries; all movement, control,
  # coordinates, projection, native terrain and export now execute6502.
  c=super().source(name);self.cost.append(c.processorCycles);return c
 def step(self,pad):
  W.N.put(self.m,SavedJoypad1Bits=pad)
  c=self.source('PpHostUpdate')
  phase=(self.s[0xa6]-1)&3
  assert c.p&1
  return dict(X=self.x(),Y=self.s[0x611],foot=self.field('PpWorldFoot')|(self.field('PpWorldFoot',delta=1)<<8),frame=self.s[0x617],action=self.s[0x616],mode=self.s[0x618],phase=phase,nativeX=W.N.get(self.m,'Player_X_Position')|(W.N.get(self.m,'Player_PageLoc')<<8),nativeY=W.N.get(self.m,'Player_Y_Position'),nativeYHigh=W.N.get(self.m,'Player_Y_HighPos'),cameraSample=W.N.get(self.m,'Player_Pos_ForScroll'))
