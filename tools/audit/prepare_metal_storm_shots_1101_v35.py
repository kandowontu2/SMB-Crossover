"""Integrate source shot rectangles with native enemies in the current candidate."""
import hashlib,json,subprocess
import prepare_metal_storm_death_host_1101_v34 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
P=B.P;BASE=B.O;O=P.R/'build/metal-storm-shots-1101-v35'
REF=P.R/'tools/reference/metal_storm_shot_contact_1101_v35.inc'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes')
 t=(BASE/'component.s').read_text()
 old=' .elseif I=5\n  jmp Ms24Injury';assert t.count(old)==1
 t=t.replace(old,' .elseif I=34\n  jmp Ms35Weapons\n'+old)
 names=['ObjectOffset','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','HandleEnemyFBallCol']
 t='\n'.join(f'{n}=${address(b,n):04x}' for n in names)+'\n'+t+'\n'+REF.read_text()
 (O/'component.s').write_text(t)
 (O/'body-compact.bin').write_bytes((BASE/'body-compact.bin').read_bytes())
 (O/'component.cfg').write_text((BASE/'component.cfg').read_text().replace(BASE.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16));cc=P.R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.M,'--bin-include-dir',P.R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
 compile();actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();extra=(O/'native-extra.bin').read_bytes()
 assert len(render)<=3072 and len(extra)<=352,(len(render),len(extra))
 cookie=bytes([167,35,35])+hashlib.sha256(actor+render+extra+t.encode()).digest()[:13]
 (O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray(b['raw'])
 for role,bank,off in [('auth',25,0x1f9e),('finish',99,0x176e)]:
  a=(BASE/f'native-{role}.bin').read_bytes();z=(O/f'native-{role}.bin').read_bytes();at=16+bank*8192+off
  assert len(a)==len(z) and raw[at:at+len(a)]==a;raw[at:at+len(z)]=z
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-render.bin','native-extra.bin','native-auth.bin','native-finish.bin']:
   assert f.read_bytes()==(BASE/f.name).read_bytes(),f.name
 for i,page in enumerate([831,500,494]):
  data=(render+bytes(3072-len(render)))[i*1024:(i+1)*1024]
  at=16+1048576+page*1024;raw[at:at+1024]=data
 at=16+1048576+499*1024+672;raw[at:at+352]=extra+bytes(352-len(extra))
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(assembled=True,verified=False,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),renderer_bytes=len(render),extra_bytes=len(extra),cookie=cookie.hex(),scope='Original normal/upgraded source shot rectangles, native 16x24 enemy-body proxy and fireball defeat transaction. Native enemy immunity retained. Original enemy HP/armor mapping and full-route behavior not yet qualified.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
