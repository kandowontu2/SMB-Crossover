"""Freeze compact semantic adapters/receipts; exclude all compiled lab code."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/metal-storm-host-contract-1101-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not(OUT/'source-stage.json').exists(),'Qualified component is immutable'
    receipts=['assembly.json','CPU-controls.json','host-contract.json'];external={}
    for name in receipts:
        q=json.loads((OUT/name).read_text());assert q['passed']
        for p,h in q['bindings'].items():assert sha(p)==h,p;external[p]=h
    sources=[ROOT/'tools/audit'/f'{n}_metal_storm_host_{t}_1101_v4.py'for n,t in[]]
    sources=[ROOT/p for p in['tools/audit/build_metal_storm_host_contract_1101_v4.py','tools/audit/check_metal_storm_host_contract_1101_v4.py','tools/audit/audit_metal_storm_host_resources_1101_v4.py','tools/audit/freeze_metal_storm_host_contract_1101_v4.py','tools/reference/metal_storm_host_contract_1101_v4.inc','tools/reference/metal_storm_menu_contract_1101_v4.inc','tools/reference/metal_storm_host_contract_1101_v4.md']]
    members={p.relative_to(ROOT).as_posix():p.read_bytes()for p in sources}
    members.update({'proof/'+n:(OUT/n).read_bytes()for n in receipts});members['assets/body-meta.bin']=(OUT/'body-meta.bin').read_bytes()
    handoff='''# Metal Storm host-contract component v4

Original actor6323B rebased to A3:A000/C2:C000 and foreground03/04;
323B real host step/input/240Y/delta adapters;45B cold raw35/menu-bit leaves;
1002B exact compact original-body metadata. Kernel6759B before cookie.

480 original/rebased/typed-step comparisons (1440 executions), both gravity
directions, all256 inputs,65536 signedY cases,896 resolve/start cases each,
480 duplicate/pause cases each and208 original graphics packet/order cases
pass. Current NES input is queued AFTER the source step, preserving original
one-update polling latency. Original bound07E4 is2020, not just low byte228.

No native admission. External tile/scene/platform/object/audio effects are
recorded/replayed, not implemented host callbacks. Constructor, source shots,
upgrades/health, native cache/header/ISR/SMC/Main stack, palette/OAM and stage
routes remain. The14 proposed CHR pages and extra resident ROM have NO grant.

See tools/reference/metal_storm_host_contract_1101_v4.md and proof/host-contract.json.
The original semantic source stays in the already frozen v3 packet; compiled
lab objects remain external at build/metal-storm-host-contract-1101-v4.
No complete PRG, ROM, code image, object, debug or symbol output is published.
'''
    members['handoff.md']=handoff.encode()
    manifest=dict(passed=True,component_only=True,native=False,installed=False,menu_admitted=False,members={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())for n,b in members.items()},external_laboratory_root=str(OUT.resolve()),external_bindings=external,excluded=['ROM/full PRG','compiledkernel.bin/cold.bin','objects/debug/symbols','original actor copy/dependency trees'],scope='Compact tested source-contract publication; no resource grant or playable/native admission.')
    mb=(json.dumps(manifest,indent=2)+'\n').encode();members['manifest.json']=mb
    target=OUT/'source-proof.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(members.items()):z.writestr(name,data)
    for p,h in external.items():assert sha(p)==h,p
    (OUT/'handoff.md').write_text(handoff);(OUT/'manifest.json').write_bytes(mb)
    stage=dict(passed=True,qualified_component=True,native=False,installed=False,menu_admitted=False,source_packet=dict(path=str(target.resolve()),sha256=sha(target),bytes=target.stat().st_size,members=len(members)),manifest_sha256=hashlib.sha256(mb).hexdigest(),source_files=[str(p.relative_to(ROOT))for p in sources],scope='Source/adapters and source-CPU/metadata evidence frozen. Lab bytes are not admitted native code; no source callback, resource, menu readiness or nightly change.')
    (OUT/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n');print(json.dumps(stage))
if __name__=='__main__':main()
