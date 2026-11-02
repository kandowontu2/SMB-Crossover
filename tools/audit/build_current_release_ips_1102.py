"""Build the public IPS from clean SMB World and verify exact reconstruction."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'build/current-release-ips-1102'
BASE=Path('C:/NES/Super Mario Bros. (World).nes')
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    a,b=BASE.read_bytes(),ROM.read_bytes()
    assert len(a)==40976 and a[:4]==b'NES\x1a'
    assert digest(b)=='f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
    patch=bytearray(b'PATCH');i=0
    while i<len(b):
        if i<len(a) and a[i]==b[i]:i+=1;continue
        start=i
        if start==0x454f46:start-=1
        i=max(i,start+1)
        while i<len(b) and i-start<65535 and (i>=len(a) or a[i]!=b[i]):i+=1
        patch+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+b[start:i]
    patch+=b'EOF'+len(b).to_bytes(3,'big')
    restored=bytearray(a);pos=5
    while patch[pos:pos+3]!=b'EOF':
        offset=int.from_bytes(patch[pos:pos+3],'big');size=int.from_bytes(patch[pos+3:pos+5],'big');pos+=5
        assert size>0
        if len(restored)<offset+size:restored.extend(bytes(offset+size-len(restored)))
        restored[offset:offset+size]=patch[pos:pos+size];pos+=size
    restored=restored[:int.from_bytes(patch[pos+3:pos+6],'big')]
    assert restored==b
    O.mkdir(exist_ok=True)
    (O/'SMB-Crossover-Latest-WIP-MMC5.ips').write_bytes(patch)
    q=dict(base=str(BASE),base_SHA256=digest(a),ROM_SHA256=digest(b),IPS_SHA256=digest(patch),IPS_bytes=len(patch),roundtrip=True)
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    (O/'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply the IPS to a clean, headered Super Mario Bros. (World) ROM.\nBase SHA-256: '+digest(a)+'\nPatched ROM SHA-256: '+digest(b)+'\n\nNovember 2: native helper platform enables verified full 1-1 clears for Hogan, DiBiase, Bigelow, Honky Tonk Man and Savage. Andre remains under testing. Includes prior playable character updates; full roster and all powerup verification remain in progress. The patch reconstructs the exact tested Downloads nightly.\n')
    print(json.dumps(q))
if __name__=='__main__':main()
