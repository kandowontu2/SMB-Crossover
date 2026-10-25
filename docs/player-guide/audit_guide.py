"""Read-only verification of the final Astra edition and its reviewed renders."""
from pathlib import Path
import hashlib,json
def main():
    root=Path(__file__).resolve().parents[2]
    current=root/'Player Guide/Guide-Verification.json'
    qa=root/'build/verification/player-guide-astra-redesign'
    receipt=json.loads((current if current.exists()else qa/'final-validation.json').read_text())
    qa=Path(receipt.get('qa_directory',str(qa)))
    assert receipt['passed'] and receipt['standalone_rebuild']['exact_match']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name,record in receipt['outputs'].items():
        assert sha(root/'Player Guide'/name)==record['sha256'],name
    for group in ['renders','review_sheets']:
        for name,digest in receipt[group].items():assert sha(qa/name)==digest,name
    audit=root/'docs/player-guide/image-audit.json'
    assert sha(audit)==receipt['image_audit_sha256']
    assert all(x['source'] for x in json.loads(audit.read_text())['images'])
    print(f"Verified {receipt['pages']} pages, {len(receipt['review_sheets'])} review sheets and exact standalone PDF rebuild receipt.")
if __name__=='__main__':main()
