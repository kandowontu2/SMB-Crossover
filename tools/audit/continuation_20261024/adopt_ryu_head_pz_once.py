"""Adopt the verified private retained-air head repair once. Never rerun."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
C=D/'ryu-head-candidate-v5';P=D/'ryu-head-packet-v5'
FINAL=R/'build/checkpoints/native-head-pz';QA=R/'build/verification/native-head-pz'
OLD='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
NEW='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d'
sys.path.insert(0,str(R/'tools/audit'))
from archive_workspace_hz import inventory
from check_tmnt_audio_fallback_oc import qualified
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(n):return json.loads((D/n).read_text())
def record(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def main():
 assert not FINAL.exists()and not QA.exists(),'One-shot adoption already started; inspect before any retry'
 packet=read('ryu-head-packet-v5/packet.json');cpu=read('ryu-head-cpu-v5/proof.json');native=read('ryu-head-native-v5/results.json');entry=read('ryu-head-entry-v5/results.json')
 assert sha(C/'candidate.nes')==packet['ROM_sha256']==NEW and packet['passed'] and packet['source_only_roundtrip_exact'] and packet['source_file_count']==1217
 assert cpu['passed'] and cpu['candidate_sha256']==NEW and cpu['baseline_sha256']==OLD
 assert cpu['restore_cases']==68380 and cpu['geometry_cases']==972 and cpu['ordinary_differential_cases']==360 and cpu['negative_differential_cases']==18
 assert cpu['changed_ROM_bytes']==461 and cpu['changed_banks']==[22]and cpu['old_qualified_symbols_outside_helper_fixed']
 assert native['passed']and native['ROM_sha256']==NEW and len(native['runs'])==2 and all(x['exit']==0 for x in native['runs'])
 for mode in ['easy','hard']:
  assert read('ryu-head-native-v5/'+mode+'/proof.json')==dict(passed=True,cases=4,retained_source_resolves=[1,1,1,1])
 assert entry['rom_sha256']==NEW and entry['identities']==37 and len(entry['results'])==37 and all(x['exit']==0 for x in entry['results'].values())
 frames=0;checks={}
 for mode in ['easy','hard']:
  review=read('ryu-head-review-v5/'+mode+'/proof.json');guard=read('ryu-head-guard-v5/'+mode+'/proof.json')
  assert review['passed']and review['ROM_sha256']==NEW and review['strict_route']['max_world_step']<=2 and review['strict_route']['max_camera_step']<=3
  assert guard['passed']and guard['ROM_sha256']==NEW and guard['observed']['first_invalid_pc']==-1 and guard['observed']['first_poison_frame']==-1 and guard['observed']['observed_minimum_SP']>=153
  cap=read('ryu-head-direct-v5/'+mode+'/proof.json');assert cap['passed']and cap['ROM_sha256']==NEW and cap['fixed_inputs_and_trace_exact']and cap['raw_gzip_roundtrip_exact']and cap['actual_PPU_frame_ids_complete']
  frames+=cap['direct_frames']
  for kind,base in [('review','ryu-head-review-v5'),('guard','ryu-head-guard-v5'),('capture','ryu-head-direct-v5')]:checks[mode+'-'+kind]=record(D/base/mode/'proof.json')
 parent=R/'build/checkpoints/native-rest-py';assert sha(parent/'candidate.nes')==OLD
 before=json.loads((parent/'manifest.json').read_text())['source_files'];changes=packet['changes'];assert list(changes)==['src/ryu_source_head.s']
 assert all(sha(R/n)==h for n,h in before.items())
 assert all(sha(P/'source'/n)==h for n,h in packet['source_files'].items())
 assert {n:h for n,h in packet['source_files'].items()if before[n]!=h}=={'src/ryu_source_head.s':changes['src/ryu_source_head.s']['after']}
 old=(parent/'candidate.nes').read_bytes();new=(C/'candidate.nes').read_bytes();assert old[16+1048576:]==new[16+1048576:]
 names=['smb-crossover-mmc3.nes','smb-crossover-mmc5.nes','smb-crossover-mmc3-oversized.nes','smb-crossover-mmc5-expanded.nes'];public={n:sha(R/'build'/n)for n in names};guide=R/'Player Guide/SMB-Crossover-Players-Guide-NU.pdf';guidehash=sha(guide)
 need=sum((C/('candidate'+ext)).stat().st_size for ext in ['.nes','.lbl','.map'])+(P/'candidate.dbg.gz').stat().st_size+600000
 used=sum(n for _,n,_ in inventory(R,skip_reparse=True));assert used+need<30000000000,(used,need)
 FINAL.mkdir();QA.mkdir();shutil.copy2(Path(__file__),QA/'adoption-driver.py')
 backup=QA/'before/src/ryu_source_head.s';backup.parent.mkdir(parents=True);shutil.copy2(R/'src/ryu_source_head.s',backup)
 assert sha(backup)==changes['src/ryu_source_head.s']['before']
 shutil.copy2(P/'source/src/ryu_source_head.s',R/'src/ryu_source_head.s')
 assert all(sha(R/n)==h for n,h in packet['source_files'].items())
 for ext in ['.nes','.lbl','.map']:shutil.copy2(C/('candidate'+ext),FINAL/('candidate'+ext))
 shutil.copy2(P/'candidate.dbg.gz',FINAL/'candidate.dbg.gz')
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 manifest=dict(utc=stamp,status='PRIVATE_RETAINED_AIR_HEAD_REPAIR_FULL_ROSTER_INCOMPLETE',parent_checkpoint='native-rest-py',rom_sha256=NEW,source_zip_sha256=sha(P/'source.zip'),source_zip_path=str(P/'source.zip'),source_packet_path=str(P/'packet.json'),source_files=packet['source_files'],source_changes=changes,builds=packet['builds'],evidence_directory=str(D),goal_complete=False)
 (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 assert public=={n:sha(R/'build'/n)for n in names}and sha(guide)==guidehash
 used=sum(n for _,n,_ in inventory(R,skip_reparse=True));assert used<30000000000
 for n in ['ryu-head-cpu-v5/proof.json','ryu-head-native-v5/results.json','ryu-head-entry-v5/results.json','ryu-head-packet-v5/packet.json']:checks[n]=record(D/n)
 proof=dict(passed=True,adopted=True,goal_complete=False,utc=stamp,ROM_sha256=NEW,parent_ROM_sha256=OLD,source_zip_path=str(P/'source.zip'),source_zip_sha256=manifest['source_zip_sha256'],source_file_count=1217,source_changes=changes,changed_ROM_bytes=461,changed_PRG_banks=[22],CHR_bytes_changed=0,other_qualified_PCs_fixed=True,RAM_bytes_added=0,OAM_parts_added=0,current_Ryu_modes=2,current_Ryu_lossless_frames=frames,current_retained_head_native_scenes=8,current_cold_entries=37,checks=checks,unchanged_public_ROMs=public,guide_sha256=guidehash,workspace_bytes_after=used,
 scope='Source25 retained-air attacks now use the published body for underside crossing, preventing the native side clamp from snapping X after premature head contact. Restore tail factors to preserve the771byte span; complete A/P/SP/scratch tests and fresh native bank/SMC/NMI guards pass. Two independent full native zero-death Ryu1-1 replays pass original movement/scroll/CHR limits. Ordinary flag-off targets unchanged. Every other identity full clear/item/SFX/fidelity/performance/mapper/guide obligations remain open on the successor; old-hash evidence is retained under its actual hash. No universal60Hz or exhaustive human frame claim. Source ZIP stays external to respect the30GB cap.')
 (QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(adopted=True,ROM_sha256=NEW,source_zip_sha256=manifest['source_zip_sha256'],workspace_bytes=used,goal_complete=False)),flush=True)
if __name__=='__main__':main()
