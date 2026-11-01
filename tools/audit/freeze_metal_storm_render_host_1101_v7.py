"""Compact renderer/lifecycle source packet, no ROM/object/debug/code images."""
from pathlib import Path
import hashlib,json,zipfile
import prepare_metal_storm_render_host_1101_v7 as P
ROOT=P.ROOT;OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assembly=json.loads((OUT/'assembly.json').read_text());cpu=json.loads((OUT/'CPU-controls.json').read_text());art=json.loads((OUT/'art.json').read_text())
    assert assembly['passed']and cpu['passed']and not cpu['native']and not cpu['admitted']
    for receipt in[assembly,cpu,art]:
        for path,h in receipt['bindings'].items():assert sha(path)==h,path
    code=[ROOT/'tools/audit/capture_metal_storm_native_render_1101_v7.py',ROOT/'tools/audit/prepare_metal_storm_render_assets_1101_v7.py',Path(P.__file__),ROOT/'tools/audit/check_metal_storm_render_host_1101_v7.py',Path(__file__),P.REF,P.REF.with_suffix('.md')]
    items={p.relative_to(ROOT).as_posix():p.read_bytes()for p in code}
    for name in['host-step.inc','objects-ready.inc','render-life.inc','renderer.s','symbols.s','render.cfg']:items['source/'+name]=(OUT/name).read_bytes()
    for name in['body.chr','body-meta.bin','shots.chr','shot-meta.bin']:items['assets/'+name]=(OUT/name).read_bytes()
    for name in['CPU-controls.json','art.json','native-render-witness.json']:items['proof/'+name]=(OUT/name).read_bytes()
    summary={k:v for k,v in assembly.items()if k not in['labels','commands']};items['proof/assembly-summary.json']=(json.dumps(summary,indent=2)+'\n').encode()
    items['proof/native-render-preview.png']=(OUT/'native-render-preview.png').read_bytes()
    external=dict(v6_packet=P.V6.relative_to(ROOT).as_posix()+'/source-proof.zip',v6_packet_sha256=sha(P.V6/'source-proof.zip'),v6_lab='Read-only specific includes referenced by the recipe; compiled actor/renderer/gate, objects, debug and labels remain lab-only.',original_packet='docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip',witness='Exactly1059bytes of actual native renderer/CHR/SMC and mapping data in proof/native-render-witness.json; no whole ROM/PRG/debug snapshots.',scope='Unintegrated/unselectable source component, not native admission or resource lease. CHR800..805 and ROM9000 are CPU test arenas only.')
    items['external-inputs.json']=(json.dumps(external,indent=2)+'\n').encode()
    manifest={n:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())for n,data in items.items()};items['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    path=OUT/'source-proof.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(items.items()):
            assert not name.endswith(('.nes','.fds','.o','.dbg','.lbl'))
            assert not(name.endswith('.bin')and not name.startswith('assets/'))
            info=zipfile.ZipInfo(name,(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path)as z:
        assert z.testzip()is None
        for name,r in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256']
    result=dict(passed=True,component_only=True,native=False,installed=False,menu_admitted=False,complete=False,archive=path.relative_to(ROOT).as_posix(),archive_sha256=sha(path),archive_bytes=path.stat().st_size,members=len(items),source_paths=[p.relative_to(ROOT).as_posix()for p in code],actor_bytes=assembly['actor_bytes'],renderer_bytes=assembly['renderer_bytes'],unfunded_gate_bytes=assembly['gate_bytes'],external_inputs=external,scope='Original body/shot art and lifecycle, exact native producer CPU evidence and composed constructor/terrain/actor/life/render. Remaining host/source features and actual native qualification required.')
    (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
