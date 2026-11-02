"""Natural donor frames using original support/side/landing component."""
from pathlib import Path
import hashlib,json
import recover_prince_landing_1102_v3 as B
R,O=B.R,B.O


def main():
 p=R/'tools/audit/check_prince_landing_sequence_1102_v3.py';s=p.read_text()
 changes={
  'landing-recovery.json':'contact-recovery.json',
  'landing-core':'contact-core',
  'landing-sequence-CPU.json':'contact-sequence-CPU.json',
  'recover_prince_landing_1102_v3.py':'recover_prince_contact_1102_v4.py',
  "(5,0x8710):'PpCombatLoseHP'":"(5,0x8710):'PpCombatLoseHP',(7,0xd17a):'PpTerrainContact'",
 }
 for old,new in changes.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_contact_natural_sequence')
 exec(compile(s,str(p),'exec'),env);env['main']()
 out=O/'contact-sequence-CPU.json';q=json.loads(out.read_text())
 q['full_original_postphysics_contact_replacements_enabled']=True
 q['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 out.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
