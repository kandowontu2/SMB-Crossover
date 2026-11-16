"""Read-only current Bowser owning-code/menu census; no old build recovery."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import json
import current_sunny_stock_live_bc5_1115 as Boundary
import check_bowser_natural_powerups_1113 as Cold

W,N=Cold.W,Cold.N
def run(raw):
    Boundary.reference(raw);b=dict(W.Symbols.bundle(),raw=raw);rows=[]
    names=('BwImage','BwCacheServices','BwCoreBegin','BwCoreEnd','BwMovement','BwCoreFinish','BwWeaponTail','BwPickup',
        'BwConstruct','BwEnsure','BwPowerupTick','Bw3Step','Bw1Step','BwLoad','BwCheck','BwScene','BwCookie','BwStream')
    for name in names:
        if name not in b['syms']:rows.append(dict(name=name,missing=True));continue
        pc=W.address(b,name);sym=b['syms'][name]
        try:at=W.location(b,name);data=raw[at:at+16]
        except Exception:at=None;data=b''
        rows.append(dict(name=name,PC=pc,file=at,size=sym.get('size'),segment=sym.get('seg'),first16=data.hex()))
    openings=[]
    for identity in(0,1):
        m,opening=Cold.cold(raw,identity)
        assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        runtime=bytes(m.ram[3]);functions=[]
        for name in names:
            if name not in b['syms']:continue
            pc=W.address(b,name)
            if not 0xa000<=pc<0xc000 or name in('BwLoad','BwCheck','BwScene'):continue
            size=int(b['syms'][name].get('size','0'),0)
            functions.append(dict(name=name,PC=pc,bytes=size,first16=runtime[pc&8191:(pc&8191)+16].hex(),SHA256=sha256(runtime[pc&8191:(pc&8191)+size]).hexdigest()if size else None))
        openings.append(dict(identity=identity,opening=opening,runtime_SHA256=sha256(runtime).hexdigest(),cookie=runtime[0x1fe0:0x1ff0].hex(),functions=functions))
    q=dict(passed=True,ROM_SHA256=Boundary.PIN,typed_inverse_reference67=Boundary.Original.REFERENCE,rows=rows,openings=openings,
        scope='Actual compiled menu/Start/parser/cold constructor, no stock acquisition/fullstage claim; source bus lacks real title vblank',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest();return q

if __name__=='__main__':
    raw=Boundary.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Bowser census attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
