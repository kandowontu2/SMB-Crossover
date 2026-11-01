"""Recover exact original option activation/selection and timed-effect leaves."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,graph,emit
from private_build_outputs_v1 import validate
O=R/'build/karnov-options-component-1101-v7';HOST=R/'tools/reference/karnov_options_1101_v7.inc'
A=R/'build/karnov-original-source-1101-v1/source';W=R/'build/karnov-original-weapons-1101-v1/source'
F=R/'docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4'
PIN='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[('options',0xeaa7,0xedb7,{0xead5:9},None,()),
       ('timers',0xada8,0xae33,{0xadcb:8},(1,12),()),
       ('owner',0xc28c,0xc29d,{},None,(0xc8b2,)),
       ('palette',0xc5a0,0xc5bb,{},None,()),
       ('BCD',0xcf9a,0xcfba,{},None,()),
       ('HUD',0xc534,0xc5a0,{},None,())]


def transform_terrain(text):
    """Pure proposed input/call hook, not a code grant or an owning link."""
    a=' and KrState+$1b\n and #3\n sta KrState+$21\n'
    assert text.count(a)==1;text=text.replace(a,' and KrState+$1b\n sta KrState+$21\n')
    a=' sta KrPrevious\n jsr KrSourceFrame\n jsr KrSourceWeapons\n'
    assert text.count(a)==1
    text=text.replace(a,' sta KrPrevious\n jsr KrOptionsControls\n jsr KrSourceFrame\n jsr KrSourceWeapons\n jsr KrOptionsTick\n')
    return text


def main():
    O.mkdir(exist_ok=True);assert sha(ROM)==EXPECTED
    frozen=json.loads((F/'handoff.json').read_text())
    assert frozen['output_sha256']==PIN and sha(F/'source.zip')==frozen['source']['sha256']
    raw=ROM.read_bytes();chunks=[];portable=[];external=set();metadata=[];sources=[]
    for name,lo,hi,dispatch,bank,extra in SPANS:
        m,code,tables,ext,ram,reads=graph(raw,lo=lo,hi=hi,dispatch=dispatch,extra_bank=bank,extra_data=extra)
        original=emit(m,code,tables,False,lo=lo,hi=hi)
        port=emit(m,code,tables,True,lo=lo,hi=hi,romdata={0xc8b2:'KrOptionNativeMasks'})
        if name in ['palette','HUD']:
            # These leaves use source58/59 as private temporary DATA. Only
            # the actual inline dispatcher borrows host3/4 as a code pointer.
            port=port.replace('KrPointer+1','KrState+$0059').replace('KrPointer','KrState+$0058')
        for mode,text in [('original',original),('portable',port)]:
            p=O/(mode+'-'+name+'.inc');p.write_text(text);sources.append(p)
        chunks.append(dict(name=name,start=lo,end=hi,data=bytes(m.memory[lo:hi])))
        portable.append(port);external.update(ext)
        metadata.append(dict(name=name,original_start=lo,original_end=hi,instructions=len(code),inline_pointer_words=len(tables),external_callbacks={hex(k):[hex(v)for v in values]for k,values in ext.items()},RAM_operands=sorted(ram)))
    dispatcher=(A/'portable_dispatch.inc').read_text()
    native_dispatch=(A/'original_dispatch.inc').read_text()
    masks=raw[16+14*8192+0x8b2:16+14*8192+0x8bb];assert masks==bytes([1,2,4,8,16,32,64,128,1])
    (O/'karnov-options-portable-v7.inc').write_text('\n'.join(portable)+'\nKrOptionNativeMasks:.byte '+','.join(map(str,masks))+'\n')
    # Exact source islands reproduce requested donor code/data, never whole
    # donor PRG or the original fixed bank.
    defs='KrDispatch=$c831\n'+''.join(f'KrExternal_{n:04X}=${n:04x}\n'for n in sorted(external)if n!=0xc831)
    orig='.setcpu "6502"\n'+defs
    memory=[];segments=[]
    for z in chunks:
        n=z['name'];orig+=f'.segment "N_{n}"\n.include "original-{n}.inc"\n'
        memory.append(f'M_{n}:start=${z["start"]:04x},size=${z["end"]-z["start"]:04x},file=%O;')
        segments.append(f'N_{n}:load=M_{n},type=ro;')
    (O/'original.s').write_text(orig);(O/'original.cfg').write_text('MEMORY{'+''.join(memory)+'}SEGMENTS{'+''.join(segments)+'}\n')
    constants='''KrState=$c000
KrPointer=$03
KrSaved0=$c7fe
KrSaved1=$c7ff
KrOptionSound=$ff10
KrOptionUnsupportedScene=$ff20
KrExternal_C81D=KrOptionSound
KrExternal_C6FC=KrOptionUnsupportedScene
KrExternal_C28C=Kr_C28C
KrExternal_C534=Kr_C534
KrExternal_C5A0=Kr_C5A0
KrExternal_CF9A=Kr_CF9A
KrExternal_C1C7=$ff30
KrExternal_C3D8=$ff40
KrExternal_C2B7=Kr_C2B7
'''
    component='.setcpu "6502"\n.macpack longbranch\n'+constants+'.segment "CODE"\nKrDispatch:\n'+dispatcher+'\n.include "karnov_options_1101_v7.inc"\nKrOptionsComponentEnd:\n'
    component+=' .include "portable_actor.inc"\n.include "portable_weapon.inc"\n.include "portable_clear.inc"\n'
    component+='''KrOptionActor:
 KrOptionSourceCall Kr_F28D
KrOptionWeapons:
 KrOptionSourceCall Kr_AAB2
KrOptionSequenceEnd:
'''
    (O/'component.s').write_text(component)
    (O/'component.cfg').write_text('MEMORY{P:start=$7000,size=$4000,file=%O;}SEGMENTS{CODE:load=P,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for name in ['original','component']:
        for cmd in [[cc/'ca65.exe','-g','-I',O,'-I',HOST.parent,'-I',A,'-I',W,O/(name+'.s'),'-o',O/(name+'.o')],
            [cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin'),'--dbgfile',O/(name+'.dbg'),'-Ln',O/(name+'.lbl')]]:
            cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True)
            commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    assert(O/'original.bin').read_bytes()==b''.join(z['data']for z in chunks)
    labels={}
    for line in(O/'component.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            z=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
            if 'val'in z:labels[z['name'].strip('"')]=int(z['val'],0)
    with zipfile.ZipFile(F/'source.zip')as z:terrain=z.read('host/kr-terrain.inc').decode()
    (O/'original-terrain-input.inc').write_text(terrain)
    transformed=transform_terrain(terrain)
    (O/'terrain-input-proposal.inc').write_text(transformed)
    # Assemble the actual frozen bit converter with its original context
    # addresses. Only SavedJoypadBits uses a declared test input location.
    table=next(line for line in terrain.splitlines()if line.startswith('KrReverseNibble:'))
    input_files=[]
    for name,text in [('input-original',terrain),('input-full',transformed)]:
        lo=text.index(' lda SavedJoypadBits\n and #15\n');hi=text.index(' sta KrPrevious\n',lo)+len(' sta KrPrevious\n')
        code='.setcpu "6502"\nSavedJoypadBits=$10\nKrState=$c000\nKrPrevious=$c81c\nKrTemp=$c81d\n.segment "INPUT"\n'+text[lo:hi]+' rts\n'+table+'\n'
        (O/(name+'.s')).write_text(code)
        (O/(name+'.cfg')).write_text('MEMORY{P:start=$6000,size=$100,file=%O;}SEGMENTS{INPUT:load=P,type=ro;}\n')
        for cmd in [[cc/'ca65.exe','-g',O/(name+'.s'),'-o',O/(name+'.o')],
            [cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin')]]:
            cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True)
            commands.append(dict(command=cmd,guard=guard,returncode=z.returncode,stderr=z.stderr));assert z.returncode==0,z.stderr
        input_files.extend(O/(name+suffix)for suffix in ['.s','.cfg','.bin'])
    q=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False,
        base_ROM_sha256=PIN,donor_sha256=EXPECTED,original_island_bytes=sum(z['end']-z['start']for z in chunks),
        original_islands_reproduced=True,spans=metadata,labels=labels,
        source_component_bytes=labels['KrOptionsComponentEnd']-0x7000,
        existing_actor_weapon_test_fixture_bytes=labels['KrOptionSequenceEnd']-labels['KrOptionsComponentEnd'],
        supported_host_options=[0,3,7],source_pointer=[3,4],new_private_scratch=[0xc865],
        production_callback_imports=['KrOptionSound','KrOptionUnsupportedScene'],
        source_context_imports=['KrState','KrPointer','KrSaved0','KrSaved1'],
        source_NMI_clock_increment_evidence=dict(original_address=0xc1fc,bytes=raw[16+14*8192+0x1fc:16+14*8192+0x1fe].hex()),
        host_clock='SourceE8 accepted-update epoch copied to original0F; original64-tick divider and queue order preserved, not original wall-clock lag timing.',
        proposed_terrain_change_bytes=4,commands=commands,
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),HOST,ROM,F/'handoff.json',F/'source.zip',O/'original-terrain-input.inc',
            R/'tools/audit/recover_karnov_actor_1101_v1.py',A/'portable_dispatch.inc',A/'original_dispatch.inc',A/'portable_actor.inc',W/'portable_weapon.inc',W/'portable_clear.inc',
            *sources,*input_files,O/'karnov-options-portable-v7.inc',O/'original.s',O/'original.cfg',O/'original.bin',O/'component.s',O/'component.cfg',O/'component.bin',O/'component.dbg',O/'terrain-input-proposal.inc']})
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','original_island_bytes','source_component_bytes','existing_actor_weapon_test_fixture_bytes','code_lease_granted']}))
if __name__=='__main__':main()
