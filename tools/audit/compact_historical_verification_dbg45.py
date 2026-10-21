"""Reversibly compress exact checkpoint-matching, completed verification DBGs."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'build/verification/historical-dbg-inventory-20261018/inventory.json'
OUT=ROOT/'build/verification/root-historical-verification-dbg-compaction45'
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes

def sha(p,opener=open):
    h=hashlib.sha256()
    with opener(p,'rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def safe(n,namespace):
    p=ROOT/n
    assert p.resolve(strict=True).is_relative_to(ROOT/namespace) and p.resolve(strict=True)==p.absolute()
    for q in (p,*p.parents):
        if q==ROOT:break
        assert not q.is_symlink() and not q.is_junction()
    return p

def main():
    assert sha(PLAN)=='9c2de79792f33b2f692b6c89f39c84e686eb2cb479165f09db82cd847df32de1'
    data=json.loads(PLAN.read_text())
    targets=[q for q in data['rows']if q['scope']=='verification'and q['category']=='completed-success-exact-pair-review-only']
    assert len(targets)==159 and not OUT.exists()
    paths={safe(q['path'],'build/verification')for q in targets};assert len(paths)==159
    # Creator identity was not recorded historically. Root now authorizes this
    # reversible management of generated outputs under the user's workspace-cap
    # goal; this does not invent or alter the old inventory's ownership fields.
    OUT.mkdir()
    (OUT/'explicit-allowlist.json').write_text(json.dumps(targets,indent=2)+'\n')
    protected={p for parent in {p.parent for p in paths}for p in parent.iterdir()if p.is_file()and p not in paths}
    for q in targets:
        c=q['canonical'];protected.add(safe(c['rom'],'build/checkpoints'));protected.add(safe(c['dbg'],'build/checkpoints'))
    originals={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(protected)}
    before=workspace_bytes(ROOT);assert before<30_000_000_000
    report=dict(completed=False,inventory_sha256=sha(PLAN),workspace_before=before,entries=[],protected_files=originals,
        authorization_basis='User explicitly requires workspace under30GB; root selects reversible compression of this goal generated completed verification outputs. Historical creator remains unknown; byte-identical archive and canonical copies are independently verified.',
        live_state='Root checked no Mesen processes immediately before this operation; all selected native runs have completion receipts. Current agents perform isolated read-only preparation.',
        exclusions='All routes including previous rejected deletion scope, all canonical raw DBG files,84 held raw negatives,114 older profiling copies, source snapshots and current44/45/component records.',
        restore='To restore an original path, exclusively create it from gzip.open(archive,rb), verify raw_sha256; never overwrite an existing file.')
    receipt=OUT/'receipt.json'
    def save():receipt.write_text(json.dumps(report,indent=2)+'\n')
    save()
    for i,q in enumerate(targets,1):
        path=safe(q['path'],'build/verification');c=q['canonical']
        assert path.suffix=='.dbg' and path.stat().st_size==q['bytes'] and path.stat().st_mtime_ns==q['mtime_ns_at_inventory']
        assert sha(path)==q['sha256']==c['dbg_sha256']
        assert sha(safe(q['adjacent_rom'],'build/verification'))==q['rom_sha256']==c['rom_sha256']
        assert sha(safe(c['rom'],'build/checkpoints'))==c['rom_sha256'] and sha(safe(c['dbg'],'build/checkpoints'))==c['dbg_sha256']
        assert q['completion_status']=='completed-success-bound-ROM-exit-and-PASS'
        for ev in q['completion_evidence']:
            assert sha(ROOT/ev['metadata'])==ev['metadata_sha256']
            log=ev['completion_log'];assert sha(ROOT/log['path'])==log['sha256'] and log['PASS_line_present']and not log['negative_line_present']
        archive=path.with_suffix('.dbg.gz');assert not archive.exists()
        # One new compressed file at a time;64MiB margin also covers the small
        # receipt and the agents' bounded text-only preparation output.
        if i%16==1:assert workspace_bytes(ROOT)+path.stat().st_size+64*1024*1024<30_000_000_000
        with path.open('rb')as src,gzip.open(archive,'xb',compresslevel=6)as dst:
            for block in iter(lambda:src.read(1048576),b''):dst.write(block)
        assert sha(archive,gzip.open)==q['sha256'] and archive.stat().st_size<path.stat().st_size
        row=dict(path=q['path'],archive=str(archive.relative_to(ROOT)),raw_bytes=q['bytes'],raw_sha256=q['sha256'],
            archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),canonical=c,status='roundtrip-verified-raw-still-present')
        report['entries'].append(row);save()
        assert path.resolve(strict=True).is_relative_to(ROOT/'build/verification')
        path.unlink() # Single explicit compiled duplicate; gzip+canonical both verified.
        row['status']='replaced-with-lossless-archive';save()
        if i%20==0:print('Verified',i,'of159 exact debug archives',flush=True)
    for n,q in originals.items():assert (ROOT/n).stat().st_size==q['bytes']and sha(ROOT/n)==q['sha256'],n
    assert all(sha(ROOT/q['archive'],gzip.open)==q['raw_sha256']for q in report['entries'])
    report.update(completed=True,protected_files_unchanged=True,workspace_after=workspace_bytes(ROOT),
        raw_bytes=sum(q['raw_bytes']for q in report['entries']),archived_bytes=sum(q['archive_bytes']for q in report['entries']))
    report['bytes_saved']=report['raw_bytes']-report['archived_bytes'];save()
    assert report['workspace_after']<30_000_000_000
    print('PASS',report['bytes_saved'],'bytes saved;',len(originals),'protected files unchanged',flush=True)

if __name__=='__main__':main()
