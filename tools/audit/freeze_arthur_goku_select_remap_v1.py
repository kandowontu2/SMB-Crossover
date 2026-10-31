"""Freeze the source-only remap dependency with inherited SMB2 palette hold."""
from pathlib import Path
import json,re,zipfile
import prepare_functional_roster_visuals58_v1 as B
R=B.R;O=R/'build/arthur-goku-select-remap-v3';J=O/'joint';P=R/'build/functional-roster-coherent62-v4'
C=R/'docs/qa/checkpoints/2026-10-30/arthur-goku-select-source'

def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 parent=json.loads(B.read(P/'handoff.json'));B.bound(parent)
 controls=[O/'menu-controls-v4.json',O/'isr-controls.json',O/'preview-compaction-controls.json']
 for p in controls:
  d=json.loads(B.read(p));assert d['passed'];B.bound(d)
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
 assert stage['candidate']=='40bce248c22f29c0cfb4f7e15be731a08c99e743e177dc8e838f2719cd568f0d'
 # Exact currentMain transitive source dependencies and all actual linker
 # object inputs are read-only bound. No inherited command is replayed.
 deps=set();main=json.loads(B.read(O/'main-build.json'))['command']
 for flag in['--create-full-dep','--create-dep']:
  if flag in main:
   dep=Path(main[main.index(flag)+1]);deps.add(dep)
   first=B.read(dep).split(':\t',1)[1].splitlines()[0]
   for token in re.split(r'(?<!\\)\s+',first):
    if token:
     p=Path(token.replace('\\ ',' '));p=(R/p).resolve()if not p.is_absolute()else p.resolve();assert p.is_file(),str(p);deps.add(p)
 link=json.loads(B.read(O/'final-link.json'))['command'];deps.update(Path(v)for v in link if v.endswith('.o'));deps.add(J/'private.cfg')
 B.write(O/'source-closure-current.json',json.dumps(dict(passed=True,candidate=stage['candidate'],recipe_logs=['main-build.json','final-link.json'],bindings={str(p.resolve()):B.sha(p)for p in sorted(deps)}),indent=2)+'\n')
 note='''# Arthur/Goku Select remap source dependency

Source40bce248c22f29c0cfb4f7e15be731a08c99e743e177dc8e838f2719cd568f0d
is a NEW genuineMain successor of frozen62 source408acae2. No native run,
Downloads install, canonical source mutation or new resource lease occurred.

Arthur stays default menu31/raw32. Select toggles existingFmAlts.bit7 and
resolves Goku raw24 at that same cell. AnotherSelect returnsArthur. Goku's
original source physics/contact/render/name/portrait/audio modules are
unchanged. This preserves the current audio route, not a new completed
original-game music claim. Start retains only80 on31 or20 on9, clears every
other alternate bit and FmGroups, preserving flags/X/Y contract.

Freed menu23 is futureBattletoads raw33, permanentlypending. The actual
pending guard prevents every native constructor/table callback for33.
Its generic *BATTLETOADS name and blankoriginalzero pattern are truthful
placeholders, not Rash/Zitz art or functional admission. Root/S2 lane has
authentic donor assets separately; these are NOT joined or leased here.
All original80 individuals remain reachable;62 are ready. There is one
additional genericpending family placeholder (81UIprofiles), not an82-
identity/Rash+Zitz implementation claim. No navigation cell was added.

NrMenuCharacter retains its original4B entry viaJMP/NOP. The new17B helper
uses only the root-approved existing124:ADEE..<AE00 gate-owned tail, after
the genuine unreferencedKmCycleEnd marker. Its exact18FF-byte preimage,
originalNEW_ROSTER_GATE sizeDEE, hardAE00sourceassert and nextRogueAux
AE00consumer are bound; the pad is now explicit, with1FFbyte remaining.
The original marker and all checked public entries remain fixed.

ExistingFULL_ROSTER_MENU has no added span: removing trulydead25/27 tests,
equivalentSelect logic and26B coordinate-table compaction preserves all
publicFm entryPCs. Old2Bslack plus26B pays the28B Start worker. Existing
21B Start block becomes18B genuinefarcall plus3pad; every laterPROTO_MENU
PC remains fixed. SparsepreviewX/Y tables become exactASL/ADC source,
not rescaledpixels. Actual2048 comparisons match full64OAM/palette/CHR,
all64flags on32 unchangedindices; pendingBT9 is intentionallyblank.

Actual controls:80 existing profiles/name packets and160Start/A boundaries
preserved (Goku's intentionalX23->31 recorded);6144 real resolver flag
cases;16256 Start policy cases including all256bytes/every64liveflags;
4992 completeforeignSelectcaller cases exactAXYP/ZP/VRAM/variants; actual
Ar->Goku->Ar coloredportrait calls; both genuineStart/Fresh paths execute
Ic/Sunny/QwBoot once and exactlytheir own ArGenConstruct orDpAdmissionFresh.
1196 actualnormal/lagNMI/unmaskedIRQ cuts preserve33SMC/liveAXYP/SP,
staticpage1/maps/WRAM and foreground continuation at all reachednewhelpers,
coordinate instructions andmapper/SMC seams. No native cadenceclaim.

Retained negatives: guardv1 stopped beforecopy because it classified the
unreferencedKmCycleEnd marker aspayload; v2assembler rejectednonconstant
padding expressions, so v3 usesexactconstantpads withlinkedsizeguards.
Controlv1 expectedoldGokuX23 instead ofnew31; v2 compared rawrelocated
FmNames R2/R3 scratch address; v3's literal-only commandparser faulted on
a native streamformat. Finalv4 normalizes ONLY the exactsame linkedname
pointer, asserts everyotherZP byte and full84BVRAM region, allactualname
packets andAXYP strict. Source/cart was neverchanged for those fixtures.

PUBLICATION HOLD: root's genuine408a SMB2 nativeframes have blackoverworld
sky from fullP0header3F10 aliasing3F00. This inherited failure is not fixed
or hidden here. Rebase root/DK's frozen sourcepalette+eye repair before
publication or finalnativepreparation. Frozen408a/997bindings stayexact.
'''
 B.write(O/'HANDOFF.md',note)
 tools=[R/'tools/audit'/n for n in['prepare_arthur_goku_select_remap_v1.py','prepare_arthur_goku_select_remap_v2.py','prepare_arthur_goku_select_remap_v3.py','arthur_goku_select_remap_controls_v1.py','arthur_goku_select_remap_controls_v2.py','arthur_goku_select_remap_controls_v3.py','arthur_goku_select_remap_controls_v4.py','arthur_goku_select_remap_isr_v1.py','arthur_goku_menu_compaction_controls_v1.py','freeze_arthur_goku_select_remap_v1.py']]
 files=deps|set(tools)|{P/'handoff.json'}|set(p for p in O.glob('*')if p.is_file())
 files.update(p for p in(R/'build/arthur-goku-select-remap-v2').glob('*.json')if p.is_file())
 archive=O/'source-only.zip';members=[]
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix in['.py','.s','.inc','.cfg','.json','.md','.patch','.d','.dep']and p.is_relative_to(R):rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 files.update(J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','ram3.bin','code.bin','data.bin','menu.rle'])
 d=dict(status='FROZEN_SOURCE_REMAP_INHERITED_SMB2_PALETTE_HOLD',candidate=stage['candidate'],parent=parent['candidate'],native=False,installed=False,publication_allowed=False,ready=62,existing_individual_profiles_preserved=80,generic_pending_BT_profiles=1,Arthur=dict(menu=31,raw=32),Goku=dict(menu=31,raw=24,FmAlts=128),Battletoads=dict(menu=23,raw=33,pending=True,authentic_art_joined=False),source_members=len(members),bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n');C.mkdir(parents=True)
 for p in[O/'HANDOFF.md',O/'source-stage.json',O/'source.patch',O/'menu-controls-v4.json',O/'isr-controls.json',O/'preview-compaction-controls.json']:B.write(C/p.name,B.read(p))
 receipt=dict(status=d['status'],candidate=d['candidate'],native=False,installed=False,handoff=dict(path=str(O/'handoff.json'),sha256=B.sha(O/'handoff.json')),bindings={str(p.resolve()):B.sha(p)for p in sorted(C.iterdir())if p.is_file()})
 B.write(C/'receipt.json',json.dumps(receipt,indent=2)+'\n')
 owned=[p.relative_to(R).as_posix()for p in tools]+[p.relative_to(R).as_posix()for p in sorted(C.iterdir())if p.is_file()];B.write(O/'owned-files.txt','\n'.join(owned)+'\n')
 print(json.dumps(dict(handoff_sha256=B.sha(O/'handoff.json'),candidate=d['candidate'],bindings=len(d['bindings']),archive_members=len(members),archive_bytes=archive.stat().st_size,checkpoint_sha256=B.sha(C/'receipt.json'),status=d['status'])))

if __name__=='__main__':main()
