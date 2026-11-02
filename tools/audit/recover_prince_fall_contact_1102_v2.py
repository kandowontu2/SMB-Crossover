"""Expand genuine original F882 ledge-catch family, not a damage shim.

The frozen v1 component and receipts stay immutable. This separate source
candidate adds true source contact logic; host world/align bindings stay explicit.
"""
from pathlib import Path
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 p=Path(B.__file__);s=p.read_text()
 replacements={
  ",(7,0xf882):'PpNativeFallDamage'":'',
  "(7,0xc8d4):'PpWorldAlign',":"(7,0xc8d4):'PpWorldAlign',(7,0xd7df):'PpWorldPlaceAligned',(7,0xd164):'PpWorldRowAdjusted',",
  "(6 if a==0xaa19 else (2 if a==0xbb4f else (5 if bank==7 else bank)))":"(6 if a==0xaa19 else (2 if a in [0xbb4f,0xa804] else (5 if bank==7 else bank)))",
  "'PpControls':(7,0xeff2)":"'PpControls':(7,0xeff2),'PpFallContact':(7,0xf882)",
  "O/'prince-core":"O/'fall-contact-core",
  "O/'original-core":"O/'fall-contact-original",
  "O/'core-recovery.json'":"O/'fall-contact-recovery.json'",
  'SCRIPTS:load=M,type=ro,start=$b000':'SCRIPTS:load=M,type=ro,start=$b200',
 }
 for old,new in replacements.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_fall_contact_candidate')
 exec(compile(s,str(p),'exec'),env);q,_=env['recover']()
 q['extension_scope']='Original F882 falling ledge catch/recovery and its bank2 A804 fallback. This is source behavior, not a host damage-only callback. Original aligned room placement D7DF is an explicit host world boundary alongside C8D4.'
 q['source_producer_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (O/'fall-contact-recovery.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
