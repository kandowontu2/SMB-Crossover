"""One sequential Mesen queue for six wrestlers and the whole-menu regression."""
from pathlib import Path
import argparse,json,subprocess,sys
import prepare_wwf_roster_native_bounded_v1 as W
import prepare_wwf_menu_native_bounded_v1 as M


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['prepare','run']);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--joint',type=Path);ap.add_argument('--expected');a=ap.parse_args();o=a.output.resolve()
    names=['hogan','dibiase','bigelow','honky','savage','andre','menu']
    if a.action=='prepare':
        assert a.joint and a.expected;o.mkdir(exist_ok=True)
        for v,n in enumerate(names):
            sys.argv=['prepare','--joint',str(a.joint),'--output',str(o/n),'--expected',a.expected]
            if v<6:sys.argv+=['--variant',str(v)];W.main()
            else:M.main()
    else:
        results=[]
        for n in names:
            print('NATIVE '+n,flush=True)
            p=subprocess.run([sys.executable,str(o/n/'run.py')]);assert p.returncode==0,(n,p.returncode)
            q=json.loads((o/n/'capture/result.json').read_text());assert q['passed'],(n,q.get('reason'))
            results.append(dict(name=n,passed=q['passed'],ROM=q['ROM_sha256'],frames=q['frames'],Main=q.get('main_updates'),reason=q['reason']))
            print(json.dumps(results[-1]),flush=True)
        (o/'suite-results.json').write_text(json.dumps(dict(passed=True,native=True,runs=results),indent=2)+'\n')


if __name__=='__main__':main()
