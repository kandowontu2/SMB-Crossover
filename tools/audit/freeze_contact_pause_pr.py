"""Freeze/rebuild the combined candidate from source only; no live adoption."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/checkpoints/grant-grip-pm'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--expected-sha256',required=True);a=p.parse_args();LIVE=a.candidate
    a.output.mkdir(parents=True,exist_ok=False);parent=json.loads((PARENT/'manifest.json').read_text())
    assert sha(PARENT/'candidate.nes')==parent['rom_sha256'] and sha(PARENT/'source.zip')==parent['source_zip_sha256']
    assert sha(LIVE/'candidate.nes')==a.expected_sha256
    sources={p.relative_to(LIVE/'source').as_posix():p for p in (LIVE/'source').rglob('*') if p.is_file()}
    changes={}
    for n,path in sources.items():
        if n.startswith(('src/','chr/')) or n.endswith('.cfg'):
            old=parent['source_files'].get(n)
            if sha(path)!=old:
                assert (not (ROOT/n).exists()) if old is None else sha(ROOT/n)==old,n
                changes[n]=dict(before=old,after=sha(path))
    assert len(changes)>10,changes
    for suffix in ['pn','po','pp','pq','pr','ps']:
        sources.update({p.relative_to(ROOT).as_posix():p for p in (ROOT/'tools/audit').glob('*_'+suffix+'.py')})
    sources.update({p.relative_to(ROOT).as_posix():p for p in (ROOT/'tools/audit/fixtures').glob('*_p[prqs].*')})
    names=sorted(sources);hashes={n:sha(sources[n]) for n in names};archive=a.output/'source.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in names:z.write(sources[n],n)
    stage=a.output/'source'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist())==set(hashes)
        assert all((stage/n).resolve().is_relative_to(stage.resolve()) for n in z.namelist());z.extractall(stage)
    command=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    previous=json.loads((ROOT/'build/verification/grant-grip-pm/proof.json').read_text())
    ordinary=previous['ordinary_flag_off_hashes'];builds={}
    for target in ['expanded','mmc3','mmc5']:
        out=a.output/(target+'.nes');args=command+['--output',str(out)]
        if target!='expanded':args+=['--flag-off',target]
        z=subprocess.run(args,cwd=stage,capture_output=True,text=True);(a.output/(target+'.log')).write_text(z.stdout+z.stderr)
        assert z.returncode==0,(target,(z.stdout+z.stderr)[-2000:])
        builds[target]=sha(out)
        assert builds[target]==(sha(LIVE/'candidate.nes') if target=='expanded' else ordinary[target]),target
    assert all(sha(stage/n)==h for n,h in hashes.items())
    packed=gzip.compress((LIVE/'candidate.dbg').read_bytes(),mtime=0);(a.output/'candidate.dbg.gz').write_bytes(packed)
    q=dict(passed=True,accepted=False,goal_complete=False,parent_ROM_sha256=parent['rom_sha256'],
        ROM_sha256=builds['expanded'],source_files=hashes,source_zip_sha256=sha(archive),changes=changes,
        builds=builds,source_only_roundtrip_exact=True,debug_gzip_sha256=sha(a.output/'candidate.dbg.gz'),
        compiler_sha256=sha(ROOT/'tools/Windows/cc65/bin/cl65.exe'),driver_sha256=sha(Path(__file__)))
    (a.output/'packet.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,source_files=len(hashes),changes=list(changes),builds=builds)),flush=True)
if __name__=='__main__':main()
