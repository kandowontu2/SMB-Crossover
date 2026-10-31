"""Copy the frozen bounded CF source checkpoint, files only, never Git."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-guarded-runtime-qualified-v1'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-guarded-runtime'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir(parents=True)
 assert sha(P/'handoff.json')=='d097fbc9b5b2ea30107dcfbc0daac8da312020af2c466d205ca6bac1a65e0322'
 d=json.loads((P/'handoff.json').read_text());owned=[]
 def copy(a,b):
  b=O/b;b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);assert sha(a)==sha(b);owned.append(str(b.relative_to(R)).replace('\\','/'))
 for n in['handoff.json','integration-api.json','source-only.zip']:copy(P/n,n)
 for name,path in[
  ('source-stage.json','build/contra-force-guarded-cart-v2/source-stage.json'),
  ('boundary-controls.json','build/contra-force-host-boundaries-controls-v3/controls.json'),
  ('phase-cadence-controls.json','build/contra-force-phase-cadence-controls-v1/controls.json'),
  ('router-controls.json','build/contra-force-a2-router-controls-v3/controls.json'),
  ('guard-controls.json','build/contra-force-external-guard-controls-v2/controls.json'),
  ('guard-vector-controls.json','build/contra-force-external-guard-isr-controls-v3/controls.json')]:copy(R/path,'evidence/'+name)
 for i,path in enumerate(d['retained_negatives']):copy(R/path,'retained-negatives/%02d-%s'%(i,Path(path).parent.name+'.json'))
 scope='''Contra Force guarded runtime: source-only checkpoint

Frozen handoff d097fbc9 and actual source cart c1159eff are pending, not playable admission.
The genuine current9529 parent relinks exactly. All79,572 previous symbol PCs remain exact.
The actual new cartridge has only the granted567B ROM guard/bootstrap and CHR935..<969 changes.
No shared resolver, scene/menu operand, readiness or installed download is modified.

The118B retained-ROM guard authenticates the complete16-byte C2cookie and selected class BEFORE
the first A2 opcode. The449B forcedblank bootstrap copies and verifies all24KiB, clears both C2
and RAM3 cookies before writes, and publishes A7 last. The partial source runtime preserves genuine
motion, all original actor fields, source body/shot art, SMB terrain and ordinary/Bowser defeat paths.
The source-only ZIP contains source/commands/assets and the retained evidence lineage; it excludes
NES/object/debug/map and derived payload binaries. It does not contain another older archive ZIP.

The API JSON lists all20 still-unimplemented rows and the required real cold/menu/lives/palette/draw
routes. Native was not launched. No functional readiness, complete native Main, or performance claim.
The CFcookie also covers RAM3: leaving CF MUST invalidate it before any foreign RAM3 replacement.
That acquisition/retirement chain is not installed by this checkpoint.

Retained counterexamples include actor-index53 contamination and duplicate source weapon phase.
Guard-vector v1 ran112 real resident-SFC cuts only due to a raw-versus-physical bank comparison;
the original112 positives remain, the wider claim is withdrawn. The current v3 runs848 real cuts.
See handoff and exact retained-negative files; no prior receipt was rewritten.
'''
 (O/'SCOPE.txt').write_text(scope);owned.append(str((O/'SCOPE.txt').relative_to(R)).replace('\\','/'))
 tool=Path(__file__).relative_to(R).as_posix();freeze='tools/audit/freeze_contra_force_guarded_runtime_v1.py'
 out=O/'owned-files.json';owned.extend([str(out.relative_to(R)).replace('\\','/'),tool,freeze])
 out.write_text(json.dumps(dict(files=owned,files_only=True,no_git_operation=True,
  checkpoint_file_hashes={str(p.relative_to(R)).replace('\\','/'):sha(p)for p in O.rglob('*')if p.is_file()},
  tools={q:sha(R/q)for q in[tool,freeze]}),indent=2)+'\n')
 print(json.dumps(dict(checkpoint=str(O),owned_files=len(owned),owned_manifest_sha256=sha(out),bytes=sum(p.stat().st_size for p in O.rglob('*')if p.is_file()))))
if __name__=='__main__':main()
