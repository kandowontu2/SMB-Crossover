"""Freeze semantic owning source and aggregate proof, without binary forests."""
from pathlib import Path
import hashlib,json,zipfile,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import prepare_metal_storm_owning_graft_1101_v11 as P
O=P.O;sha=P.sha
NAMES=['prepare_metal_storm_owning_graft_1101_v11.py','check_metal_storm_owning_graft_1101_v11.py','audit_metal_storm_old_readers_1101_v11.py','freeze_metal_storm_owning_graft_1101_v11.py']

def main():
 assert not(O/'source-stage.json').exists()
 receipts=[O/n for n in['ownership.json','owning-link.json','CPU-controls.json','old-reader-controls.json']]
 for p in receipts:
  q=json.loads(p.read_text());assert q['passed'],p
  for name,h in q.get('bindings',{}).items():assert sha(name)==h,name
 result=json.loads((O/'owning-link.json').read_text());cpu=json.loads((O/'CPU-controls.json').read_text());assert cpu['ROM_sha256']==result['ROM_sha256']==sha(O/'candidate.nes')
 sources=[R/'tools/audit'/n for n in NAMES]+[P.REF,R/'tools/reference/metal_storm_owning_graft_1101_v11.md']
 # Local semantic source is compact; native/dependency source trees remain
 # external read-only bindings. No .o/.dbg/.lbl/compiledcode or ROM snapshots.
 semantic=[O/n for n in['component.s','actor.s','renderer.inc','loader.inc','entrypoint.s','cv3.s','candidate.cfg','component.cfg','main-build.json','link.json']]
 extra=[R/'build/mario-tank-loader-1101-v4/Bill-tail-readers.json',P.V9/'red-white-black.chr']
 members={p.relative_to(R).as_posix():p for p in sources+receipts+semantic+extra}
 assert all(p.suffix.lower()not in['.nes','.fds','.o','.dbg','.lbl','.bin']for p in members.values())
 manifest=dict(native=False,installed=False,menu_admitted=False,CHR_granted=True,PRG_granted=False,RAM_granted=False,baseline=P.PIN,ROM_sha256=result['ROM_sha256'],files={n:dict(bytes=p.stat().st_size,sha256=sha(p))for n,p in members.items()},
  external_lab_objects={str(p.resolve()):sha(p)for p in[O/'candidate.nes',O/'candidate.dbg',O/'main.o',O/'component.o',O/'actor.bin',O/'render.bin',O/'carrier-pack.bin',O/'cv3-granted-pages.bin',O/'cookie.bin']},external_frozen_inputs={str(p.resolve()):sha(p)for p in[P.V7/'source-proof.zip',P.V8/'source-proof.zip',P.V9/'source-proof.zip',P.V10/'source-proof.zip',P.GRANT,P.PACKET]},scope='Private owning-source ROM and scoped CPU/reader proof. Compiled outputs remain external immutable lab objects, not publication payload. No selectable/native admission.')
 (O/'hash-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 packet=O/'source-proof.zip';assert not packet.exists()
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,p in members.items():z.write(p,n)
  z.write(O/'hash-manifest.json','hash-manifest.json')
 with zipfile.ZipFile(packet)as z:assert z.testzip()is None
 stage=dict(passed=True,private_owning_relink=True,native=False,installed=False,menu_admitted=False,CHR_granted=True,PRG_granted=False,RAM_granted=False,baseline=P.PIN,ROM_sha256=result['ROM_sha256'],archive=str(packet.resolve()),archive_sha256=sha(packet),archive_bytes=packet.stat().st_size,archive_members=len(members)+1,source_paths=[p.relative_to(R).as_posix()for p in sources],actor_bytes=result['actor_bytes'],renderer_bytes=result['renderer_bytes'],source_frames=cpu['donor_differential_frames'],source_pixel_cases=cpu['owning_source_pixel_cases'],next='Historical c864 composition; future graft must preserve new367266d2 Kirby Main/Weapons/injury changes. Parent PRG/RAM acceptance, retirement/menu/Main constructor/update/camera wiring, original callbacks, Main/ISR and native qualification remain.',bindings={str(p.resolve()):sha(p)for p in sources+receipts+[O/'hash-manifest.json']})
 (O/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n');print(json.dumps({k:v for k,v in stage.items()if k not in['source_paths','bindings']}))
if __name__=='__main__':main()
