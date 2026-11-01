"""Compact source/aggregate object-callback checkpoint, no compiled outputs."""
from pathlib import Path
import hashlib,json,zipfile
import prepare_metal_storm_objects_host_1101_v6 as P
ROOT=P.ROOT;OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assembly=json.loads((OUT/'assembly.json').read_text());cpu=json.loads((OUT/'CPU-controls.json').read_text())
    assert assembly['passed']and cpu['passed']and not cpu['native']and not cpu['admitted']
    for receipt in[assembly,cpu]:
        for p,h in receipt['bindings'].items():assert sha(p)==h,p
    code=[ROOT/'tools/audit/prepare_metal_storm_objects_host_1101_v6.py',ROOT/'tools/audit/check_metal_storm_objects_host_1101_v6.py',Path(__file__),P.REF,ROOT/'tools/reference/metal_storm_objects_host_1101_v6.md']
    items={str(p.relative_to(ROOT)).replace('\\','/'):p.read_bytes()for p in code}
    for n in['actor-relaxed.inc','object-leaves.inc','host-step.inc','terrain-adapter.inc']:items['source/'+n]=(OUT/n).read_bytes()
    for n in['assembly.json','CPU-controls.json']:items['proof/'+n]=(OUT/n).read_bytes()
    external=dict(v5_packet=str((P.V5/'source-proof.zip').relative_to(ROOT)),v5_packet_sha256=sha(P.V5/'source-proof.zip'),original_packet='docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip',original_actor_sha256=sha(P.ACTOR),native_ROM_read=False,scope='Frozen original/v4/v5 lab/source inputs remain external. No compiled kernel, ROM/PRG, object, debug, label or dependency graph copies. Not a selectable admission/resource grant.')
    items['external-inputs.json']=(json.dumps(external,indent=2)+'\n').encode()
    manifest={n:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest())for n,v in items.items()}
    items['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    path=OUT/'source-proof.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,v in sorted(items.items()):
            assert not n.endswith(('.nes','.fds','.bin','.o','.dbg','.lbl'))
            info=zipfile.ZipInfo(n,(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path)as z:
        assert z.testzip()is None
        for n,r in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
    result=dict(passed=True,component_only=True,native=False,installed=False,menu_admitted=False,complete=False,archive=str(path.relative_to(ROOT)).replace('\\','/'),archive_sha256=sha(path),archive_bytes=path.stat().st_size,members=len(items),source_paths=[str(p.relative_to(ROOT)).replace('\\','/')for p in code],kernel_bytes=assembly['kernel_bytes'],remaining_before_cookie=assembly['remaining_before_BFE0'],long_branches_shortened=assembly['long_branches_shortened'],external_inputs=external,scope='Source-verified FF27/owned projectiles/empty platform pass plus reset-control and renderer-mask dependencies, composed with ctor/terrain/actor. Native host admission and remaining features required.')
    (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
