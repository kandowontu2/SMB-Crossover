"""Avoid repeated owner authentication for Getsu's ordinary native head probe."""
import argparse,json,hashlib,subprocess,inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import check_mini_native_head_direct_1109_v1 as Old
import check_getsu_head_callback_1110 as G
R=G.R;BASE=R/'build/getsu-callback-final-native-1110/candidate.nes'
PIN='c6ab56107cf78954ff24f0fddbd40a0207afd4e7743eaeb8c762a53329d30f1b'
SOURCE=R/'tools/reference/getsu_native_head_direct_1110.s'
AT=16+89*8192+0x1fb0

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(exist_ok=True)
 raw=BASE.read_bytes();assert G.Q.sha(raw)==PIN
 old=raw[AT:AT+80]
 assert old.hex()=='08484929f039a9b08d6c01a9bf8d6d01a99c205a01901468288d6a01a9fe8d6c01a9b68d6d01a9024c5a0168288d6a01a9f18d6c01a9b68d6d01a9c24c5a016828a93e8d6c01a9b48d6d01a9d44c5a01'
 with TemporaryDirectory(dir=out) as folder:
  f=Path(folder);cfg=f/'head.cfg';obj=f/'head.o';binary=f/'head.bin'
  cfg.write_text('MEMORY{H:start=$bfb0,size=80,file=%O;}SEGMENTS{HEAD:load=H,type=ro;}')
  cc=R/'tools/Windows/cc65/bin'
  subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
  subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True);code=binary.read_bytes()
 assert len(code)==80
 trial=raw[:AT]+code+raw[AT+80:]
 # Existing fixed ingress is retained; genuine Mini and other character paths
 # must match. Getsu now uses the exact already-qualified native head routine.
 text=inspect.getsource(Old.compare)
 text=text.replace('assert maps[0]>maps[1]','assert maps[0]==maps[1]')
 text=text.replace('25,26,28,38,42)','25,26,28,38)')
 scope=dict(Old.__dict__);exec(text,scope)
 compare=scope['compare'](raw,trial)
 bundle=G.Q.Earned.D.Current.Getsu.W.bundle(trial)
 H=G.Q.Earned.H;N=G.Q.Earned.N;cuts=[]
 native=0xbfb0+code.index(bytes.fromhex('68284c8795'))
 for pc in (0xbfb0,native,0x9587):
  for kind in ('FF','IRQ'):
   m=H.prepare(bundle);hit=[]
   def watch(c):
    tag,at=H.point(c)
    if at==pc and tag==(254 if pc==0x9587 else 217) and not hit:
     hit.append(H.vector(c,kind))
   H.S.frame(m,0,watch)
   assert hit,(pc,kind)
   cuts.append(dict(pc=pc,kind=kind,min_SP=hit[0]))
 q=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=G.Q.sha(trial),
   patches=[dict(file_offset=AT,old_hex=old.hex(),new_hex=code.hex())],cases=compare,cuts=cuts,
   scope='Actual fixed988F ingress parity, unchanged Mini private entry, direct native Getsu head without owner transport.',
   bindings={str(p.relative_to(R)):G.Q.sha(p.read_bytes()) for p in (Path(__file__).resolve(),SOURCE,BASE,Path(Old.__file__))})
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(q['expected_memory_only_SHA256'],flush=True)

if __name__=='__main__':main()
