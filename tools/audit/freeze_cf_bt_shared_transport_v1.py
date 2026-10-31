"""Freeze current66 inert authenticated CF transport; no cold/readiness claim."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/bowser-playable-jump-v1';O=R/'build/cf-bt-shared-transport-v3';J=O/'joint'
C=R/'docs/qa/checkpoints/2026-10-31/cf-bt-inert-shared-transport-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 manifests=[P/'handoff.json',R/'build/contra-force-guarded-runtime-qualified-v1/handoff.json',R/'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v2/handoff.json',R/'build/cf-bt-current66-carrier-v1/source-stage.json',O/'source-stage.json']
 files={Path(__file__)};checked=0
 for p in manifests:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('frozen input',f);files.add(Path(f));checked+=1
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='a7da1094265701d69fc52588f495eddb09e3c1ff7d76e55e62f5bdfdf45d501d'
 controls=[]
 names=['cf-bt-shared-endpoints-v1','cf-bt-shared-router-controls-v1','cf-bt-shared-foreign-main-v1','cf-bt-shared-menu-controls-v1','cf-bt-shared-bowser-cold-v1','contra-force-shared-transport-controls-v1','contra-force-shared-transport-isr-controls-v3']
 for n in names:
  p=R/'build'/n/'controls.json';q=json.loads(p.read_text());assert q['passed'],p
  files.add(p);controls.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('actual joined control binding',f);files.add(Path(f))
 # Actual source/input closure of this cart and every new object.
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p
   assert p.is_file(),p;files.add(p)
 files|={p for p in O.glob('*.json')}
 files|={p for p in(R/'build/cf-bt-current66-carrier-v1').glob('*.json')}
 files|={J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin','cf-stream.bin','cf-cookie.bin','source-stage.json']}
 own_tools=set((R/'tools/audit').glob('*cf_bt_shared*.py'))|{Path(__file__)}
 files|=own_tools|set((R/'build/cf-bt-builder-v1').glob('*.py'))
 files.add(R/'build/cf-bt-shared-integration-plan-v1/plan.json')
 negatives=[]
 for root in[R/'build/cf-bt-shared-transport-v1',R/'build/cf-bt-shared-transport-v2',R/'build/contra-force-shared-transport-isr-controls-v1',R/'build/contra-force-shared-transport-isr-controls-v2']:
  for p in root.glob('*.json'):
   try:q=json.loads(p.read_text())
   except ValueError:continue
   if isinstance(q,dict)and q.get('passed')is False:
    files.add(p);negatives.append(dict(path=str(p),sha256=sha(p),error=q.get('error',q.get('failure',''))))
 witness=R/'build/contra-force-shared-transport-input-witness-v1/controls.json'
 # The exact witness path is recovered from the joined-v3 manifest, rather
 # than guessing its name or fabricating an input oracle.
 cfv=json.loads((R/'build/contra-force-shared-transport-isr-controls-v3/controls.json').read_text())
 for f,h in cfv['bindings'].items():
  if 'input' in f and Path(f).suffix=='.json':witness=Path(f)
 save(O/'retained-negatives.json',dict(negatives=negatives,
  preparation='v1 assumed an inherited union command had --create-full-dep. v2 linked correctly but post-check guessed a private finish address. v3 adds an actual dependency output and derives finish from parent BwResolveRAM+6=B282. Frozen outputs untouched.',
  normal_input_handoff='Retained joined-v2 d71aa3b7: real normalNMI polls fixture4016=0, changing manuallyseeded SavedJoypadBits1 to0 before source read. ImmediateRTI CPU/33SMC/page1/maps were exact. Passing joined-v3 uses explicit stablezero normal/paused and heldRight lag/IRQ, with no input restoration or source normalization. No serial-heldRight/naturalMain claim.'))
 patch=[]
 for n in['union.s','src/new_roster_dispatch.s','bowser/router.s']:
  patch.extend(difflib.unified_diff((P/'joint'/n).read_text().splitlines(True),(J/n).read_text().splitlines(True),fromfile='installed-c663/'+n,tofile='inert-cf-bt/'+n))
 (O/'source.patch').write_text(''.join(patch),encoding='utf-8')
 save(O/'freeze-proof.json',dict(source=True,passed=True,native=False,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_pending=True,BT_pending=True,
  original36x11B_prologues_and_publicPCs_exact=True,one_byte_A79_growth_within_existing2Bpad=True,one_byte_padding_remains=True,
  own16B_A67_tail=True,ungranted_A69_tail_untouched=True,raw31_target='BE00+3Y/raw02 after genuine imported ROM69:BF47 full16/class auth',
  BW_BT_target='A000+3Y/raw03',all_other_header_CHR_payloads_cookies_preserved=True,
  actual_public_endpoint_pairs=9216+18576+40248,actual_CF_public_invalid_cases=2716,actual_BT_callback_pairs=4736,full16poison_flags=1024,pure27_33_targets=18432,actual_BT_joined_vectors=348,
  actual_CF_shared_source_pairs=1536,actual_CF_poison_foreign_first_opcode_rejections=84,actual_CF_joined_vectors=360,min_CF_ISR_SP=176,
  actual_foreign_Main=282,foreign_Main_CPU_delta=[0,6],actual_menu_identities=83,Start_flag_cases=10240,actual_Bowser_parser_Main=240,
  source_controls=controls,
  missing=['CF natural cold/menu/lives/name/palette/nativeDrawAll integrations','CF invalidation before every foreign A3/C2 replacement and selected publication','BTv7 cold/menu/lifecycle producer not adopted in this first join','No CF/BT readiness/native/install'],
  future_dependencies=['Corrected BT immutable bc5a4a7e','CF retire01a85af9 and internal checkpointloader60a5 are separate later source leaves, not adopted here']))
 save(O/'verified-source-stage.json',dict(stage,status='SOURCE_CPU_QUALIFIED_INERT_CF_BT_SHARED_TRANSPORT',source_controls_pass=True,publication_allowed=False))
 note='''Current66 INERT shared CF/BT source join, exact a7da1094 on installedc663.

Raw31 reaches the existing genuine ROM87:B020 table, then source resolver
calls imported ROM69:BF47 CfOrBtCheck before ANY A2opcode. Full16/class valid
returns BE00+3Y/raw02;27/33 remain A000+3Y/raw03. Original nativeAXYP stays on
the actualB020 saved stack and returns from the genuine callback. No|80RAM
tag or executable numeric alias is invented. All36original11B prologues and
publicPCs stay exact. Three local comparisons/share-one-JMP spend1 of2owned
A79 padbytes;16B ownA67tail is exact. RemainingA69tail is untouched.

9216 true-table/allflag pairs,18576 allraw/Quickalt pairs,40248Onlyforeign
pairs and2716CFpublic/reject cases pass.4736 genuineBTcallback/allflags,
1024all16poison flags,18432pure27/33targets and348joinedvectors pass. CFowner
independently proves1536 actualB020->guard->A2worker pairs,84poison/foreign
first-opcode rejections and4real loader->constructor->16movement cohorts.
360newjoinedCFvectors preserve CPU/33SMC/livepage1/maps/sourcecontinuation,
minimumISRSP B0. Retained normalNMInegative was real native input polling:
fixture4016=0 replaced manuallyseededRight1 before workerread. Passingproof
uses stablezero for normal/pausedNMI and heldRight for lag/IRQ. No input is
restored after ISR. No physical serial-heldRight/naturalMain claim.

Current66 menus/readiness stay exact:83 identities/10240Startflag cases.
282actualforeignMain pairs preserve state/OAM/maps/APXY with0..6CPUadded.
Both Bowser forms complete native parser plus120Main each on this exactcart.
CurrentBenj callbacks/cycle/Peachconstants and BW/FF/Quick/Ar images remain.

CF andBT STILLPENDING. CF coldstartup, lives/palette/name/default services
and nativeDrawAll adapters are incomplete. CF C2cookie authenticates all3
banks; every foreignA3overwrite must invalidate it before write/publication.
CfRetire/internalcheckpointloader are later qualified own leaves, NOT part
of this cart. Corrected BTv7API is bound as a future dependency; its menu,
cold acquire/lifecycle andnewcache are NOT silently integrated. This source
join is authentication/transport foundation, not playable admission. No
native run or Downloads modification. ExistingFF419/WIP issues unchanged.

Actual producer recipes are build/cf-bt-shared-transport-v3/*build.json and
final-link.json. Carrier rebase uses the bound generated source recipe in
build/cf-bt-builder-v1, which reproduces c663 first. Every output/dep/cfg side
file was validated beneath its new private root before compiler execution.
Only source/own generated guest stream goes in the archive, not fullROMs.
'''
 (O/'HANDOFF.txt').write_text(note,encoding='utf-8')
 files|={O/n for n in['HANDOFF.txt','source.patch','freeze-proof.json','retained-negatives.json','verified-source-stage.json']}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.name in['cookie.bin','ff-cookie.bin','cf-cookie.bin']or p==J/'cf-stream.bin':
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 q=dict(source=True,status='FROZEN_SOURCE_CPU_QUALIFIED_INERT_CF_BT_SHARED_TRANSPORT',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',q)
 for f,h in q['bindings'].items():assert sha(f)==h,('post-freeze binding',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 C.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','HANDOFF.txt','source.patch','freeze-proof.json','retained-negatives.json']:shutil.copyfile(O/n,C/n)
 for item in controls:
  p=Path(item['path']);r=json.loads(p.read_text());r={k:v for k,v in r.items()if k not in['rows','vectors','checks','cohorts','menus','bindings']}
  r.update(full_receipt=str(p),sha256=sha(p));save(C/(p.parent.name+'.json'),r)
 save(C/'receipt.json',dict(source=True,candidate=q['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(C.iterdir())}))
 owned=own_tools|set((R/'build/cf-bt-builder-v1').glob('*.py'))|set(C.iterdir())
 # Generated build recipes remain build artifacts; the replayable script is
 # inside the archive. Root only stages actual tools + compact checkpoint.
 owned={p for p in owned if not p.is_relative_to(R/'build')}
 owned.add(C/'owned-files.txt');(C/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=q['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(C),receipt_sha256=sha(C/'receipt.json'))))
if __name__=='__main__':main()
