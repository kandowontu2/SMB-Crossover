"""Recover runtime code room by losslessly encoding regular body cell grids."""
import hashlib,json,re,subprocess
import prepare_metal_storm_pickup_1101_v25 as B
from private_build_outputs_v1 import validate
P=B.P;BASE=B.O;O=P.R/'build/metal-storm-compact-body-1101-v29'

def main():
 O.mkdir(exist_ok=True);t=(BASE/'component.s').read_text()
 old=(P.R/'build/metal-storm-render-host-1101-v7/body-meta.bin').read_bytes()
 assert len(old)==1002
 coords6=[(4,1),(12,1),(20,1),(4,17),(12,17),(20,17)]
 coords8=[(0,1),(8,1),(16,1),(24,1),(0,17),(8,17),(16,17),(24,17)]
 for group in range(33):
  count=old[97+group];at=130+4*old[64+group];coords=coords6 if count==6 else coords8
  assert count in [6,8]
  assert [(old[at+4*i],old[at+4*i+1]) for i in range(count)]==coords
  assert all(old[at+4*i+3]==0 for i in range(count))
 compact=old[:130]+bytes(old[i+2] for i in range(130,946,4))+old[946:]
 assert len(compact)==390
 (O/'body-compact.bin').write_bytes(compact)
 def replace(a,b):
  nonlocal t
  assert t.count(a)==1,(a[:80],t.count(a));t=t.replace(a,b)
 replace(' lda MsBodyOffsets,x\n ldx #0\n stx R1\n asl a\n rol R1\n asl a\n rol R1\n clc\n adc #<MsBodyCells\n sta MsBaseLo\n lda R1\n adc #>MsBodyCells',
         ' lda MsBodyOffsets,x\n clc\n adc #<MsBodyCells\n sta MsBaseLo\n lda #0\n adc #>MsBodyCells')
 replace(' lda (R0),y\n asl a\n asl a\n clc\n adc MsBaseLo\n sta R0\n lda MsBaseHi\n adc #0\n sta R1\n ldy #0\n lda (R0),y\n sta MsCellDx\n iny\n lda (R0),y\n sta MsCellDy\n iny\n lda (R0),y\n sta MsCellPattern\n iny\n lda (R0),y\n eor MsFlip\n sta MsCellAttr',
         ' lda (R0),y\n tay\n tax\n lda MsCount\n cmp #8\n bne Ms29Coordinate\n txa\n clc\n adc #6\n tax\nMs29Coordinate:\n lda Ms29Dx,x\n sta MsCellDx\n lda Ms29Dy,x\n sta MsCellDy\n lda MsBaseLo\n sta R0\n lda MsBaseHi\n sta R1\n lda (R0),y\n sta MsCellPattern\n lda MsFlip\n sta MsCellAttr')
 replace('MsBodyMap:.incbin "body-meta.bin"','MsBodyMap:.incbin "body-compact.bin"')
 replace('MsBodyOrders6=MsBodyMap+946','MsBodyOrders6=MsBodyMap+334')
 replace('MsBodyOrders8=MsBodyMap+970','MsBodyOrders8=MsBodyMap+358')
 replace('MsShotMeta:.incbin', 'Ms29Dx:.byte '+','.join(str(x) for x,y in coords6+coords8)+'\nMs29Dy:.byte '+','.join(str(y) for x,y in coords6+coords8)+'\nMsShotMeta:.incbin')
 (O/'component.s').write_text(t);(O/'component.cfg').write_text((BASE/'component.cfg').read_text().replace(BASE.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16));cc=P.R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.M,'--bin-include-dir',P.R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 compile();actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();extra=(O/'native-extra.bin').read_bytes()
 cookie=bytes([167,35,29])+hashlib.sha256(actor+render+extra+t.encode()).digest()[:13];(O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray((BASE/'candidate.nes').read_bytes())
 for role,bank,off in [('auth',25,0x1f9e),('finish',99,0x176e)]:
  a=(BASE/f'native-{role}.bin').read_bytes();b=(O/f'native-{role}.bin').read_bytes();at=16+8192*bank+off
  assert len(a)==len(b) and raw[at:at+len(a)]==a;raw[at:at+len(b)]=b
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-actor.bin','native-render.bin','native-extra.bin','native-auth.bin','native-finish.bin']:assert f.read_bytes()==(BASE/f.name).read_bytes(),f.name
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16)
 carriers=bytes(image)+render+bytes(3072-len(render))
 for i,page in enumerate([247,248,249,250,827,828,829,830,831,500,494]):
  at=16+1048576+page*1024;raw[at:at+1024]=carriers[i*1024:(i+1)*1024]
 assert len(extra)<=352
 at=16+1048576+499*1024+672;raw[at:at+352]=extra+bytes(352-len(extra))
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),base_ROM_sha256=P.sha(BASE/'candidate.nes'),cookie=cookie.hex(),renderer_bytes=len(render),renderer_bytes_recovered=len((BASE/'native-render.bin').read_bytes())-len(render),metadata_before=1002,metadata_after=390,extra_bytes=len(extra),bindings={str(p):P.sha(p) for p in [__file__,O/'component.s',O/'body-compact.bin',O/'candidate.nes']},scope='Source-asserted lossless grid encoding. Actual renderer CPU comparisons and native verification required; death not integrated.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))
if __name__=='__main__':main()
