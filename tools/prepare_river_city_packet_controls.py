"""Actual linked seven-cell status-name contract; retains first-leaf negative."""
from pathlib import Path
import argparse,hashlib,json
from prepare_river_city_controls import fresh,scoped_load,address,location

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def check(rom):
    b=scoped_load(rom);rows=[]
    at=location(b,'TopStatusBarLine')
    packet=b['raw'][at:at+40]
    assert packet[:11]==bytes.fromhex('23c07faa23c201ea204307')
    assert packet[18:21]==bytes.fromhex('20520b')
    for variant in (0,1):
        text_at=location(b,'RcStatusName::AlexText' if variant==0 else 'RcStatusName::RyanText')
        text=b['raw'][text_at:text_at+7]
        assert text==bytes([10,21,14,33,36,36,36] if variant==0 else [27,34,10,23,36,36,36])
        for sentinel in (0x20,0xd7):
            q=fresh(b,variant);base=address(b,'VRAM_Buffer1')
            q.m[base:base+84]=list(packet)+[0xa5]*(84-len(packet))
            q.m[base+18]=sentinel
            before=bytes(q.m[base:base+84])
            c,trace=q.invoke('RcStatusName',a=0,x=0x37,y=0x5a)
            after=bytes(q.m[base:base+84])
            writes=[r['address']-base for r in trace if base<=r['address']<base+84]
            rows.append(dict(variant=variant,sentinel=sentinel,writes=writes,
              seven_cells_exact=after[11:18]==text,
              outside_unchanged=after[:11]==before[:11]and after[18:]==before[18:],
              no_write_outside_name=sorted(writes)==list(range(11,18)),
              real_return_Y_SP_A=(c.y==0x5a and c.sp==0xfd and c.a==0)))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();original=check(a.original);fixed=check(a.rom)
    assert all(not r['no_write_outside_name'] for r in original)
    assert all(all(r[k]for k in ('seven_cells_exact','outside_unchanged','no_write_outside_name','real_return_Y_SP_A')) for r in fixed)
    assert all(not r['outside_unchanged'] for r in original)
    proof=dict(passed=True,native_run=False,original=original,corrected=fixed,
      note='Native charmap encodes space as24. Original eighth space overwrites next WORLD command high byte20 with24. Exact write ownership and final packet/sentry bytes both reject it.',
      bindings=[dict(path=str(f),sha256=sha(f))for f in (a.original,a.original.with_suffix('.dbg'),a.rom,a.rom.with_suffix('.dbg'),Path(__file__))])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(fixed),original_negative=len(original),output=str(a.output))))

if __name__=='__main__':main()
