"""Locate exact retained102 transition difference before changing its oracle."""
import json
from pathlib import Path
import check_dkjr_prince_cold_1103_v102 as T


def main():
    b,q=T.P.image();old,_=T.C.cold(b,37);expected,_=T.C.cold(b,38)
    T.C.fields(old,38);z=T.C.I.invoke(old,193,0xae00,(83,71,109,0x21));assert z['regs'][3]&1
    differences=[]
    for bank in [2,3]:
        items=[(i,a,c)for i,(a,c)in enumerate(zip(old.ram[bank],expected.ram[bank]))if a!=c]
        groups=[]
        for i,a,c in items:
            if not groups or i!=groups[-1]['half_open'][1]:groups.append(dict(half_open=[i,i+1],actual_hex=f'{a:02x}',expected_hex=f'{c:02x}'))
            else:groups[-1]['half_open'][1]=i+1;groups[-1]['actual_hex']+=f'{a:02x}';groups[-1]['expected_hex']+=f'{c:02x}'
        differences.append(dict(bank=bank,bytes=len(items),ranges=groups))
    out=dict(passed=True,diagnostic_only=True,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=T.A.sha(b['raw']),retained_negative='native-combined-cold-v102-negative.json',differences=differences,
        scope='Exact37→38 fullcold difference classification only; no weakened byte contract or runtime fix. Source ownership must explain every range before a successor acceptance test.',
        bindings={p.relative_to(T.R).as_posix():T.A.sha(p.read_bytes())for p in [Path(__file__),Path(T.__file__),T.O/'native-combined-owner-v101-measurement.json']})
    (T.O/'native-combined-transition-v103-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','diagnostic_only','differences']}))


if __name__=='__main__':main()
