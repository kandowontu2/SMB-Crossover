"""Compile typed injury-status return into the authenticated Metal capsule."""
import json,re,subprocess,hashlib
import prepare_metal_storm_background_1101_v19 as P
from private_build_outputs_v1 import validate
O=P.R/'build/metal-storm-status-1101-v22'
REF=P.R/'tools/reference/metal_storm_injury_status_1101_v22.inc'

def main():
 O.mkdir(exist_ok=True);t=(P.O/'component.s').read_text()
 old=' .elseif I=11\n  jmp Ms12BodyPolicy'
 assert t.count(old)==1;t=t.replace(old,' .elseif I=6\n  jmp Ms22InjuryStatus\n'+old)
 t+='\n.segment "MS11_RENDER"\n'+REF.read_text().replace('.import MsState','')
 (O/'component.s').write_text(t);(O/'component.cfg').write_text((P.O/'component.cfg').read_text().replace(P.O.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16));cc=P.R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.M,'--bin-include-dir',P.R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 compile();actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();assert len(render)<=3072
 cookie=bytes([167,35,22])+hashlib.sha256(actor+render+t.encode()).digest()[:13];(O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray((P.O/'candidate.nes').read_bytes())
 for role,bank,offset in [('auth',25,0x1f9e),('finish',99,0x176e)]:
  old=(P.O/f'native-{role}.bin').read_bytes();new=(O/f'native-{role}.bin').read_bytes();at=16+bank*8192+offset
  assert len(old)==len(new) and raw[at:at+len(old)]==old;raw[at:at+len(new)]=new
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-actor.bin','native-render.bin','native-auth.bin','native-finish.bin']:assert f.read_bytes()==(P.O/f.name).read_bytes(),f.name
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16);carriers=bytes(image)+render+bytes(3072-len(render))
 for i,page in enumerate([247,248,249,250,827,828,829,830,831,500,494]):
  at=16+1048576+page*1024;raw[at:at+1024]=carriers[i*1024:(i+1)*1024]
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),base_ROM_sha256=P.sha(P.O/'candidate.nes'),cookie=cookie.hex(),renderer_bytes=len(render),conditional_RAM_grant=dict(bank=2,half_open=[0xcd00,0xcd00+len(render)],condition='Exclusive selected35 and both full revision22 headers; existing cold load/retirement'),bindings={str(p):P.sha(p) for p in [REF,__file__,O/'component.s',O/'candidate.nes']},scope='Typed status query only. Injury start/armor lifecycle and death remain unfinished; do not deliver.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))
if __name__=='__main__':main()
