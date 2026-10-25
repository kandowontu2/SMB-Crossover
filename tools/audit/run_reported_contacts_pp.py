"""One native worker runs explicit reported-contact diagnostics, externally."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--names',nargs='+',default=['kirby','mike','sypha']);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    syms={}
    for line in a.rom.with_suffix('.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            z=dict(v.split('=',1) for v in line[4:].split(',') if '=' in v)
            if 'val' in z:syms[z['name'].strip('"')]=int(z['val'],0)
    aliases=''.join('L['+json.dumps(n)+']='+str(v)+'\n' for n,v in syms.items() if n.startswith(('Kb','Jn','Cv3')))
    results={}
    for name in a.names:
        folder=a.output/name;folder.mkdir();slot,addr,variant={'kirby':(12,0,0),'mike':(15,0,0),'sypha':(5,syms['Cv3Variant'],2)}[name]
        script=folder/'run.lua';script.write_text(aliases+f'NAME={json.dumps(name)}\nTARGET_SLOT={slot}\nVARIANT_ADDRESS={addr}\nVARIANT={variant}\n'+(ROOT/'tools/audit/fixtures/reported_contacts_native_pp.lua').read_text())
        args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(script),str(a.rom.resolve()),
            '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
        z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(folder/'host.log').write_text(z.stdout+z.stderr)
        results[name]=dict(exit=z.returncode,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest());print(name,z.returncode,(z.stdout+z.stderr)[-1000:],flush=True)
        (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(q['exit']==0 for q in results.values()),results
if __name__=='__main__':main()
