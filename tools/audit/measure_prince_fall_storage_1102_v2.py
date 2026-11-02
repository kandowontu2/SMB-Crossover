"""Remeasure private codec against expanded, qualified ledge-catch core."""
from pathlib import Path
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 proof=json.loads((O/'fall-contact-CPU.json').read_text());assert proof['passed']and proof['expanded_original_ledge_catch_source_included']
 p=R/'tools/audit/measure_prince_lossless_storage_1102_v1.py';source=p.read_text()
 changes={
  'prince-core.bin':'fall-contact-core.bin',
  "'lzss.":"'fall-lzss.",
  'lossless-storage-cost.json':'fall-lossless-storage-cost.json',
  '(0xc800 if dest==0xa000 else 0x9000)':'(0xc500 if dest==0xa000 else 0x9000)',
 }
 for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_fall_contact_storage')
 exec(compile(source,str(p),'exec'),env);env['main']()
 out=O/'fall-lossless-storage-cost.json';q=json.loads(out.read_text())
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 q['expanded_code_remaining_before_BFE0_header']=0xbfe0-0xb9c1
 q['original_ledge_catch_core_qualified']=True
 out.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
