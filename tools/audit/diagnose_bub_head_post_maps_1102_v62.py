"""Locate the first expanded post-head mapper return mismatch; no ROM change."""
import json
from pathlib import Path
import check_bub_head_nmi_i1_1102_v60 as H
O,N,R,sha=H.O,H.N,H.R,H.sha

def main():
    text=H.text.replace('if active or bank==3 and newlo<=c.pc<newhi:','if active or headreturn is not None or bank==3 and newlo<=c.pc<newhi:')
    before="assert ins in[bytes.fromhex(x)for x in['8d1551','8d1651','8e1651']]";assert text.count(before)==1
    text=text.replace(before,before+",('Post-head map window',interrupt,maps,m.rawtags,hex(c.pc),ins.hex(),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),low)")
    env=dict(H.env);exec(compile(text,str(Path(__file__)),'exec'),env);run=env['run']
    _,b,route,q,p,_=H.P.H.bundle();m,_=H.seeds(b,route)[0];reference=run(N.fork(m),p,q)
    for index,cut in enumerate(reference['cuts'][3000:],start=3000):
        z=N.fork(m)
        try:run(z,p,q,('lagNMI',cut))
        except Exception as error:
            out=dict(passed=False,diagnostic=True,ROM_written=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],identity=0,index=index,cut=cut,exception=repr(error),native_maps=z.rawtags,CurrentBank=N.get(z,'CurrentBank'),CurrentBankC=N.get(z,'CurrentBankC'),sound={n:N.get(z,n)for n in['Square1SoundQueue','Square2SoundQueue','Squ1_SfxLenCounter','Squ2_SfxLenCounter','Sfx_SecondaryCounter']},bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(H.__file__),O/'head-projection-v55.json']})
            (O/'head-projection-v62-map-negative.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));return
    raise AssertionError('Expected retained post-head mismatch was not reproduced')

if __name__=='__main__':main()
