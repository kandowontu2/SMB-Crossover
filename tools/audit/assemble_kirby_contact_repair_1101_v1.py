"""Assemble the isolated, genuinely source-funded Kirby repair."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_kirby_inhale_shell_fix_1101_v1 import labels
O=R/'build/kirby-inhale-shell-fix-1101-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    src=(O/'fixed-source.s').read_text();base=json.loads((O/'baseline-assembly.json').read_text());native=json.loads((O/'native-box-witness.json').read_text())
    for old,call in zip(['farcall KbInputs','farcall MegaManWeapons::Blocks'],base['external_farcall_boundaries']):
        assert src.count(old)==1;src=src.replace(old,'.byte '+','.join(f'${v:02x}'for v in bytes.fromhex(call['bytes'])))
    prefix=(O/'baseline.s').read_text().split('.include "baseline-weapons.inc"')[0]
    prefix+=f'Enemy_BoundBoxCtrl=${native["globals"]["Enemy_BoundBoxCtrl"]:x}\nBoundBoxCtrlData=${native["rows"]["BoundBoxCtrlData"]["CPU"]:x}\n'
    (O/'fixed-weapons.inc').write_text(src);(O/'fixed.s').write_text(prefix+'.include "fixed-weapons.inc"\n');(O/'fixed.cfg').write_text((O/'baseline.cfg').read_text())
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for cmd in[[cc/'ca65.exe','-g','-I',O,O/'fixed.s','-o',O/'fixed.o'],[cc/'ld65.exe','-C',O/'fixed.cfg',O/'fixed.o','-o',O/'fixed.bin','--dbgfile',O/'fixed.dbg']]:
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    l=labels(O/'fixed.dbg');size=(O/'fixed.bin').stat().st_size;delta=size-3005
    r=dict(passed=True,production_modified=False,native=False,old_weapons_bytes=3005,fixed_weapons_bytes=size,net_growth=delta,projected_full_abilities_bytes=8188+delta,capacity=8192,source_funding_fits=8188+delta<=8192,helper_bytes=size-(l['KbShellEnemyContact']-0xa000),labels=l,commands=commands,
      bindings={str(x.resolve()):sha(x)for x in[Path(__file__),R/'tools/audit/check_kirby_inhale_shell_fix_1101_v1.py',O/'fixed-source.s',O/'baseline.s',O/'baseline-assembly.json',O/'native-box-witness.json',O/'fixed-weapons.inc',O/'fixed.s',O/'fixed.cfg',O/'fixed.bin',O/'fixed.dbg']})
    (O/'fixed-assembly.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in['bindings','commands','labels']}))
if __name__=='__main__':main()
