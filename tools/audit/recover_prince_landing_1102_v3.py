"""Recover original landing, fall injury and both original HP leaves.

The previously qualified source candidates remain immutable. D487 is an
explicit world-height boundary: the original 64-pixel room snap cannot be
silently substituted for a native 16-pixel platform alignment.
"""
from pathlib import Path
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 p=Path(B.__file__);s=p.read_text()
 replacements={
  ",(7,0xf882):'PpNativeFallDamage'":'',
  "(7,0xc8d4):'PpWorldAlign',":"(7,0xc8d4):'PpWorldAlign',(7,0xd7df):'PpWorldPlaceAligned',(7,0xd164):'PpWorldRowAdjusted',(7,0xd487):'PpWorldLandingAlign',",
  "(7,0xcb00):2}":"(7,0xcb00):2,(7,0xd8fc):4}",
  "(6 if a==0xaa19 else (2 if a==0xbb4f else (5 if bank==7 else bank)))":"(6 if a==0xaa19 else (2 if a in [0xbb4f,0xa804] else (5 if bank==7 else bank)))",
  "'PpControls':(7,0xeff2)":"'PpControls':(7,0xeff2),'PpFallContact':(7,0xf882),'PpLanding':(7,0xd427),'PpLoseHP':(5,0x8574),'PpCombatLoseHP':(5,0x8710)",
  "PpMap5:lda #5":"PpMap4:lda #4\n jmp PpMap\nPpMap5:lda #5",
  "O/'prince-core":"O/'landing-core",
  "O/'original-core":"O/'landing-original",
  "O/'core-recovery.json'":"O/'landing-recovery.json'",
  'SCRIPTS:load=M,type=ro,start=$b000':'SCRIPTS:load=M,type=ro,start=$b300',
 }
 for old,new in replacements.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_landing_candidate')
 exec(compile(s,str(p),'exec'),env);q,_=env['recover']()
 q['extension_scope']='Original F882 falling ledge catch, D427 landing/action/fall-injury selection, player HP8574 and contextual HP8710. Original64px landing alignment D487 remains an explicit native-height boundary. Mapper4 private bank/Y-scratch effects are retained.'
 q['source_producer_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (O/'landing-recovery.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
