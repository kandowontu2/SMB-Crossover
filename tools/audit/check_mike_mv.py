"""Recheck frozen Mike components and native interactions after composition."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/mike-kd-private/handoff-Mike-core-m'
O=R/'build/verification/mike-adoption-mv'
P=O/'mike-final.nes'

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    raw=P.read_bytes();private=(R/'build/mike-kd-private/mike-m.nes').read_bytes()
    assert raw[16+98*8192:16+99*8192]==private[16+98*8192:16+99*8192]
    assert raw[16+97*8192:16+98*8192]==private[16+97*8192:16+98*8192]
    asset=(R/'chr/characters/mike-jones.chr').read_bytes()
    assert raw[16+1048576+708*1024:16+1048576+708*1024+len(asset)]==asset
    for name in ('test_owner_terrain','test_native_health'):
        file=D/'verification'/(name+'.py');text=file.read_text()
        text=text.replace("D=Path(__file__).resolve().parent",'D=Path('+repr(str(O))+')')
        text=text.replace("ROM=D/'mike-m.nes'",f'ROM=Path({str(P)!r})')
        text=text.replace("rom=D/(sys.argv[1]if len(sys.argv)>1 else'mike-j.nes')",f'rom=Path({str(P)!r})')
        if name=='test_owner_terrain':text=text[:text.index("Q=D/'qa-m'")]
        (O/(name+'.py')).write_text(text)
        exec(compile(text,str(file),'exec'),{'__file__':str(file),'__name__':'root_mike'})
    (O/'native-bank-and-CHR-proof.json').write_text(json.dumps(dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),combat98_and_art97_exact_private=True,CHR708_to711_exact_asset=True),indent=2)+'\n')
    s=importlib.util.spec_from_file_location('mv_runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    results={}
    for name in ('smoke-b','natural-c','arsenal-c','arsenal-left-e','fatal-b'):
        folder=O/name;folder.mkdir(exist_ok=True);script=folder/(name+'.lua')
        script.write_text((D/'verification/qa-m'/(name+'.lua')).read_text());runner.ROOT=folder
        results[name]=runner.run(script,P,timeout=45)
        (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n')
        assert results[name]==0,name
    print('PASS Mike composed source components and all5 native interaction fixtures')

if __name__=='__main__':main()
