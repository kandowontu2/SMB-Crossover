"""Keep Mini window4 through the unconditional native shot-bank publisher."""
from pathlib import Path
import json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
W,R,O=H.W,H.R,H.O
def assemble(p,src,start,size):
 p.with_suffix('.s').write_text(src);p.with_suffix('.cfg').write_text('MEMORY{P:start=$%04x,size=$%x,file=%%O;}SEGMENTS{CODE:load=P,type=ro;}'%(start,size));cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
  c=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert c.returncode==0,c.stderr
 return p.with_suffix('.bin').read_bytes(),{n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
def main():
 S=H.symbols();src=(O/'mini-host-v32.s').read_text();src=f'SsChrPhysical=${S["SsChrPhysical"]:04x}\n'+src
 needle=' jmp MiniHostNo           ;4 native shot fallback';assert src.count(needle)==1;src=src.replace(needle,' jmp MiniHostYes          ;4 original B-run owned; source projectile not admitted')
 a=src.index('MiniHostGraphics:\n');b=src.index('MiniHostDraw:\n',a);part=src[a:b]
 needle=' sta CurrentCHRBank+4\n';assert part.count(needle)==1;part=part.replace(needle,needle+' sta SsChrPhysical\n')
 needle=' lda #0\n sta SsChrActive\n';assert part.count(needle)==1;part=part.replace(needle,' lda #3\n sta X5SpecialChrUpper\n lda #1\n sta SsChrActive\n lda #0\n');src=src[:a]+part+src[b:]
 data,L=assemble(O/'mini-host-v39',src,0xa000,0x2000);assert len(data)<=5120
 native=(R/'src/mmc5_expanded.s').read_text();a=native.index('  ldy SsChrActive\n  beq X5Default4');b=native.index('  lda X5ChrMode+5',a);leaf=native[a:b]
 direct='.setcpu "6502"\n.segment "CODE"\n.export TestNativeWindow4\n'+''.join(f'{n}=${v:04x}\n'for n,v in dict(SsChrActive=S['SsChrActive'],SsChrPhysical=S['SsChrPhysical'],X5SpecialChrUpper=0x73ec,X5ChrMode=0x73e0,CurrentCHRBank=S['CurrentCHRBank'],ChrPhysicalMap=0x7000).items())+'TestNativeWindow4:\n'+leaf+' rts\n'
 code,N=assemble(O/'native-publisher4-v39',direct,0x6000,0x200);cases=[]
 for stale in[0,1,23,200,255]:
  m=MPU();m.memory[0xa000:0xa000+len(data)]=data;m.memory[0x6000:0x6000+len(code)]=code;T.call(m,L['MiniHostGraphics'])
  # This exact late store comes from LoadAreaTypeCHR after the own Draw.
  m.memory[S['CurrentCHRBank']+4]=stale;T.call(m,N['TestNativeWindow4']);physical=(m.memory[0x5130]&3)*256+m.memory[0x5124];assert physical==968
  cases.append(dict(late_native_Current4=stale,actual_publisher_physical4=physical))
 # Retain the source-exact negative mode83+lateCurrent23 without override.
 m.memory[S['SsChrActive']]=0;m.memory[S['CurrentCHRBank']+4]=23;T.call(m,N['TestNativeWindow4']);negative=(m.memory[0x5130]&3)*256+m.memory[0x5124];assert negative==791
 out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],actual_native_source_window4_cases=cases,retained_negative_physical4=negative,source_window4_excerpt_SHA256=W.sha(leaf.encode()),override=dict(SsChrActive=1,SsChrPhysical=200,X5SpecialChrUpper=3,X5WideChrActive=1),source_caller_chain='metasprite_engine.s HandleFloateyNumbers unconditionally JSR MegaManFullShotBank -> RlFullShotBankDispatch -> RlOriginalFullShotBank. Rootwriter38 bank78:BCC3 Current4=23 exactly. Row4SEC owns B-run/no private projectile but DOES NOT skip this unconditional publisher; specialoverride is required.',correction='Earlier v32 AreaType reset diagnosis was a source-compatible hypothesis, contradicted by actual writer38. Do not claim the observed writer was AreaType.',scope='Exact existing X5WidePublication special window4 mechanism wins before X5Default4. Native unconditional shot-bank leaf may write Current4 freely; all ordinary enemy/background windows remain source-native. Row4SEC prevents unsupported native weapon fallback for original B-run, no new attack. No sharedcode orphysics change. Rootnativefullroute acceptance pending.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v32.s',O/'mini-host-v32.json',R/'src/mmc5_expanded.s',R/'src/roll_shot_bank.inc',R/'src/roll_dispatch.s',R/'src/metasprite_engine.s']})
 (O/'mini-host-v39.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels','actual_native_source_window4_cases']}))
if __name__=='__main__':main()
