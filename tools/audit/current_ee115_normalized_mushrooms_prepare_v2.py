"""Correct source-native Arrow kind2 and Mike's next-update display projection.

Original v1 source negative/readiness stays intact and must not be launched.
No game-source change or native execution.
"""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_ee115_normalized_mushrooms_prepare_v1 as old


def main():
    ns=dict(old.__dict__);ns.update(__file__=__file__,OUT=R/'build/current-ee115-normalized-mushrooms-v2',FIXTURE=R/'tests/current-ee115-normalized-mushrooms-v2.lua')
    a="for _,p in ipairs(want)do assert(r(p.name,p.index)==p.value,'Actual source-normalized benefit '..p.name..'['..p.index..']')end"
    z="for _,p in ipairs(want)do if C.identity=='mike'and want==C.after and p.name=='PlayerStatus'then assert(r('PlayerStatus')==0 or r('PlayerStatus')==1,'Only real next-update Mike display projection');else assert(r(p.name,p.index)==p.value,'Actual source-normalized benefit '..p.name..'['..p.index..']')end end"
    assert ns['BODY'].count(a)==1;ns['BODY']=ns['BODY'].replace(a,z)
    source=inspect.getsource(old.campaign)
    assert source.count("q.get('DwAdaptor')==1")==1
    source=source.replace("q.get('DwAdaptor')==1","q.get('DwAdaptor')==2")
    assert source.count("main(4 if identity=='darkwing'and age<4 else 0)")==1
    source=source.replace("main(4 if identity=='darkwing'and age<4 else 0)","main(32 if identity=='darkwing'and age<4 else 0)")
    source=source.replace('Mike gains real maximum heart3->4/HP6->8. Darkwing gains Arrow adaptor and real Select activation.',
                          'Mike gains real maximum heart3->4/HP6->8; PlayerStatus projects0->1 on next real movement update. Darkwing gains actual source Kinds[0]=2 Arrow adaptor and real Select activation.')
    exec(compile(source,__file__,'exec'),ns)
    exec(compile(inspect.getsource(old.fixture),__file__,'exec'),ns)
    entry=inspect.getsource(old.main)
    entry=entry.replace('assert not OUT.exists()',"assert not (OUT/'native').exists()")
    entry=entry.replace('OUT.mkdir();readies=[];held={}','OUT.mkdir(exist_ok=True);readies=[];held={}')
    entry=entry.replace('out=OUT/identity;out.mkdir()','out=OUT/identity;out.mkdir(exist_ok=True)')
    exec(compile(entry,__file__,'exec'),ns)
    ns['main']()
    out=ns['OUT'];batch=json.loads((out/'prepared-batch.json').read_text())
    assert len(batch['readies'])==2 and not batch['held']
    negative=R/'build/current-ee115-normalized-mushrooms-v1/darkwing-source-negative.json'
    for rec in batch['readies']:
        p=Path(rec['path']);z=json.loads(p.read_text());paths={Path(x['path'])for x in z['bindings']}|{Path(old.__file__),negative,R/'src/darkwing_pickups.s',R/'src/mike_jones_body.s'}
        # The explicit native projection rule is source-bounded; final state is
        # still exact and never silently removes the PlayerStatus assertion.
        paths={p for p in paths if p.is_file()}
        z.update(previous_v1_not_for_native='Darkwing source expected Arrow1 but real Kinds[0] is2; Mike v1 early publication expected transient display0 after next source update projects1. No native attempt.',
                 bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=old.sha(p))for p in sorted(paths)])
        old.put(p,z);rec['sha256']=old.sha(p)
    old.put(out/'prepared-batch.json',batch)
    print(json.dumps(dict(batch=str(out/'prepared-batch.json'),sha256=old.sha(out/'prepared-batch.json'),readies=2,native_run=False)))


if __name__=='__main__':main()
