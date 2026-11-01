"""Assemble actual owning kernel plus the proposed C2 equipment component.

No ROM, cache header, existing build input or native session is changed.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_karnov_options_host_1101_v8 import transform_sources
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

O=R/'build/karnov-options-host-1101-v8';B=R/'build/karnov-host-resource-base-1101-v1'
PIN='0ffb1d79c4fbc52bb337a4726f8e61f984f30e4795fd2555b204322140c0a717'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    assert sha(B/'candidate.nes')==PIN
    b=scoped_load(B/'candidate.nes')
    q=transform_sources(kernel=(B/'kr-kernel.s').read_text(),resident=(B/'kr-resident.inc').read_text(),
        terrain=(B/'kr-terrain.inc').read_text(),config=(B/'candidate.cfg').read_text(),output=O,
        carrier_helper=(B/'kr-loader-carrier-v6.inc').read_text())
    for name,text in {**q['fragments'],'kr-kernel.s':q['kernel'],'kr-terrain.inc':q['terrain'],'resident-proposal.inc':q['resident']}.items():
        (O/name).write_text(text,encoding='utf-8',newline='\n')
    commands=[];cc=R/'tools/Windows/cc65/bin'
    def run(cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr))
        (O/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert p.returncode==0,p.stderr
    run([cc/'ca65.exe','-g','-I',O,'-I',B,'-I',R/'build/karnov-original-source-1101-v1/source',
         '-I',R/'build/karnov-original-weapons-1101-v1/source','--bin-include-dir',B,O/'kr-kernel.s','-o',O/'kernel.o'])
    imports=subprocess.run([str(cc/'od65.exe'),'--dump-imports',str(O/'kernel.o')],capture_output=True,text=True,check=True).stdout
    names=re.findall(r'Address size:\s+0x([0-9A-Fa-f]+)[^\n]*\n\s+Name:\s*"([^"]+)"',imports)
    assert names and len(names)==int(re.search(r'Count:\s+(\d+)',imports)[1])
    source='.setcpu "6502"\n';groups={}
    for size,name in names:
        value=address(b,name)
        if int(size,16)==1:source+=f'.exportzp {name}\n{name}=${value:04x}\n';continue
        bank=((location(b,name)-16)//8192)&127 if value>=0x8000 else 0
        groups.setdefault(bank,[]).append((name,value))
    for bank,values in groups.items():
        source+=f'.segment "NATIVE_{bank}"\nNativeBase{bank}:\n'
        for name,value in values:source+=f'.export {name}\n{name}=NativeBase{bank}+${value:04x}\n'
    (O/'bindings.s').write_text(source)
    cfg='MEMORY{\n'+''.join(f'{m}:start=${at:04x},size=${size:04x},bank={bank},file="{(O/name).as_posix()}",fill=yes,fillval=$ff;\n'
        for m,at,size,bank,name in [('K',0xa000,8192,3,'kernel.bin'),('C',0xc900,1280,2,'combat.bin'),('E',0xd600,2048,2,'options.bin')])
    cfg+=''.join(f'N_{bank}:start=0,size=0,bank={bank},file="";\n'for bank in groups)+'}\n'
    cfg+='SEGMENTS{KR_KERNEL:load=K,type=ro;KR_COMBAT_ROM:load=C,type=ro;KR_OPTIONS_ROM:load=E,type=ro;'+''.join(f'NATIVE_{bank}:load=N_{bank},type=ro;'for bank in groups)+'}\n'
    (O/'component.cfg').write_text(cfg)
    run([cc/'ca65.exe','-g',O/'bindings.s','-o',O/'bindings.o'])
    run([cc/'ld65.exe','-C',O/'component.cfg',O/'kernel.o',O/'bindings.o','-o',O/'unused.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl'])
    labels={m[2]:int(m[1],16)for m in re.finditer(r'(?m)^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text())}
    assert labels['KrKernelEnd']<=0xbfe0 and labels['KrOptionsEnd']<=0xde00
    result=dict(passed=True,component_only=True,native=False,installed=False,root_build_modified=False,
        parent_ROM_sha256=PIN,kernel_bytes=labels['KrKernelEnd']-0xa000,options_bytes=labels['KrOptionsEnd']-0xd600,
        source_clock='accepted E8 -> original0F',new_context=[0xc865],new_life_selection=255,same_life_cursor_retained=True,
        supported_options=[0,3,7],labels=labels,
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),R/'tools/audit/prepare_karnov_options_host_1101_v8.py',
            R/'tools/reference/karnov_options_1101_v7.inc',B/'candidate.nes',B/'candidate.dbg',
            *[p for p in O.iterdir()if p.is_file()and p.suffix not in ['.o','.dbg']and p.name!='assembly.json']]})
    (O/'assembly.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['passed','component_only','kernel_bytes','options_bytes','supported_options']}))


if __name__=='__main__':main()
