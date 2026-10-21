"""Accept narrowly resolved B layout references, preserving the failed B guard."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49o2-bill-shape-b-layout-c'
SOURCE=ROOT/'build/verification/root49o2-bill-shape-private-b/source'
C=ROOT/'build/verification/agent49o2-bill-shape-relocation-review-c'
B=ROOT/'build/verification/agent49o2-bill-jump-shape-proposal-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(C/'freeze.json')=='a1f3dc630f04a6ddb3d5773b536965152db8b7040a86088aaca4185943e695d7'
    for name,pin in json.loads((C/'freeze.json').read_text())['files'].items():
        assert sha(C/name)==pin['sha256']and (C/name).stat().st_size==pin['bytes']
    failed=ROOT/'build/verification/root49o2-bill-shape-private-b-driver.log'
    assert "AssertionError: ('DPCM/post-DPCM/vectors exact', 'mmc3')" in failed.read_text()
    manifest=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2/manifest.json'
    original=json.loads(manifest.read_text())['source_hashes'];assert len(original)==409
    overlay=json.loads((B/'contract.json').read_text())['materialization']
    expected=dict(original)
    for row in overlay:expected[row['path']]=row['after']['sha256']
    assert len(expected)==410 and all(sha(SOURCE/n)==h for n,h in expected.items())
    current=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json'
    shared=json.loads(current.read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in shared.items())
    OUT.mkdir()
    for script in ('review.py','layout_supplement.py'):
        with (OUT/(script+'.log')).open('wb')as f:
            r=subprocess.run([sys.executable,str(C/script)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        assert r.returncode==0
    builds={}
    for mapper,baseline in [('mmc3',False),('mmc5',False),('mmc3',True)]:
        name='smb-crossover-'+mapper+('-baseline'if baseline else'')
        files={}
        for ext in ('nes','dbg','lbl','map'):
            p=(SOURCE/'build'/name).with_suffix('.'+ext)
            files[ext]=dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
        rom=(SOURCE/'build'/name).with_suffix('.nes')
        if baseline:assert sha(rom)=='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
        else:
            a=ROOT/'build/verification/root49o2-bill-shape-private-a/source/build'/rom.name
            assert rom.read_bytes()==a.read_bytes()
        text=(SOURCE/'build'/name).with_suffix('.map').read_text()
        segments={m[0]:dict(start=int(m[1],16),end=int(m[2],16),size=int(m[3],16))
                  for m in re.findall(r'^([A-Z_0-9]+)\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+([0-9A-F]{6})\s+[0-9A-F]+\s*$',text,re.M)}
        builds[name]=dict(outputs=files,segments=segments)
    archive=OUT/'source-bill-shape-b.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name in sorted(expected):z.write(SOURCE/name,name)
        z.writestr('archived-file-hashes.json',json.dumps(expected,indent=2)+'\n')
    assert all(sha(SOURCE/n)==h for n,h in expected.items())and all(sha(ROOT/n)==h for n,h in shared.items())
    refs={n:dict(path=(C/n).relative_to(ROOT).as_posix(),sha256=sha(C/n))
          for n in ('freeze.json','actual-review.json','actual-layout-supplement.json','revised-invariant.json')}
    report=dict(status='PASS_PRIVATE_B_BUILD_AND_NARROW_C_LAYOUT_REVISION_ONLY',accepted_release=False,goal_complete=False,
                script_sha256=sha(Path(__file__)),original_B_guard_remains_failed=True,
                original_B_failure=dict(path=failed.relative_to(ROOT).as_posix(),sha256=sha(failed)),
                source410_hashes=expected,source_archive_sha256=sha(archive),builds=builds,layout_references=refs,
                root_assessment='The only post-DPCM deltas are resolved operands of two unchanged Samus continuation JMPs and two unchanged scoped vector targets. DPCM data, remaining tail and IRQ literal. Exact compiled Start/NMI operand relocations resolve to original scoped targets. Accept this explicit revised invariant for private component validation only; no broad relocation allowance.',
                qualification='Original A/B guards and negatives retained. No build rerun, CPU/native/interrupt/ABI or corrected ordinary trajectory inferred. Fractional source projection, cache/pose/lifecycle/water/Firebar/art obligations remain. Shared current-P source and outputs untouched.')
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],sha(OUT/'report.json'))

if __name__=='__main__':main()
