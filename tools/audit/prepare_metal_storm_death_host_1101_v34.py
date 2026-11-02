"""Wire original death clocks into native guest callbacks; visual WIP."""
import hashlib,json,subprocess
import prepare_metal_storm_compact_body_1101_v29 as B
from private_build_outputs_v1 import validate
P=B.P;BASE=B.O;O=P.R/'build/metal-storm-death-host-1101-v34'
REFS=[P.R/'tools/reference'/s for s in ['metal_storm_death_leaves_1101_v27.inc','metal_storm_death_host_1101_v34.inc']]

def main():
 O.mkdir(exist_ok=True);t=(BASE/'component.s').read_text()
 old=' .elseif I=6\n  jmp Ms22InjuryStatus';assert t.count(old)==1
 t=t.replace(old,old+'\n .elseif I=7\n  jmp Ms34DeathStart\n .elseif I=8\n  jmp Ms34DeathTick')
 # Do not misinterpret explosion poses as walking body poses while its
 # original artwork is still awaiting a separate CHR allocation.
 old='MsRBody:\n';assert t.count(old)==1
 t=t.replace(old,old+' lda MsState+$528\n cmp #2\n jne Ms34LiveBody\n rts\nMs34LiveBody:\n')
 t+='\n.segment "MS11_RENDER"\n'+'\n'.join(p.read_text() for p in REFS)
 (O/'component.s').write_text(t);(O/'body-compact.bin').write_bytes((BASE/'body-compact.bin').read_bytes())
 (O/'component.cfg').write_text((BASE/'component.cfg').read_text().replace(BASE.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16));cc=P.R/'tools/Windows/cc65/bin'
 def compile():
  for cmd in [[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',P.M,'--bin-include-dir',P.R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
 compile();actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes();extra=(O/'native-extra.bin').read_bytes()
 assert len(render)<=3072
 cookie=bytes([167,35,34])+hashlib.sha256(actor+render+extra+t.encode()).digest()[:13];(O/'native-cookie.bin').write_bytes(cookie);compile()
 raw=bytearray((BASE/'candidate.nes').read_bytes())
 for role,bank,off in [('auth',25,0x1f9e),('finish',99,0x176e)]:
  a=(BASE/f'native-{role}.bin').read_bytes();b=(O/f'native-{role}.bin').read_bytes();at=16+bank*8192+off
  assert len(a)==len(b) and raw[at:at+len(a)]==a;raw[at:at+len(b)]=b
 for f in O.glob('native-*.bin'):
  if f.name not in ['native-cookie.bin','native-actor.bin','native-render.bin','native-extra.bin','native-auth.bin','native-finish.bin']:assert f.read_bytes()==(BASE/f.name).read_bytes(),f.name
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16);carriers=bytes(image)+render+bytes(3072-len(render))
 for i,page in enumerate([247,248,249,250,827,828,829,830,831,500,494]):
  at=16+1048576+page*1024;raw[at:at+1024]=carriers[i*1024:(i+1)*1024]
 at=16+1048576+499*1024+672;assert len(extra)<=352;raw[at:at+352]=extra+bytes(352-len(extra))
 # Compose the delivered Tank walking fix without losing Metal's changes.
 tank=P.R/'build/tank-normal-walk-1101-v33';q=json.loads((tank/'assembly.json').read_text());before=(P.R/'build/mario-tank-visible-host-1101-v5/candidate.nes').read_bytes();after=(tank/'candidate.nes').read_bytes()
 for at,n in [(q['helper_offset'],27),(q['hook_offset'],18)]:
  assert raw[at:at+n]==before[at:at+n];raw[at:at+n]=after[at:at+n]
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,ROM_sha256=P.sha(O/'candidate.nes'),cookie=cookie.hex(),renderer_bytes=len(render),installed=False,source_bindings={str(p):P.sha(p) for p in [__file__,*REFS]},scope='Death callbacks and native life-loss handoff, original animation state advances but explosion artwork not displayed yet. Tank walking successor preserved. CPU/native tests pending.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
