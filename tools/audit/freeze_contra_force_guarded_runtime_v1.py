"""Freeze the genuine, pending CF carrier/auth/runtime with precise cold gaps."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/contra-force-guarded-runtime-qualified-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROOTS=[
 'build/contra-force-guarded-cart-v2/source-stage.json',
 'build/contra-force-a2-router-v2/build-proof.json',
 'build/contra-force-host-boundaries-v5/build-proof.json',
 'build/contra-force-host-boundaries-controls-v3/controls.json',
 'build/contra-force-phase-cadence-controls-v1/controls.json',
 'build/contra-force-a2-router-controls-v3/controls.json',
 'build/contra-force-external-guard-controls-v2/controls.json',
 'build/contra-force-external-guard-isr-controls-v3/controls.json',
 'build/contra-force-bootstrap-qualified-v2/handoff.json',
 'docs/qa/checkpoints/2026-10-30/contra-force-source-kernel-resource-review/resource-grant.json',
 'docs/qa/checkpoints/2026-10-31/contra-force-loader-resources/root-review-and-reservations.json',
 'docs/qa/checkpoints/2026-10-31/contra-force-rom-guard-resources/root-review-and-reservations.json',
]
NEGATIVES=[
 'build/contra-force-host-boundaries-v1/negative.json',
 'build/contra-force-host-boundaries-controls-v1/controls.json',
 'build/contra-force-a2-router-controls-v1/controls.json',
 'build/contra-force-external-guard-isr-controls-v1/controls.json',
 'build/contra-force-external-guard-isr-controls-v2/controls.json',
]
def main():
 assert not O.exists();O.mkdir()
 bound={};seen=set()
 def add(p,expected=None):
  p=Path(p).resolve();h=sha(p)
  if expected:assert h==expected,('Frozen binding changed',str(p),expected,h)
  if str(p)in bound:assert bound[str(p)]==h
  bound[str(p)]=h
  if p in seen or p.suffix!='.json' or 'contra-force-'not in str(p):return
  seen.add(p);d=json.loads(p.read_text())
  if not isinstance(d,dict):return
  edges=d.get('bindings',{})
  assert isinstance(edges,dict),('Unexpected CF bindings schema',str(p))
  for q,v in edges.items():add(q,v)
 for p in ROOTS+NEGATIVES:add(R/p)
 add(__file__)
 stage=json.loads((R/ROOTS[0]).read_text())
 assert stage['candidate']=='c1159eff9e3d3caf80411be99a4c5b0fd19695c7517d3c74bb31cc0a44e056a6'
 assert stage['all_preexisting_symbol_PCs_exact']==79572
 for p in ROOTS[1:8]:assert json.loads((R/p).read_text())['passed'],p
 api=dict(status='SOURCE_CPU_QUALIFIED_AUTHENTICATION_AND_PARTIAL_RUNTIME_ONLY',
  identity=dict(raw=31,menu_slot=30,variants=4,variant='(FmGroups >> 3) & 3',start_mask='18'),
  guard=dict(source='tools/reference/contra_force_rom_guard_v1.s',cart_source='build/contra-force-guarded-cart-v2/joint/cf-guard.s',entry='CfOrBtCheck',physical_ROM=69,PC='BF47',bytes=118,
   input='A=3*service; arbitrary X/Y/P and current rawC',result='AXYP preserved except result C; A unchanged; all33SMC and rawA/C unchanged; no guest opcode/write',
   selected31='Full16 cookie versus retained A-ROM expected bytes; byte2 must equal current Groups18 class; validity A7, family1F, version01, exact12-byte payload SHA prefix',
   other='Genuine FarCallCommon tail to actual imported BtCheck ADC0/ROM93; no numeric shadow alias'),
  cookie=stage['cookie'],payload_sha256=stage['payload_sha256'],
  runtime=dict(entry='CfServiceVeneers',raw_A_tag='02 (never OR80)',PC='BE00',entries='36 genuine3-byte JMPs; service36 at BE6C CLC/RTS',
   ABI='Real SFC sets FarcallJmpTarget_SMC low=3*service. Original worker A/P/X/Y input and AXYP output; original rawC restored. Five private source transport bytes02EC..<02F1 are declared outputs. Stable A2 executes return while C is restored; C2 phase bridge restores originating A2 before RTS.',
   prerequisite='External ROM guard MUST authenticate BEFORE FIRST A2 opcode; loader success cannot be inferred from selected identity.',
   unavailable=json.loads((R/ROOTS[1]).read_text())['unimplemented_rows']),
  loader=dict(source='tools/reference/contra_force_loader_proposal_v1.s',cart_source='build/contra-force-guarded-cart-v2/joint/cf-loader.s',entry='CfLoaderProposal',A_ROM=115,PC='BF38',bytes_A=147,C_ROM=78,core_PC='CE68',bytes_C=302,
   preconditions=['Selected31','FamilyMainCommit bit0=1','OperMode1','forcedblank MirrorPPUMASK&18=0 and DisableScreenFlag!=0','NmiDisable negative','retire previous C2/RAM3 owners BEFORE overwrite','actual X5PublishChr12-window/upper0 checkpoint before copy'],
   result='24576B buffered2007 copy+readback; clear C2 and RAM3 cookies first, publish full16 C2 cookie A7 last; fullAXYP except C result, rawA/C/R0..3/reload/PPUCTRL/latch/scroll/BG11 restored. No5102/5103/5113 writes.'),
  actual_source_cart=dict(parent=stage['parent'],candidate=stage['candidate'],stage=ROOTS[0],builder='tools/audit/prepare_contra_force_guarded_cart_v2.py',
   own_ROM_sources=['joint/cf-loader.s','joint/cf-guard.s','joint/cf-carrier.s'],
   cfg='Source MEMORY splits exact A115 BF38..<BFCB, C78 CE68..<CF96, A69 BF47..<BFBD and CHR935..<969; preserve parent Roll/adjacent automatic owner starts. All outputs validated beneath newroot.',
   scope='Genuine9529 parent relink exact; 79572 old symbol PCs exact; source kernel separately assembled and embedded into carrier. No common/native lifecycle/frontend/readiness producer changed.'),
  cold_plan=[
   'Keep raw31 pending in inert common guard join. No construction may enter A2 on a missing or wrong-class cookie.',
   'ROM-only ready menu route must explicitly call genuine FmDrawCfPreview; current raw>=28 branch otherwise draws DK/Arthur. Keep original CF two-palette preview helper and BT/CF lease retirement source.',
   'Pre-load Fresh15 falls back to genuine native CmFresh. Actual forcedblank InitScreen must preserve current BwScene/S2/Qw/Ar/Fw/nativeMove chain exactly once, retire old guests, checkpoint native CHR, call CF loader, then guarded constructor15 only on C1.',
   'Warm source reset preserves native earned tier; class change requires exact new cookie and load. Reentry/alternate-player/death/area behavior still needs actual cold/wholeMain qualification.',
   'Lives must use authentic body through genuine late portrait/status context after native WriteGameText, independent of unready RAM. Name18/status30 and colors26/29/world32 need real source contracts.',
   'Native DrawAll world actor loop must run exactly once around CF source emitter. Current row2 own RenderAll is not a native DrawAll wrapper.',
   'Native body P0=[37,12,0F] plus exact source red16 mask on existing P2index1. Shot source role[20,38,16] requires faithful P1 acquisition/restore and whole-object fairness before such parts are admitted. Current palette-owned bit rejects unmatched objects; no scheduler is installed.'
  ])
 ap=O/'integration-api.json';ap.write_text(json.dumps(api,indent=2)+'\n');add(ap)
 sources=sorted(Path(p)for p in bound if Path(p).is_relative_to(R)and Path(p).suffix in['.s','.asm','.inc','.cfg','.dep','.py','.json','.chr'])
 archive=O/'source-only.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED)as z:
  for p in sources:z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None and len(z.namelist())==len(sources)
  for p in sources:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 assert archive.stat().st_size<50*1024*1024
 report=dict(passed=True,source=True,native=False,ready=False,installed=False,
  status='FROZEN_SOURCE_CPU_AUTH_AND_PARTIAL_NATIVE_BOUNDARIES_FRONTEND_PENDING',candidate=stage['candidate'],parent=stage['parent'],
  source_stage=ROOTS[0],integration_api=str(ap),API_sha256=sha(ap),
  evidence=dict(boundaries='320 real blockbuffer cases;1152 body/shot updates;40 native contacts;192 pickups',phase='12 real class/gear duplicate-shot negatives retained, new exact-step guard',
   router='2304 realSFC worker pairs, all36×64 flags; wrong-cookie/class/invalidservice rejects',guard='3072 direct CF cases;74 SFC cases;1024 poisonedcookie cases;20 arbitrary foreignC2;60 genuineBtCheck API comparisons;4 loader/construct/movement sequences',
   vectors='848 actual instruction normal/lagNMI and unmaskedIRQ cuts; genuineROM69/ROM93/SFC seams; no guest opcode/write before authentication'),
  retained_negatives=NEGATIVES,
  coverage_corrections=['Guard ISR v1 only112 resident-SFC cuts executed because it compared raw197/221 with physical69/93. Those112 positives remain valid; broad worker coverage withdrawn. V2/v3 corrected actualphysical848 cuts.',
   'Runtime source actor index53 had remained21 after shots; current source restores0 before each player step.',
   'Old duplicate row4/34 weapon dispatch advanced actual shotfields twice; new private02DE source-step stamp prevents repeat within source23 step.',
   'Old direct-vs-router fixture incorrectly compared distinct incomingC; each endpoint now proves restoration against its own input.'],
  actual_cart_hooks=False,open=api['cold_plan'],
  source_archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(sources),excludes='NES/object/debug/map/derivedpayload binaries; actual sources/commands/CHR assets retained'),
  bindings={**bound,str(archive.resolve()):sha(archive)})
 hp=O/'handoff.json';hp.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(path=str(hp),sha256=sha(hp),bindings=len(report['bindings']),archive=report['source_archive'],integration_api_sha256=sha(ap))),flush=True)
if __name__=='__main__':main()
