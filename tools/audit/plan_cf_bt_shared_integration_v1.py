"""Concrete source-only CF/BT join plan; emits no assembly/cart mutation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
O=R/'build/cf-bt-shared-integration-plan-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists()
 sources=[R/'build/bowser-playable-jump-v1/handoff.json',
  R/'build/contra-force-guarded-runtime-qualified-v1/handoff.json',
  R/'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v2/handoff.json']
 bindings={};verified=0
 for p in sources:
  q=json.loads(p.read_text());bindings[str(p)]=sha(p)
  for f,h in q['bindings'].items():
   assert sha(f)==h,('immutable input binding',f);verified+=1
 inputs=[R/'build/contra-force-guarded-runtime-qualified-v1/integration-api.json',
  R/'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v2/row-and-cold-API.json',
  R/'build/bowser-playable-jump-v1/joint/union.s',
  R/'build/bowser-playable-jump-v1/joint/bowser/router.s',
  R/'build/bowser-playable-jump-v1/joint/bt/router.s',
  R/'build/bowser-playable-jump-v1/joint/bowser/cold.s',
  R/'build/bowser-playable-jump-v1/joint/src/new_roster_dispatch.s',
  R/'build/bowser-playable-jump-v1/joint/src/character_select.s',
  R/'build/bowser-playable-jump-v1/joint/src/full_roster_menu.s',Path(__file__)]
 bindings.update({str(p):sha(p)for p in inputs})
 q=dict(source_plan=True,implemented=False,native=False,installed=False,
  parent_candidate='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a',
  next_private_root='build/cf-bt-shared-transport-v1',
  immutable_inputs=[dict(path=str(p),sha256=sha(p))for p in sources],
  immediate_scope='Rebase genuine CF loader/guard/carrier and corrected BT producer on c663. Shared transport remains inert/pending for CF until real cold/graphics/retirement APIs exist. Preserve current66.',
  source_ownership=dict(common_router='claude_goku_maaa_review',CF_guard_loader_runtime_cold_API='claude_dk_review',BT_menu_lifecycle_cache_preview='claude_gimmick_review',native_install='root'),
  common_delta=dict(
   old='CMP27/JEQ HuExtendedBT; CMP33/JEQ HuExtendedBT =14B',
   new='CMP27/BEQ LocalBT; CMP31/BEQ LocalBT; CMP33/BNE NotBT; LocalBT:JMP HuExtendedBT; NotBT =15B',
   growth=1,funding='Existing2B pre-HuResolve padding; public suffix stays fixed.',
   raw_and_flags='Do not AND raw IDs. A remains the true selected raw value; ordinary fallthrough still exits finalCMP33 with the same flags. OriginalAPXY is saved by each11B service prologue.',
   only='Change existing GmOnlyCommon CMP32 immediate to31; GmNrIndex already routes31 rare with C1. Keep all36 eleven-byte prologues/publicPCs and genuine frame reuse.'),
  resolver_delta=dict(
   auth='Existing resolver farcall BtCheck becomes genuine imported CfOrBtCheck BF47/ROM69. Selected31 authenticates full16 C2 cookie/class in ROM before any A2 opcode; every other raw genuinely tails BtCheck ADC0/ROM93.',
   original_ABI='IncomingA=3*service. Resolver returns A=rawbank/C=valid+true targetSMC only. NativeAXYP lives on BtRouter stack and is restored before callback exactlyonce.',
   patch='Original12B BwResolveRAM: STAlo; JMP Tail; Finish:STAhi;TXA;SEC;RTS. Tail16B:LDA#A0;LDX#3;LDYSelected;CPY#31;BNEFinish;LDA#BE;DEX;BNEFinish.',
   funding='Exact16B tail after still-public BwStartFlags within owned A67 B22B..<B300. No publicPC movement or rawRAM tagOR80.',
   outputs=dict(raw27_33='A000+3*service/raw03',raw31='BE00+3*service/raw02'),
   rejection='Missing/wrong-family/wrong-class/corrupt full cookie returns Cclear before A2. Common clamps invalid services to original ROM slot36 reject.'),
  actual_cold_paths=dict(
   menu_current='MenuResolveCharacter -> BwMenuResolve -> FwMuxMenuResolve -> S2MenuResolve -> QwMenuResolve -> ArGenResolve; retirement must precede Selected publication.',
   Start='Slot30 class=(FmGroups>>3)&3, preserve exactly18. Corrected BT source FmStartRetireFlags retains native flags and current masks80slot31/20slot9/08slot26, Groups20slot23/18slot30; current66 Benj callbacks remain. Pending CF still cannot launch.',
   Fresh='Native Ic/Sunny/QwBoot precede service15. Unloaded CF15 must call genuine CmHostFresh exactlyonce without A2; valid warm hook semantics must be explicitly source-owned.',
   scene_current='Actual forcedblank InitScreen -> BwScene -> S2InitScreenPrepare -> QwSceneInit -> ArGenSceneInit -> FwSceneInit -> nativeMove exactlyonce, then selected27 owned load.',
   scene_CF_required='At selected31 only, after genuine existing scene chain: retire all old C2/RAM3 owners, checkpoint X5PublishChr, call147B+302B CF loader under busy/forcedblank/negativeNmiDisable, then externally authenticated constructor15 onlyonC1. No helper span assumed.',
   menu_preview='Raw31 and33 must be exceptions to ready>=28 DK/Arthur shortcut. CF ready menu explicitly retains original ROM FmDrawCfPreview; BT uses true native-other preparation+ROM17. Never execute unloaded A2 for preview.',
   CF_missing='Own current A2 rows1/3/6/7/8/9/17/18/20/21/22/23/26/27/29/30/31/32/33/35 decline. Genuine menu/lives/palette/name/status/world/nativeDrawAll adapters and constructor hook are still prerequisite work.',
   BT_cold='Corrected API: ROM17 always BtColdPortrait; ROM26 always BtColdColors->BtAcquire legalforcedblank. Cache3 declines. Valid cookie15/19 -> raw3 row; invalid -> genuine CmHostFresh/JnReset. ROM18 FmQueueName/32 HuNativeWorldPalette. Sourcejoin must implement these true imports.'),
  retirement_requirement=dict(
   demonstrated_gap='CF cookie in C2 authenticates A1+C2+A3. Existing BW/BT/FF replacement of RAM3 can leave stale valid CF C2 cookie; external guard alone cannot prove A3 still CF.',
   required_fix='CF owner supplies own-ROM CfRetire or equivalent existing-source barrier that clears validity before Selected publication/any foreignRAM3 write; class/life/newgame/warm/foreign transitions proven. Do not fabricate a grant from unallocated A69 tail.',
   CF_owner_action='Measure a factored helper within existing owned CF567B; no new span/global allocation.'),
  sequence=[
   'Parent reviews plan. No common hook written by this plan.',
   'Newprivate c663 source rebase of genuine three CF objects/config/source image and corrected immutable BT own source; validate every output before compiler invocation.',
   'One-byte-funded common selector, external guard import and exact16B target tail; retain CF pending and unchanged cold entry until owned prerequisites are qualified.',
   'Close owner retirement across CF/BW/BT/FF before claiming lifecycle-safe shared transport. Compose BT cold policies after genuine Start helper consumer closure; no presumed release in frozen parents.',
   'Qualify actual allrows/allflags external guard before A2, actual caller stack/AXYP/33SMC/maps and normal/lag/IRQ cuts; current66 menus/foreign/Main/Benj/Bowser scopes.',
   'When own CFcold adapters arrive, source-join exact native Fresh/Init/menu/lives/DrawAll once, then natural wholeparser/Main qualification before readiness/native request.'
  ],
  no_new_leases=True,no_download_install=True,verified_frozen_bindings=verified,bindings=bindings)
 O.mkdir(parents=True);(O/'plan.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(path=str(O/'plan.json'),sha256=sha(O/'plan.json'),verified_frozen_bindings=verified,source_mutations=False)))
if __name__=='__main__':main()
