from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,zipfile
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-ship-lives-v25';P=D/'native-probes-qa-v2';receipt=R/'build/verification/mmc3-ships-current-v25/proof.json';assert not receipt.exists(),'One-shot tool adoption already completed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='09c5ced7680c303f07ff9ad4655e56300d63c99eab90b4dafcf61938d75fd45c';assert sha(O/'candidate.nes')==expected
parents={}
for name,count in [('cold-entries-v1',37),('native-routes-v1',4),('direct-v1',4)]:
 f=O/name/'proof.json';q=json.loads(f.read_text());assert q['passed']and q['complete']and q['ROM_sha256']==expected;assert len(q.get('runs',q.get('results',[])))==count;parents[name]=sha(f)
motion=list((O/'cold-entries-v1').glob('*/build/verification/completed-loop-motion.json'));assert len(motion)==37
for f in motion:
 q=json.loads(f.read_text());assert q['passed']and q['checks']>30 and q['max_world_step']<=8 and q['max_camera_step']<=4
visual={}
for name in ['vic','octopus','twinbee','pentarou']:
 for prefix in ['overview-','start-pole-']:
  f=O/'direct-v1'/(prefix+name+'-easy.png');assert f.exists();visual[f.relative_to(O).as_posix()]=sha(f)
packet=json.loads((P/'packet-current-v3/packet.json').read_text());catalog=packet['source_files'];assert len(catalog)==1220
assert all(sha(R/n)==h for n,h in catalog.items()),'Current root source catalog changed'
name='tools/mmc3_oversized/repairs.json';target=R/name;before=sha(target);assert before=='1ed109ed1c934bd45d2b28a024577f70de17cbed43bb57e2e7218a99af4c5539'
for n in ['tools/prepare_mmc3_oversized.py','tools/mmc3_current_repairs.py','tools/mmc3_oversized/mmc3-menu-previews.chr']:assert sha(O/n)==sha(R/n)
recipe=O/name;m=json.loads(recipe.read_text());m['expected_ROM_sha256']=expected;m['scope']='Qualified current MMC3 preparation: retained atlas/native cache/audio repairs plus scripted ship flagpole gate, separate existing5c/5d state pages, and tagged lives portrait OAM resolution.37cold entries and four independent all-PPU-frame ship1-1 replays pass; full other-family MMC3 campaigns/items/music/overload/fidelity remain separate.';recipe.write_text(json.dumps(m,indent=2))
backup=O/'root-before'/name;backup.parent.mkdir(parents=True,exist_ok=True);assert not backup.exists();shutil.copy2(target,backup)
public={n:sha(R/'build'/n)for n in ['smb-crossover-mmc3.nes','smb-crossover-mmc5.nes','smb-crossover-mmc3-oversized.nes','smb-crossover-mmc5-expanded.nes']}
occupied=sum(os.stat(Path(dp)/n,follow_symlinks=False).st_size for dp,dn,nn in os.walk(R,followlinks=False)for n in nn);growth=recipe.stat().st_size-target.stat().st_size;assert occupied+growth+25000<30_000_000_000
try:
 shutil.copy2(recipe,target);build=O/'canonical-build'
 with(O/'canonical-build.log').open('w')as log:p=subprocess.run([sys.executable,str(R/'tools/build_mmc3_oversized.py'),'--reference-rom',str(P/'candidate.nes'),'--output-dir',str(build)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(O/'canonical-build.log').read_text()[-3000:]
 rebuilt=build/'smb-crossover-mmc3-oversized.nes';assert sha(rebuilt)==expected,'Canonical root build differs from physically tested candidate'
 changed={n:dict(before=h,after=sha(R/n))for n,h in catalog.items()if sha(R/n)!=h};assert set(changed)=={name},changed
 assert all(sha(R/'build'/n)==h for n,h in public.items())
 # Freeze the complete updated catalog outside the capped workspace.
 packet_out=O/'source-packet-v1';packet_out.mkdir(exist_ok=False);updated={n:sha(R/n)for n in catalog};archive=packet_out/'source.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n,h in updated.items():z.write(R/n,n)
 with zipfile.ZipFile(archive)as z:assert len(z.infolist())==len(updated)and all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in updated.items())
 packet_report=dict(passed=True,source_files=updated,source_zip_sha256=sha(archive),MMC5_ROM_sha256=sha(P/'candidate.nes'),MMC3_ROM_sha256=expected,parent_packet_sha256=sha(P/'packet-current-v3/packet.json'),scope='Exact current1220-file game/build catalog; one MMC3 preparation recipe changed. MMC5 source and its exact-ROM receipts are unchanged.')
 (packet_out/'packet.json').write_text(json.dumps(packet_report,indent=2))
 proof=dict(passed=True,goal_complete=False,adopted_root_tools=True,public_release_installed=False,ROM_sha256=expected,MMC5_ROM_sha256=sha(P/'candidate.nes'),parents=parents,source_catalog_changes=changed,source_files=len(updated),source_packet=str(archive),source_packet_sha256=sha(archive),canonical_private_output=str(rebuilt),all_game_source_unchanged=True,public_four_ROMs_unchanged=True,workspace_bytes_before=occupied,recipe_byte_growth=growth,workspace_cap_bytes=30_000_000_000,sampled_visual_sheets=visual,visual_review_scope='Human overview samples and native startup/pole frames; not every-frame subjective/source-art certification. Octopus fixed lives portrait observed at native frames408/432/456; old five-frame snapshot can still be loading black.',scope='Source/build-tool adoption of qualified specific MMC3 ship state/flagpole/lives fixes.37cold selections with committed motion checks and four independent zero-death native1-1 all-PPU-frame replays pass. Full other-family campaigns/items/music/overload/source fidelity and hardware remain open.')
 receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text(json.dumps(proof,indent=2));checkpoint=R/'build/checkpoints/mmc3-ships-v25/checkpoint.json';checkpoint.parent.mkdir(parents=True,exist_ok=True);checkpoint.write_text(json.dumps(dict(ROM=str(rebuilt),ROM_sha256=expected,source_packet=str(archive),source_packet_sha256=sha(archive),adoption_proof=str(receipt)),indent=2));print(json.dumps(dict(passed=True,ROM_sha256=expected,source_files=len(updated),recipe_growth=growth,receipt=str(receipt))),flush=True)
except BaseException:
 shutil.copy2(backup,target)
 raise
