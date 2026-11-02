"""Replace three proven static reject veneers with equivalent ROM returns."""
import json,re,subprocess
import prepare_metal_storm_shots_1101_v35 as B
from private_build_outputs_v1 import validate
P=B.P;BASE=B.O;O=P.R/'build/metal-storm-decline-1101-v40'
REF=P.R/'tools/reference/metal_storm_decline_1101_v40.s'

def main():
 O.mkdir(exist_ok=True)
 labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(BASE/'component.lbl').read_text(),re.M)}
 renderer=(BASE/'native-render.bin').read_bytes()
 gate=labels['Ms12Veneers'];enter=labels['Ms12Enter'];cache=labels['Ms12CacheRows'];reject=labels['Ms12Reject']
 (O/'patch.cfg').write_text('MEMORY{M:start=$0000,size=3,file=%O;}SEGMENTS{PATCH:load=M,type=ro;}')
 cc=P.R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',REF,'-o',O/'patch.o'],[cc/'ld65.exe','-C',O/'patch.cfg',O/'patch.o','-o',O/'patch.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 patch=(O/'patch.bin').read_bytes();assert len(patch)==3
 raw=bytearray((BASE/'candidate.nes').read_bytes());changes=[]
 for row in [9,13,29]:
  assert renderer[cache-0xcd00+row*3:cache-0xcd00+row*3+3]==bytes([0x4c,reject&255,reject>>8])
  at=16+78*8192+gate-0xa000+row*3
  before=bytes(raw[at:at+3]);assert before==bytes([0x4c,enter&255,enter>>8])
  raw[at:at+3]=patch;changes.append(dict(row=row,offset=at,before=before.hex(),after=patch.hex()))
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(assembled=True,verified=False,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),base_sha256=P.sha(BASE/'candidate.nes'),changes=changes,scope='Only static rejected visibility9,box13,UI29 veneers. Source state, cache headers, all supported handlers, CHR, movement and physics unchanged.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
