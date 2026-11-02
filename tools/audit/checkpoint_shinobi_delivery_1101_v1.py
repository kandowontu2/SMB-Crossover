"""Finalize the exact Downloads launch and retain the full unfinished scope."""
import json,subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from nightly_patch_guard_v1 import check
O=R/'build/roster-combined-1101-v1'
def main(arthur=False):
 global O
 if arthur:O=R/'build/roster-combined-1101-v3'
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');digest=sha(dest);assert digest==sha(O/'candidate.nes')
 c=O/'downloads/capture';b=json.loads((c/'binding.json').read_text());r=json.loads((c/'result.json').read_text());assert b['exit_code']==0 and b['ROM_sha256']==digest and r['passed']
 d=json.loads((O/'delivery.json').read_text());d['downloads_launch_verified']=True;d['after_downloads_launch_patch_guard']=check(dest);(O/'delivery.json').write_text(json.dumps(d,indent=2)+'\n')
 p=R/'docs/qa/continuation-current.json';q=json.loads(p.read_text());q['installed_nightly']=dict(d,destination=str(dest),complete=False,candidate=str((O/'candidate.nes').relative_to(R)),character_selection='Ryu slot10, Select once to Shinobi (raw36/FmAlts04). Menu currently retains pending-style name prefix; actual Select/Start admission works.',native_scope='Exact candidate Shinobi1-1→active1-2 in8462physicalframes and Metal Storm1-1→active1-2 in5498frames; lives2→2 ineach. Actual Downloads cold menu/Start/idle/walk passed with aligned OAM-count/rotation writes. No backup. No helpers added.')
 q['roster_integration_followup']['installed_ROM_sha256']=digest
 q['roster_integration_followup']['shinobi'].update(candidate='build/roster-combined-1101-v1/candidate.nes',ROM_sha256=digest,installed=True,verified=q['installed_nightly']['native_scope'],remaining='Exact original-pose body hitbox ingress remains; current native small SMB enemy/contact box is too short. Original audio/melee/magic and HUD name/palette review remain. Full-roster/allpowerup verification incomplete.')
 q['roster_integration_followup']['arthur']['verified']='Source auth optimization/clock guards pass; camera restores scroll, actions+firstpipe doublejump pass. Full1-1 negative clearsfourpipes but fallsstairgap; engine11 persistedwithoutlifeadvance. Supersededbyv4localdeathfix; currentv4fullroute/pitlife tests passed; cumulativeadoptionpending unlessinstalledc3dd.'
 if arthur:
  q['installed_nightly']['native_scope']='Exact cumulative Arthur1-1 to active1-2 in6107physicalframes,lives2to2,nohelpers; intentionalpitdeathreachesnextlife/resumedcontrol. Shinobi actualDownloads coldmenu/Start/idle/walkOAMaligned and Metalidle/walk pass. Earlier933Shinobi/Metal full1-1 bytes retained outsideArthur531-byteownedpatch. No backup. Fullroster/allpowerups incomplete.'
  q['roster_integration_followup']['arthur'].update(candidate='build/roster-combined-1101-v3/candidate.nes',ROM_sha256=digest,installed=True,verified=q['installed_nightly']['native_scope'])
  q['roster_integration_followup']['shinobi'].update(candidate='build/roster-combined-1101-v3/candidate.nes',ROM_sha256=digest,verified='Shinobi full1-1 throughactive1-2 passed on933 in8462frames/lives2to2/nohelpers. C3dd preserves thoseShinobi/Metal bytes outsideArthur531-byteownedpatch; cumulativeShinobiOAMsmoke and actualDownloads coldlaunch passed. Not a fresh fullShinobi route onC3dd.')
 q['previous_goal_turn_classification']='progress'
 # Place current delivery first so historical handoff sections cannot be
 # mistaken for the live nightly on a short continuation read.
 top={k:q.pop(k)for k in ['installed_nightly','roster_integration_followup','goal_status','previous_goal_turn_classification']};p.write_text(json.dumps({**top,**q},indent=2)+'\n')
 doc=R/'docs/qa/helper-platform-inventory-1101.md';text=doc.read_text(encoding='utf-8');note='\nNative 1-1 addendum: Shinobi now clears the entire stage into active 1-2 on installed 933c0650, in 8462 physical frames, lives 2 to 2, without helpers. Tall-pipe takeoffs at 692/868 and later gap input were sufficient with original motion. Metal Storm also clears on this hash in 5498 frames, lives 2 to 2, without helpers. These are stage-specific results; exact Shinobi body-policy review remains open.\n'
 if not text:text=subprocess.check_output(['git','show','HEAD:docs/qa/helper-platform-inventory-1101.md'],cwd=R).decode('utf-8')
 if 'Native 1-1 addendum: Shinobi'not in text:text+=note
 if arthur and 'Arthur on cumulative c3dd0303'not in text:
  text+='\nArthur on cumulative c3dd0303 also clears 1-1 into active 1-2 in 6107 physical frames, lives 2 to 2, without helpers. His intended second jump press is required. This covers Arthur only, not his Goku alternate.\n'
 doc.write_text(text,encoding='utf-8',newline='\n')
 print(json.dumps(dict(installed=True,downloads_launch_verified=True,ROM_sha256=digest,goal_complete=False,backup=False)))
if __name__=='__main__':
 import sys
 main('--arthur' in sys.argv)
