"""Read-only authenticated authored 1UP placement census; no CPU/game seeds."""
from pathlib import Path
from hashlib import sha256
import json,re

R=Path(__file__).resolve().parents[2]
PINS={'aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe','7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0'}

def run(raw):
    pin=sha256(raw).hexdigest();assert pin in PINS
    source=(R/'src/level_tiles.s').read_text();rows=[];stage=None;label=None;data=bytearray()
    def finish():
        if not label or not data or data[-1]!=253:return
        blob=bytes(data);page=0
        for i in range(2,len(blob)-1,2):
            a,b=blob[i:i+2];row=a&15
            if b&128:page+=1
            if row==13 and not b&64:page=b&31;continue
            if row>=12 or b&112 or b&15 not in(3,8):continue
            count=raw.count(blob);at=raw.find(blob)
            rows.append(dict(level=stage,label=label,object_byte_offset=i,object_hex=blob[i:i+2].hex(),
                kind='hidden1UP'if b&15==3 else'brick1UP',world_x=page*256+(a>>4)*16,world_y=32+row*16,
                source_bytes=len(blob),source_SHA256=sha256(blob).hexdigest(),actual_blob_occurrences=count,
                actual_file_offset=at if count==1 else None))
    for line in source.splitlines():
        if line.startswith(';level '):stage=line[len(';level '):].strip()
        found=re.match(r'^(L_(?:Ground|Underground)Area\d+):',line)
        if found:
            finish();label=found[1];data=bytearray()
        elif label:
            if'.byte'in line:
                data.extend(int(v,16)for v in re.findall(r'\$([\da-fA-F]{2})',line.split(';')[0]))
                if data and data[-1]==253:finish();label=None;data=bytearray()
            elif re.match(r'^[A-Za-z_][A-Za-z_0-9]*:',line):label=None;data=bytearray()
    known=[x for x in rows if x['label']=='L_GroundArea6'and x['kind']=='hidden1UP']
    assert len(known)==1 and(known[0]['world_x'],known[0]['world_y'])==(1024,128)and known[0]['actual_blob_occurrences']==1
    q=dict(passed=True,ROM_SHA256=pin,source_rows=rows,
        scope='Static authored object coordinates only; rendering flags, support and gameplay reachability unqualified',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest();return q

if __name__=='__main__':print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),separators=(',',':')),flush=True)
