"""Save actual delivered proof and keep omitted roster requirements visible."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from nightly_patch_guard_v1 import check
O=R/'build/shinobi-bbox-candidate-1101-v30'
def main():
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');digest=sha(dest);assert digest==sha(O/'candidate.nes')
 c=O/'downloads/capture';r=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text());assert r['passed']and b['exit_code']==0 and b['ROM_sha256']==digest
 d=json.loads((O/'delivery.json').read_text());d.update(downloads_launch_verified=True,after_downloads_launch_patch_guard=check(dest));(O/'delivery.json').write_text(json.dumps(d,indent=2)+'\n')
 menu=json.loads((R/'build/playable-menu-1101-v4/inventory.json').read_text());assert menu['ROM_sha256']==digest and menu['installed_bytes_identical']
 p=R/'docs/qa/continuation-current.json';q=json.loads(p.read_text());q['installed_nightly']=dict(d,destination=str(dest),candidate='build/shinobi-bbox-candidate-1101-v30/candidate.nes',complete=False,character_selection='Select on Ryu slot10 to Shinobi; Star/pending-style name prefix still cosmetic, confirmation works. Reopen ROM/start fresh after updating.')
 f=q['roster_integration_followup'];f['installed_ROM_sha256']=digest
 f['shinobi'].update(candidate='build/shinobi-bbox-candidate-1101-v30/candidate.nes',ROM_sha256=digest,installed=True,verified=d['scope'],contact='Original shot bounds/motion retained. Native body enemy/contact rectangle now follows original pose, including40/30/19px-high profiles; source coordinates/caller state restored.',remaining='Head/side tile probes still use existing profile3; original audio/melee/magic/powerups and HUD name/palette review remain. No full-roster/allpowerup completion claim.')
 f['arthur'].update(candidate='build/shinobi-bbox-candidate-1101-v30/candidate.nes',ROM_sha256=digest,verified='Exact new body-bbox candidate Arthur full1-1→active1-2 native regression passes6107frames,lives2to2,nohelpers. C3dd pitdeath→nextlife fix bytes retained; previouspitproof unchanged.')
 f['menu_audit']=dict(receipt='build/playable-menu-1101-v4/inventory.json',distinct_names=menu['distinct_named_entries'],confirmable_names=menu['confirmable_named_entries'],blocked=['Excitebike','Prince of Persia'],absent=menu['requested_names_absent'],scope='CPU actualSelect/Start/A only; menu admission is not gameplay/fullstage/powerup qualification.')
 f['shinobi_bbox_source_checkpoint']='docs/qa/checkpoints/2026-11-01/shinobi-bbox-source-v30 (fiveexactretainedinputs,69362sourcebytes,17965-byteZIP; noROM/historicaltree).'
 f['active_helpers']={'arthur_sol61':'Prince original actor/script/control/renderer recovery.','excitebike_sol61':'Excitebike source motor/pose/terrain and compact three-owner router/scene integration.','shinobi_sol61':'Bub/Bob original Bubble Bobble actor/bubble/trap/pop recovery.'}
 f['next']='Continue all missing roster entries; Excitebike/Prince currentlyblocked, eight requested identities absent (see menu_audit). Complete every-character1-1 and every-powerup proof; source/CPU-only components and menuadmission cannot stand in for native playability. Preserve installed6f319.'
 q['completion']='ACTIVE_INCOMPLETE. Installed menu has91distinctnames/89confirmable inCPUtests; Excitebike/Princeblocked andeightrequestedidentitiesabsent. All-character1-1/shortcut/every-powerup/nativegraphicsandabilityverificationremainrequired.'
 q['other_full_objective_work'][1]='Metal Storm/Shinobi/Arthur delivered WIP with native1-1 proof; Excitebike/Prince source-backed hostintegration and Bub/Bob source recovery remain underway.'
 q['previous_goal_turn_classification']='progress';p.write_text(json.dumps(q,indent=2)+'\n')
 lines=['# Current roster gaps — November 1','',f'Installed MMC5 SHA256: `{digest}`.','',f'The actual compiled menu has {menu["distinct_named_entries"]} distinct displayed entries; {menu["confirmable_named_entries"]} accept Start and A in CPU tests. This is menu admission only. It does not prove that all those characters can clear 1-1 or use every powerup.','','Excitebike and Prince of Persia are displayed but still reject confirmation. Their source-backed integrations remain in progress.','','The following requested identities are absent from the emitted menu names:','']
 lines.extend('- '+n for n in menu['requested_names_absent'])
 lines+=['','Shinobi now has original pose-dependent native enemy/contact bounds and a fresh no-helper 1-1 to active 1-2 clear (8924 physical frames, lives 2 to 2). Arthur also passes the full-stage regression on this exact ROM (6107 frames, lives 2 to 2). Shinobi idle/walk throughput remains 80/78 updates per 120 physical frames; CPU work increases by 1523 cycles per update.','','No new natural-powerup coverage is claimed by these runs. Remaining original moves, upgrades, audio, every-character routes, and helper-assisted crossings remain required.','']
 (R/'docs/qa/current-roster-gaps-1101.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
 doc=R/'docs/qa/helper-platform-inventory-1101.md';t=doc.read_text(encoding='utf-8');note='\nWith original pose-based contact bounds installed in 6f319d20, Shinobi again clears 1-1 into active 1-2 without helpers (8924 physical frames, lives 2 to 2). Arthur also passes on this exact ROM in 6107 frames without helpers.\n'
 if 'contact bounds installed in 6f319d20'not in t:doc.write_text(t+note,encoding='utf-8',newline='\n')
 print(json.dumps(dict(installed=True,ROM_sha256=digest,downloads_verified=True,backup=False,goal_complete=False,menu_names=menu['distinct_named_entries'])))
if __name__=='__main__':main()
