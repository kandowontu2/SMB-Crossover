"""Reproduce the exact current Kirby weapon source island before repair."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
O=R/'build/kirby-inhale-shell-fix-1101-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    q=json.loads((O/'current-witness.json').read_text());blob=(O/'current-kirby-code.bin').read_bytes();symbols=q['symbols'];segments=q['segments']
    source=(R/'src/kirby_weapons.s').read_text();assert sha(R/'src/kirby_weapons.s')==q['canonical_sources']['kirby_weapons.s']['sha256']
    abilities=next(s for s in segments if s['name']=='KIRBY_ABILITIES');actual=blob[abilities['witness_offset']:abilities['witness_offset']+abilities['bytes']]
    macros='''.setcpu "6502"
.macpack longbranch
.macro phx
 txa
 pha
.endmacro
.macro plx
 pla
 tax
.endmacro
.macro phy
 tya
 pha
.endmacro
.macro ply
 pla
 tay
.endmacro
'''
    # Only two original farcalls occur in this island. Preserve their exact
    # native ABI bytes, target/bank and callsite without pretending imported
    # absolute symbols have a ca65 bank attribute. These are external test
    # boundaries, not an invented farcall implementation.
    pat=rb'\x8d\x6a\x01\xa9.\x8d\x6c\x01\xa9.\x8d\x6d\x01\xa9.\x20\x5a\x01'
    calls=list(re.finditer(pat,actual[:0xbbd]));assert len(calls)==2,len(calls)
    for old,match in zip(['farcall KbInputs','farcall MegaManWeapons::Blocks'],calls):
        assert source.count(old)==1
        source=source.replace(old,'.byte '+','.join(f'${v:02x}'for v in match.group()))
    locals=set(re.findall(r'^\s*\.proc\s+(\w+)|^\s*(\w+):',source,re.M));localnames={n for row in locals for n in row if n}|{'I'}
    definitions=[]
    for name,s in symbols.items():
        if '::'in name or name in localnames or not re.fullmatch(r'[A-Za-z_]\w*',name):continue
        definitions.append(f'{name}=${int(s["val"],0):x}\n')
    (O/'baseline-weapons.inc').write_text(source)
    (O/'baseline.s').write_text(macros+''.join(definitions)+'.include "baseline-weapons.inc"\n')
    (O/'baseline.cfg').write_text('MEMORY{P:start=$a000,size=$2000,file=%O;}SEGMENTS{KIRBY_ABILITIES:load=P,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for cmd in[[cc/'ca65.exe','-g','-I',O,O/'baseline.s','-o',O/'baseline.o'],[cc/'ld65.exe','-C',O/'baseline.cfg',O/'baseline.o','-o',O/'baseline.bin','--dbgfile',O/'baseline.dbg']]:
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True)
        commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    emitted=(O/'baseline.bin').read_bytes();assert emitted==actual[:len(emitted)],next((i,a,b)for i,(a,b)in enumerate(zip(emitted,actual))if a!=b)
    assert len(emitted)==0xbbd
    report=dict(passed=True,source_CPU=False,native=False,host_modified=False,actual_source_island_bytes=len(emitted),exact_current_reproduction=True,
        external_farcall_boundaries=[dict(CPU=0xa000+m.start(),bytes=m.group().hex())for m in calls],commands=commands,
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'current-witness.json',O/'current-kirby-code.bin',R/'src/kirby_weapons.s',O/'baseline.s',O/'baseline.cfg',O/'baseline-weapons.inc',O/'baseline.bin',O/'baseline.dbg']})
    (O/'baseline-assembly.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['bindings','commands']}))
if __name__=='__main__':main()
