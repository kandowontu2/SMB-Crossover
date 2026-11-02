"""Reassemble Metal's palette packet with the native shared background color."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from prepare_selected_native_packet_v1 import prepare
import prepare_metal_storm_world_palette_1101_v18 as P
O=R/'build/metal-storm-background-1101-v19'
S=R/'build/metal-storm-lifecycle-1101-v13'
M=R/'build/metal-storm-native-integration-1101-v12'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 O.mkdir(exist_ok=True);host=qualified(P.O/'candidate.nes');raw=bytearray(host['raw'])
 assert sha(P.O/'candidate.nes')=='a32494f1db125fa1f53cf70a6818c74e72e9387de4ca15f3e92357d70f2f274d'
 t=(S/'component.s').read_text()
 t=t.replace('.byte $3f,$11,3','.byte $3f,$10,4,0')
 old=' cpy #6\n bcc MsPaletteByte\n lda #0'
 new=' cpy #7\n bcc MsPaletteByte\n ldy BackgroundColorCtrl\n bne :+\n ldy AreaType\n:lda Ms19BackgroundColors,y\n sta VRAM_Buffer1-4,x\n lda #0'
 assert t.count(old)==1;t=t.replace(old,new)
 at=location(host,'BackgroundColors');bg=bytes(raw[at:at+8])
 t=t.replace('MsPalettePacket:Ms9PalettePacket','MsPalettePacket:Ms9PalettePacket\nMs19BackgroundColors:.byte '+','.join(str(v) for v in bg))
 t=''.join(f'{n}=${address(host,n):04x}\n' for n in ['BackgroundColorCtrl','AreaType'])+t
 # Compile both original query contracts into the same source, preserving v17.
 old='.repeat 37,I\n jmp Ms12Enter\n.endrepeat'
 new='.repeat 37,I\n .if I=10\n jmp BlockBufferColli_Head\n .elseif I=14\n jmp BlockBufferColli_Side\n .else\n jmp Ms12Enter\n .endif\n.endrepeat'
 assert t.count(old)==1;t=t.replace(old,new)
 t=''.join(f'{n}=${address(host,n):04x}\n' for n in ['BlockBufferColli_Head','BlockBufferColli_Side'])+t
 (O/'component.s').write_text(t)
 (O/'component.cfg').write_text((S/'component.cfg').read_text().replace(S.as_posix(),O.as_posix()))
 (O/'native-cookie.bin').write_bytes(bytes(16))
 cc=R/'tools/Windows/cc65/bin'
 def compile():
  cmds=[[cc/'ca65.exe','-g','--bin-include-dir',O,'--bin-include-dir',M,'--bin-include-dir',R/'build/metal-storm-render-host-1101-v7',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl']]
  for cmd in cmds:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
 compile()
 actor=(O/'native-actor.bin').read_bytes();render=(O/'native-render.bin').read_bytes()
 cookie=bytes([0xa7,35,19])+hashlib.sha256(actor+render+t.encode()).digest()[:13]
 (O/'native-cookie.bin').write_bytes(cookie);compile()
 assert len(actor)==8128 and len(render)<=2810
 patches=[]
 # Exact existing capsule allocations; updates are confined to source-owned bytes.
 for role,bank,off,cap in [('gate',78,0xb6d,147),('common',95,0x580,128),('work',37,0x1f89,119),('check',21,0x1f8a,118),('auth',25,0x1f9e,98),('cold',116,0xf87,121),('copy',36,0x1f46,122),('map',34,0x1d9e,98),('finish',99,0x176e,146),('zero',94,0xd98,104)]:
  data=(O/f'native-{role}.bin').read_bytes();assert len(data)<=cap
  at=16+bank*8192+off
  if raw[at:at+len(data)]!=data:
   patches.append(dict(role=role,offset=at,size=len(data)));raw[at:at+len(data)]=data
 image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16)
 carriers=bytes(image)+render+bytes(3072-len(render))
 for i,page in enumerate([247,248,249,250,827,828,829,830,831,500,494]):
  at=16+1048576+page*1024;raw[at:at+1024]=carriers[i*1024:(i+1)*1024]
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(passed=True,installed=False,ROM_sha256=sha(O/'candidate.nes'),base_ROM_sha256=sha(P.O/'candidate.nes'),renderer_bytes=len(render),previous_renderer_bytes=2777,
  conditional_RAM_grant=dict(bank=2,half_open=[0xcd00,0xcd00+len(render)],condition='Only Metal35 with both complete matching revision19 headers; existing full-header retirement and cold load retained.'),cookie=cookie.hex(),native_background_bytes=bg.hex(),capsules=patches,
  bindings={str(p):sha(p) for p in [Path(__file__),S/'component.s',O/'component.s',O/'component.cfg',O/'candidate.nes']})
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
 source=P.O/'native-smoke/controller.lua'
 prepare(O/'native-smoke',O/'candidate.nes',source.read_text(),[Path(__file__),source],expected=sha(O/'candidate.nes'),timeout=90,scope='Cold Metal entry and movement; inspect real background palette. No full-level/combat claim.')
 print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))
if __name__=='__main__':main()
