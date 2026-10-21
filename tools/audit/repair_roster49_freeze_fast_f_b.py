"""Retain the first branch-range failure and regenerate with a long branch."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-freeze-render-fast-f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    n=H/'compile-negative-a';r=json.loads((n/'receipt.json').read_text())
    for name,h in r['files'].items():assert sha(n/name)==h,name
    old=json.loads((H/'preparation.json').read_text())
    for name,h in old['source_hashes'].items():assert sha(H/'source'/name)==h,name
    assert not(H/'preparation-b.json').exists()
    p=R/'tools/audit/build_roster49_freeze_fast_f.py';code=p.read_text()
    anchors={"assert not H.exists();H.mkdir()":"assert H.exists()",
      "'preparation.json'":"'preparation-b.json'", "(stem+'.log')":"(stem+'-b.log')"}
    for a,b in anchors.items():assert a in code,a;code=code.replace(a,b)
    adapter=H/'repair-adapter-b.py';adapter.write_text(code)
    (H/'repair-preparation-b.json').write_text(json.dumps(dict(status='PREPARED_BRANCH_RANGE_REPAIR',
      script_sha256=sha(__file__),original_builder_sha256=sha(p),adapter_sha256=sha(adapter),
      failed_preparation_sha256=sha(H/'preparation.json'),negative_receipt_sha256=sha(n/'receipt.json'),
      only_gameplay_source_repair='bne Scan becomes jne Scan; same loop predicate, long branch encoding.',main_changed=False),indent=2)+'\n')
    exec(compile(code,str(p),'exec'),dict(__file__=str(p),__name__='__main__'))
if __name__=='__main__':main()
