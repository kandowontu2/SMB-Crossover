"""Deliver Getsu's missing upgrade callback after real pickup and route replays."""
import argparse,json,subprocess,sys
from pathlib import Path
import check_getsu_powerup_callback_1110 as Q
from deliver_giant_impact_1110 import packet_result,NIGHTLY,SMALL
from deliver_manual_title_1110 import ips_for,ASSET,REPO
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import sha

R=Q.R; PROOF=R/'build/getsu-head-callback-1110/proof.json'
PIN='c6ab56107cf78954ff24f0fddbd40a0207afd4e7743eaeb8c762a53329d30f1b'
BINDER=R/'tools/audit/prepare_getsu_powerup_replay_1110.py'

def qualified(rom):
 q=json.loads(PROOF.read_text());assert q['passed'] and q['parent_SHA256']==Q.PIN and q['expected_memory_only_SHA256']==PIN
 assert q['gait'] and q['render'] and q['vectors']
 for name,digest in q['bindings'].items():assert sha(R/name)==digest,name
 parent=Q.BASE.read_bytes();assert Q.sha(parent)==Q.PIN
 image=bytearray(parent)
 for row in q['patches']:
  at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex']);assert image[at:at+len(old)]==old
  image[at:at+len(old)]=new
 raw=bytes(image);assert Q.sha(raw)==PIN and raw==rom.read_bytes()
 return raw

def stage_packet(out,rom,mode):
 subprocess.run([sys.executable,'-B',str(BINDER),'--output',str(out),'--rom',str(rom),'--proof',str(PROOF),'--mode',mode],check=True)

def evidence(native):
 rom=native/'candidate.nes';raw=qualified(rom)
 pu=packet_result(native/'powerup',rom,PIN);route=packet_result(native/'route',rom,PIN)
 assert pu['terminal']['lives']==route['terminal']['lives']==2
 assert len(pu['pickup']['events'])>=4 and route['terminal']['level']==2
 completed=[e for e in pu['pickup']['events'] if e['active']==0]
 assert [(e['status'],e['age']) for e in completed]==[(1,60),(2,60)]
 assert pu['terminal']['x']>=pu['pickup']['recovered_x']+16
 return raw,pu,route

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('stage','deliver','publish'))
 p.add_argument('--output',type=Path,required=True);p.add_argument('--native',type=Path)
 a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(R/'build')
 if a.action=='stage':
  rom=out/'candidate.nes';qualified(rom)
  for mode in ('powerup','route'):stage_packet(out/mode,rom,mode)
  return
 assert a.native;native=a.native.resolve();raw,pu,route=evidence(native)
 receipt=out/'verified-delivery.json';patch=out/ASSET
 if a.action=='deliver':
  before=check(NIGHTLY);assert before['ROM_sha256']==Q.PIN;out.mkdir(exist_ok=True)
  try:
   NIGHTLY.write_bytes(raw);assert check(NIGHTLY)['ROM_sha256']==PIN
   stage_packet(out/'downloads-powerup',NIGHTLY,'powerup')
   subprocess.run([sys.executable,'-B',str(SMALL),'--files','12',str(out/'downloads-powerup/run.py')],check=True)
   actual=packet_result(out/'downloads-powerup',NIGHTLY,PIN);assert actual['terminal']['lives']==2
   patch.write_bytes(ips_for(raw))
   q=dict(installed=True,Downloads_launch_verified=True,IPS_roundtrip=True,backup_created=False,
          ROM_SHA256=PIN,previous_ROM_SHA256=Q.PIN,IPS_SHA256=sha(patch),proof_SHA256=sha(PROOF),
          native=str(native),powerup_result_SHA256=sha(native/'powerup/capture/result.json'),
          route_result_SHA256=sha(native/'route/capture/result.json'),
          Downloads_result_SHA256=sha(out/'downloads-powerup/capture/result.json'),before=before,after=check(NIGHTLY))
   receipt.write_text(json.dumps(q,indent=2)+'\n')
  except (Exception,KeyboardInterrupt):
   NIGHTLY.write_bytes(Q.BASE.read_bytes());assert check(NIGHTLY)['ROM_sha256']==Q.PIN;raise
 else:
  q=json.loads(receipt.read_text());assert q['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==PIN
  packet_result(out/'downloads-powerup',NIGHTLY,PIN)
  assert q['IPS_SHA256']==sha(patch) and patch.read_bytes()==ips_for(raw)
  notes=out/'release-notes.txt';notes.write_text('Current MMC5 WIP. Apply to clean headered Super Mario Bros. (World).\n\n'
   'Fixed Getsu Fuma freezing after mushroom or Fire Flower pickup. Native transformations now finish in60gameupdates. '
   'Verified real block pickups, continued movement, full1-1 clear, original gait and sprite/palette checks. '
   'Combat lag and full-roster testing remain in progress.\nROM SHA-256 '+PIN+'\n')
  subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
  subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
  latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/latest'],encoding='utf-8'));asset,=latest['assets']
  assert latest['tag_name']=='Current' and asset['name']==ASSET and asset['digest']=='sha256:'+sha(patch)
  q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=asset['digest']);receipt.write_text(json.dumps(q,indent=2)+'\n')
 print(a.action,PIN,flush=True)

if __name__=='__main__':main()
