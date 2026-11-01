"""Compile original ctor/contact leaves and native terrain adapter, isolated."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
from py65.disassembler import Disassembler
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
OUT=ROOT/'build/metal-storm-terrain-host-1101-v5'
OLD=ROOT/'build/metal-storm-host-contract-1101-v4'
NATIVE=ROOT/'build/karnov-host-resource-base-1101-v1/candidate.nes'
EXPECTED='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
REF=ROOT/'tools/reference/metal_storm_terrain_host_1101_v5.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[(0x911b,0x9130),(0x9371,0x93ed),(0x9431,0x944a),(0xe2c4,0xe324),(0xda71,0xda80)]
INSIDE=lambda a:any(lo<=a<hi for lo,hi in SPANS)
TABLES=[(0x8ae8,0x8b09),(0x8b4b,0x8b8d)]

def source():
    c=M.machine();c.memory.regs[6:8]=[0,1];c.memory.map();d=Disassembler(c)
    result=[];code={}
    for lo,hi in SPANS:
        p=lo
        while p<hi:
            n,t=d.instruction_at(p);mn,mode=c.disassemble[c.memory[p]]
            assert t!='???';a=c.memory[p+1]+(256*c.memory[p+2]if n==3 else 0)if n>1 else None
            code[p]=dict(size=n,text=t,bytes=list(c.memory[p:p+n]),mnemonic=mn,mode=mode,operand=a)
            if mode=='rel':
                target=(p+2+(a if a<128 else a-256))&65535;assert INSIDE(target)
                t='j'+mn.lower()[1:]+f' MsCtor_{target:04X}'
            elif mode in['abs','abx','aby','zpg','zpx','zpy','inx','iny','ind']:
                if mn in['JSR','JMP']:
                    target=f'MsCtor_{a:04X}'if INSIDE(a)else 'MsNativePlacement'if a==0x944a else f'Ms_{a:04X}'
                    assert INSIDE(a)or a in[0x944a,0xb08f],hex(a)
                else:
                    target=f'MsCtor_{a:04X}'if any(lo<=a<hi for lo,hi in TABLES)else f'MsState+${a:04x}'
                old=re.search(r'\$[0-9a-fA-F]+',t);assert old;t=t[:old.start()]+target+t[old.end():]
            result.append(f'MsCtor_{p:04X}: {t} ; original ${p:04x}')
            p+=n
        assert p==hi
        #9371 pure state phase ends immediately before8874's indirect map script.
        if hi==0x93ed:result.append(' rts ; native boundary before donor scene script8874')
    for lo,hi in TABLES:
        for a in range(lo,hi):result.append(f'MsCtor_{a:04X}: .byte ${c.memory[a]:02x}')
    result+=['MsNativeFF33=MsCtor_E2C4','MsNativeFF36=MsCtor_E2E7','MsNativeFF3F=MsCtor_DA71']
    return '\n'.join(result)+'\n',code

def main():
    assert sha(NATIVE)==EXPECTED
    b=scoped_load(NATIVE);OUT.mkdir(exist_ok=True)
    native=['Block_Buffer_1','BlockBufferAddr','MTileAttribute','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']
    old=json.loads((OLD/'assembly.json').read_text())
    # Qualified original/v4 sources are external read-only inputs, not copied.
    wrapper=(OLD/'kernel.s').read_text();wrapper=wrapper[:wrapper.index('.segment "COLD"')]
    for api,target in[('FF1E','MsNativeTileQuery'),('FF33','MsNativeFF33'),('FF36','MsNativeFF36'),('FF3F','MsNativeFF3F')]:
        oldline='.import MsExternal_'+api;assert wrapper.count(oldline)==1
        wrapper=wrapper.replace(oldline,'MsExternal_'+api+'='+target)
    wrapper+='\n.include "donor-leaves.inc"\n.include "metal_storm_terrain_host_1101_v5.inc"\n'
    donor,code=source();(OUT/'donor-leaves.inc').write_text(donor)
    (OUT/'terrain.s').write_text(wrapper)
    (OUT/'terrain.cfg').write_text('MEMORY{CODE:start=$a000,size=$1fe0,file=%O;}SEGMENTS{CODE:load=CODE,type=ro;}\n')
    fields={**old['native_symbols'],**{n:address(b,n)for n in native}}
    symbols=''.join(f'.export {n}=${v:04x}\n'for n,v in fields.items())
    symbols+=''.join(f'.export {n}=${v:04x}\n'for n,v in old['callbacks'].items()if n.rsplit('_',1)[1]not in['FF1E','FF33','FF36','FF3F'])
    (OUT/'symbols.s').write_text(symbols)
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    for cmd in[[cc/'ca65.exe','-g','-I',ROOT/'build/metal-storm-component-1101-v2/source','-I',ROOT/'tools/reference','-I',OUT,OUT/'terrain.s','-o',OUT/'terrain.o'],[cc/'ca65.exe',OUT/'symbols.s','-o',OUT/'symbols.o'],[cc/'ld65.exe','-C',OUT/'terrain.cfg',OUT/'terrain.o',OUT/'symbols.o','-o',OUT/'terrain.bin','--dbgfile',OUT/'terrain.dbg','-Ln',OUT/'terrain.lbl']]:
        cmd=list(map(str,cmd));guard=validate(cmd,OUT,cwd=ROOT);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    labels={}
    for line in(OUT/'terrain.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:labels[m[2]]=int(m[1],16)
    size=len((OUT/'terrain.bin').read_bytes())
    deps=[Path(__file__),REF,Path(M.__file__),M.ROM,NATIVE,NATIVE.with_suffix('.dbg'),OLD/'kernel.s',OLD/'assembly.json',ROOT/'tools/reference/metal_storm_host_contract_1101_v4.inc',ROOT/'build/metal-storm-component-1101-v2/source/portable-actor.inc',ROOT/'tools/audit/verify_native_relocation.py',ROOT/'tools/audit/private_build_outputs_v1.py',cc/'ca65.exe',cc/'ld65.exe',OUT/'terrain.s',OUT/'donor-leaves.inc',OUT/'symbols.s',OUT/'terrain.cfg',OUT/'terrain.bin',OUT/'terrain.dbg',OUT/'terrain.lbl']
    result=dict(passed=True,component_only=True,native=False,installed=False,admitted=False,ROM_sha256=EXPECTED,source_spans=SPANS,constructor_table_bytes=99,recovered_instructions=len(code),kernel_origin=0xa000,kernel_bytes=size,bytes_if_rebased_A000=size,remaining_before_BFE0=8160-size,donor_leaf_bytes=labels['MsNativeTileQuery']-labels['MsHostContractEnd'],native_adapter_bytes=labels['MsTerrainHostEnd']-labels['MsNativeTileQuery'],source_fields=fields,labels=labels,callbacks=old['callbacks'],commands=commands,bindings={str(p.resolve()):sha(p)for p in deps})
    (OUT/'assembly.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in['labels','commands','bindings','source_fields']}))
if __name__=='__main__':main()
