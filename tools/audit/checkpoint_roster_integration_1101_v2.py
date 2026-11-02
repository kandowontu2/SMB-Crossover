"""Record current evidence without promoting a partial roster test to completion."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha

def main():
 o=R/'build/roster-integration-checkpoint-1101-v2';o.mkdir(exist_ok=True)
 installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 assert sha(installed)=='27dee145eead745dfe94cc6e4734a88fdd03811c7f7c3c9d1ee55e54d3057318'
 def load(s):return json.loads((R/s).read_text())
 kirby=load('build/kirby-current-1101-v4/native-final/capture/result.json')
 assert kirby['passed']and all(x['injuries']==0 and len(x['defeats'])==1 for x in kirby['cases'])
 sh=load('build/roster-combined-1101-v1/native/capture/result.json');assert sh['passed']
 q=dict(installed_ROM_sha256=sha(installed),goal_status='ACTIVE_INCOMPLETE',helpers_model='gpt-6.1-sol',helpers_reasoning='xhigh',
  shinobi=dict(candidate='build/roster-combined-1101-v1/candidate.nes',ROM_sha256=sha(R/'build/roster-combined-1101-v1/candidate.nes'),installed=False,
    verified='Metal41 exact180-byte delta composed with source contact/draw repairs; cold title/select/idle/walk passes with aligned OAM counts/rotation on every observed write. Walking image inspected; former HUD-area sprite corruption absent.',
    contact='120 CPU cases preserve original shots and all borrowed/native boxes. Separate real crouch controller defeats opening Goomba and keeps lives but stalls at third pipe X721, both takeoff688 and704; no full-stage claim.',
    remaining='Tall-pipe collision/clearance, full1-1, name/palette/audio and remaining native services. Candidate remains private.'),
  arthur=dict(candidate='build/arthur-camera-1101-v3/candidate.nes',ROM_sha256=sha(R/'build/arthur-camera-1101-v3/candidate.nes'),installed=False,
    verified='Authentication saves about1887 cycles/update; short actions passes before/after. Baseline terrain stuck239; camera successor reaches429. Source tests pass; first pipe controller still fails and is under diagnosis.'),
  kirby=dict(ROM_sha256=kirby['ROM_sha256'],receipt='build/kirby-current-1101-v4/native-final/capture/result.json',verified='Cold Hard selection, moving close-enemy inhale/spit and green/red grounded shell powers pass. HP6 retained, zero injuries, native defeats observed. Three screenshots inspected. Disclosed flat terrain/NPC setup; notfull1-1.',test_repair='GameLoop observer now returns after done, preventing finalization nil task error; gameplay assertions retained.'),
  next='Complete source-owned Shinobi/Arthur traversal fixes, Excitebike owner dispatch/admission, compose nonoverlapping deltas and test exact successor before nightly replacement. Full-roster1-1, everypowerup and assisted crossings remain open.')
 p=R/'docs/qa/continuation-current.json';old=load('docs/qa/continuation-current.json');old['roster_integration_followup']=q;old['previous_goal_turn_classification']='progress';p.write_text(json.dumps(old,indent=2)+'\n')
 (o/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(recorded=True,goal_complete=False,installed_changed=False)))
if __name__=='__main__':main()
