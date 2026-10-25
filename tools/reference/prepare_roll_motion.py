"""Reuse the installed MegaMan motion profile without changing player identity.

Mobile timing is not claimed: the deliberate SMB adaptation retains Crossover's
Easy/Hard jump/water integration. Roll suppresses Down+A slide in her input
wrapper, has no Bass dash/double jump, and never changes SelectedCharacter.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def main():
 source=ROOT/'src/megaman_physics.s';s=source.read_text();body=s[s.index('.proc MegaManMovement'):s.index('.endproc')+len('.endproc')]
 assert body.count('sta SelectedCharacter')==0
 body=body.replace('.proc MegaManMovement','.proc RlSourceMovement').replace('lda SelectedCharacter','lda #CHARACTER_MEGAMAN').replace('ldx SelectedCharacter','ldx #CHARACTER_MEGAMAN')
 body=body.replace('MegaMan202Integrated','Rl202Integrated')
 assert 'SelectedCharacter'not in body
 out=ROOT/'src/roll_motion.inc';out.write_text('; Installed MegaMan profile with constant identity reads; see prepare_roll_motion.py.\n.pushseg\n.segment "ROLL_WORLD"\n'+body+'\n.popseg\n')
 (ROOT/'reference/roll-mobile/motion.json').write_text(json.dumps(dict(source_file='src/megaman_physics.s',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
   output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),adaptation=__doc__),indent=2)+'\n')
 print('Prepared independent motion profile; native player identity is never changed')
if __name__=='__main__':main()
