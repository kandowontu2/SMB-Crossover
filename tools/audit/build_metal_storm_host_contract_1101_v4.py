"""Rebase frozen original actor onto proposed native C2/A3/R0 resources.

Isolated component only: no shared edits, ROM, native loader or menu admission.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from private_build_outputs_v1 import validate
OUT=ROOT/'build/metal-storm-host-contract-1101-v4'
OLD=ROOT/'build/metal-storm-component-1101-v2'
PACK=ROOT/'docs/qa/checkpoints/2026-11-01/metal-storm-original-component-v3/source-proof.zip'
HOST=ROOT/'docs/qa/checkpoints/2026-11-01/karnov-menu-health-nightly-v3/source.zip'
REF=ROOT/'tools/reference/metal_storm_host_contract_1101_v4.inc'
MENU=ROOT/'tools/reference/metal_storm_menu_contract_1101_v4.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    with zipfile.ZipFile(PACK)as z:
        actor=z.read('source/portable-actor.inc');wrapper=z.read('source/portable.s').decode();proof=json.loads(z.read('proof/assembly.json'));art=json.loads(z.read('proof/art.json'))
    assert actor==(OLD/'source/portable-actor.inc').read_bytes()
    assert wrapper==(OLD/'source/portable.s').read_text()
    with zipfile.ZipFile(HOST)as z:baseline=json.loads(z.read('menu-composed/baseline.json'))
    native=['SelectedCharacter','SavedJoypadBits','FrameCounter','GamePauseStatus','OperMode','GameEngineSubroutine']
    callbacks={f'MsExternal_{k}':int(v)for k,v in proof['portable_callbacks'].items()}
    wrapper=wrapper.replace('MsState=$6000','MsState=$c000').replace('MsPointer=$00','MsPointer=$03')
    for n,v in callbacks.items():
        old=f'{n}=${v:04x}';assert wrapper.count(old)==1;wrapper=wrapper.replace(old,'.import '+n)
    wrapper=wrapper.replace('.segment "CODE"','.segment "CODE"\nMsHostServiceRows:\n.repeat 37,I\n .if I=0\n  jmp MsHostStep\n .else\n  jmp MsHostReject\n .endif\n.endrepeat\nMsHostReject:clc\n rts\n',1)
    wrapper+='\n.include "metal_storm_host_contract_1101_v4.inc"\n.export MsHostServiceRows\n.segment "COLD"\n.include "metal_storm_menu_contract_1101_v4.inc"\n'
    (OUT/'kernel.s').write_text(wrapper)
    (OUT/'kernel.cfg').write_text('MEMORY{CODE:start=$a000,size=$1fe0,file=%O;COLD:start=$8000,size=$100,file="'+(OUT/'cold.bin').as_posix()+'";}SEGMENTS{CODE:load=CODE,type=ro;COLD:load=COLD,type=ro;}\n')
    native+=['CrossoverMenuIndex']
    (OUT/'host-symbols.s').write_text(''.join(f'.export {n}=${baseline["public"][n][0]:04x}\n'for n in native)+'.export FmAlts=$5fe5\n'+''.join(f'.export {n}=${v:04x}\n'for n,v in callbacks.items()))
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    for cmd in[[cc/'ca65.exe','-g','-I',OLD/'source','-I',ROOT/'tools/reference',OUT/'kernel.s','-o',OUT/'kernel.o'],[cc/'ca65.exe',OUT/'host-symbols.s','-o',OUT/'host-symbols.o'],[cc/'ld65.exe','-C',OUT/'kernel.cfg',OUT/'kernel.o',OUT/'host-symbols.o','-o',OUT/'kernel.bin','--dbgfile',OUT/'kernel.dbg','-Ln',OUT/'kernel.lbl']]:
        cmd=list(map(str,cmd));guard=validate(cmd,OUT,cwd=ROOT);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    labels={}
    for line in(OUT/'kernel.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:labels[m[2]]=int(m[1],16)
    # Exact small original-body dictionary, with a1KB metadata proposal.
    # Runtime graphics can reflect original cells using the proven24/18 axes.
    bases={};mapping=[255]*64;records=[];offsets=[];counts=[]
    for p in art['packets']:
        if p['facing']or p['gravity']:continue
        cells=tuple((c['dx'],c['dy'],c['pattern_index'],c['attributes'])for c in p['cells'])
        if cells not in bases:
            bases[cells]=len(bases);offsets.append(len(records)//4);counts.append(len(cells));records.extend(v&255 for c in cells for v in c)
        mapping[p['state']*8+p['frame']]=bases[cells]
    order=[]
    for n in[6,8]:
        columns=n//2
        for bits in range(4):
            for r in[1,0]:
                for c in reversed(range(columns)):
                    sr=1-r if bits&2 else r;sc=columns-1-c if bits&1 else c;order.append(sr*columns+sc)
    meta=bytes(mapping+offsets+counts+records+order)
    assert len(bases)==33 and len(meta)==1002 and max(offsets)<256
    (OUT/'body-meta.bin').write_bytes(meta)
    q=dict(passed=True,component_only=True,native=False,installed=False,menu_admitted=False,source_packet_sha256=sha(PACK),host_packet_sha256=sha(HOST),source_state=0xc000,source_pointer=[3,4],source_saved_pointer=[0xc7fe,0xc7ff],kernel_origin=0xa000,kernel_bytes=len((OUT/'kernel.bin').read_bytes()),remaining_before_cookie=0xbfe0-labels['MsHostContractEnd'],source_core_bytes=labels['MsEnd']-labels['MsAlias_FF69'],host_adapter_bytes=labels['MsHostContractEnd']-labels['MsEnd'],cold_fragment_bytes=len((OUT/'cold.bin').read_bytes()),service_rows=37,native_symbols={**{n:baseline['public'][n][0]for n in native},'FmAlts':0x5fe5},callbacks=callbacks,labels=labels,graphics=dict(original_patterns=144,body_bytes=4608,body_pages=5,metadata_bytes=len(meta),unique_base_packets=len(bases),pointer_units=4,frame_map_offset=0,offsets_offset=64,counts_offset=97,cells_offset=130,order_offset=946,orders6_offset=946,orders8_offset=970,world_windows_unchanged=[4,5,6,7],maximum_body_windows=2),source_contract='Original semantic actor unchanged. Only baseC000/pointer03/04,113B service header and new selected-owner ABI adapter differ. Callback addresses5000..501B are CPU test ports only, not native runtime code. No native constructor/callback/loader/graphics or playable admission.',commands=commands)
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),REF,MENU,PACK,HOST,OLD/'source/portable-actor.inc',OLD/'source/portable.s',OUT/'kernel.s',OUT/'host-symbols.s',OUT/'kernel.cfg',OUT/'kernel.bin',OUT/'cold.bin',OUT/'kernel.dbg',OUT/'kernel.lbl',OUT/'body-meta.bin',cc/'ca65.exe',cc/'ld65.exe']}
    (OUT/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','labels','commands']}))
if __name__=='__main__':main()
