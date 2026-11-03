"""Actual LoadAreaTypeCHR lifetime: republish own row at every body draw."""
from pathlib import Path
import json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
W,R,O=H.W,H.R,H.O
def main():
 src=(O/'mini-host-v30.s').read_text();src='X5SpecialChrUpper=$73ec\nX5HudChrUpper=$73ed\n'+src
 needle='MiniHostFresh:\n jsr MiniInit\n';assert src.count(needle)==1
 src=src.replace(needle,needle+''' lda #0
 ldx #11
@clearChrModes:
 sta X5ChrMode,x
 dex
 bpl @clearChrModes
 sta X5SpecialChrUpper
 sta X5HudChrUpper
 sta X5WideChrActive
 lda #1
 sta ReloadCHRBank
''')
 needle='MiniHostDraw:\n jsr MiniHostPixelX';assert src.count(needle)==1;src=src.replace(needle,'MiniHostDraw:\n jsr MiniHostGraphics\n jsr MiniHostPixelX')
 p=O/'mini-host-v32';p.with_suffix('.s').write_text(src);p.with_suffix('.cfg').write_bytes((O/'mini-host-v30.cfg').read_bytes());cc=R/'tools/Windows/cc65/bin'
 for attempt in range(8):
  c=subprocess.run(list(map(str,[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')])),capture_output=True,text=True)
  if c.returncode==0:break
  bad=[int(x)-1 for x in re.findall(r':(\d+): Error: Range error',c.stderr)];assert bad,c.stderr
  lines=p.with_suffix('.s').read_text().splitlines()
  for i in bad:lines[i]=re.sub(r'^(\s*)b(cc|cs|eq|ne|mi|pl|vc|vs)\b',r'\1j\2',lines[i],flags=re.I)
  p.with_suffix('.s').write_text('\n'.join(lines)+'\n')
 else:raise AssertionError('Range did not converge')
 for cmd in[[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
  c=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert c.returncode==0,c.stderr
 data=p.with_suffix('.bin').read_bytes();L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)};assert len(data)<=5120
 S=H.symbols();cases=0
 for stale in[0x80,0x81,0x82,0x83,0xff]:
  m=T.memory(data,L,0);m.memory[0x73e0:0x73ef]=[stale]*15;T.call(m,L['MiniHostFresh']);assert m.memory[0x73e0:0x73ef]==[0]*15
  # Actual LoadAreaTypeCHR writes this seven-byte native row on scroll.
  m.memory[S['CurrentCHRBank']:S['CurrentCHRBank']+8]=[56,20,21,22,23,24,25,26];m.memory[S['CurrentOAMOffset']]=24;m.memory[0xc250:0xc254]=[128,2,128,12];m.memory[0xc310]=0
  for epoch in range(4):
   m.memory[S['CurrentCHRBank']:S['CurrentCHRBank']+8]=[56,20,21,22,23,24,25,26];m.memory[S['CurrentOAMOffset']]=24;m.memory[S['ReloadCHRBank']]=0;T.call(m,L['MiniHostDraw'])
   assert m.memory[S['CurrentCHRBank']+4]==200 and m.memory[0x73e4]==0x83 and m.memory[0x73ee]==1 and m.memory[S['ReloadCHRBank']]==1
   assert m.memory[0x73e1]==0 and m.memory[S['CurrentCHRBank']+1]==20
   assert m.memory[S['CurrentOAMOffset']]==28 and m.memory[0xc315]==1
   assert m.memory[S['ObjectMetasprite']]==0 and m.memory[S['SmPosePtr']:S['SmPosePtr']+2]==[0xe1,6]
   cases+=1
 old=(O/'mini-host-v30.bin').read_bytes();at=L['MiniHostFresh']-0xa000;assert data[114:at]==old[114:at]
 out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],CPU_area_theme_reset_and_Draw_cases=cases,Fresh_all12_modes_and_upper_flags_cleared=True,source_kernel_render_animate_prefix_exact=True,scope='Source LoadAreaTypeCHR resets CurrentCHRBank+1..7 during scroll. Own completedDraw republishes CHR4physical968 only; native enemywindows retained. Fresh follows actualX5ClearChrModes to remove stale menuwindow1high3. No sourcephysics/palette/terrain/camera change. Actual native/fullstage acceptance root-owned.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v30.s',O/'mini-host-v30.json',R/'src/mmc5.s',R/'src/mmc5_expanded.s']})
 (O/'mini-host-v32.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels','CPU_area_theme_reset_and_Draw_cases']}))
if __name__=='__main__':main()
