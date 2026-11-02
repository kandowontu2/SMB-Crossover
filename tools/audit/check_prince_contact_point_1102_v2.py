"""Place qualified native point reader in owned script-alignment padding."""
from pathlib import Path
import hashlib,json,re
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 lab=B.P.T.labels(O/'contact-core.lbl');start=lab['PpCoreEnd'];end=lab['PpScripts']
 core=(O/'contact-core.bin').read_bytes();assert core[start-0xa000:end-0xa000]==bytes([0])*(end-start)
 p=R/'tools/audit/check_prince_host_point_1102_v1.py';s=p.read_text()
 changes={
  "O/'host-point":"O/'contact-point",
  'start=$b9c1,size=$61f':f'start=${start:04x},size=${end-start:x}',
  'start=0xb9c1':f'start={start}',
  'fall-contact-core.bin':'contact-core.bin',
 }
 for old,new in changes.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_owned_alignment_point');exec(compile(s,str(p),'exec'),env);env['main']()
 q=json.loads((O/'contact-point-CPU.json').read_text())
 q['owned_source_alignment_half_open']=[start,end]
 q['remaining_source_alignment_bytes']=end-start-q['component_bytes']
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (O/'contact-point-CPU.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
