"""Freeze the completed body repair proof without emitting a ROM."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_body_backing_1103_v180 as M
import build_storage_guard_v1 as G
O=M.O


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=200000,reserved_files=3,fresh=True)
    base,manifest=M.image()
    assert hashlib.sha256(base['raw']).hexdigest()==manifest['expected_memory_only_SHA256']
    receipts=['measurement.json','renderer-CPU-v179.json','renderer-source-CPU-v181.json',
              'source-cold-CPU-v181.json','reader-flag-CPU-v182.json','body-ISR-v183.json']
    checked=0
    for name in receipts:
        q=json.loads((O/name).read_text())
        assert q.get('passed',q.get('measured',False)),name
        for name,digest in q.get('bindings',{}).items():
            assert sha(R/name)==digest,name
            checked+=1
    sources=[R/'tools/audit'/name for name in [
        'measure_prince_body_owner_1103_v178.py','check_prince_body_owner_1103_v179.py',
        'prepare_prince_body_backing_1103_v180.py','check_prince_body_cold_1103_v181.py',
        'check_prince_body_reader_1103_v182.py','check_prince_body_isr_1103_v183.py',
        Path(__file__).name]]
    generated=[O/name for name in [
        'body-owner.s','body-owner.cfg','body-owner.bin','body-owner.lbl',
        'body-runtime.bin','body-metadata.bin','body-worker.s','body-worker.cfg',
        'body-worker.bin','body-worker.lbl','body-pool.bin','body-manifest-v180.json',
        'source-cold-prefix-v181.json','renderer-negative-v179.json','source-cold-negative-v181.json',
        *receipts]]
    files=sources+generated
    assert len(files)==len(set(files))
    archive=O/'body-source-v184.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(files)
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    result=dict(passed=True,status='SOURCE_QUALIFIED_NATIVE_DEFERRED_FOR_MINI_PRIORITY',
        ROM_written=False,emulator_run=False,source_code_injected=False,
        parent_SHA256=manifest['parent_SHA256'],memory_SHA256=manifest['expected_memory_only_SHA256'],
        Prince_cookie=manifest['Prince_cookie'],archive=str(archive.relative_to(R)),
        archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),
        direct_receipt_bindings_checked=checked,
        reconstruction='prepare_prince_body_backing_1103_v180.image() validates exact source bindings and returns the full image only in memory.',
        physical_scope='Existing44 Prince carriers and exact16B PRG65 ABA9 cookie data. All current83 shared instructions/pointers/selector/Sh exact.',
        tests='Actual four-owner cold;16 transitions;128 header poisons;Fresh15/36;408 original poses/2578 parts/82496 pattern bytes;actual A132/C201 late-reader;256 OAM/CV inputs;38IRQ/38 genuineFF and777 nested winners, minimumSP126.',
        scope_annotations=[
            'Inherited179 wording refers to the original159 component. Current181/182/183 reconstruction parent is exact granted80d3 current83.',
            'Inherited181 pending late-reader/IRQ text is closed by182/183 here. Native hardware body, gameplay, armed combat and audio remain unqualified/deferred.',
            'All38 reached changed-seam foreground cuts were I0. No fabricated I1 coverage; FF harness requires actual lag branch/INC and excludes regular branch.',
            'Native176/177 four-zero-body-parts failure remains authoritative negative; no new Mesen success is claimed.'
        ],bindings={str(p.relative_to(R)):sha(p)for p in files})
    (O/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
