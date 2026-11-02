"""Bind Downloads smoke, create matching IPS and verify its reconstruction."""
import hashlib,json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from nightly_patch_guard_v1 import check

def main():
    out=R/'build/thomas-delivery-1102-v3';p=out/'downloads-smoke'
    d=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    pin='d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d'
    ready=json.loads((p/'ready.json').read_text());binding=json.loads((p/'capture/binding.json').read_text())
    result=json.loads((p/'capture/result.json').read_text())
    assert result['passed'] and binding['exit_code']==0 and binding['ROM_sha256']==sha(d)==pin
    assert binding['ready_sha256']==sha(p/'ready.json') and Path(ready['ROM'])==d
    for name,h in ready['bindings'].items():assert sha(name)==h,name
    guard=check(d)
    base=Path('C:/NES/Super Mario Bros. (World).nes')
    assert sha(base)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
    a,b=base.read_bytes(),d.read_bytes();patch=bytearray(b'PATCH');i=0
    while i<len(b):
        if i<len(a) and a[i]==b[i]:i+=1;continue
        start=i if i!=0x454f46 else i-1;i=max(i,start+1)
        while i<len(b) and i-start<65535 and (i>=len(a) or a[i]!=b[i]):i+=1
        patch+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+b[start:i]
    patch+=b'EOF'+len(b).to_bytes(3,'big')
    restored=bytearray(a);pos=5
    while patch[pos:pos+3]!=b'EOF':
        at=int.from_bytes(patch[pos:pos+3],'big');size=int.from_bytes(patch[pos+3:pos+5],'big');pos+=5
        assert size>0;restored.extend(bytes(max(0,at+size-len(restored))))
        restored[at:at+size]=patch[pos:pos+size];pos+=size
    restored=restored[:int.from_bytes(patch[pos+3:pos+6],'big')];assert restored==b
    (out/'SMB-Crossover-Latest-WIP-MMC5.ips').write_bytes(patch)
    q=json.loads((out/'delivery.json').read_text());q.update(downloads_launch_verified=True,latest_patch_guard=guard,IPS_SHA256=hashlib.sha256(patch).hexdigest(),IPS_roundtrip=True,
        verification_scope='Exact candidate Thomas full1-1, six native helper crossings, no life loss; actual Downloads cold menu/lives/first assisted crossing and IRQ/NMI pass. Other characters/all powerups/both modes remain incomplete.')
    (out/'published-receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    (out/'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply to clean headered Super Mario Bros. (World).\nBase SHA256: '+sha(base)+'\nROM SHA256: '+pin+'\n\nThomas now clears non-shortcut1-1 into1-2 without life loss, using native helper lifts at leftX400/560/688/864/2560/2816, initialY192 (width32; centers+16). Both late crossings verified. Actual Downloads cold launch and first helper crossing verified. Existing Bub/Bob and prior roster retained. Full roster/all powerups qualification remains ongoing.\n')
    print(json.dumps(q))

if __name__=='__main__':main()
