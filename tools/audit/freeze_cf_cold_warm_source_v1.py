"""Freeze pending CF cold/warm source consumers without readiness/native."""
from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/cf-owner-retirement-v2';O=R/'build/cf-cold-warm-source-v3';J=O/'joint';D=R/'docs/qa/checkpoints/2026-10-31/cf-cold-warm-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--BT-controls',required=True,type=Path);a=ap.parse_args()
 assert not(O/'handoff.json').exists()and not D.exists()
 files={Path(__file__)};verified=0
 manifests=[P/'handoff.json',R/'build/contra-force-lifecycle-qualified-v1/handoff.json',O/'source-stage.json',R/'docs/qa/checkpoints/2026-10-31/contra-force-cold-warm-resources/root-review-and-reservations.json',R/'docs/qa/checkpoints/2026-10-31/contra-force-cold-warm-resources/root-extension-review-v2.json',R/'build/battletoads-shared-owner-gate-review-v1/review.json']
 for p in manifests:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('immutable input',f);files.add(Path(f));verified+=1
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='8f0a925be0f1845952583a28dac7b54dd716c35539cfd65a13df37a7f9cdb310'
 names=['cf-cold-warm-parser-controls-v2','cf-cold-warm-retirement-controls-v1','cf-cold-warm-hook-isr-controls-v2','cf-cold-warm-source-closure-v2','cf-cold-warm-foreign-main-v1','cf-cold-warm-menu-controls-v1','cf-cold-warm-bowser-cold-v1','contra-force-cold-warm-rebind-v1','contra-force-cold-warm-rebind-isr-v1']
 paths=[R/'build'/n/'controls.json'for n in names]+[a.BT_controls.resolve()]
 receipts=[];checks={}
 for p in paths:
  q=json.loads(p.read_text());assert q['passed'],p;checks[p.parent.name]=q;files.add(p);receipts.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('exact control input',f);files.add(Path(f))
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o','.bin']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p;assert p.is_file(),p;files.add(p)
 files|=set(O.glob('*.json'))|{J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-stage.json']}
 own_tools={Path(__file__)}|set((R/'tools/audit').glob('cf_cold_warm*.py'))|set((R/'tools/audit').glob('prepare_cf_cold_warm*.py'))|set((R/'tools/audit').glob('measure_cf_cold_existing_fit*.py'))
 own_tools={p for p in own_tools if 'palette_source'not in p.name}
 own_reference=set((R/'tools/reference').glob('cf_cold_warm_resource_proposal*.s'));files|=own_tools|own_reference
 negatives=[]
 for root in[R/'build'/n for n in['cf-cold-warm-source-v1','cf-cold-warm-source-v2','cf-cold-warm-parser-controls-v1','cf-cold-warm-hook-isr-controls-v1','cf-cold-warm-source-closure-v1','cf-cold-warm-resource-proposal-v2']]:
  for p in root.glob('*.json'):
   try:q=json.loads(p.read_text())
   except ValueError:continue
   if isinstance(q,dict)and(q.get('passed')is False or 'negative'in p.name):files.add(p);negatives.append(dict(path=str(p),sha256=sha(p),error=q.get('error','')))
 patch=[]
 for n in['entrypoint.s','src/full_roster_menu.s','src/cf_menu_body.inc','bowser/cold.s','bowser/router.s','bt/router.s','cf-loader.s','cf-guard.s','cf-carrier.s','cf-retire.s','private.cfg']:
  patch.extend(difflib.unified_diff((P/'joint'/n).read_text().splitlines(True),(J/n).read_text().splitlines(True),fromfile='f523/'+n,tofile='CF-cold-warm/'+n))
 patch.extend(difflib.unified_diff([],(J/'cf-cold-warm.s').read_text().splitlines(True),fromfile='/dev/null',tofile='CF-cold-warm/cf-cold-warm.s'))
 (O/'source.patch').write_text(''.join(patch),encoding='utf-8')
 closure=checks['cf-cold-warm-source-closure-v2'];vectors=checks['cf-cold-warm-hook-isr-controls-v2']
 proof=dict(source=True,passed=True,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,
  actual_current66_Main_pairs=282,ordinary_Main_CPU_delta=[0,0],menu_identities=83,Start_mask_cases=10240,Bowser_parser_Main=240,
  actual_CF_future_ready_block_parser_classes=4,CF_actual_Main=128,actual_pending_Start_rejections=4,explicit_frontend_identity_projection_only=True,no_guest_RAM_Ready_cookie_or_physics_preload=True,
  menu_retire_before_Selected=128,foreign_scene_retire_before_every_A3_write=12,warm_CF_scene_no_copy_or_validity_clear=4,global_clear_before_Selected=4,
  new_helper_real_vectors=vectors['real_vector_cases'],new_helper_minimum_ISR_SP=vectors['minimum_ISR_SP'],CF_own_joined_vectors=424,
  actual_scoped_parent_symbols=closure['actual_scoped_parent_symbols'],only_declared_internal_or_retired_symbols=closure['only_declared_internal_or_retired_symbols'],all_current66_publicPCs_fixed=True,
  original_51B_Start_mask_byteexact_at_menu_B5CF=True,original_BW_15B_constructor_byteexact=True,menu_used_granted=[359,400],BT_router_used_granted=[211,224],new_ROM_grants=[dict(bank=69,start='BFE1',end='BFF2',bytes=17),dict(bank=115,start='BFCB',end='BFF5',bytes=42)],
  changed_bytes=closure['changed_bytes'],exact_changed_envelopes=closure['exact_changed_envelopes'],all_other_header_ROM_CHR_images_cookies_exact=True,CF_payload_cookie_exact_141b=True,
  source_controls=receipts,remaining=['CF pending menu identity0; explicit future-ready-block parser fixture is not natural-ready admission','ROM-only name18 fallback before load still needed; ready CF preview branch and cold art/name presentation remain frontend work','P0/name/status/world own source e82e is a separate frozen next dependency, not adopted','P1 yellow-shot fairness/ownership remains unadopted; no palette/mailbox/NMI grant','Corrected BTv7 cold/menu/lifecycle producer remains separate; this source retains prior BT cache and pending gate','No native run, installation, campaign or audio completion claim'])
 save(O/'freeze-proof.json',proof);save(O/'retained-negatives.json',dict(negatives=negatives,scope='No product assertion relaxed. Source remains exact8f0a. Pending-menu identity0, native music pointer initialization and historical union-producer assumptions were corrected only in successor fixtures; original failures retained.'))
 api=dict(source=True,candidate=stage['candidate'],ready=66,CF_pending=True,BT_pending=True,
  real_chain={'menu':'MenuResolveCharacter -> CfRetire before Bw/Fw/S2/Qw/Ar/Fm/Cm Selected publication','scene':'InitScreen -> BwScene -> CfSceneRetireForeign -> S2InitScreenPrepare -> QwSceneInit -> ArGenSceneInit -> FwSceneInit/nativeMove, then BwCfSceneLoad for exactly27/31','foreign_scene':'Selected!=31 calls genuine CfRetire BEFORE any inner FW/BW A3 overwrite','CF_cold':'Selected31 -> pure CfOrBtCheck -> if invalid verified CfLoaderProposal -> B020 service15 -> pure ROM guard -> BE2D/raw02 -> CfHostSceneEnsure; C0 skips original BW constructor','CF_warm':'Selected31 retains full valid image; guarded SceneEnsure preserves source gear/HP, native player/life policy141b','unready_rows':'15 -> CmHostFresh;19 -> JnResetDispatch; others decline before A2; owner gate rejects foreign before these fallbacks','CF_reset19':'valid guard -> real JnResetDispatch once then general Ensure+area transient reset, no duplicate CmFresh'},
  true_exports={},
  ABI='B02036JSR row saves original nativeAXYP. Resolver A=3*service returns true target/rawbank/C. Guard preserves AXY/P except resultC/rawC/33SMC and executes no guest. CF BE00+3*service/raw02 requires full ROM auth BEFORE firstA2. Actual native callback outputs returned; genuineSFC publishes NZ from returnedA.',
  source_state='CF A1/A3 code+C2 state/router, full16class cookie DFE0; Ready=CurrentPlayer+1; last-life DDB8; unchanged141b policy. No new global/ZP/RAM lease.',
  source_stage=str(J/'source-stage.json'),actual_link_recipe=str(O/'final-link.json'),remaining=proof['remaining'])
 # Import once, outside the metadata loop: no stale absolute callback aliases.
 import sys
 sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
 from prepare_ff_current_component_v2 import qualified
 from check_tmnt_render_oa import address,location
 b=qualified(J/'candidate.nes')
 for n in['BtServiceVeneers','BtRouter','BtServiceUnavailable','BwBtResolve','BwResolveColdNative','BwCfSceneLoad','CfOrBtCheck','CfRetire','CfSceneRetireForeign','CfLoaderProposal','CfLoadIfCold','BwScene','FmStartIdentityFlags']:
  api['true_exports'][n]=dict(address=hex(address(b,n)),physical_ROM_bank=(location(b,n)-16)//8192,raw_ROM_bank=((location(b,n)-16)//8192)|128)
 api['CF_cache_veneer']=dict(address='BE00',execution_raw_PRG_bank=2,slot36='BE6C',full_ROM_guard_required_before_opcode=True)
 save(O/'integration-api.json',api)
 note='''Source-qualified pending CF cold/warm successor on frozen f523.

Candidate 8f0a925be0f1845952583a28dac7b54dd716c35539cfd65a13df37a7f9cdb310.
Installed/current66 readiness remains unchanged. CF and BT are pending.
Adopts exact CF lifecycle/presentation141b source payload, not the later
P0/name/status/world e82e packet. No new palette/mailbox/NMI authority.

Root-granted helpers use exactly ROM69 BFE1..<BFF2 (17B) and ROM115
BFCB..<BFF5 (42B). Current BT B020 router is196->211/224B, with13 left;
original table/slot36/worker entries stay fixed. The original byteexact51B
Start mask moves from A67 B2BD to menu-owned B5CF; real Start consumer is
rebound, no old import remains. Menu helper359/400 leaves41. Reclaimed A67
51B funds14B native fallback and37B selected load routing. Original BW
constructor15B is byteexact and runs only after genuine BwLoad succeeds.

Menu still retires CF before Selected publication. Foreign scenes retire
before the inner S2/Qw/Ar/Fw chain and BEFORE any FF/BW A3 write. Selected31
keeps valid warm code/state, uses genuine ROM full16/class auth, loads only
when invalid under original forcedblank prerequisites, then real B02015
re-authenticates before first A2 and calls guarded SceneEnsure. CF returns
C0 so the BW-only constructor is skipped. Invalid15/19 invoke real CmFresh/
JnReset once; other invalid rows decline. Valid19 invokes real JnReset once
then source Ensure and transient reset. Gear/HP warm/life/1up policy is the
exact CF-owner141b policy, no invented native status swapping.

Finite checks pass:282 current Main pairs0CPU delta;83 menus/10240 Start
masks;240 Bowser parser/Main;128 menu and12 foreign scene retirement-before-
write cases;4 warm scenes without copy/validityclear;4 global clear cases.
Four CF parser cohorts first observe real pending Start rejection, THEN
explicitly project only future frontend identity31 and enter actual native
ready block/ChkContinue, full InitializeArea/ScreenRoutines/parser/entrance,
128 actual Main. No guest RAM/cookie/Ready/physics is preloaded. This is
NOT a natural ready-menu/admission claim. Guard witnesses precede firstA2.
446 new helper/gate/fallback real vector cuts, minISRSP AD; own424 joined
CF vectors/full warm/life/reset/presentation checks also bind exact8f0a.

All80,242 parent scoped symbols checked: current66 publicPCs fixed; only
explicitly retired Start labels, menu helper end and private rejectionlabel
change. All header/other ROM/CHR/Quick/Ar/FF/BW images/cookies remain exact.
Actual consumed common object is frozen a7da union.o; historical consumer-18
name is not assumed. Full private output guards, real objects/importers and
source dependencies are archived. All failed fixture/build attempts remain.

Next dependencies are P0/names/world source and authentic P1 fairness,
real pre-load ROM name routing, final ready preview/constructor consumers,
then root-coordinated native. Corrected BTv7 producer is separate and not
silently admitted. No native run/install/download/publication by this lane.
'''
 (O/'HANDOFF.txt').write_text(note,encoding='utf-8');files|={O/n for n in['source.patch','freeze-proof.json','retained-negatives.json','integration-api.json','HANDOFF.txt']}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.suffix.lower()=='.bin'and p.stat().st_size<=65536:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 out=dict(source=True,status='FROZEN_SOURCE_CPU_QUALIFIED_PENDING_CF_COLD_WARM',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',out)
 for f,h in out['bindings'].items():assert sha(f)==h,('post-freeze binding',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 D.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','HANDOFF.txt','source.patch','freeze-proof.json','retained-negatives.json','integration-api.json']:shutil.copyfile(O/n,D/n)
 for row in receipts:
  p=Path(row['path']);q=json.loads(p.read_text());q={k:v for k,v in q.items()if k not in['ABI','vectors','rows','checks','menus','scene','menu','global_init','direct_BT_contract','cohorts','bindings','foreign_scene','warm_scene','paths']};q.update(full_receipt=str(p),sha256=sha(p));save(D/(p.parent.name+'.json'),q)
 save(D/'receipt.json',dict(source=True,candidate=out['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(D.iterdir())}))
 owned=own_tools|own_reference|set(D.iterdir())|{D/'owned-files.txt'};(D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),candidate=out['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(D),receiptSHA256=sha(D/'receipt.json'))))
if __name__=='__main__':main()
