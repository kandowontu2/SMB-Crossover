"""Retain the four reviewed private host units while their common spine is merged.

This archives source and bounded evidence, not ROM/debug binaries, and makes no
new gameplay-admission claim. A stale independent Maaa debug artifact is recorded.
"""
from pathlib import Path
import hashlib,json,re,zipfile

ROOT=Path(__file__).resolve().parents[2]
UNITS=['dk-admission-review-v2','goku-admission-review-v2','gimmick-nmi-menu-v1','supermaaa-host-v1']
TARGET=ROOT/'docs/qa/checkpoints/2026-10-30/reviewed-private-hosts'
ALLOWED={'.s','.inc','.cfg','.c','.chr','.bin','.py','.lua','.json','.txt','.md','.csv','.png','.d','.patch'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(v,out):
    if isinstance(v,dict):
        if 'path'in v and'sha256'in v:out[v['path']]=v['sha256']
        for k,z in v.items():
            if isinstance(k,str)and isinstance(z,str)and re.fullmatch('[a-f0-9]{64}',z)and k.lower().startswith('c:'):out[k]=z
            else:rows(z,out)
    elif isinstance(v,list):
        for z in v:rows(z,out)


def main():
    assert not TARGET.exists(),'Preserve frozen checkpoint';files={Path(__file__)};reports=[]
    for unit in UNITS:
        folder=ROOT/'build'/unit;hp=folder/'handoff.json';data=json.loads(hp.read_text());bound={};rows(data,bound);stale=[]
        for name,expected in bound.items():
            p=Path(name);actual=sha(p)if p.is_file()else None
            if actual!=expected:
                assert p==ROOT/'build/supermaaa-host-v1/independent.dbg','Unexpected changed input: '+name
                stale.append(dict(path=name,expected=expected,actual=actual,scope='Independent debug output only; candidate ROM/DBG/LBL and source inputs remain exact.'))
            else:files.add(p)
        deps={}
        for dep in folder.rglob('*.d'):
            raw=dep.read_text()
            if ':\t'not in raw:continue
            rhs=raw.split(':\t',1)[1].splitlines()[0].strip().removesuffix(':')
            for word in re.split(r'(?<!\\)\s+',rhs):
                p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else ROOT/p).resolve()
                assert p.is_file(),str(p);deps[str(p)]=sha(p);files.add(p)
            files.add(dep)
        for group in ['owned_files','owned_tools']:
            for p in data.get(group,[]):files.add(Path(p['path']if isinstance(p,dict)else p))
        # Newly reviewed unit-local code and small receipts retain their paths.
        files|={p for p in folder.rglob('*')if p.is_file()and p.suffix in ALLOWED and p.stat().st_size<=5_000_000}
        files.add(hp)
        reports.append(dict(unit=unit,handoff_sha256=sha(hp),verified_bindings=len(bound)-len(stale),
                            retained_stale_artifacts=stale,actual_ASM_dependencies=deps,status=data.get('status',data.get('passed'))))
    composition=ROOT/'build/character-host-union-review-v1'
    files|={p for p in composition.iterdir()if p.is_file()and p.suffix in ALLOWED}
    TARGET.mkdir(parents=True);members={};omitted=[]
    with zipfile.ZipFile(TARGET/'frozen-source-packet.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):
            if not p.is_relative_to(ROOT)or p.suffix not in ALLOWED:continue
            if p.stat().st_size>5_000_000:omitted.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size));continue
            b=p.read_bytes();n=p.relative_to(ROOT).as_posix();info=zipfile.ZipInfo(n,(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b);members[n]=hashlib.sha256(b).hexdigest()
    with zipfile.ZipFile(TARGET/'frozen-source-packet.zip')as z:assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    report=dict(status='Reviewed private sources/evidence retained; not newly admitted to shared gameplay',units=reports,
                archive_sha256=sha(TARGET/'frozen-source-packet.zip'),members=members,large_bound_evidence_not_copied=omitted,
                limits='Original finite CPU/native receipts retain their exact ROM scope. Full shared integration and final all-character/all-item campaign remain open.')
    (TARGET/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(units=len(reports),source_files=len(members),archive_bytes=(TARGET/'frozen-source-packet.zip').stat().st_size,stale_debug_artifacts=sum(len(x['retained_stale_artifacts'])for x in reports))))


if __name__=='__main__':main()
