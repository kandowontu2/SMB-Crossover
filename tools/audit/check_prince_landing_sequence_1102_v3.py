"""Replace original landing/HP calls inside genuine donor frame sequencing."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json
import recover_prince_core_1101_v1 as B
R,O=B.R,B.O


def main():
 q=json.loads((O/'landing-recovery.json').read_text())
 callbacks={(v[0],int(v[1],16)):n for n,v in q['declared_original_environment_boundaries'].items()}
 proxy=SimpleNamespace(O=O,CALLBACKS=callbacks,__file__=str(R/'tools/audit/recover_prince_landing_1102_v3.py'))
 p=R/'tools/audit/check_prince_sequence_1101_v1.py';source=p.read_text()
 changes={
  'import recover_prince_core_1101_v1 as B':'B=PROXY',
  "O/'prince-core":"O/'landing-core",
  "O/'core-recovery.json'":"O/'landing-recovery.json'",
  "O/'source-sequencing-CPU.json'":"O/'landing-sequence-CPU.json'",
  "(5,0x839f):'PpDecodeInput'":"(5,0x839f):'PpDecodeInput',(7,0xf882):'PpFallContact',(7,0xd427):'PpLanding',(5,0x8574):'PpLoseHP',(5,0x8710):'PpCombatLoseHP'",
 }
 for old,new in changes.items():assert old in source,old;source=source.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_landing_sequence',PROXY=proxy)
 exec(compile(source,str(p),'exec'),env);env['main']()
 out=O/'landing-sequence-CPU.json';q=json.loads(out.read_text())
 q['original_landing_and_HP_replacements_enabled']=True
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 out.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
