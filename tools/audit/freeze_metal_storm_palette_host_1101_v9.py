"""Freeze compact semantic source, small art, scoped witnesses and receipts."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/metal-storm-coexistence-1101-v9';V7=ROOT/'build/metal-storm-render-host-1101-v7';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCES=[ROOT/'tools/audit'/n for n in['audit_metal_storm_coexistence_1101_v9.py','capture_metal_storm_palette_consumers_1101_v9.py','prepare_metal_storm_palette_host_1101_v9.py','check_metal_storm_palette_host_1101_v9.py','freeze_metal_storm_palette_host_1101_v9.py']]+[ROOT/'tools/reference'/n for n in['metal_storm_palette_host_1101_v9.inc','metal_storm_palette_host_1101_v9.md']]
def main():
 assert not(OUT/'source-stage.json').exists()
 receipts=[OUT/n for n in['palette-inputs.json','native-palette-callers.json','palette-assembly.json','palette-CPU-controls.json']]
 for p in receipts:
  q=json.loads(p.read_text());assert q['passed']
  for name,h in q['bindings'].items():assert sha(name)==h,name
 controls=json.loads(receipts[-1].read_text());assert controls['body_shape_remap_contexts']==624 and controls['shot_shape_remap_contexts']==312 and controls['composed_original_constructor_actor_terrain_lifecycle_render_frames']==576
 assets=[OUT/n for n in['original-body.chr','red-white-black.chr','blue-white-black.chr','player-palette-comparison.png','renderer-palette.inc','renderer.s','red-white-black-symbols.s','red-white-black.cfg']]+[V7/'body-meta.bin',V7/'shot-meta.bin']
 members={p.relative_to(ROOT).as_posix():p for p in SOURCES+receipts+assets}
 assert all(p.suffix.lower()not in['.o','.dbg','.lbl','.nes','.fds']for p in members.values())
 assert not any(p.name.endswith(('-actor.bin','-render.bin','-unused.bin'))for p in members.values())
 external={str(p.resolve()):sha(p)for p in[V7/'source-stage.json',V7/'source-proof.zip',V8/'source-stage.json',V8/'source-proof.zip',V8/'native-witness.json',V7/'actor.s',V7/'render-life.inc']}
 manifest=dict(source_files={n:dict(bytes=p.stat().st_size,sha256=sha(p))for n,p in members.items()},external_frozen_lab_objects=external,root_baseline_ROM_sha256=json.loads(receipts[0].read_text())['baseline_ROM_sha256'],native=False,installed=False,resource_granted=False,global_CHR_consumer_closure=False,scope='Intentional selected-player P0 adaptation only; original actor/geometry exact. Native P1/P2/P3 and all native patterns retained. Existing star/flower phase0 sharedP0 exception explicit. No full PRG/ROM/object/debug/code snapshots, tree copies or admission.')
 (OUT/'hash-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 archive=OUT/'source-proof.zip';assert not archive.exists()
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,p in members.items():z.write(p,name)
  z.write(OUT/'hash-manifest.json','hash-manifest.json')
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None and len(z.namelist())==len(members)+1
 result=dict(passed=True,native=False,installed=False,resource_granted=False,global_CHR_consumer_closure=False,recommended='red-white-black',archive=str(archive.resolve()),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(members)+1,source_paths=[p.relative_to(ROOT).as_posix()for p in SOURCES],actor_bytes=8083,renderer_bytes=2350,original_body_shape_contexts=624,original_shot_shape_contexts=312,native_world_contexts=1056,composed_original_frames=576,body_shading_pixels_recolored=1140,shot_pixels_recolored=200,existing_shared_P0_cycle_pixels=dict(star=122,flower=100),next_gate='Global CHR500 and old carrier/body consumer closure, then root resource grant and actual loader/Main/ISR/native admission.',bindings={str(p.resolve()):sha(p)for p in SOURCES+receipts+[OUT/'hash-manifest.json']})
 (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['bindings','source_paths']}))
if __name__=='__main__':main()
