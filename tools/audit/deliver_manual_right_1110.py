"""Install/publish the tested initially-right oscillating manual platform build."""
import argparse,json,subprocess,sys
from pathlib import Path
from stage_manual_right_native_1110 import reconstruct,R,BASE,PARENT
from deliver_giant_impact_1110 import packet_result,NIGHTLY,SMALL
from deliver_manual_title_1110 import ips_for,ASSET,REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import sha


def motion(q):
 assert q['terminal']['lives']==2 and len(q['births'])==6
 assert len(q['terminal']['vertical'])==len(q['terminal']['horizontal'])==1
 samples={s['name']:s for s in q['samples']}
 for name in ('horizontal carry','right endpoint','left endpoint'):
  assert samples[name]['carry_updates']>=6,name
 first=samples['right endpoint']['horizontal'][0]['x']
 left=samples['left endpoint']['horizontal'][0]['x']
 second=samples['second right endpoint']['horizontal'][0]['x']
 assert first==second==left+112


def evidence(native,proof):
 raw,q=reconstruct(proof);digest=q['expected_memory_only_SHA256'];rom=native/'candidate.nes'
 assert rom.read_bytes()==raw
 assert not q.get('interrupt_qualification_pending',False)
 assert not q.get('interrupt_pending',False)
 for name in ('mini','karnov'):motion(packet_result(native/'native'/name,rom,digest))
 mini=packet_result(native/'regression/mini',rom,digest)
 cadence=json.loads((native/'regression/mini/capture/timing.json').read_text())['cadence']['fullstage']
 assert mini['full_stage'] and cadence['physical']==cadence['updates']==3494,cadence
 assert all(cadence.get(k,0)==0 for k in ('lag_nmi','zero_update','no_controller_read')),cadence
 getsu=packet_result(native/'regression/getsu',rom,digest)
 assert getsu['terminal']['lives']==2
 assert [(e['status'],e['age']) for e in getsu['pickup']['events'] if e['active']==0]==[(1,60),(2,60)]
 return raw,digest,cadence


def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('deliver','publish'))
 p.add_argument('--output',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--proof',type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();native=a.native.resolve();proof=a.proof.resolve()
 assert out.is_relative_to(R/'build');raw,digest,cadence=evidence(native,proof)
 receipt=out/'verified-delivery.json';patch=out/ASSET
 if a.action=='deliver':
  assert not out.exists();before=check(NIGHTLY);assert before['ROM_sha256']==PARENT;out.mkdir()
  try:
   NIGHTLY.write_bytes(raw);assert check(NIGHTLY)['ROM_sha256']==digest
   subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_right_native_1110.py'),
    '--output',str(out/'downloads'),'--rom',str(NIGHTLY),'--proof',str(proof)],check=True)
   for name in ('mini','karnov'):
    subprocess.run([sys.executable,'-B',str(SMALL),'--files','10',str(out/'downloads'/name/'run.py')],check=True)
    motion(packet_result(out/'downloads'/name,NIGHTLY,digest))
   patch.write_bytes(ips_for(raw))
   q=dict(installed=True,Downloads_launch_verified=True,backup_created=False,IPS_roundtrip=True,
    ROM_SHA256=digest,previous_ROM_SHA256=PARENT,IPS_SHA256=sha(patch),proof=str(proof),proof_SHA256=sha(proof),
    mini_cadence=cadence,before=before,after=check(NIGHTLY),
    Downloads_results={n:sha(out/'downloads'/n/'capture/result.json') for n in ('mini','karnov')})
   receipt.write_text(json.dumps(q,indent=2)+'\n')
  except (Exception,KeyboardInterrupt):
   NIGHTLY.write_bytes(BASE.read_bytes());assert check(NIGHTLY)['ROM_sha256']==PARENT;raise
 else:
  q=json.loads(receipt.read_text());assert q['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==digest
  assert q['proof_SHA256']==sha(proof) and patch.read_bytes()==ips_for(raw) and q['IPS_SHA256']==sha(patch)
  for name in ('mini','karnov'):motion(packet_result(out/'downloads'/name,NIGHTLY,digest))
  latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/tags/Current'],encoding='utf-8'))
  old,=latest['assets'];assert old['name']==ASSET
  notes=out/'release-notes.txt';notes.write_text('Current MMC5 WIP. Apply to clean headered Super Mario Bros. (World).\n\n'
   'Mini Mario and Karnov: Down + Select summons a separate native horizontal platform to the right, regardless of facing. '
   'It starts moving right and repeats a112-pixel right/left trip. Up + Select retains the separate vertical platform. '
   'One of each can coexist; a fresh combination replaces only that type.\n'
   'Verified from actual Downloads: both characters, full right-left-right motion with native carrying/scrolling, held edges, '
   'axis-only replacement and right-side spawn while facing left. Mini normal1-1 remains3494updates/3494gameplayframes with zero lag NMIs; '
   'Getsu real mushroom/flower pickups recover normally. Full roster testing remains in progress.\nROM SHA-256 '+digest+'\n')
  subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
  subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
  latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/latest'],encoding='utf-8'));asset,=latest['assets']
  assert latest['tag_name']=='Current' and asset['name']==ASSET and asset['digest']=='sha256:'+sha(patch)
  q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=asset['digest'])
  receipt.write_text(json.dumps(q,indent=2)+'\n')
 print(a.action,digest,flush=True)


if __name__=='__main__':main()
