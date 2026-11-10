"""Deliver independently owned native vertical/horizontal manual assistance."""
import argparse,json,subprocess,sys
from pathlib import Path
import check_manual_dual_rebase_1110 as Q
from deliver_giant_impact_1110 import packet_result,NIGHTLY,SMALL
from deliver_manual_title_1110 import ips_for,ASSET,REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import sha

R=Q.R;PIN='4e7bcde589328f720ae86d98e6fcf8d2561bdd3db5006361a454531b85fbd117'
PROOF=R/'build/manual-dual-platform-1110/rebase-proof.json';NATIVE=R/'build/manual-dual-native-1110'

def qualified():
 q=json.loads(PROOF.read_text());assert q['passed'] and q['parent_SHA256']==Q.PIN and q['expected_memory_only_SHA256']==PIN
 assert q['upstream_disjoint'] and q['interrupt_reuse']
 for name,h in q['bindings'].items():assert sha(R/name)==h,name
 raw=Q.D.P.install(Q.BASE.read_bytes(),q['patches']);assert Q.D.sha256(raw).hexdigest()==PIN
 assert raw==(NATIVE/'candidate.nes').read_bytes()
 return raw

def evidence():
 qualified();rom=NATIVE/'candidate.nes'
 results={name:packet_result(NATIVE/'qualified'/name,rom,PIN) for name in ('mini','karnov')}
 for q in results.values():
  assert q['terminal']['lives']==2 and len(q['births'])==4
  assert any(s['name']=='horizontal carry' and s['carry_updates']>=6 for s in q['samples'])
  assert len(q['terminal']['vertical'])==len(q['terminal']['horizontal'])==1
 mini=packet_result(NATIVE/'regression/mini',rom,PIN)
 timing=json.loads((NATIVE/'regression/mini/capture/timing.json').read_text())['cadence']['fullstage']
 assert mini['full_stage'] and timing==dict(physical=3494,updates=3494,lag_nmi=0,zero_update=0),timing
 getsu=packet_result(NATIVE/'regression/getsu',rom,PIN)
 assert getsu['terminal']['lives']==2
 assert [(e['status'],e['age']) for e in getsu['pickup']['events'] if e['active']==0]==[(1,60),(2,60)]
 return timing

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('deliver','publish'));p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert out.is_relative_to(R/'build');raw=qualified();timing=evidence()
 receipt=out/'verified-delivery.json';patch=out/ASSET
 if a.action=='deliver':
  before=check(NIGHTLY);assert before['ROM_sha256']==Q.PIN;out.mkdir(exist_ok=True)
  try:
   NIGHTLY.write_bytes(raw);assert check(NIGHTLY)['ROM_sha256']==PIN
   subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_dual_native_1110.py'),'--output',str(out/'downloads'),
    '--rom',str(NIGHTLY),'--proof',str(PROOF)],check=True)
   for name in ('mini','karnov'):
    subprocess.run([sys.executable,'-B',str(SMALL),'--files','10',str(out/'downloads'/name/'run.py')],check=True)
    actual=packet_result(out/'downloads'/name,NIGHTLY,PIN);assert actual['terminal']['lives']==2 and len(actual['births'])==4
   patch.write_bytes(ips_for(raw))
   q=dict(installed=True,Downloads_launch_verified=True,backup_created=False,IPS_roundtrip=True,ROM_SHA256=PIN,previous_ROM_SHA256=Q.PIN,
    IPS_SHA256=sha(patch),proof_SHA256=sha(PROOF),mini_cadence=timing,before=before,after=check(NIGHTLY),
    Downloads_results={n:sha(out/'downloads'/n/'capture/result.json') for n in ('mini','karnov')})
   receipt.write_text(json.dumps(q,indent=2)+'\n')
  except (Exception,KeyboardInterrupt):
   NIGHTLY.write_bytes(Q.BASE.read_bytes());assert check(NIGHTLY)['ROM_sha256']==Q.PIN;raise
 else:
  q=json.loads(receipt.read_text());assert q['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==PIN
  assert q['IPS_SHA256']==sha(patch) and patch.read_bytes()==ips_for(raw)
  for name in ('mini','karnov'):packet_result(out/'downloads'/name,NIGHTLY,PIN)
  notes=out/'release-notes.txt';notes.write_text('Current MMC5 WIP. Apply to clean headered Super Mario Bros. (World).\n\n'
   'Mini Mario and Karnov: Up + Select summons a vertical platform; Down + Select summons a horizontal platform in front. '
   'One of each type can coexist. A fresh combination replaces only that type; holding it does not recreate the platform. '
   'A full native actor pool queues the request.\n'
   'Actual Downloads input, movement, independent replacement and horizontal carrying passed for both characters. '
   'Mini normal1-1 retained3494 updates/3494 gameplay frames, zero lag NMIs or missed updates. '
   'Getsu mushroom and flower regression passed. Full roster testing remains in progress.\nROM SHA-256 '+PIN+'\n')
  subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
  subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
  latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/latest'],encoding='utf-8'));asset,=latest['assets']
  assert latest['tag_name']=='Current' and asset['name']==ASSET and asset['digest']=='sha256:'+sha(patch)
  q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=asset['digest']);receipt.write_text(json.dumps(q,indent=2)+'\n')
 print(a.action,PIN,flush=True)

if __name__=='__main__':main()
