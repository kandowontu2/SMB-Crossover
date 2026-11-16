"""Read-only linked Sunny extent census after the broad-range negative."""
from pathlib import Path
from unittest.mock import patch
import json
import current_sunny_stock_bc5_1115 as Current

def run(raw):
    assert Current.digest(raw)==Current.PIN
    old=Current.HISTORICAL_ROM.read_bytes();assert Current.digest(old)==Current.HISTORICAL
    b=dict(Current.W.Symbols.bundle(),raw=raw);rows=[]
    names=('SunnyCoreBegin','SunnyCoreEnd','SunnyNativeMovement','SunnyCollectIntegrated','SunnyColorsIntegrated','SunnyIntegrationPalette',
        'SunnyHead','SunnyBody','SunnyEnsure','SunnyReset','SunnyGraphicsIntegrated','SunnyDraw','SunnyArtBegin','SunnyArtEnd')
    for name in names:
        if name not in b['syms']:rows.append(dict(name=name,missing=True));continue
        sym=b['syms'][name];pc=Current.W.address(b,name);at=Current.W.location(b,name)
        size=int(sym.get('size','0'),0)
        rows.append(dict(name=name,PC=pc,file=at,bytes=size,old_equal=raw[at:at+size]==old[at:at+size]if size else None,
            current_first16=raw[at:at+16].hex(),old_first16=old[at:at+16].hex(),segment=sym.get('seg')))
    at=16+81*8192+0x1200;diff=[i for i in range(0x500)if raw[at+i]!=old[at+i]];ranges=[]
    for i in diff:
        if ranges and i==ranges[-1][1]:ranges[-1][1]+=1
        else:ranges.append([i,i+1])
    edits=[dict(PC=0xb200+lo,file=at+lo,bytes=hi-lo,old=old[at+lo:at+min(hi,lo+32)].hex(),current=raw[at+lo:at+min(hi,lo+32)].hex())for lo,hi in ranges]
    q=dict(ROM_SHA256=Current.PIN,retained_Sunny_ROM_SHA256=Current.HISTORICAL,Sunny_symbols=rows,broad_core_changed_bytes=len(diff),
        broad_core_changed_ranges=edits,scope='Read-only source/ROM census; no preservation conclusion or CPU gameplay',outputs=0,Mesen=False)
    q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*a,**k):raise AssertionError('Sunny extent census attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
