"""One-shot private checkpoint adoption. Never rerun after adoption starts."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
C=D/'food-candidate-v3';P=D/'food-packet-v3';FINAL=R/'build/checkpoints/native-rest-py';QA=R/'build/verification/native-rest-py'
EXPECTED='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for data in iter(lambda:f.read(1048576),b''):h.update(data)
 return h.hexdigest()
def read(name):return json.loads((D/name).read_text())
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
sys.path.insert(0,str(R/'tools/audit'))
from archive_workspace_hz import inventory
from check_tmnt_audio_fallback_oc import qualified
def main():
 assert not FINAL.exists()and not QA.exists(),'Adoption already started: do not rerun blindly'
 packet=read('food-packet-v3/packet.json');hud=read('food-hud-static-v3.json');food=read('food-static-v2.json');wave=read('wave-static-v1.json');health=read('health-food-final-v3/results.json');copies=read('kirby-copies-final-v3/results.json');entry=read('food-entry-v3/results.json')
 assert packet['passed']and packet['ROM_sha256']==sha(C/'candidate.nes')==EXPECTED and packet['source_file_count']==1217
 assert hud['passed']and hud['ROM_sha256']==EXPECTED and hud['changed_ROM_bytes']==2 and hud['opcode_and_instruction_cycles_unchanged']
 assert food['passed']and food['collection_cases']==5040 and food['collection_extra_CPU_cycles']==[22]
 assert wave['passed']and wave['native_motion_span_cases']==46080 and wave['all_span_CPU_cycles_exact']
 assert health['passed']and health['ROM_sha256']==EXPECTED and len(health['runs'])==8 and sum(len(x['result']['items'])for x in health['runs'])==44
 assert all(x['exit']==0 and x['result']['passed']for x in health['runs'])
 assert copies['passed']and copies['ROM_sha256']==EXPECTED and len(copies['runs'])==2 and all(x['exit']==0 and x['result']['passed']and len(x['result']['powers'])==14 for x in copies['runs'])
 assert entry['rom_sha256']==EXPECTED and entry['identities']==len(entry['results'])==37 and all(x['exit']==0 for x in entry['results'].values())
 parent=R/'build/checkpoints/native-items-px/candidate.nes';a=parent.read_bytes();b=(C/'candidate.nes').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y]
 assert len(diff)==19 and sorted({(i-16)//8192 for i in diff})==[74,79]and a[16+1048576:]==b[16+1048576:]
 qa,qb=qualified(parent),qualified(C/'candidate.nes');assert len(qa)==54005 and all(qb.get(k)==v for k,v in qa.items())and len(qb)==54006
 streams=['copies-easy','copies-hard','health-chip-easy','health-chip-hard','health-dale-easy','health-dale-hard'];frames=0;capture_checks={}
 for name in streams:
  p=D/(name+'-food-v3-direct-v1/proof.json');q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==EXPECTED and q['actual_PPU_frame_ids_complete']and q['every_saved_PNG_RGB_exact']and q['raw_gzip_roundtrip_exact'];frames+=q['direct_physical_frames'];capture_checks[name]=record(p)
 visuals=['copy-visual-final-easy-v3/sampling-manifest.json','copy-visual-final-hard-v3/sampling-manifest.json']+[n+'-visual-v3/sampling-manifest.json'for n in streams[2:]]
 assert all((D/n).exists()for n in visuals),'Human-sampled visual review manifests must exist'
 changes=packet['changes'];assert len(changes)==4
 for name,digest in packet['source_files'].items():
  assert sha(P/'source'/name)==digest
  assert sha(R/name)==(changes[name]['before']if name in changes else digest),name
 names=['smb-crossover-mmc3.nes','smb-crossover-mmc5.nes','smb-crossover-mmc3-oversized.nes','smb-crossover-mmc5-expanded.nes'];public={n:sha(R/'build'/n)for n in names};guide=R/'Player Guide/SMB-Crossover-Players-Guide-NU.pdf';gh=sha(guide)
 need=sum((P/n).stat().st_size for n in ['source.zip','candidate.dbg.gz'])+sum((C/('candidate'+e)).stat().st_size for e in ['.nes','.lbl','.map'])+3_000_000
 used=sum(n for _,n,_ in inventory(R,skip_reparse=True));assert used+need<30_000_000_000,(used,need)
 QA.mkdir();FINAL.mkdir();shutil.copy2(Path(__file__),QA/'adoption-driver.py')
 for name,row in changes.items():
  backup=QA/'before'/name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,backup);assert sha(backup)==row['before'];shutil.copy2(P/'source'/name,R/name);assert sha(R/name)==row['after']
 assert all(sha(R/name)==digest for name,digest in packet['source_files'].items())
 for ext in ['.nes','.lbl','.map']:shutil.copy2(C/('candidate'+ext),FINAL/('candidate'+ext))
 for name in ['source.zip','candidate.dbg.gz']:shutil.copy2(P/name,FINAL/name)
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();manifest=dict(utc=stamp,status='PRIVATE_NATIVE_FOOD_WAVE_HUD_REPAIR_OPEN_ROSTER_WORK',parent_checkpoint='native-items-px',rom_sha256=EXPECTED,source_zip_sha256=sha(P/'source.zip'),source_files=packet['source_files'],source_changes=changes,builds=packet['builds'],evidence_directory=str(D),goal_complete=False)
 (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 assert public=={n:sha(R/'build'/n)for n in names}and sha(guide)==gh
 used=sum(n for _,n,_ in inventory(R,skip_reparse=True));assert used<30_000_000_000
 checks={n:record(D/n)for n in ['food-hud-static-v3.json','food-static-v2.json','wave-static-v1.json','health-food-final-v3/results.json','kirby-copies-final-v3/results.json','food-entry-v3/results.json']+visuals}
 q=dict(passed=True,adopted=True,goal_complete=False,inventory_complete=False,utc=stamp,ROM_sha256=EXPECTED,parent_ROM_sha256=sha(parent),source_zip_sha256=manifest['source_zip_sha256'],source_files=1217,source_changes=changes,changed_ROM_bytes=19,changed_PRG_banks=[74,79],CHR_bytes_changed=0,old_qualified_symbols_fixed=54005,new_labels=1,checks=checks,captures=capture_checks,current_component_frames=frames,current_native_food_actors=44,current_copy_ability_mode_cases=28,current_cold_entries=37,unchanged_public_ROMs=public,guide_sha256=gh,ordinary_flag_off_hashes={k:packet['builds'][k]for k in ['mmc3','mmc5']},workspace_bytes_after=used,scope='Three bounded repairs: ground-wave initial phase, native Chip/Dale next-food progression, copied-enemy HUD origin. Two wave immediates preserve motion instruction cycles; Chip/Dale helper adds22cycles only at health collection; two HUD immediates add no sprites or CPU. Static execution proofs are explicitly parent-wave/combined hashes with exact remaining-byte relationships, plus current native ability/food/entry runs and full direct component captures. Source-only packet independently rebuilds exact candidate. Whole-roster routes, shortcuts, remaining item uses/SFX/fidelity/lag/music/mapper/guide work remain incomplete. No universal60Hz or exhaustive human all-frame review claim.')
 (QA/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(adopted=True,goal_complete=False,ROM_sha256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],workspace_bytes=used),indent=2))
if __name__=='__main__':main()
