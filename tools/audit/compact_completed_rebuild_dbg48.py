"""Reversibly gzip DBGs from 17 successful old source rebuilds."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes
VERSIONS=('35a','36d','37c','38d','38e','39a','40c','41d','41e',
          '42b','42d','42e','43a','44a','45b','46a','47a')
OUT=ROOT/'build/verification/root-completed-rebuild-dbg48-compaction-b'

def sha(p,opener=open):
    digest=hashlib.sha256()
    with opener(p,'rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):digest.update(b)
    return digest.hexdigest()

def safe(p):
    p=p.resolve(strict=True)
    assert p.is_relative_to((ROOT/'build/checkpoint-tests').resolve())
    for q in (p,*p.parents):
        if q==ROOT:break
        assert not q.is_symlink()and not q.is_junction()
    return p

def main():
    assert not OUT.exists()
    canonical={}
    for p in (ROOT/'build/checkpoints').glob('*/smb-crossover-mmc[35].dbg'):
        canonical.setdefault(sha(p.with_suffix('.nes')),[]).append(p)
    targets=[]
    protected={}
    for version in VERSIONS:
        base=ROOT/f'build/checkpoint-tests/source-v{version}-rebuild-smoke'
        receipt=base/'report.json'
        report=json.loads(receipt.read_text())
        assert len(report['cases'])==2 and all(c['exit']==0 and c['equal']for c in report['cases'])
        for c in report['cases']:
            files=list(base.rglob(f"smb-crossover-{c['mapper']}.dbg"))
            assert len(files)==1
            p=safe(files[0])
            assert sha(p.with_suffix('.nes'))==c['sha256']
            digest=sha(p)
            controls=canonical[c['sha256']]
            assert controls
            cp=controls[0]
            assert not p.with_suffix('.dbg.gz').exists()
            targets.append(dict(path=p.relative_to(ROOT).as_posix(),raw_bytes=p.stat().st_size,
                raw_sha256=digest,canonical=cp.relative_to(ROOT).as_posix(),
                canonical_dbg_sha256=sha(cp),canonical_dbg_byte_identical=digest==sha(cp),
                canonical_rom_sha256=c['sha256'],report=receipt.relative_to(ROOT).as_posix(),
                report_sha256=sha(receipt)))
        for p in base.rglob('*'):
            if p.is_file()and p.suffix!='.dbg':protected[p.relative_to(ROOT).as_posix()]=sha(p)
    assert len(targets)==34 and len({r['path']for r in targets})==34
    selected={r['path']for r in targets}
    # Preserve extra baseline DBGs too; only the two exact guest copies per
    # successful rebuild are selected. No failed rebuild, route, or capture.
    for version in VERSIONS:
        base=ROOT/f'build/checkpoint-tests/source-v{version}-rebuild-smoke'
        for p in base.rglob('*.dbg'):
            if p.relative_to(ROOT).as_posix()not in selected:protected[p.relative_to(ROOT).as_posix()]=sha(p)
    OUT.mkdir()
    report=dict(completed=False,workspace_before=workspace_bytes(ROOT),allowlist=targets,
        entries=[],protected_files=protected,
        scope='Only34 guest DBGs from17 completed successful old source rebuilds. Canonical ROMs match; DBG byte differences remain explicit. Exact gzip round trips preserve each original. All failed rebuilds, current48 rebuild, routes, captures and canonical DBGs excluded.',
        prior_preflight_negative='build/verification/root-rebuild-dbg48-preflight-negative-a/report.json',
        restore='Exclusively create each original path by gzip decompression, verify raw_sha256, never overwrite existing files.')
    rp=OUT/'receipt.json'
    def save():rp.write_text(json.dumps(report,indent=2)+'\n')
    save()
    for row in targets:
        p=safe(ROOT/row['path'])
        assert sha(p)==row['raw_sha256']
        assert sha(ROOT/row['canonical'])==row['canonical_dbg_sha256']
        assert sha((ROOT/row['canonical']).with_suffix('.nes'))==row['canonical_rom_sha256']
        assert sha(ROOT/row['report'])==row['report_sha256']
        assert workspace_bytes(ROOT)+p.stat().st_size+16*1024*1024<30_000_000_000
        z=p.with_suffix('.dbg.gz')
        with p.open('rb')as src,gzip.open(z,'xb',compresslevel=6)as dest:
            for b in iter(lambda:src.read(1024*1024),b''):dest.write(b)
        assert sha(z,gzip.open)==row['raw_sha256']and z.stat().st_size<p.stat().st_size
        item=dict(**row,archive=z.relative_to(ROOT).as_posix(),archive_bytes=z.stat().st_size,
            archive_sha256=sha(z),status='verified-original-present')
        report['entries'].append(item)
        save()
        assert safe(p)==p and p.suffix=='.dbg'
        p.unlink()
        item['status']='losslessly-archived'
        save()
    assert all(sha(ROOT/n)==v for n,v in protected.items())
    assert all(sha(ROOT/r['archive'],gzip.open)==r['raw_sha256']for r in report['entries'])
    report.update(completed=True,protected_files_unchanged=True,workspace_after=workspace_bytes(ROOT),
        bytes_saved=sum(r['raw_bytes']-r['archive_bytes']for r in report['entries']),
        script_sha256=sha(Path(__file__)))
    save()
    print('PASS',len(targets),'lossless archives;',report['bytes_saved'],'bytes saved')

if __name__=='__main__':main()
