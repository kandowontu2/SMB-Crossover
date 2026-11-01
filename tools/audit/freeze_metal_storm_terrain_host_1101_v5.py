"""Freeze compact semantic source/aggregate evidence; no code/ROM/object trees."""
from pathlib import Path
import hashlib,json,zipfile
import prepare_metal_storm_terrain_host_1101_v5 as P
ROOT=P.ROOT;OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assembly=json.loads((OUT/'assembly.json').read_text());cpu=json.loads((OUT/'CPU-controls.json').read_text())
    assert assembly['passed']and cpu['passed']and not cpu['native']and not cpu['admitted']
    for receipt in[assembly,cpu]:
        for p,h in receipt['bindings'].items():assert sha(p)==h,p
    code=[Path(__file__),ROOT/'tools/audit/prepare_metal_storm_terrain_host_1101_v5.py',ROOT/'tools/audit/check_metal_storm_terrain_host_1101_v5.py',P.REF,ROOT/'tools/reference/metal_storm_terrain_host_1101_v5.md']
    items={str(p.relative_to(ROOT)).replace('\\','/'):p.read_bytes()for p in code}
    items.update({'source/donor-leaves.inc':(OUT/'donor-leaves.inc').read_bytes(),'proof/assembly.json':(OUT/'assembly.json').read_bytes(),'proof/CPU-controls.json':(OUT/'CPU-controls.json').read_bytes()})
    external=dict(original_packet='docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip',v4_lab='build/metal-storm-host-contract-1101-v4',native_ROM=str(P.NATIVE.relative_to(ROOT)),native_ROM_sha256=cpu['ROM_sha256'],native_DBG_sha256=cpu['DBG_sha256'],disclaimer='External lab objects and qualified native ROM/debug stay read-only; packet has no native admission and no dependency-tree or compiled-code copies.')
    items['external-inputs.json']=(json.dumps(external,indent=2)+'\n').encode()
    manifest={n:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest())for n,v in items.items()}
    items['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    path=OUT/'source-proof.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,v in sorted(items.items()):
            assert not n.endswith(('.nes','.fds','.o','.dbg','.lbl','.bin'))
            info=zipfile.ZipInfo(n,(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,v,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path)as z:
        assert z.testzip()is None
        for n,r in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
    result=dict(passed=True,component_only=True,native=False,installed=False,menu_admitted=False,complete=False,archive=str(path.relative_to(ROOT)).replace('\\','/'),archive_sha256=sha(path),archive_bytes=path.stat().st_size,members=len(items),source_paths=[str(p.relative_to(ROOT)).replace('\\','/')for p in code],kernel_bytes=assembly['kernel_bytes'],remaining_before_cookie=assembly['remaining_before_BFE0'],external_inputs=external,scope='Original constructor/native static terrain component only; next graft is authenticated owner transport, remaining source callbacks, graphics and lifecycle/ISR/native admission. No playable claim.')
    (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':main()
