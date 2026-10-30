"""Resume checkpoint export after retained Windows text-encoding failure."""
from pathlib import Path
import json,zipfile
import freeze_celeste_name_native_v1 as B
R=B.R;O=B.O;C=B.C;sha=B.B.sha
def main():
 h=O/'native-handoff-v1.json';d=json.loads(h.read_text())
 for p,v in d['bindings'].items():assert sha(p)==v,p
 assert C.exists()and not(C/'source-and-native.zip').exists()
 (O/'checkpoint-export-negative-v1.json').write_text(json.dumps(dict(native_unchanged=True,error='Default Windowscp1252 could not encode README arrow; failed before archive. Separate successor writes ASCII README explicitlyUTF8; frozen native/source evidence unchanged.'),indent=2)+'\n')
 text='''CELESTE MARIO: exact character-select label, released52 successor.

Candidate a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48 derives from authoritative18de0155. Only12ROMbytes change in existing own A81 cold-menu space: one branch operand and11B helperBFAE..<BFB9. All63734existing labels keep their PCs except nonentryKmMenuEnd. Header,CHR,gameplay,NMI,dispatcher and all52ready flags are byte-exact. The source uses the original Names44 and SAMEBANK native name publisher.

CPU: all80 actual MenuResolve / QueueSelection / Select identities pass; other79 names and application states stay exact. FiveMario variants x64flags preserve foreign ABI; intentionalCeleste path matches the original index44 worker.

Native: ONE cold AllZeros/normal8 run exited0 at232frames. Four actual Select presses cycle Mario,Luigi,Maaa,Kamikaze,Celeste. Real PPU2328..2337 equals16authenticated CELESTE MARIO glyphs. Both whole256x240screens were root-reviewed; no testRAMwrites. Bounds2PNG/64files/512MiB/60s; bindings verified before/after. Inherited cyan menu band remains identical to parent.

Separate Arthur53 label descendant is source-only and retains Arthur's gameplay negative; it is not the release artifact. Source/link/helper verifier negatives remain in build/celeste-menu-name-current-v1 and current-v2; none launched native. Archive includes actual new source/config/objects/ROM/DBG/LBL, own tools,CPU/native proofs. Genuine recorded linker command depends on already-frozen18de predecessor objects; no predecessor changed.
'''
 (C/'README.md').write_text(text,encoding='utf-8',newline='\n')
 tools=[Path(p)for p in d['bindings']if'/tools/audit/'in p.replace('\\','/')and'celeste'in p]+[Path(__file__)]
 paths=[p for p in O.rglob('*')if p.is_file()]+tools;paths=list(dict.fromkeys(paths))
 archive=C/'source-and-native.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in paths:z.write(p,p.relative_to(R).as_posix())
 manifest=dict(status=d['status'],candidate=d['candidate'],parent=d['parent'],native_handoff=sha(h),source_handoff=sha(O/'handoff.json'),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():sha(p)for p in paths},own_tools=[p.relative_to(R).as_posix()for p in tools],source_patch='build/celeste-menu-name-current-v2/source.patch',release_artifact='build/celeste-menu-name-current-v2/joint/candidate.nes')
 (C/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(checkpoint=str(C),manifest=sha(C/'manifest.json'),native_handoff=sha(h),candidate=d['candidate'],archive_bytes=archive.stat().st_size,own_tools=manifest['own_tools'])))
if __name__=='__main__':main()
