"""Compose a Quick-only native-climb material adapter in its owned stream."""
from hashlib import sha256
import json
from pathlib import Path

from compose_metal_head_bridge_1112 import assemble_segments

R=Path(__file__).resolve().parents[2]
SOURCE=R/'tools/reference/quick_climb_material_1113.s'
CHR=16+128*8192
STREAM=CHR+884*1024
CODE_SIZE,DATA_SIZE=6541,1921
COPY_CODE,COPY_DATA=7168,2048
HOOK=0xb1a9
HELPER=0xa000+CODE_SIZE
OLD=bytes.fromhex('29014cb0b1')
OLD_COOKIE=bytes.fromhex('a7092005e731d952bdb4b950826271bc')
COOKIE_SITES=(0x8ca7d,0xa5d94) # Genuine QwCookie and QwLoadCookie.
LAYOUT={'WORLD_HOOK':HOOK,'CLIMB_MASK':HELPER}


def code():
    parts,_=assemble_segments(SOURCE.read_text(),LAYOUT,{'HostMaterial':0xb1b0})
    assert parts['WORLD_HOOK']==bytes.fromhex('208db9b002')
    assert parts['CLIMB_MASK']==bytes.fromhex('082903c901f002a9002860')
    return parts


def transform(raw):
    assert len(raw)==2097168
    stream=raw[STREAM:STREAM+COPY_CODE+COPY_DATA]
    payload=stream[:CODE_SIZE]+stream[COPY_CODE:COPY_CODE+DATA_SIZE]
    assert bytes.fromhex('a7092005')+sha256(payload).digest()[:12]==OLD_COOKIE
    assert stream[HOOK-0xa000:HOOK-0xa000+5]==OLD
    assert stream[CODE_SIZE:COPY_CODE]==bytes([255])*(COPY_CODE-CODE_SIZE)
    assert raw.count(OLD_COOKIE)==len(COOKIE_SITES)
    assert all(raw[at:at+16]==OLD_COOKIE for at in COOKIE_SITES)
    parts=code();result=bytearray(raw);edits=[]
    for name,pc in LAYOUT.items():
        at=STREAM+pc-0xa000;body=parts[name]
        result[at:at+len(body)]=body;edits.append(dict(name=name,file=at,size=len(body),PC=pc))
    used=CODE_SIZE+len(parts['CLIMB_MASK'])
    new_payload=result[STREAM:STREAM+used]+result[STREAM+COPY_CODE:STREAM+COPY_CODE+DATA_SIZE]
    cookie=bytes.fromhex('a7092006')+sha256(new_payload).digest()[:12]
    for at in COOKIE_SITES:
        result[at:at+16]=cookie;edits.append(dict(name='Quick source identity',file=at,size=16))
    allowed=set().union(*(set(range(e['file'],e['file']+e['size']))for e in edits))
    assert all(a==b or i in allowed for i,(a,b)in enumerate(zip(raw,result)))
    output=bytes(result)
    return output,dict(parent_SHA256=sha256(raw).hexdigest(),candidate_SHA256=sha256(output).hexdigest(),
        cookie=cookie.hex(),old_cookie=OLD_COOKIE.hex(),code_used=used,data_used=DATA_SIZE,
        copied_code_bytes=COPY_CODE,copied_data_bytes=COPY_DATA,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),edits=edits,
        changed_bytes=sum(a!=b for a,b in zip(raw,output)),allocation_growth=0,ROM_written=False)


def inverse(raw):
    result=bytearray(raw);parts=code()
    assert raw[STREAM+HOOK-0xa000:STREAM+HOOK-0xa000+5]==parts['WORLD_HOOK']
    assert raw[STREAM+CODE_SIZE:STREAM+CODE_SIZE+11]==parts['CLIMB_MASK']
    cookie=bytes.fromhex('a7092006')+sha256(raw[STREAM:STREAM+CODE_SIZE+11]+
        raw[STREAM+COPY_CODE:STREAM+COPY_CODE+DATA_SIZE]).digest()[:12]
    assert raw.count(cookie)==len(COOKIE_SITES)
    assert all(raw[at:at+16]==cookie for at in COOKIE_SITES)
    result[STREAM+HOOK-0xa000:STREAM+HOOK-0xa000+5]=OLD
    result[STREAM+CODE_SIZE:STREAM+CODE_SIZE+11]=bytes([255])*11
    for at in COOKIE_SITES:result[at:at+16]=OLD_COOKIE
    output=bytes(result);assert transform(output)[0]==raw
    return output


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    candidate,info=transform(raw);assert inverse(candidate)==raw
    print(json.dumps(info,separators=(',',':')))
