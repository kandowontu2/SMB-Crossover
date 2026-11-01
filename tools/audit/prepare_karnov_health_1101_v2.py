"""Link only new health/death bytes against read-only current Karnov symbols."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
O=ROOT/'build/karnov-health-component-1101-v2';BASE=ROOT/'build/karnov-host-resource-base-1101-v1'
SRC=ROOT/'tools/reference/karnov_health_1101_v2.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes');text=SRC.read_text()
    imported=[]
    for line in text.splitlines():
        if line.startswith('.import '):imported+=line[8:].split(',')
    context=['KrState','KrReady','KrHaveEpoch','KrLastEpoch','GameEngineSubroutine','GamePauseStatus','FrameCounter','Player_Y_Position','Player_Y_HighPos','Player_X_Position','Player_PageLoc','Player_X_Speed','Player_X_Scroll','Player_Y_Speed','Player_State','Block_Buffer_1','Block_Buffer_2','KrSoundCallback','KrSourceFrame']
    start=address(b,'KrKernelEnd')
    (O/'component.s').write_text('.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in context)+'.segment "HEALTH"\n.include "karnov_health_1101_v2.inc"\n')
    (O/'host-symbols.s').write_text(''.join(f'.export {n}=${address(b,n):04x}\n'for n in imported))
    (O/'component.cfg').write_text(f'MEMORY{{LAB:start=${start:04x},size=${0xbfe0-start:04x},file=%O;}}SEGMENTS{{HEALTH:load=LAB,type=ro;}}\n')
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    for name in ['component','host-symbols']:
        cmd=list(map(str,[cc/'ca65.exe','-g','-I',ROOT/'tools/reference',O/(name+'.s'),'-o',O/(name+'.o')]))
        guard=validate(cmd,O,cwd=ROOT);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    cmd=list(map(str,[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o',O/'host-symbols.o','-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl']))
    guard=validate(cmd,O,cwd=ROOT);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    labels={}
    for line in(O/'component.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:labels[m[2]]=int(m[1],16)
    result=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,base_ROM_sha256=sha(BASE/'candidate.nes'),origin=start,bytes=len((O/'component.bin').read_bytes()),available_before_BFE0=0xbfe0-start,labels=labels,required_new_host_exports=imported,existing_kernel_symbols=context,private_scratch=[0xc839,0xc83a],services={5:'KrHealthInjury',6:'KrHealthStatus',7:'KrHealthDeathStart',8:'KrHealthDeathUpdate'},AXYP_contract='5/7/8 preserveAXYP exceptC1handled/C0rejected;6 returnsA0or1/NZ with XY/CVDI preserved. R0..R7 unchanged; source frame borrows/restores3/4 only. Four caller stack bytes; no nested full KrColors save.',commands=commands,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),SRC,BASE/'candidate.nes',BASE/'candidate.dbg',ROOT/'tools/audit/private_build_outputs_v1.py',cc/'ca65.exe',cc/'ld65.exe',O/'component.s',O/'host-symbols.s',O/'component.cfg',O/'component.bin',O/'component.dbg',O/'component.lbl']})
    (O/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','commands','labels']}))
if __name__=='__main__':main()
