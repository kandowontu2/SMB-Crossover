"""67B source worker API in a synthetic ROM fetchview; no cartridge claim."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_loader_isr_controls_v2 as U
import contra_force_p1_stale_palette_ppu_v2 as F
V=F.V;Q,T,C=V.Q,V.T,V.C;U.B=T.B
A=R/'build/contra-force-p1-restore-arena-v2';O=R/'build/contra-force-p1-restore-arena-controls-v3';IMAGE=(A/'worker.bin').read_bytes()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class ArenaBus(T.Bus):
 def raw_page(self,win,raw):
  super().raw_page(win,raw)
  if win==1 and raw==219:list.__setitem__(self,slice(40960,40960+67),IMAGE[:67])
def arena(m):
 m.__class__=ArenaBus
 if m.rawtags[1]==219:m.raw_page(1,219)
 return m
def capture(m,p=0x79):
 c=T.cpu(m,'FwNativeDrawAll',public=True,p=p);saved=None;hits=[]
 while c.pc!=32767:
  if c.pc==T.address(T.B,'DrawAllMetasprites')and m.rawtags[1]==132:hits.append('nativeDraw')
  if c.pc==T.address(T.B,'FarCallCommon')and m.rawtags[1]==190 and m[T.address(T.B,'FarcallJmpTarget_SMC')+1]+256*m[T.address(T.B,'FarcallJmpTarget_SMC')+2]==T.address(T.B,'BtServiceVeneers')+18:
   assert saved is None;saved=U.clone(m,c)
  assert m[c.pc]!=0,('BRK',hex(c.pc),m.rawtags);c.step()
 assert saved is not None and hits==['nativeDraw'];return saved,dict(AXYP=[c.a,c.x,c.y,c.p],rawmaps=m.rawtags[:],SMC=list(T.smc(m)),OAM=list(m[512:768]))
def redirect(m,c):
 arena(m);c.a=219;m[T.address(T.B,'FarcallJmpTarget_SMC')+1]=0;m[T.address(T.B,'FarcallJmpTarget_SMC')+2]=160
 return T.finish(m,c)
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,actual_cartridge=False,resource_adopted=False,checks={})
 try:
  for p,h in json.loads((A/'proof.json').read_text())['bindings'].items():assert sha(p)==h,p
  base=V.scene();valid=[]
  for age in range(6):
   before=bytes(base.ram[2]);(m,c),old=capture(base);oldram=[bytes(x)for x in base.ram];oldglobal=bytes(base[:32768]);model=redirect(m,c)
   assert model['AXYP']==old['AXYP']and m.rawtags==old['rawmaps']and list(T.smc(m))==old['SMC']
   delta=[i for i,(a,b)in enumerate(zip(oldglobal,m[:32768]))if a!=b]
   assert [bytes(x)for x in m.ram]==oldram and all(0x100<=i<=0x1e0 for i in delta),('valid final state outside inactive lower stack',age,delta)
   assert bytes(m[0x1e1:0x200])==oldglobal[0x1e1:0x200]
   assert list(m[512:768])==old['OAM']
   valid.append(dict(age=age,AXYP=model['AXYP'],Last=T.get(m,'SmFreezeLastBlue'),Pending=T.get(m,'SmFreezePalettePending'),Turn=T.get(m,'SmFreezeTurn'),minimum_SP=model['minimum_SP'],inactive_stack_deltas=delta))
  out['checks']['six_valid_epochs_exact_original_final_state']=valid
  # Genuine C1 completed epoch is the starting stale-hardware counterexample.
  base=V.scene()
  for _ in range(5):V.draw(base);F.normal(base)
  assert T.get(base,'SmFreezeLastBlue')==193 and list(base.vram[0x3f15:0x3f18])==[32,56,22]
  rows=[]
  for byte in range(16):
   z=C.clone(base);z.ram[2][0x1fe0+byte]^=1
   (m,c),old=capture(z);m.executed_guest=[];model=redirect(m,c);n=F.normal(m)
   assert not m.executed_guest,('invalid cache first guest',byte,m.executed_guest[:5])
   assert list(m[512:768])==old['OAM']and n['paletteP1']==[26,48,39]
   assert T.get(m,'SmFreezeLastBlue')==192 and T.get(m,'SmFreezeTurn')==1
   rows.append(dict(poisoned_byte=byte,AXYP=model['AXYP'],minimum_SP=model['minimum_SP'],native_P1=n['paletteP1'],actual_normalNMI_CPU=n['CPU']))
  out['checks']['16_stale_yellow_invalid_cookie_actual_native_PPU']=rows
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(F.__file__),Path(V.__file__),A/'proof.json',A/'worker.bin',V.P/'source-stage.json',V.P/'joint/candidate.nes',R/'build/contra-force-p1-stale-palette-ppu-v2/controls.json',R/'build/contra-force-p1-restore-arena-controls-v2/controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'))),flush=True)
if __name__=='__main__':main()
