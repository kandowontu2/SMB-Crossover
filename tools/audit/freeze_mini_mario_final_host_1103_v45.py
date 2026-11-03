"""Compact final Mini host supplement; preserve the earlier source freeze verbatim."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
W,R,O=H.W,H.R,H.O
NEW_SOURCES=[
 'tools/audit/prepare_mini_mario_scroll_1103_v31.py',
 'tools/audit/prepare_mini_mario_chr_republish_1103_v32.py',
 'tools/audit/prepare_mini_mario_chr_override_1103_v39.py',
 'tools/audit/prepare_mini_mario_oam_rotation_1103_v42.py',
 'tools/audit/prepare_mini_mario_oam_reservation_1103_v43.py',
 'tools/audit/freeze_mini_mario_final_host_1103_v45.py',
]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native-result',type=Path);args=ap.parse_args()
 prior=json.loads((O/'mini-native-host-v30.json').read_text())
 assert W.sha((O/'mini-native-host-v30.zip').read_bytes())==prior['archive_SHA256']
 q=json.loads((O/'mini-host-v43.json').read_text());assert q['passed']and q['bytes']==5043 and q['SHA256']==W.sha((O/'mini-host-v43.bin').read_bytes())
 files=[R/n for n in NEW_SOURCES]+[O/'mini-native-host-v30.json']
 for version in[30,32,39,42,43]:
  files +=[O/f'mini-host-v{version}.{suffix}'for suffix in['s','cfg','bin','lbl','json']]
 for name in['native-publisher4-v39','native-reservation-v43']:
  files +=[O/f'{name}.{suffix}'for suffix in['s','cfg','bin','lbl']]
 native_scope='No native acceptance claim in this source supplement; root owns native execution/install.'
 if args.native_result:
  p=args.native_result.resolve();assert p.is_relative_to(R);n=json.loads(p.read_text());assert n.get('passed')is True
  files.append(p);native_scope='Root-owned exact native result copied verbatim; inspect its explicit assertions and ROM hash. This source recipe never runs Mesen or installs.'
 members={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=W.sha(p.read_bytes()))for p in files}
 archive=O/'mini-final-host-v45.zip'
 with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 source_files=list(dict.fromkeys(prior['world_git_source_files']+prior['git_source_files']+NEW_SOURCES))
 out=dict(passed=True,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=W.sha(archive.read_bytes()),final_kernel=dict(path=(O/'mini-host-v43.bin').relative_to(R).as_posix(),bytes=q['bytes'],SHA256=q['SHA256'],five_pages_spare=5120-q['bytes'],labels=q['labels'],vectors=q['vectors']),prior_source_checkpoint=dict(manifest=(O/'mini-native-host-v30.json').relative_to(R).as_posix(),archive=prior['archive'],archive_bytes=prior['archive_bytes'],archive_SHA256=prior['archive_SHA256'],retention='Required compact historical/direct-input checkpoint, unchanged; not recursively extracted or duplicated in this supplement.'),source_step_unchanged=True,source_native_scope=native_scope,git_source_files=source_files,new_git_source_files=NEW_SOURCES,source_fixes=['Native small-player anchor sourceYpixel-24; actual independent source8x16 canvas sourceYpixel-8, original6x7small bounds.','Real source head/side own narrow solids, with native coin/vine query packets preserved.','Player_Pos_ForScroll published before source Step so native camera can follow.','Existing native special window4 override owns CHR968 against unconditional RlOriginalFullShotBank writes. Previous AreaType writer hypothesis was contradicted by actual writer38.','Native logical OAM reservation via existing SmPose6B05=4/SmPosePtr=&SmPose; ObjectMetasprite0 separately remains0.','Physical sprite slot logical+rotation when GuestOamRotationActive; logical cursor advances4.8064finite source allocator/renderer cases pass.'],deliberate_adaptation='User-authorized native wall cling/jump queues original JUMP_INIT with original velocity/gravity. No helper platform actor placed by these sources.',remaining=['Root-owned final native route, installation/Downloads context and IPS roundtrip verification.','Extended swim/climb/scripts/source audio and unique menu portrait remain deferred.','Actual native injury/death/power fidelity is limited to declared native fallback/typed adapters, not fully qualified donor lifecycle.'],no_ROM_DBG_PNG_object_or_executable=True,members=members)
 (O/'mini-final-host-v45.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in['passed','archive_bytes','archive_SHA256','final_kernel','new_git_source_files']}))
if __name__=='__main__':main()
