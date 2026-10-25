"""Re-run unchanged MM/Bass native injury oracles around the shared cold end."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--diagnostic',action='store_true',help='Print the unchanged fixture endpoint counters')
    p.add_argument('--logic-endpoint',action='store_true',help='Wait for all75native immunity decrements within the unchanged160video-frame bound')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    bootstrap=ROOT/'tests/menu-bootstrap.lua';fixture=ROOT/'tests/megaman-bass-injury-202.lua'
    source=fixture.read_text()
    if a.diagnostic:
        anchor="  assert(invulSeen and invulLast==0 and invulDec==75,'Full1250ms post-recoil immunity expires independently of recoil')"
        assert source.count(anchor)==1
        source=source.replace(anchor,"  print('ENDPOINT age='..age..' moves='..moves..' invulSeen='..tostring(invulSeen)..' invulLast='..tostring(invulLast)..' invulDec='..invulDec)\n"+anchor)
    if a.logic_endpoint:
        anchor=' if age>=130 then\n';assert source.count(anchor)==1
        source=source.replace(anchor,' if age>=130 and(not invulSeen or invulLast==0)then\n')
    def run(char):
        out=a.output/str(char);out.mkdir()
        script=out/'run.lua';script.write_text(bootstrap.read_text()+'\nHURT_CHARACTER='+str(char)+'\n'+source)
        z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),
            '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT)
        (out/'host.log').write_text(z.stdout+z.stderr)
        return dict(character=char,passed=z.returncode==0,exit=z.returncode,script_sha256=sha(script),log_sha256=sha(out/'host.log'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:cases=list(pool.map(run,[1,9]))
    q=dict(passed=all(c['passed']for c in cases),ROM_sha256=sha(a.rom),cases=cases,
           fixture_sha256=sha(fixture),bootstrap_sha256=sha(bootstrap),
           endpoint_diagnostic=a.diagnostic,wait_for_75_native_decrements=a.logic_endpoint,
           scope='Independent source2.02 injury oracle:14explicit arenas per MM/Bass, ground/air/water/page seams/both facings,26locked updates,75update immunity, live world/input and actual original public-return caller preservation. Optional endpoint scheduling waits within the original160video-frame bound; movement, duration-count and input assertions remain unchanged. Seeded native components; not natural item delivery or campaign proof.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
