"""Write compact source-only S2 eye/backdrop Git checkpoint; never stage."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from finalize_ff_current_component_v3 import dependencies
O=R/'build/smb2-eye-sky-v3';C=R/'docs/qa/checkpoints/2026-10-30/smb2-eye-backdrop-source';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
def main():
 h=json.loads((O/'handoff.json').read_text());assert sha(O/'handoff.json')=='ff49c753b8d323eea5ab4a342bd8dfaf79d9438522e0d9fca39a1a28b82bb850'
 for p,v in h['bindings'].items():assert sha(p)==v,p
 assert C.is_dir() and not(C/'source-only.zip').exists();assert set(p.name for p in C.iterdir())=={'handoff.json','source-proof.json','controls.json','original-eye-role.json','sky-negative.json','consumer-proposal.json'}
 tools=[R/'tools/audit'/n for n in['prepare_smb2_eye_sky_v1.py','prepare_smb2_eye_sky_v2.py','prepare_smb2_eye_sky_v3.py','smb2_eye_palette_audit_v1.py','smb2_eye_palette_audit_v2.py','smb2_sky_negative_v1.py','smb2_eye_sky_controls_v1.py','freeze_smb2_eye_sky_v1.py','checkpoint_smb2_eye_sky_v1.py']]
 copies={'handoff.json':O/'handoff.json','source-proof.json':O/'source-proof.json','controls.json':R/'build/smb2-eye-sky-controls-v1/controls.json','original-eye-role.json':R/'build/smb2-eye-role-audit-v2/audit.json','sky-negative.json':R/'build/smb2-sky-negative-v1/negative.json','consumer-proposal.json':R/'build/smb2-sky-negative-v1/consumer-proposal.json'}
 for n,p in copies.items():assert sha(C/n)==sha(p)
 write(C/'checkpoint-export-negative.json',json.dumps(dict(failure='Source-only extension guard initially excluded genuine ca65 longbranch.mac/generic.mac include files; no archive created. Resumed only after exact six previously-copied proof hashes matched.',no_frozen_change=True),indent=2)+'\n')
 paths=set(tools)|set(copies.values())|{O/'README.txt',O/'source.patch',O/'component-build.json',O/'asset-build.json',O/'final-link.json',J/'private.cfg',J/'asset.s',J/'eye-red.chr',J/'component.s'}
 paths|=set(dependencies(J/'component.dep'))|set(dependencies(J/'asset.dep'))
 for d,n in [('smb2-eye-sky-v1','component-build.json'),('smb2-eye-sky-v2','final-link.json')]:paths.add(R/'build'/d/n)
 paths.add(C/'checkpoint-export-negative.json');allowed={'.py','.s','.inc','.mac','.cfg','.json','.txt','.patch','.chr'};assert all(p.suffix.lower()in allowed for p in paths);assert all(p.resolve().is_relative_to(R)for p in paths)
 archive=C/'source-only.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(paths):z.write(p,p.relative_to(R).as_posix())
 assert archive.stat().st_size<=4*1024*1024
 with zipfile.ZipFile(archive)as z:
  for p in paths:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 write(C/'README.md','''Source-only SMB2 eye/backdrop repair. Private candidate f0ce3d16fe0130924e6d1afeb541ed1c7cd8fe4bfd06c86621a5713fa73e979c derives immutable final62 408acae. No native run or install in this receipt. Only205 own bytes change; no extra palette ownership/OAM/CHR/RAM/PRG allocation. Ground/water backdrop22; lives/underground/castle0F under actual native selection. Eyes preserve original NES16 through stable nativeP2 index1, same5parts/max3line.

The archive contains actual own source+component include closure,12KB derived CHR source input, bounded tools/recipes/proofs and retained preparation negatives. It excludes ROM/object/debug binaries; it is an incremental producer packet depending on the already frozen final62 source closure. Full handoff retains1109 exact bindings. Actual controls:256 original-color/priority poses,96 scene+normalNMI palette cases,85 queue offsets/canaries,8 actual cold/lives/entrance cohorts+64Main total,82 genuine IRQ/lagNMI instruction cuts. Original star/published-ROM/ACK guards and vegetableP1 role unchanged/disclosed. See README.txt inside for exact source-consumer reasoning and rebase instructions.

Retained source1 negative: native bulk3F00=0F lacks later S2 native-backdrop restore. Existing source already3F11-only, so no fictional S2 universal write was removed. Original eye-role static white/black assumption is rejected by21 genuine donor producer+PPU-consumer cases. v1 assembly label-constant failure and v2 generic debug-name collision remain archived. No frozen evidence was normalized.

No Git stage/commit was performed by this tool. Root owns adoption/native and Git publication.
''')
 own=[p.relative_to(R).as_posix()for p in tools]+[p.relative_to(R).as_posix()for p in sorted(C.iterdir())]+[(C/'manifest.json').relative_to(R).as_posix(),(C/'owned-files.txt').relative_to(R).as_posix()]
 write(C/'owned-files.txt','\n'.join(own)+'\n')
 d=dict(status='SOURCE_CPU_QUALIFIED_NATIVE_PENDING',candidate=h['candidate_sha256'],source_handoff=sha(O/'handoff.json'),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members={p.relative_to(R).as_posix():sha(p)for p in sorted(paths)},checkpoint_copies={n:dict(original=str(p),sha256=sha(p))for n,p in copies.items()},own_tools=[p.relative_to(R).as_posix()for p in tools],owned_files_list=(C/'owned-files.txt').relative_to(R).as_posix(),no_ROM_object_debug_in_archive=True,no_git_mutation=True)
 write(C/'manifest.json',json.dumps(d,indent=2)+'\n');print(json.dumps(dict(checkpoint=str(C),manifest=sha(C/'manifest.json'),archive=sha(archive),bytes=archive.stat().st_size,members=len(paths),owned_files=own)),flush=True)
if __name__=='__main__':main()
