"""Compile only the new Ice Climbers leaf in the existing assembler context.

No live hooks/canonical output changes. A small temporary entry file appends
the owned module to the current shared entrypoint; ROOT owns final dispatch.
"""
from pathlib import Path
import configparser,hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];B=R/'build'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    cp=configparser.ConfigParser();cp.optionxform=str;cp.read(R/'build_options.ini')
    defs={k:v for section in cp.values()for k,v in section.items()}
    defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    base=R/'src/entrypoint.s';entry=B/'ice-climbers-leaf-entry.s'
    assert b'ice_climbers.s'not in base.read_bytes(),'ROOT already integrated; use actual ROOT build controls instead'
    entry.write_bytes(base.read_bytes()+b'\n.include "ice_climbers.s"\n')
    obj=B/'ice-climbers-leaf.o';cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(R),'-I',str(R/'src'),'-I',str(B),'--bin-include-dir',str(R),'-o',str(obj)]
    for k,v in defs.items():cmd+=['-D',k+'='+v]
    cmd+=[str(entry)]
    z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);log=B/'ice-climbers-leaf-compile.txt';log.write_text(z.stdout+z.stderr,encoding='utf-8')
    proof=dict(passed=z.returncode==0,source_only=True,native_run=False,live_hooks=False,command=cmd,log=str(log),bindings={str(p):sha(p)for p in[Path(__file__),base,entry,*sorted((R/'src').glob('ice_climbers*')),*sorted((R/'chr/characters').glob('ice-climbers*'))]})
    out=B/'ice-climbers-leaf-compile.json';out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(z.stdout+z.stderr);print(json.dumps(dict(passed=proof['passed'],receipt=str(out))))
    assert z.returncode==0
if __name__=='__main__':main()
