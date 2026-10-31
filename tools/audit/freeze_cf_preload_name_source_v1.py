"""Freeze actual name fallback/selector repack, current66 admission unchanged."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/cf-cold-warm-palette-source-v1';O=R/'build/cf-preload-name-source-v1';J=O/'joint';D=R/'docs/qa/checkpoints/2026-10-31/cf-preload-name-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 assert not(O/'handoff.json').exists()and not D.exists();files={Path(__file__)}
 for p in[P/'handoff.json',R/'build/cf-name-fallback-factor-proposal-v2/proposal.json',O/'source-stage.json']:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('immutable input',f);files.add(Path(f))
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='38a6259ca3abacccc10b8adb3b256f94a72f90307d44fb5ed5afe15114c372cd'
 receipts=[];checks={}
 for n in['cf-preload-name-transport-controls-v1','cf-preload-name-caller-controls-v2','cf-preload-name-hook-isr-controls-v2','cf-preload-name-source-closure-v1','cf-preload-name-foreign-main-v1','cf-preload-name-menu-controls-v2','cf-preload-name-bowser-cold-v1','cf-preload-name-parser-controls-v1']:
  p=R/'build'/n/'controls.json';q=json.loads(p.read_text());assert q['passed'],p;files.add(p);checks[n]=q;receipts.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('exact control input',f);files.add(Path(f))
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o','.bin']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p;assert p.is_file(),p;files.add(p)
 files|=set(O.glob('*.json'))|{J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-stage.json']}
 tools={Path(__file__)}|set((R/'tools/audit').glob('cf_preload_name*.py'))|set((R/'tools/audit').glob('prepare_cf_preload_name*.py'))|set((R/'tools/audit').glob('measure_cf_name_fallback_factor*.py'))
 references=set((R/'tools/reference').glob('cf_name_fallback_factor_proposal*.s'));files|=tools|references
 patch=''.join(difflib.unified_diff((P/'joint/bowser/router.s').read_text().splitlines(True),(J/'bowser/router.s').read_text().splitlines(True),fromfile='ef2f/bowser/router.s',tofile='preload-name/bowser/router.s'));(O/'source.patch').write_text(patch,encoding='utf-8')
 closure=checks['cf-preload-name-source-closure-v1'];caller=checks['cf-preload-name-caller-controls-v2'];transport=checks['cf-preload-name-transport-controls-v1'];vectors=checks['cf-preload-name-hook-isr-controls-v2']
 proof=dict(source=True,passed=True,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,
  emitted_old_owned51=[19,31,1],private_symbols_relocated=closure['only_private_symbol_changes'],all_current66_publicPCs_fixed=True,actual_scoped_parent_symbols=closure['actual_scoped_parent_symbols'],sole_actual_importer=closure['sole_actual_BwCfSceneLoad_importer'],one_cold_import_operand=closure['one_actual_cold_import_operand_rebound'],changed_bytes=39,all_other_ROM_CHR_header_payloads_cookies_exact=True,no_new_span_state_NMI_P1_or_readiness=True,
  actual_whole_BW_CF_scene_pairs=432,warm_all64flags_cold_eightflags_each_six_identities=True,scene_CPU_delta=caller['scene_CPU_delta'],invalid_31_33_name18_native_queue_caller_pairs=512,
  all37rows_all64flags_BT_pairs=4736,unchanged_pairs=4672,intentional_invalid18_genuine_native_pairs=64,cookie_poison_cases=1024,foreign_raw_all64flags_15_18_19_reject_before_resolver=48576,accepted_owner_probes=768,
  real_transport_vectors=1024,real_new_helper_vectors=658,minimum_new_helper_ISR_SP=vectors['minimum_ISR_SP'],source_callback_AXYP_SP_orderedapp_4WRAM_rawmaps_33SMC_livepage1_exact=True,
  actual_legacy_Main=282,ordinary_Main_CPU_delta=[0,0],menu_identities=83,Start_masks=10240,Bowser_parser_Main=240,CF_future_ready_parser_classes=4,CF_actual_Main=128,CF_actual_pending_Start_blocks=4,explicit_frontend_identity_projection_only=True,
  source_controls=receipts,remaining=['Correct future readyCF preview and admission remain unimplemented; current menu pending gate blocks Start','P1 experimental branch is separate on ef2f and unadopted here; later surgical composition required','Corrected BTv7 cold/lifecycle/menu producer is separate, current BT stillpending','No native/install/campaign/audio completion claim'])
 save(O/'freeze-proof.json',proof)
 api=json.loads((P/'integration-api.json').read_text());api.update(candidate=stage['candidate'],parent=stage['parent'],source_stage=str(J/'source-stage.json'),actual_link_recipe=str(O/'final-link.json'),source_controls=receipts,remaining=proof['remaining'])
 api['true_exports']['BwCfSceneLoad']['address']='0xb2d0'
 api['name_fallback']='Unready31 or33 service18 resolves genuine ROM FmQueueName after actual full-cookie auth fails; native AXYP/queue returned.15CmFresh/19JnReset once remain; foreign owners rejected before resolver. Valid CF18 still source own names.'
 api['private_load_ABI']='The sole genuine BwScene caller already saves nativeAXYP.31B selector uses X/Y as target high/rawbank, worker accepts no caller parameters, outer scene restores actual nativeAXYP. BWconstructor15B byteexact, CF helper42B byteexact and C0 skips it.'
 save(O/'integration-api.json',api)
 (O/'HANDOFF.txt').write_text('''Source-qualified preload-name source child of frozen ef2f.

Candidate 38a6259ca3abacccc10b8adb3b256f94a72f90307d44fb5ed5afe15114c372cd.
Exactly39ROMbytes change. Existing A67 51B repacks as19B genuine15/18/19
fallback +31B private load selector +1EA. No new span/state/lease. All current66
public/stablePCs remain; two PRIVATE labels move: BwCfSceneLoad B2CB->B2D0,
Cf B2E1->B2DF. The sole real cold.o importer is genuinely reassembled and
only its target-low operand CB->D0 changes. B020 table/slot36/worker, existing
fallbackstart B2BD, familytail B2F0, BwScene and originalBWctor15B stayfixed.

Actual native caller already saves AXYP before the private selector. X/Y can
hold target high/rawbank; real cold/warm BW/CF callbacks preserve all outputs
after outer restoration. Cold helper42B, retire17B, allguard/loader/public
interfaces and own e82e P0/name/runtime payloads/cookies remain byteexact.
Invalid31/33 service18 calls true FmQueueName without any guest opcode.15/19
native fallback-once semantics remain. Every other raw owner is rejected by
the unchanged outer gate before fallback. Valid CF18 uses own source names.

Finite emitted-code checks pass:432 complete native scene pairs (all64flags
warm/eight cold flags for BWtwoforms+CFfourclasses),512 unready31/33 original
namequeue/caller pairs,4736BT37row/allflag outcomes,1024cookiepoisons,
48576foreignraw/allflag15/18/19rejects,768ownerprobes. Actual ordered native
writes,AXYP/SP,4WRAM,rawmaps,33SMC/liveupperpage1 exact. New coldscene cost
is+2..5CPU; unchanged BT callbacks0..6CPU due native fallback selector order.
1024realtransportvectors plus658 newhelper vectors(minISRSP AD) pass.
All80,253parent scoped symbols checked; only the two declared private moves.

282legacyMain pairs0CPUdelta,83menus/10240Startmasks,240BWparser/Main pass.
Four CF cohorts first prove realpending Start rejects, then explicitlyproject
only futurefrontend identity31 to real readyblock/ChkContinue/fullnative
parser/entrance/128Main. No guestRAM/Ready/cookie/physics preload; this is
NOT natural-ready admission. CF andBTremainpending; current66exact.

P1 experimental source stays separate on frozenef2f and needs later surgical
composition. CorrectedBTv7 producer is separate. FutureCFreadypreview and
rootnative stillneeded. No native launch/install/publication. All frozen
source/recipes/dependencies and retained failed fixtures are hash-bound.
''',encoding='utf-8')
 files|={O/n for n in['source.patch','freeze-proof.json','integration-api.json','HANDOFF.txt']}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.suffix.lower()=='.bin'and p.stat().st_size<=65536:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 out=dict(source=True,status='FROZEN_PENDING_CF_PRELOAD_NAME_AND_LOAD_SELECTOR',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',out)
 for f,h in out['bindings'].items():assert sha(f)==h,('postfreeze',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 D.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','source.patch','integration-api.json','freeze-proof.json','HANDOFF.txt']:shutil.copyfile(O/n,D/n)
 for row in receipts:
  p=Path(row['path']);q=json.loads(p.read_text());compact={k:v for k,v in q.items()if k not in['cohorts','checks','rows','vectors','bindings','scene','name','paths','menus']};compact.update(full_receipt=str(p),sha256=sha(p));save(D/(p.parent.name+'.json'),compact)
 save(D/'receipt.json',dict(source=True,candidate=out['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(D.iterdir())}))
 owned=tools|references|set(D.iterdir())|{D/'owned-files.txt'};(D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),candidate=out['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(D),receiptSHA256=sha(D/'receipt.json'))))
if __name__=='__main__':main()
