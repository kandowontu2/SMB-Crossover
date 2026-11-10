"""Deliver verified opening prototypes without claiming full-stage completion."""
import argparse,json,subprocess,sys
from pathlib import Path
import compose_remaining_roster_starts_1110 as Q
import prepare_manual_dual_native_1110 as P
from deliver_giant_impact_1110 import packet_result,NIGHTLY,SMALL
from deliver_manual_title_1110 import ips_for,ASSET,REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import prepare,sha

R=Q.R;NATIVE=R/'build/remaining-roster-native-1110';PROOF=Q.OUT/'proof.json'


def evidence():
 q=json.loads(PROOF.read_text());assert q['passed']and not q['ROM_written']
 for name,h in q['bindings'].items():assert sha(R/name)==h,name
 parent,raw,rows,_,_=Q.compose();digest=Q.digest(raw)
 assert digest==q['expected_memory_only_SHA256']and rows==q['patches']and raw==(NATIVE/'candidate.nes').read_bytes()
 for name,owner in (('prince',38),('dkjr',40)):
  result=packet_result(NATIVE/name,NATIVE/'candidate.nes',digest)
  assert result['terminal']['owner']==owner and result['terminal']['lives']==2
 for name in ('mini','getsu'):packet_result(NATIVE/'regression'/name,NATIVE/'candidate.nes',digest)
 cadence=json.loads((NATIVE/'regression/mini/capture/timing.json').read_text())['cadence']['fullstage']
 assert cadence['physical']==cadence['updates']==3494 and all(cadence.get(k,0)==0 for k in ('lag_nmi','zero_update','no_controller_read'))
 return raw,digest,cadence


def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('deliver','publish'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert out.is_relative_to(R/'build');raw,digest,cadence=evidence()
 receipt=out/'verified-delivery.json';patch=out/ASSET
 if a.action=='deliver':
  assert not out.exists();before=check(NIGHTLY);assert before['ROM_sha256']==Q.PIN;out.mkdir()
  try:
   NIGHTLY.write_bytes(raw);assert check(NIGHTLY)['ROM_sha256']==digest
   symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
   for name in ('prince','dkjr'):
    old=NATIVE/name;packet=out/name
    prepare(packet,NIGHTLY,(old/'controller.lua').read_text(),{Path(__file__),PROOF,old/'controller.lua',old/'capture/result.json'},
     expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,
     scope='Actual Downloads: exact verified character-select/authentic-header/walk/jump opening prototype input, no state writes; full1-1 not qualified.')
    subprocess.run([sys.executable,'-B',str(SMALL),'--files','10',str(packet/'run.py')],check=True)
    assert packet_result(packet,NIGHTLY,digest)['terminal']['lives']==2
   patch.write_bytes(ips_for(raw))
   q=dict(installed=True,Downloads_launch_verified=True,backup_created=False,IPS_roundtrip=True,
    ROM_SHA256=digest,previous_ROM_SHA256=Q.PIN,IPS_SHA256=sha(patch),proof_SHA256=sha(PROOF),mini_cadence=cadence,
    scope='Prince/DKJr verified opening prototypes; known full-route failures remain. Mini full1-1 and Getsu powerup regression passed.',
    before=before,after=check(NIGHTLY),Downloads_results={n:sha(out/n/'capture/result.json')for n in ('prince','dkjr')})
   receipt.write_text(json.dumps(q,indent=2)+'\n')
  except(Exception,KeyboardInterrupt):
   NIGHTLY.write_bytes(Q.PARENT.read_bytes());assert check(NIGHTLY)['ROM_sha256']==Q.PIN;raise
 else:
  q=json.loads(receipt.read_text());assert q['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==digest
  assert q['proof_SHA256']==sha(PROOF) and q['IPS_SHA256']==sha(patch) and patch.read_bytes()==ips_for(raw)
  for name in ('prince','dkjr'):packet_result(out/name,NIGHTLY,digest)
  current=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/tags/Current'],encoding='utf-8'));old,=current['assets'];assert old['name']==ASSET
  notes=out/'release-notes.txt';notes.write_text('Current MMC5 WIP. Apply to clean headered Super Mario Bros. (World).\n\n'
   'New startable prototypes: Prince of Persia (Select on Excitebike), Donkey Kong Jr. (Select on Donkey Kong). '
   'Cold real character selection, authentic initialization/graphics and a short walk/jump opening passed, including the actual Downloads filename. '
   'These are unfinished: Prince can still die on an Easy landing later in1-1, and DKJr has a first-pipe lift/jump-detach problem. Full-stage completion is not claimed.\n'
   'Mini/Karnov Up+Select vertical and Down+Select right-first112px horizontal platforms are retained. '
   'Mini full1-1 retains3494updates/3494gameplayframes, zero lag NMIs/missed updates; Getsu real mushroom/flower regression passes. '
   'Wrestler/FinalFantasy platform support and Sonic/Jay/Steve startup prototypes are in progress.\nROM SHA-256 '+digest+'\n')
  subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
  subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
  latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/latest'],encoding='utf-8'));asset,=latest['assets']
  assert latest['tag_name']=='Current'and asset['name']==ASSET and asset['digest']=='sha256:'+sha(patch)
  q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=asset['digest'])
  receipt.write_text(json.dumps(q,indent=2)+'\n')
 print(a.action,digest,flush=True)


if __name__=='__main__':main()
