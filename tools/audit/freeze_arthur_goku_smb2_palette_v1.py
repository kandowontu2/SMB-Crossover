"""Canonical combined source handoff and replayable Git checkpoint archive."""
from pathlib import Path
import json,re,shutil,zipfile,hashlib
import prepare_functional_roster_visuals58_v1 as B
R=B.R;O=R/'build/arthur-goku-smb2-palette-v1';J=O/'joint';P=R/'build/arthur-goku-select-remap-v3';S=R/'build/smb2-eye-sky-v3'
C=R/'docs/qa/checkpoints/2026-10-30/arthur-goku-smb2-native-palette-source'

def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 roots=[P/'handoff.json',S/'handoff.json'];controls=[O/'menu-controls.json',R/'build/ff-remap-palette-combined-controls-v1/controls.json',R/'build/smb2-eye-sky-combined-controls-v1/controls.json']
 for p in roots:B.bound(json.loads(B.read(p)))
 for p in controls:
  d=json.loads(B.read(p));assert d['passed'],str(p);B.bound(d)
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage);assert stage['source']is True
 assert B.sha(J/'candidate.nes')==stage['candidate']=='37210891ffbf79373bf3390d16ead891b0e8f43408603a07273f12297a36121a'
 assert B.read(J/'source-stage.json')==B.read(O/'source-stage.json')
 deps=set()
 for name in['component-build','asset-build']:
  p=O/(name+'.json');c=json.loads(B.read(p))['command'];deps.add(p)
  for flag in['--create-full-dep','--create-dep']:
   if flag in c:
    dep=Path(c[c.index(flag)+1]);deps.add(dep);first=B.read(dep).split(':\t',1)[1].splitlines()[0]
    for token in re.split(r'(?<!\\)\s+',first):
     if token:
      q=Path(token.replace('\\ ',' '));q=(R/q).resolve()if not q.is_absolute()else q.resolve();assert q.is_file(),str(q);deps.add(q)
  deps.add(Path(c[c.index('-o')+1]))
 link=json.loads(B.read(O/'final-link.json'))['command'];deps.update(Path(p)for p in link if p.endswith('.o'));deps.add(J/'private.cfg')
 for rel in['smb2/smb2_roster_palette_v2.s','smb2/smb2_roster_main_v2.s','smb2/smb2_roster_art.inc','eye-red.chr']:assert(J/rel).resolve()in deps,('actualincludeprecedence',rel)
 deps.update(p for p in J.rglob('*')if p.is_file()and p.suffix in['.s','.inc','.cfg'])
 closure=dict(passed=True,source=True,candidate=stage['candidate'],actual_current_producer_recipes=['component-build.json','asset-build.json','final-link.json'],Main_and_other_objects_read_only_from_frozen_remap=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(deps)})
 B.write(O/'source-closure-current.json',json.dumps(closure,indent=2)+'\n')
 note='''# Combined62: Arthur/Goku Select + native SMB2 backdrop/red eyes

Canonical source:true candidate37210891ffbf79373bf3390d16ead891b0e8f43408603a07273f12297a36121a
is genuinely linked from frozen remap40bce and frozen BG/eye producerff49.
It is exactly40bce plus the205 authenticated source-leaf byte changes.
Binary deltas are verification only; no ROM patch produced this candidate.
All other bytes, prior publicPCs/header and Quick/Arthur/FF payloads/cookies
remain exact. No new lease, DKpound adoption, native run or install occurred.

CORRECTION TO THE FROZEN REMAP NOTE: the old fullP0header3F10 explanation
was an initial hypothesis, not the authoritative first wrong write. The
retained native negative was bulk native3F00=$0F without subsequent native
BackgroundColors restore. OldS2MainPalette already wrote3F11..13 only.
Frozenff49 now restores the genuine native BackgroundColorCtrl-or-AreaType
selection and exact8 BackgroundColors bytes, then appends original3body
shades. Its reviewed complete3F10 length4 packet restores native universal
color through real UpdateScreen aliasing. No custom world recoloring.

The single original eye quad remains one quad: original eye56 plane/index2
is losslessly moved to P2 index1, source NES$16 red. BodyP0 positions/art,
priority, fiveparts and max3body sprites/line remain exact; P1/P2/P3 world
roles remain unchanged. The retired zero-consumer own45B pointer gate
funds the native BG helper; palette74B public envelope and queue/Star/ACK
guards remain. CHR796..<808 producer retains12KB, changing only reviewed
eye-pattern bytes. No extra CHR/OAM/RAM/PRG allocation is used.

Arthur defaults menu31/raw32; Selectbit80 chooses originalGoku raw24;
anotherSelect returnsArthur. All80 prior individuals remain reachable,
62ready. Freed23 is raw33 generic *BATTLETOADS permanentlypending with
blankoriginalpattern, not fabricated Rash/Zitz or an82-identity claim.
Onegeneric pending family placeholder makes81 visiblemenu profiles.

Actual combined controls pass81 menu/name/ready states and162Start/A
boundaries, both genuinepostIc Ar/Goku Start constructors; FF4cold bodies,
4black lives and128Main TOTAL; S2 exactly96GetPlayerColors->normalNMI BG
cases plus8 naturalclass/rules selected/lives/fullparser/entrance cohorts
and64 controlledMain TOTAL. LivesBG$0F, enteredgroundBG$22, fourP0+oneP2
fivepart body and unchanged nativeP1/P2/P3 are observed. Parentfrozenremap
allflags/1196realISR and frozenff49 queue/pixel/82vector proofs remain
bound; no new exploratory fixture campaign was added after requiredpass.

Canonical joint/source-stage.json, candidate.nes/.dbg/.lbl, ram3.bin and
ff-cookie.bin are present for root's generic native binders. SourceZIP,
handoff and ownsource producers are copied into this Git checkpoint.
The archive includes original source, exact generatedeye-red.chr and
all current command/dependency metadata, not ROM/DBG/object binaries.
Original donor ROMs and ancestral source archives remain separately hash
bound, not silently republished. Top-level component/asset/final-link logs
are the current recipes; inherited copied joint logs are historical.

Exact combined native S2+FF and Arthur->Goku->Arthur smoke is pending root
review/one-run queue grants. No publication or native hardware success is
claimed here. Lag is disclosed and is not an unlock veto under current
user instructions. All1-1/allitems/music/fullcharacter completion remains
outside these short native-firstlook and targeted source claims.
'''
 B.write(O/'HANDOFF.md',note)
 tools=[R/'tools/audit'/n for n in['prepare_arthur_goku_smb2_palette_v1.py','arthur_goku_smb2_palette_menu_v1.py','ff_remap_palette_combined_controls_v1.py','freeze_arthur_goku_smb2_palette_v1.py','smb2_eye_sky_combined_controls_v1.py','smb2_eye_sky_controls_v1.py']]
 files=deps|set(roots)|set(controls)|set(tools)|set(p for p in O.glob('*')if p.is_file())|{J/'source-stage.json'}
 for p in controls:
  d=json.loads(B.read(p));files.update(Path(n)for n in d['bindings']if Path(n).suffix=='.py')
 files.update(J/n for n in['component.s','asset.s','eye-red.chr'])
 archive=O/'source-only.zip';members=[]
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.is_relative_to(R)and(p.suffix in['.py','.s','.inc','.cfg','.json','.md','.patch','.d','.dep']or p==J/'eye-red.chr'):
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 files.update(J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','ram3.bin','ff-cookie.bin','code.bin','data.bin'])
 d=dict(status='FROZEN_SOURCE_COMBINED62_REMAP_NATIVE_BG_RED_EYE_NATIVE_PENDING',source=True,candidate=stage['candidate'],joint=str(J.resolve()),source_stage=str((J/'source-stage.json').resolve()),native=False,installed=False,publication_allowed=False,ready=62,existing_individual_profiles=80,generic_pending_BT_profiles=1,visible_menu_profiles=81,FF_Main_TOTAL=128,S2_controlled_Main_TOTAL=64,source_archive_members=len(members),source_producer_BG205_disjoint_composition=True,no_new_resource_lease=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
 # Independent archive/member/hash verification before creating Git copies.
 B.bound(d)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for rel in z.namelist():assert hashlib.sha256(z.read(rel)).hexdigest()==B.sha(R/rel),rel
 review=dict(passed=True,source=True,candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),verified_bindings=len(d['bindings']),verified_archive_members=len(members),native=False,installed=False)
 B.write(O/'root-review-preflight.json',json.dumps(review,indent=2)+'\n')
 C.mkdir(parents=True)
 for p in[O/'handoff.json',O/'HANDOFF.md',O/'source-stage.json',O/'source.patch',O/'menu-controls.json',O/'source-closure-current.json',O/'root-review-preflight.json',archive]:shutil.copyfile(p,C/p.name)
 for rel in['smb2/smb2_roster_palette_v2.s','smb2/smb2_roster_main_v2.s','smb2/smb2_roster_art.inc','asset.s','eye-red.chr']:
  q=C/'source'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(J/rel,q)
 receipt=dict(status=d['status'],source=True,candidate=d['candidate'],native=False,installed=False,handoff=dict(path=str(O/'handoff.json'),sha256=B.sha(O/'handoff.json')),bindings={str(p.resolve()):B.sha(p)for p in sorted(C.rglob('*'))if p.is_file()})
 B.write(C/'receipt.json',json.dumps(receipt,indent=2)+'\n')
 owned=[p.relative_to(R).as_posix()for p in tools if p.name not in['smb2_eye_sky_combined_controls_v1.py','smb2_eye_sky_controls_v1.py']]+[p.relative_to(R).as_posix()for p in sorted(C.rglob('*'))if p.is_file()];B.write(O/'owned-files.txt','\n'.join(owned)+'\n')
 print(json.dumps(dict(candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),bindings=len(d['bindings']),ZIP_members=len(members),ZIP_bytes=archive.stat().st_size,checkpoint_sha256=B.sha(C/'receipt.json'),source=True,native=False)))

if __name__=='__main__':main()
