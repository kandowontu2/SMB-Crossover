"""Exact root-leased Bub pose palette change; memory-only portable inverse."""
from hashlib import sha256
import json
from pathlib import Path
import audit_bub_palette_40a_1115 as A

R,B,W,N,ROM=A.R,A.B,A.W,A.N,A.F.ROM
PARENT=A.PIN
CANDIDATE='174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4'
GRANT=R/'docs/qa/allocations/bub-native-palette-current-source-1115.json'
GRANT_SHA='0daf2ece6fb9511132716478580ac61ba3c9c248f919f440a5a0f083bbdcb59c'
AUDIT_SHA='0f381818fe9a8d5a56120fa009c814c6b76af720b25fddef65bd9e7f8328fcae'
COOKIE=536570
OLD_COOKIE=bytes.fromhex('a72702dac1da2fc79faa02b5b5381392')
EDITS=((1731082,'b902c1','203eb4'),(1731088,'b906c1','2038b4'),
    (1499208,'ff'*29,'b906c14c41b4b902c148ad00c3d00c684829034903d0046829fc606860'),
    (1501131,'1d','11'))
H=lambda b:sha256(b).hexdigest()

def allocation():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(A.__file__).read_bytes())==AUDIT_SHA
    q=json.loads(GRANT.read_text())
    assert tuple((x['file'],x['before'],x['after'])for x in q['logical_envelopes'])==EDITS
    assert q['owned_bytes']==52 and q['source_in_memory_composition_and_mounts_authorized']
    return q

def code(raw):return b''.join(raw[A.CH+p*1024:A.CH+(p+1)*1024]for p in B.PAGES)
def cookie(raw):return bytes((167,39,2))+sha256(code(raw)+raw[A.CH+441*1024:A.CH+442*1024]).digest()[:13]

def proposal(raw):
    allocation();assert isinstance(raw,bytes)and H(raw)==PARENT
    assert raw[COOKIE:COOKIE+16]==OLD_COOKIE
    out=bytearray(raw);own=set(range(COOKIE,COOKIE+16))
    for at,old,new in EDITS:
        old,new=bytes.fromhex(old),bytes.fromhex(new);assert raw[at:at+len(old)]==old and len(old)==len(new)
        out[at:at+len(new)]=new;own.update(range(at,at+len(old)))
    out[COOKIE:COOKIE+16]=cookie(out);out=bytes(out)
    assert len(own)==52 and all(a==b or i in own for i,(a,b)in enumerate(zip(raw,out)))
    assert H(out)==CANDIDATE
    return out,dict(parent=PARENT,candidate=H(out),logical_bytes=36,owned_bytes=52,
        changed_bytes=sum(a!=b for a,b in zip(raw,out)),cookie=out[COOKIE:COOKIE+16].hex(),
        granted_source_only=True,output_files=0)

def inverse(raw):
    allocation();assert isinstance(raw,bytes)and H(raw)==CANDIDATE
    assert raw[COOKIE:COOKIE+16]==cookie(raw)
    old=bytearray(raw)
    for at,before,after in EDITS:
        before,after=bytes.fromhex(before),bytes.fromhex(after);assert raw[at:at+len(after)]==after
        old[at:at+len(before)]=before
    old[COOKIE:COOKIE+16]=OLD_COOKIE;old=bytes(old)
    assert H(old)==PARENT and proposal(old)[0]==raw
    return old

if __name__=='__main__':
    raw,q=proposal(ROM.read_bytes())
    if CANDIDATE:assert proposal(inverse(raw))[0]==raw
    print(json.dumps(q,separators=(',',':')))
