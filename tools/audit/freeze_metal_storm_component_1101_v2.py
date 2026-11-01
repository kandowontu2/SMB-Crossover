"""Freeze only this Metal Storm component's exact source/proof files."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/metal-storm-component-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not(OUT/'source-stage.json').exists()
    receipts={n:json.loads((OUT/n).read_text())for n in ['assembly.json','CPU-controls.json','art.json']}
    for q in receipts.values():
        assert q['passed']
        for p,h in q['bindings'].items():assert sha(p)==h,p
    sources=[ROOT/'tools/audit'/n for n in ['metal_storm_cpu_1101_v2.py','prepare_metal_storm_source_1101_v2.py','recover_metal_storm_actor_1101_v2.py','check_metal_storm_actor_1101_v2.py','prepare_metal_storm_art_1101_v2.py','freeze_metal_storm_component_1101_v2.py']]
    sources+=[ROOT/'tools/reference/metal_storm_component_1101_v2.md']
    files=sources+[p for p in OUT.rglob('*')if p.is_file()]
    assert len(files)<64 and sum(p.stat().st_size for p in files)<5_000_000
    archive=OUT/'source-proof.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)).replace('\\','/'))
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(files)
        for p in files:assert hashlib.sha256(z.read(str(p.relative_to(ROOT)).replace('\\','/'))).hexdigest()==sha(p)
    result=dict(passed=True,component='Metal Storm original actor/art source',native=False,installed=False,menu_admitted=False,donor_sha256=receipts['assembly.json']['donor_sha256'],source_proof_sha256=sha(archive),source_proof_bytes=archive.stat().st_size,source_proof_members=len(files),actor_pairs=receipts['CPU-controls.json']['actor_pairs'],portable_bytes=receipts['CPU-controls.json']['portable_bytes'],art_contexts=receipts['art.json']['contexts'],CHR_bytes=receipts['art.json']['CHR_bytes'],borrowed_ZP_laboratory_only=[0,1],required_host_R0_R1=[3,4],interrupt_safety=False,next_hook='Pending Sophia slot11/FmAltsbit2; resources and typed runtimeID must be assigned first. Replace laboratory pointer with3/4; adapt10 explicit source APIs, projectile updates/earned upgrades/audio and real native lifecycle before admission.',handoff='tools/reference/metal_storm_component_1101_v2.md',bindings={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in files})
    (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))

if __name__=='__main__':main()
