"""Skip the authenticated shot worker's scratch transaction when no shots exist."""
import hashlib,json,subprocess
import prepare_metal_storm_shots_1101_v35 as P
from private_build_outputs_v1 import validate
R=P.P.R
O=R/'build/metal-storm-idle-shots-1101-v41'
BASE=R/'build/metal-storm-decline-1101-v40'

def main():
 O.mkdir(exist_ok=True)
 t=(P.O/'component.s').read_text()
 old='Ms35Weapons:\n jsr MsRSave'
 assert t.count(old)==1
 # These are the original two shot-active flag bytes, not a new cached flag.
 # The public transport has already authenticated both complete headers and
 # restores AXYP except the worker's handled carry. Do not bypass that gate.
 t=t.replace(old,'Ms35Weapons:\n lda MsState+$512\n ora MsState+$513\n bmi Ms41Active\n sec\n rts\nMs41Active:\n jsr MsRSave')
 (O/'component.s').write_text(t)
 (O/'body-compact.bin').write_bytes((P.O/'body-compact.bin').read_bytes())
 (O/'component.cfg').write_text((P.O/'component.cfg').read_text().replace(P.O.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16))
 cc=R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.P.M,'--bin-include-dir',R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R)
   z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 compile()
 actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();extra=(O/'native-extra.bin').read_bytes()
 assert len(render)<=3072 and len(extra)<=352
 cookie=bytes([167,35,41])+hashlib.sha256(actor+render+extra+t.encode()).digest()[:13]
 (O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray((BASE/'candidate.nes').read_bytes())
 for role,bank,off in [('auth',25,0x1f9e),('finish',99,0x176e)]:
  before=(P.O/f'native-{role}.bin').read_bytes();after=(O/f'native-{role}.bin').read_bytes();at=16+bank*8192+off
  assert len(before)==len(after) and raw[at:at+len(before)]==before
  raw[at:at+len(after)]=after
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-render.bin','native-extra.bin','native-auth.bin','native-finish.bin']:
   assert f.read_bytes()==(P.O/f.name).read_bytes(),f.name
 assert (O/'native-extra.bin').read_bytes()==(P.O/'native-extra.bin').read_bytes()
 for i,page in enumerate([831,500,494]):
  at=16+1048576+page*1024
  before=((P.O/'native-render.bin').read_bytes()+bytes(3072))[:3072][i*1024:(i+1)*1024]
  assert raw[at:at+1024]==before
  raw[at:at+1024]=(render+bytes(3072-len(render)))[i*1024:(i+1)*1024]
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(assembled=True,installed=False,ROM_sha256=P.P.sha(O/'candidate.nes'),renderer_bytes=len(render),scope='Only authenticated no-shot worker fast return; all supported shot/enemy logic and full-header checks retained. Native test pending.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
