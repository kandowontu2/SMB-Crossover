"""Freeze surgical FF lives palette/deadline leaf, retaining all negatives."""
from pathlib import Path
import json,re,shutil,zipfile,hashlib
import prepare_functional_roster_visuals58_v1 as B
R=B.R;O=R/'build/ff-lives-body-palette-v1';J=O/'joint';P=R/'build/arthur-goku-smb2-palette-v1'
C=R/'docs/qa/checkpoints/2026-10-30/ff-lives-only-body-palette'
def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 parent=json.loads(B.read(P/'handoff.json'));B.bound(parent)
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
 controls=json.loads(B.read(O/'controls-v6.json'));assert controls['passed'];B.bound(controls)
 assert stage['candidate']==B.sha(J/'candidate.nes')=='492b29c9893b6534ecd174d6fd8d39aacfd93aeeaf3ddbdfeadd52463a0fd75c'
 deps=set()
 for n in ['loader','ff-palette']:
  p=O/(n+'-build.json');deps.add(p);cmd=json.loads(B.read(p))['command'];deps.add(Path(cmd[cmd.index('-o')+1]))
  for flag in ['--create-full-dep','--create-dep']:
   if flag in cmd:
    dep=Path(cmd[cmd.index(flag)+1]);deps.add(dep);first=B.read(dep).split(':\t',1)[1].splitlines()[0]
    for s in re.split(r'(?<!\\)\s+',first):
     if s:
      q=Path(s.replace('\\ ',' '));q=(R/q).resolve()if not q.is_absolute()else q.resolve();assert q.is_file();deps.add(q)
 link=json.loads(B.read(O/'final-link.json'))['command'];deps.update(Path(t)for t in link if t.endswith('.o'))
 deps.add(J/'private.cfg');deps.update(p for p in J.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg'])
 closure=dict(source=True,candidate=stage['candidate'],actual_recipes=['loader-build.json','ff-palette-build.json','final-link.json'],parent_immutable_objects=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(deps)})
 B.write(O/'source-closure-current.json',json.dumps(closure,indent=2)+'\n')
 note='''# FF lives-only body palette: source deadline repair

Candidate492b29c9 is genuinely linked from frozen37210891 remap/S2 source.
Exactly21 own PRG bytes differ:19 bytes consume the existing explicit20B
padding at A62ACAC..<ACC0 after the32B FwHudNames table, and2 bytes retarget
the actual FwLivesColors JSR operand. Header/CHR/all prior public PCs and
Quick/Arthur/FF code,data,cookies are unchanged. No body coordinate, source
palette or gameplay code changes. No new resource lease or native run.

The apparent lives position failure is a displaced background, not a wrong
sprite anchor. Native IntermediatePlayerData Y88/X96 is authentic; all4
source bodies match their actual native OAM. The original first-lives49B
queue repeatedly forces unused face/weapon palettes through two6B packets.
Actual parent native evidence independently observed rendering enable at
elapsed2553CPU after pre-render reload. This leaf keeps genuine native30B
text and one7B original body/universal-color packet, total37B. It preserves
existing native P1/P2/P3, which the UI body never uses (all parts use P0).

The19B own helper saves AXYP, calls unchanged full16-byte FwCheck, chooses
ready mode1 (ACK only after successful complete queue) or cold mode2 (no
unauthenticated RAM3 state writes), and jumps to genuine FwPaletteMapC.
The existing19B late-lives wrapper still temporarily uses authentic native
black BackgroundColorCtrl2, restores it, and returns native A1/NZ. No weak
cookie check, DMA skip, snapshot normalization, or shifted body is used.

All4 real cold/select/Start/parser/lives sequences and128Main TOTAL pass.
Each actual first lives queue37 gives nominal CPU-model rendering-enable
2248 including513DMA, versus parent2552. This is instruction/order proof,
not exact native PPU or DMC-steal timing. Root must bind/run the exact new
cart before claiming corrected native lives layout or release readiness.
128 helper cases cover cold/valid full64flag sets;69 real normalNMI/lagNMI/
IRQ cuts preserve full33SMC, live stack, rawmaps and caller continuation.
Foreground SFC legitimately publishes bank and returnedA operands; initial
fixtures wrongly required pre-call33SMC identity and incomingNZ preservation
despite native final LDA1. Their negatives and report-only wrapper mistakes
remain. Final controls-v6 corrects only observation/reporting, no ROM change.

The White Mage gameplay apparent green trim is not a palette defect:
all250 authentic opaque original pixels on physical782 exactly match actual
source-jump PNG at zero translation, using red/white/pink source roles.
69 green pixels inside its bounding rectangle are transparent hill pixels.
Initial diagnostic misread CSV page2 (CPU DMA page) as physicalCHR; retained.

Separate parent Fighter gameplay render-enable deadline419 remains OPEN.
Root's native CHR trace shows a genuine slot0 page763->764 change there;
this lives fix alone does not claim to solve that budget or severe lag.
S2 first-lives palette queue-overwrite diagnosis is another separate lane.
No DK pound or other performance proposal is included. Existing62/remap/
Battletoads-pending semantics, all native/source negatives stay bound.
'''
 B.write(O/'HANDOFF.md',note)
 tools=[R/'tools/audit'/n for n in ['prepare_ff_lives_body_palette_v1.py','ff_lives_scroll_diagnostic_v1.py','freeze_ff_lives_body_palette_v1.py']+[f'ff_lives_body_palette_controls_v{i}.py'for i in range(1,7)]]
 files=deps|set(tools)|{P/'handoff.json'}|set(p for p in O.glob('*')if p.is_file())|{J/'source-stage.json'}
 files.update(Path(p)for p in controls['bindings']if Path(p).suffix=='.py')
 files.add(R/'build/ff-lives-scroll-diagnostic-v1/diagnostic.json')
 archive=O/'source-only.zip';members=[]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.is_relative_to(R)and p.suffix in ['.py','.s','.inc','.cfg','.json','.md','.patch','.d','.dep']:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive);files.update(J/n for n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','ram3.bin','ff-cookie.bin','code.bin','data.bin'])
 d=dict(status='FROZEN_SOURCE_FF_LIVES37_NATIVE_LAYOUT_PENDING',source=True,candidate=stage['candidate'],joint=str(J.resolve()),native=False,installed=False,publication_allowed=False,parent=stage['parent'],ready=62,changed_bytes=21,source_archive_members=len(members),body_coordinates_unchanged=True,gameplay_deadline419_not_fixed=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n');B.bound(d)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for rel in z.namelist():assert hashlib.sha256(z.read(rel)).hexdigest()==B.sha(R/rel)
 verification=dict(passed=True,candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),verified_bindings=len(d['bindings']),verified_archive_members=len(members),native=False)
 B.write(O/'verification.json',json.dumps(verification,indent=2)+'\n');C.mkdir(parents=True)
 for p in [O/n for n in ['handoff.json','HANDOFF.md','source-stage.json','source.patch','controls-v6.json','source-closure-current.json','verification.json','source-only.zip']]:shutil.copyfile(p,C/p.name)
 for name in ['loader.s','ff-palette.s']:
  q=C/'source'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(J/name,q)
 receipt=dict(source=True,candidate=d['candidate'],native=False,installed=False,bindings={str(p.resolve()):B.sha(p)for p in sorted(C.rglob('*'))if p.is_file()})
 B.write(C/'receipt.json',json.dumps(receipt,indent=2)+'\n');B.bound(receipt)
 B.write(O/'owned-files.txt','\n'.join(p.relative_to(R).as_posix()for p in tools+sorted(C.rglob('*'))if p.is_file())+'\n')
 B.bound(parent)
 print(json.dumps(dict(candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),bindings=len(d['bindings']),archive_members=len(members),checkpoint_receipt_sha256=B.sha(C/'receipt.json'),native=False)))
if __name__=='__main__':main()
