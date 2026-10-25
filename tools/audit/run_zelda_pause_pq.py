"""Run the real pause screen and retain physical PPU images externally."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    dbg=a.rom.with_suffix('.dbg').read_text() if a.rom.with_suffix('.dbg').exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    syms={}
    for line in dbg.splitlines():
        if line.startswith('sym\t'):
            z=dict(v.split('=',1) for v in line[4:].split(',') if '=' in v)
            if 'val' in z:syms[z['name'].strip('"')]=int(z['val'],0)
    aliases=''.join('L['+json.dumps(n)+']='+str(v)+'\n' for n,v in syms.items() if n.startswith('Z2') or n=='X5ChrMode')
    script=a.output/'run.lua';script.write_text(aliases+(ROOT/'tools/audit/fixtures/zelda2_pause_native_pq.lua').read_text())
    args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),
        '--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(a.output/'host.log').write_text(z.stdout+z.stderr)
    print((z.stdout+z.stderr)[-2500:]);return z.returncode
if __name__=='__main__':raise SystemExit(main())
