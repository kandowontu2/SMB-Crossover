"""Repair B's explicit bank-local InventoryHurt call, then build both maps."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-easy-injury-private-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not (H/'build-review-c.json').exists()
    b=H/'build-review-b.json'; original=json.loads(b.read_text())
    assert original['builds'][0]['exit']!=0
    source=H/'source/src/guest_injury.s'
    old=source.read_text(); assert old.count('farcall InventoryHurt')==1
    neg=H/'negative-b';neg.mkdir();(neg/'guest_injury.s').write_bytes(source.read_bytes())
    source.write_text(old.replace('farcall InventoryHurt','jsr InventoryHurt'))
    driver=(R/'tools/audit/build_easy49_injury_private_b.py').read_text()
    # Retain B and its failed sources/logs. Reuse its independently checked
    # driver binding, layout assertions and output hashing under a fresh report.
    driver=driver.replace("out=H/'build-review-b.json'","out=H/'build-review-c.json'")
    driver=driver.replace("original=json.loads((H/'report.json').read_text())", "original=json.loads((H/'report.json').read_text()); original['changes']['src/guest_injury.s']=sha(S/'src/guest_injury.s')")
    driver=driver.replace("mapper+'-build-b.log'","mapper+'-build-c.log'")
    driver=driver.replace("'initial_host_negative_sha256':", "'initial_host_negative_sha256':")
    driver=driver.replace("source_changes=original['changes'],builds=[]", "source_changes=original['changes'],bank_call_negative_sha256=sha(H/'build-review-b.json'),bank_call_negative_source_sha256=sha(H/'negative-b/guest_injury.s'),builds=[]")
    # B reports its own script through __file__; bind the actual executed C driver.
    saved=H/'build-driver-c.py';saved.write_text(driver)
    g={'__name__':'__main__','__file__':str(R/'tools/audit/build_easy49_injury_private_b.py')}
    exec(compile(driver,str(saved),'exec'),g)
if __name__=='__main__':main()
