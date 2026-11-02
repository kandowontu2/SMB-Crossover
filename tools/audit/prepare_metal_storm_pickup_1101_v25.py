"""Use source-proven private art padding for Metal pickup helpers."""
import json,subprocess,hashlib
import prepare_metal_storm_hurt_host_1101_v24 as B
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
P=B.P;BASE=B.O;O=P.R/'build/metal-storm-pickup-1101-v25'
REF=P.R/'tools/reference/metal_storm_pickup_1101_v25.inc'
GRANT=P.R/'build/metal-storm-art-tail-1101-v25/resource-grant.json'

def main():
 O.mkdir(exist_ok=True);g=json.loads(GRANT.read_text())
 for p,h in g['bindings'].items():assert P.sha(p)==h,p
 assert P.sha(BASE/'candidate.nes')==g['baseline_ROM_sha256']
 host=qualified(BASE/'candidate.nes');t=(BASE/'component.s').read_text()
 names=['Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType','PlayerStatus','Square2SoundQueue','Sfx_PowerUpGrab','EraseEnemyObject','SetupFloateyNumber','InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi','MarioSourcePowerupCollision']
 for name in names:
  if not __import__('re').search(r'^'+name+r'\s*=',t,__import__('re').M):t=f'{name}=${address(host,name):04x}\n'+t
 assert all(0x8000<=address(host,n)<0xa000 for n in ['EraseEnemyObject','SetupFloateyNumber'])
 t=f'MS25_NATIVE_PICKUP_BANK={128|((location(host,"MarioSourcePowerupCollision")-16)//8192)}\n'+t
 old=' .elseif I=26\n  jmp MsRenderColors';assert t.count(old)==1;t=t.replace(old,' .elseif I=24\n  jmp Ms25Pickup\n'+old)
 assert t.count(' cmp #11\n')==1;t=t.replace(' cmp #11\n',' cmp #12\n')
 for old,new in [(',$d5\n',',$d5,$d9\n'),('831,500,494\n','831,500,494,499\n')]:
  assert t.count(old)==(1 if '$d5' in old else 2);t=t.replace(old,new)
 t+='\n.segment "MS25_EXTRA"\n'+REF.read_text();(O/'component.s').write_text(t)
 cfg=(BASE/'component.cfg').read_text().replace(BASE.as_posix(),O.as_posix())
 cfg+='\nMEMORY { MS25_EXTRA_MEM:start=$dba0,size=352,bank=2,file="'+(O/'native-extra.bin').as_posix()+'"; } SEGMENTS { MS25_EXTRA:load=MS25_EXTRA_MEM,type=ro; }'
 (O/'component.cfg').write_text(cfg);(O/'native-cookie.bin').write_bytes(bytes(16));cc=P.R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.M,'--bin-include-dir',P.R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 compile();actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();extra=(O/'native-extra.bin').read_bytes();assert len(render)<=3072 and len(extra)<=352
 cookie=bytes([167,35,25])+hashlib.sha256(actor+render+extra+t.encode()).digest()[:13];(O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray((BASE/'candidate.nes').read_bytes())
 for role,bank,offset,cap in [('auth',25,0x1f9e,98),('finish',99,0x176e,146),('copy',36,0x1f46,122),('map',34,0x1d9e,98)]:
  old=(BASE/f'native-{role}.bin').read_bytes();new=(O/f'native-{role}.bin').read_bytes();at=16+bank*8192+offset
  assert len(new)<=cap and raw[at:at+len(old)]==old
  if len(new)>len(old):assert raw[at+len(old):at+len(new)]==b'\xff'*(len(new)-len(old))
  raw[at:at+len(new)]=new
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-actor.bin','native-render.bin','native-extra.bin','native-auth.bin','native-finish.bin','native-copy.bin','native-map.bin']:assert f.read_bytes()==(BASE/f.name).read_bytes(),f.name
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16);carriers=bytes(image)+render+bytes(3072-len(render))
 for i,page in enumerate([247,248,249,250,827,828,829,830,831,500,494]):
  at=16+1048576+page*1024;raw[at:at+1024]=carriers[i*1024:(i+1)*1024]
 at=16+1048576+499*1024+672;assert raw[at:at+352]==bytes(352);raw[at:at+len(extra)]=extra
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),base_ROM_sha256=P.sha(BASE/'candidate.nes'),cookie=cookie.hex(),renderer_bytes=len(render),extra_bytes=len(extra),copy_rows=12,resource_grant=str(GRANT),bindings={str(p):P.sha(p) for p in [REF,GRANT,__file__,O/'component.s',O/'candidate.nes']},scope='Mushroom armor and native star/life fallback. Flower weapons, source armor art/audio and full gameplay qualification incomplete; not delivered.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))
if __name__=='__main__':main()
