"""Freeze the bounded authentic Gimmick leaf; never claim shared/native admission."""
from pathlib import Path
import hashlib,json,shutil,sys
import gimmick_source_audit_v1 as G
R=G.R;O=R/'build/gimmick-component-v2';P=R/'build/pit-retold-host-v3'
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def bind(p):return G.bind(Path(p))
def main():
 assert not(O/'handoff.json').exists()
 assert bind(R/'build/gimmick-source-handoff-v1.json')['sha256']=='36aebf51909b65be5005ae600ea10ba94fb96cec8a1f9264501d160ac3ffdc2c'
 build=json.loads((O/'build-proof.json').read_text());assert build['candidate']==bind(O/'candidate.nes')['sha256']
 assert json.loads((O/'lease-closure.json').read_text())['status']=='PRIVATE_SOURCE_OWNER_LEASE_CLOSED'
 for n in ['kernel-controls.json','host-controls.json','caller-controls.json']:
  q=json.loads((O/n).read_text());b=q.get('candidate',q.get('actual_candidate'));assert b and b['sha256']==build['candidate'],n
 parent=json.loads((P/'build-proof.json').read_text());deps=[]
 for p,h in parent['actual_dependencies'].items():
  z=bind(p);assert z['sha256']==h,('Changed consumed parent input',p);deps.append(z)
 sources=sorted((R/'src').glob('gimmick*'));snap=O/'source';snap.mkdir(exist_ok=True)
 source_bind=[]
 for p in sources:
  q=snap/p.name;shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes();source_bind.append(bind(q))
 asset=O/'gimmick-source-v2.chr';shutil.copyfile(R/'chr/characters/gimmick-source-v2.chr',asset)
 b=scoped_load(O/'candidate.nes');api={}
 for n in ['GmNewGame','GmEnsure','GmScene','GmMovement','GmAfterTerrain','GmNmiClock','GmGraphics','GmDraw','GmPortrait','GmColors','GmWeapons','GmAdder','GmHead','GmFoot','GmSide','GmBox','GmInjury','GmDeathStart','GmPickup','GmHealth','GmFullPower','GmSync','GmRideStar']:
  s=b['syms'][n];g=b['segs'][s['seg']];a=address(b,n);bank=(int(g['ooffs'])-16)//8192
  at=int(g['ooffs'])+a-int(g['start'],0)
  api[n]=dict(physical_bank=bank,CPU=f'{a:04X}',first12=b['raw'][at:at+12].hex())
 negatives=[dict(name='Original private RAM draft',finding='132B exceeded approved128; generator rejected before link. Only actually used native fields allocated, final128.'),
  dict(name='Original ca65 draft',finding='Duplicate longbranch macro then branch-span failures; original first-assemble-error retained. No parent mutation.'),
  dict(name='Original inline inventory oracle',finding='Original8042 has four words, not three. Code0 empty,1heal,2star-kind1,3star-kind2; actual collector IDs10..12 subtract0F. Original first failed comparison retained; no old frozen report rewrite.'),
  dict(name='Original source flag contract',finding='Actual Type2 scripted status2 lost Z across native FarCallCommon (48 vs50). Frozen negative leaf/JSON retained. Actual A/P captured in owned2B and restored; strict current AXYP passes.'),
  dict(name='Initial host oracle',finding='CPU runner returns at entrySP FD, not FF; original host-first-failure retained. Legal blink early RTS needs sentinel-aware source runner.'),
  dict(name='Initial asset link',finding='Putting Gm CHR segment before earlier GB-Pit advanced shared ld65 cursor; first-link-error retained. Formal memory split now preserves both addresses.'),
  dict(name='Native UpdateScreen caller',finding='Direct UpdateScreen without genuine bank116 lease read wrong C bytes; caller-first-failure retained. Current test executes real SamusFreezeUpdateScreen gateway, not a service stub.'),
  dict(name='Support reading correction',finding='Source8369 does not snap Y. Draft snap was removed;882 actualFF13/accepted-body comparisons now preserve source positions, friction and ground/VY. Trail cutoff literal15HEX means21decimal.'),
  dict(name='Hand coding check',finding='An extra PLA in an unrun weapons draft was caught and removed before caller controls; no passing/native receipt assigned to that draft.')]
 (O/'negative-journal.json').write_text(json.dumps(negatives,indent=2)+'\n')
 note=R/'docs/qa/gimmick-component-source-2026-10-29.txt'
 note.write_text('''Gimmick private authentic leaf v2 — NOT shared/menu/native admission

Authority: supplied Japanese ROM ce2f8461…8c092, byte-authenticated existing
readable disassembly. Frozen v1 remains unchanged. Current component is a
normal source/object link over immutable ac126, not post-link ROM patching.
All64,065 pre-existing qualified symbols and all nonleased bytes are exact.
Four actual PRG spans and CHR816..819 only; no new shared RAM or globalflag.
Owner-exclusive128B is5C00..7F, first12 retained across own same-life scenes.
Constructor revokes Ready before clearing, publishes47 LAST. Raw26 admission
must occur BEFORE every private read; real menu/newgame MUST call NewGame
before trusting overlay Ready. Same-life scenes/life gains retain equipment;
death refills to earned capacity, original inventory retained.

AUTHENTIC CORE: original1/16 fractional hero arithmetic/variable jump/air
steering/friction; all3 star kinds, charge33/42, original signed half quirks,
bounce/scripted lifecycle, authentic star support/noYsnap/nohorizontalcarry,
seven B4 zero-velocity particles, four old history entries, original late
pose/protection/blink timing, all22 hero and66 star records, exact CHR8/12/13.
Host is already8x16: one original part consumes ONE OAM entry, not two.
Max sampled three-star record15 emits21 entries before body/particles; OAM
capacity/rotation is bounded and genuine hardware8-per-line is not bypassed.

EXPLICIT ADAPTATIONS: source room terrain queries -> real SMB block buffers,
native coins/brick/pipes/platform consumers; host viewport240rows instead191,
camera-relative long-world retirement; source star oneHP -> native100HP NPC
damage including existing immunity/flash/score behavior. It is not a port of
original Gimmick enemy AI/all bosses. Easy stomp is authored; Hard uses stars.
Mushroom increases/refills native capacity(initial2,max4); Flower earns
alternating native star kinds1/2 through actual inventory codes2/3, cap3.
Code0 is empty,code1 nativeheal, physical original item IDs10..12, not0F..11.
No auto-grant. FullPower is ONLY explicit user cheat endpoint.

PALETTE: original body0B/2A/30. Source palette1 is routed to nativeP2 with
approved darkbrown07 -> native16, white30/yellow27 retained. Shape and source
flip/priority exact. P0 queue writes ONLY3F11 visible triple; universal
backdrop/world/enemy palettes untouched. P2 native publisher remains owner.
All16 original palette bytes retained as reference metadata. This is one
shade quantization, NOT all-area original color equality. GmColors can decline
on busy/insufficient buffer; shared authoritative publisher must retain
invalidation/retry, respect Star palettes and actual transitions/overwrites.

EXACT SHARED CALL ORDER REQUIRED (next unit, not installed here):
 1 constructor before overlay access, reset old CHR overrides/slot ownership;
 2 genuine NMI calls GmNmiClock once, including lag/pause (not from Main);
 3 GmMovement once instead of generic movement; it integrates hero only;
 4 real native BG/coins/pipes/platforms with all7 Gm geometry probes;
 5 GmAfterTerrain once: sync accepted clamp/carry, source star support then
   source star tick/particles. Native camera once; no second physics step;
 6 GmWeapons is collision-only. GmGraphics once lateMain advances original
   pose/protection. GmDraw then emits source records/history/particles;
 7 real injury must pass actual overlap side0/1 to GmInjury, not oldfacing;
   true HP0 hands off GmDeathStart/native life engine; Star immunity upstream;
 8 actual physical collector calls GmPickup(0Mush/1Flower), checkedCF receipt;
   source original Up+B uses genuine three-slot special inventory;
 9 menu/lives portrait uses GmPortrait, no gameplay/clock/privateReady reads.

GmMovement/AfterTerrain/Graphics/Draw/Weapons preserve AXYP/SP/R0..7/5SMC and
true A/C maps. Incoming native FarCallCommon retains its real NZ-of-returnA
contract, not fictitious preservedNZ. Portrait inputsA=facing,R4/5=screenX,
R6=screenY; A/X/Y/R0..3 volatile, C/5SMC preserved. Adder returnsY0/C1; shared
player BG must intercept ALL head/feet/side points with Head/Foot/Side. Native
point geometry X8,5,11,5,5,11,11 / Y18,32,32,22,30,22,30. Body box is3x14px.
Health returnsA=current,X=capacity,C1. Helper value-output P/Y contracts are
not blanket outerAXYP claims. All28 foreign identities in controls leave
application/ZP/OAM/livepage1/33SMC/banks unchanged.

MEASURED: hero callback1607..1711CPU sampled; late callback1086CPU baseline;
star collision1189(empty)..3846(realGoomba hit), complete callback minimumSP172,
deepest actualIRQ minimum167, safely above protected page1/SMC. Source trail
sample1056..3771 vs port1801..5321, NOT free/lag-neutral. No Main/cadence/FPS
claim from primitive timing. No NES PPU/DMA timing, native pixels or waveform
qualification. NormalNMI clock/audio/mixer/DMC protocol remains OPEN.

NEXT: actual private raw26/menu25 shared routing, completeMain/lifecycle/
foreground+NMI/foreign/IRQ closure and native-ready gameplay pilot. Native
launches are ROOT-only. Keep source53px jump; qualify genuine star riding/
traversal instead of increasing jump to force1-1. Authentic Sunsoft5B music
arrangement is required separately; no stock/muted/relabelled audio claim.
No A63 common lease consumed; SMB2 B600..B800 remains its coordinator-owned.
''',newline='\n')
 own_tools=[R/'tools'/n for n in ['gimmick_leases_v2.py','gimmick_lease_closure_v2.py','prepare_gimmick_component_v2.py','prepare_gimmick_art_v2.py','build_gimmick_component_v2.py','gimmick_kernel_controls_v2.py','gimmick_host_controls_v2.py','gimmick_callers_v2.py','gimmick_freeze_v2.py']]
 outputs=[p for p in O.iterdir()if p.is_file()and p.name!='handoff.json']
 refs=deps+source_bind+[bind(asset),bind(note)]+[bind(p)for p in own_tools+outputs]
 # Full dependency closure includes actual consumed parent objects/compiler,
 # link config/debug and original/reference inputs used to generate the leaf.
 old=json.loads((R/'build/gimmick-source-handoff-v1.json').read_text())
 def visit(q):
  if isinstance(q,dict):
   if set(['path','sha256','bytes'])<=q.keys():
    p=Path(q['path']);z=bind(p);assert z['sha256']==q['sha256']and z['bytes']==q['bytes'];refs.append(z)
   else:
    for v in q.values():visit(v)
  elif isinstance(q,list):
   for v in q:visit(v)
 visit(old)
 for p in [P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P/'build-proof.json',P/'smb1base-mmc5-expanded.cfg',R/'build/kamikaze-mario-host-v4/c-full.o',P/'main.o',P/'skin.o',P/'gb.o',R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe',R/'tools/Windows/cc65/bin/cl65.exe',R/'tools/prepare_cv3_dmc_mirror.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']:refs.append(bind(p))
 refs={z['path']:z for z in refs}
 hand=dict(status='FROZEN_PRIVATE_COMPILED_LEAF_CPU_IRQ_PASS_NOT_SHARED_OR_NATIVE_READY',candidate=bind(O/'candidate.nes'),DBG=bind(O/'candidate.dbg'),LBL=bind(O/'candidate.lbl'),MAP=bind(O/'candidate.map'),source_snapshot=source_bind,API=api,
  measured_sizes=build['sizes'],RAM=dict(owner=26,start='5C00',end_exclusive='5C80',persistent12_within_active=True,new_global_marker=False),
  explicit_open=['shared raw26/menu25 admission','constructor/slot reuse/fullMain actual callers','real NMI clock and lag-input scheduling','authenticated5B-to-MMC5 music arrangement/voice allocation','actual shared SFX/mixer/DMC ownership','native gameplay/PPU/DMA/deadline/cadence/visual/audio/traversal'],
  reproducible_build='python tools/build_gimmick_component_v2.py --fixture --link --output build/gimmick-rebuild-review --source-dir build/gimmick-component-v2/source --chr-file build/gimmick-component-v2/gimmick-source-v2.chr --lease-proof build/gimmick-component-v2/lease-closure.json',
  owned_publication=[str(p.relative_to(R))for p in sources+own_tools+[R/'chr/characters/gimmick-source-v2.chr',note]],
  binding_count=len(refs),bindings=sorted(refs.values(),key=lambda z:z['path']))
 (O/'handoff.json').write_text(json.dumps(hand,indent=2)+'\n');print(json.dumps(dict(handoff=bind(O/'handoff.json'),bindings=len(refs),candidate=build['candidate'],clock=api['GmNmiClock'])))
if __name__=='__main__':main()
