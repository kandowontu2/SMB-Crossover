"""Canonical full-source joint lives-fix handoff and Git checkpoint copy."""
from pathlib import Path
import argparse,json,re,shutil,zipfile,hashlib
import prepare_functional_roster_visuals58_v1 as B
R=B.R;O=R/'build/coherent62-lives-fixes-v1';J=O/'joint';F=R/'build/ff-lives-body-palette-v1';S=R/'build/smb2-late-lives-palette-v6'
C=R/'docs/qa/checkpoints/2026-10-30/coherent62-both-lives-fixes'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--s2-controls',type=Path,nargs='+',required=True);a=ap.parse_args()
 assert not(O/'handoff.json').exists()and not C.exists()
 roots=[F/'handoff.json',S/'handoff-qualified-v2.json'];controls=[O/'ff-controls.json']+a.s2_controls
 for p in roots:B.bound(json.loads(B.read(p)))
 for p in controls:
  q=json.loads(B.read(p));assert q['passed'],p;B.bound(q)
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage);assert stage['source']and stage['candidate']==B.sha(J/'candidate.nes')=='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
 assert B.read(O/'source-stage.json')==B.read(J/'source-stage.json')
 deps=set();cmd=json.loads(B.read(O/'component-build.json'))['command'];deps.add(O/'component-build.json')
 for flag in ['--create-full-dep','--create-dep']:
  if flag in cmd:
   dep=Path(cmd[cmd.index(flag)+1]);deps.add(dep);first=B.read(dep).split(':\t',1)[1].splitlines()[0]
   for s in re.split(r'(?<!\\)\s+',first):
    if s:
     p=Path(s.replace('\\ ',' '));p=(R/p).resolve()if not p.is_absolute()else p.resolve();assert p.is_file();deps.add(p)
 for rel in ['smb2/smb2_roster.s','smb2/smb2_roster_host_v5.s']:assert(J/rel).resolve()in deps
 link=json.loads(B.read(O/'final-link.json'))['command'];deps.update(Path(t)for t in link if t.endswith('.o'));deps.add(J/'private.cfg')
 deps.update(p for p in J.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg'])
 closure=dict(source=True,candidate=stage['candidate'],actual_recipes=['component-build.json','final-link.json'],FF_owned_producers_read_only_from_frozen492b=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(deps)})
 B.write(O/'source-closure-current.json',json.dumps(closure,indent=2)+'\n')
 note='''# Joint62 lives repairs: surgical source composition

Candidate dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7
is genuinely compiled/linked from frozen FF492b plus frozen S2f3a2.
It is exactly3721 +227 disjoint own bytes: FF21 and S2206. No binary
delta produced the ROM; the exact delta comparison verifies source output.
Header/CHR/all prior publicPCs, Quick/Ar/FF code/data/cookies are unchanged.
No new lease/common/Main instruction change, native run or install occurred.
Current62 and Arthur->Goku Select/Battletoads pending semantics remain.

FF: genuine native lives body Y88/X96 is unchanged. Source draws P0 only;
the late wrapper now queues native30B text plus one7B original class/native
black P0 packet, rather than unused face/weapon packets totaling49B. Full
16-byte cookie guards ACK; cold mode never writes unready RAM3. Existing
20B own padding funds the19B helper. Actual first lives nominal render-enable
2248CPU including513DMA vs parent2552. Native P1/P2/P3 remain untouched.
WhiteMage gameplay's250 opaque original pixels match actual nativePNG
without translation;69 green pixels are transparent hill background.

S2: actual native WriteGameText overwrote its earlier queued palette before
normalNMI. Existing71B status and166B of own C80 padding now append original
black/bodyP0 after actual30B text; preserve original fullcolor/pending-ROM,
ACK invalid-first retry, R0..7/allmutableSFC and callerAXYP/C contracts.
Actual source art/CHR/red-eye/BG helper remain unchanged from3721.

Combined targeted controls repeat the existing FF4cold/lives/parser+128Main
TOTAL,128fullflag helper/cookie cases and69realvectors. Existing targeted
S2 cold/pending-order/retry controls are bound below. Parent fullflags/ISR
and original authentic source/art proofs remain bound; no exploratory
fixture expansion was required for this disjoint composition.

IMPORTANT: FF Fighter gameplay rendering-enable deadline419 is NOT fixed.
Root actualnative trace proves genuine slot0 page763->764 there. Conditional
publisher map-only capacity proposal was rejected because cookieBFE0..BFF0
is live; no publisher/dirtymask/globalNMI experiment is in this candidate.
Native exact eight-character menu/lives/gameplay smokes and final layout
review are pending root queue grants. Severe lag is disclosed, not erased.

Canonical source:true/candidate/bindings, joint/source-stage.json,
candidate.nes/.dbg/.lbl, ram3.bin and ff-cookie.bin are present for native
v6 binders. Source-only ZIP is copied to Git checkpoint for replayability.
OriginalROMs/objects/DBG are hash-bound, not republished in that archive.
Inherited joint build logs are historical; top-level component/final-link
and the two frozen parent recipes are actual current production closure.
'''
 B.write(O/'HANDOFF.md',note)
 tools=[R/'tools/audit'/n for n in ['prepare_coherent62_lives_fixes_v1.py','coherent62_lives_ff_controls_v1.py','freeze_coherent62_lives_fixes_v1.py']]
 files=deps|set(tools)|set(roots)|set(controls)|set(p for p in O.glob('*')if p.is_file())|{J/'source-stage.json',J/'eye-red.chr'}
 for p in controls:files.update(Path(n)for n in json.loads(B.read(p))['bindings']if Path(n).suffix=='.py')
 archive=O/'source-only.zip';members=[]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.is_relative_to(R)and(p.suffix in ['.py','.s','.inc','.cfg','.json','.md','.patch','.d','.dep']or p==J/'eye-red.chr'):
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive);files.update(J/n for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','ram3.bin','ff-cookie.bin','code.bin','data.bin'])
 d=dict(status='FROZEN_JOINT62_BOTH_LIVES_SOURCE_NATIVE_PENDING',source=True,candidate=stage['candidate'],joint=str(J.resolve()),source_stage=str((J/'source-stage.json').resolve()),native=False,installed=False,publication_allowed=False,ready=62,changed_bytes=227,FF_Main_TOTAL=128,FF_gameplay_deadline419_fixed=False,source_archive_members=len(members),bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n');B.bound(d)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for rel in z.namelist():assert hashlib.sha256(z.read(rel)).hexdigest()==B.sha(R/rel)
 verification=dict(passed=True,source=True,candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),verified_bindings=len(d['bindings']),verified_archive_members=len(members),native=False)
 B.write(O/'verification.json',json.dumps(verification,indent=2)+'\n');C.mkdir(parents=True)
 for p in [O/n for n in ['handoff.json','HANDOFF.md','source-stage.json','source.patch','ff-controls.json','source-closure-current.json','verification.json','source-only.zip']]:shutil.copyfile(p,C/p.name)
 for i,p in enumerate(a.s2_controls):shutil.copyfile(p,C/('S2-controls-'+str(i+1)+'.json'))
 for rel in ['smb2/smb2_roster.s','smb2/smb2_roster_host_v5.s','loader.s','ff-palette.s']:
  p=C/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(J/rel,p)
 receipt=dict(source=True,candidate=d['candidate'],native=False,installed=False,bindings={str(p.resolve()):B.sha(p)for p in sorted(C.rglob('*'))if p.is_file()})
 B.write(C/'receipt.json',json.dumps(receipt,indent=2)+'\n');B.bound(receipt)
 B.write(O/'owned-files.txt','\n'.join(p.relative_to(R).as_posix()for p in tools+sorted(C.rglob('*'))if p.is_file())+'\n')
 for p in roots:B.bound(json.loads(B.read(p)))
 print(json.dumps(dict(candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),bindings=len(d['bindings']),archive_members=len(members),checkpoint_receipt_sha256=B.sha(C/'receipt.json'),native=False)))
if __name__=='__main__':main()
