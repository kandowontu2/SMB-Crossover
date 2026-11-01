"""Recover executable original Bomb/Ladder objects and their terrain helpers."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,graph,emit
from private_build_outputs_v1 import validate
O=R/'build/karnov-equipment-component-1101-v8'
HOST=R/'tools/reference/karnov_equipment_1101_v8.inc'
A=R/'build/karnov-original-source-1101-v1/source'
V7=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[('bomb',0xae3d,0xaf3d,{0xae5e:4,0xae90:9},11,()),
 ('bombOAM',0xa27b,0xa2ee,{},11,()),
 ('blast',0xccfc,0xcd41,{},None,()),
 ('damage',0xcd6d,0xcda4,{},None,(0xcdad,0xcded)),
 ('grow',0xa4b6,0xa5bd,{},12,(0x9b97,0xc264)),
 ('restore',0xa5bd,0xa693,{},12,(0x9ac8,0xc264)),
 ('overlay',0xb46f,0xb49c,{},12,()),
 ('rebase',0xaf3f,0xb048,{0xaf49:4},12,()),
 ('map',0xc321,0xc38f,{},None,(0x8020,)),
 ('quadPointer',0xc38f,0xc3a7,{},None,()),
 ('probe',0xc3d8,0xc447,{0xc3ed:4},None,()),
 ('worldToScreen',0xc447,0xc460,{},None,()),
 ('screenToWorld',0xc460,0xc473,{},None,()),
 ('screen',0xc473,0xc4e3,{},None,(0xc224,0xc225)),
 ('attribute',0xc4e3,0xc534,{},None,()),
 ('retractOwner',0xd700,0xd73c,{},None,()),
 ('rebuildOwner',0xdb00,0xdb26,{},None,())]
DATA=[('KrEquipmentMapIndex',0x8020,256,0),
 ('KrEquipmentTileClass',0x9ac8,256,0),
 ('KrEquipmentScreenRows',0xc224,64,14),
 ('KrEquipmentAttributeMasks',0xc264,4,14),
 ('KrEquipmentEnemyHP',0xcdad,64,14),
 ('KrEquipmentEnemyScore',0xcded,64,14)]


def main():
    O.mkdir(exist_ok=True);assert sha(ROM)==EXPECTED
    raw=ROM.read_bytes();chunks=[];portable=[];external=set();metadata=[];sources=[]
    lookup={a:name for name,a,n,b in DATA}
    lookup.update({0x9b97:'KrEquipmentTileClass+$cf',0xc225:'KrEquipmentScreenRows+1'})
    for name,lo,hi,dispatch,bank,data in SPANS:
        m,code,tables,ext,ram,reads=graph(raw,lo,hi,dispatch,(1,bank)if bank else None,data)
        original=emit(m,code,tables,False,lo,hi)
        port=emit(m,code,tables,True,lo,hi,lookup)
        # 58/59 in these leaves are original private DATA scratch. The only
        # actual host ZP pointer is the separate inline-dispatch helper3/4.
        port=port.replace('KrPointer+1','KrState+$0059').replace('KrPointer','KrState+$0058')
        indirect=[]
        for pc,z in code.items():
            if z['mode']=='iny':
                assert z['mnemonic']=='LDA'and z['operand']==0x4c
                exact=f"LDA (KrState+$004c),Y ; original {hex(pc)}"
                assert port.count(exact)==1
                port=port.replace(exact,f'JSR KrEquipmentReadStage ; original {hex(pc)}: LDA ($4c),Y')
                indirect.append(pc)
        for mode,text in [('original',original),('portable',port)]:
            p=O/(mode+'-'+name+'.inc');p.write_text(text);sources.append(p)
        chunks.append(dict(name=name,start=lo,end=hi,data=bytes(m.memory[lo:hi])))
        portable.append(port);external.update(ext)
        metadata.append(dict(name=name,start=lo,end=hi,instructions=len(code),dispatch_words=len(tables),
            indirect_read_adaptation=indirect,callbacks={hex(k):list(map(hex,v))for k,v in ext.items()},
            RAM_operands=sorted(ram),ROM_read_operands=sorted(reads)))
    data_text=[]
    for name,a,n,bank in DATA:
        offset=a-(0xc000 if bank==14 else 0x8000)
        b=raw[16+bank*8192+offset:16+bank*8192+offset+n];assert len(b)==n
        data_text.append(name+':\n'+''.join('.byte '+','.join(f'${v:02x}'for v in b[i:i+16])+'\n'for i in range(0,n,16)))
    (O/'karnov-equipment-portable-v8.inc').write_text('\n'.join(portable+data_text))
    defs='KrDispatch=$c831\n'+''.join(f'KrExternal_{n:04X}=${n:04x}\n'for n in sorted(external)if n!=0xc831)
    orig='.setcpu "6502"\n'+defs;memory=[];segments=[]
    for z in chunks:
        n=z['name'];orig+=f'.segment "N_{n}"\n.include "original-{n}.inc"\n'
        memory.append(f'M_{n}:start=${z["start"]:04x},size=${z["end"]-z["start"]:04x},file=%O;')
        segments.append(f'N_{n}:load=M_{n},type=ro;')
    (O/'original.s').write_text(orig)
    (O/'original.cfg').write_text('MEMORY{'+''.join(memory)+'}SEGMENTS{'+''.join(segments)+'}\n')
    constants='''KrState=$c000
KrPointer=$03
KrSaved0=$c7fe
KrSaved1=$c7ff
KrEquipmentScore=$ff10
KrEquipmentHUD=$ff20
KrEquipmentScene=$ff30
KrEquipmentDraw=$ff40
KrEquipmentFrameGate=$ff50
KrExternal_C76E=KrEquipmentScore
KrExternal_C534=KrEquipmentHUD
KrExternal_C1C7=KrEquipmentScene
KrExternal_DF61=KrEquipmentDraw
KrExternal_C046=KrEquipmentFrameGate
'''
    own={lo for name,lo,*_ in SPANS}
    constants+=''.join(f'KrExternal_{n:04X}=Kr_{n:04X}\n'for n in sorted(external)if n in own)
    component='.setcpu "6502"\n.macpack longbranch\n'+constants+'.segment "CODE"\nKrDispatch:\n'+(A/'portable_dispatch.inc').read_text()+'\n.include "karnov_equipment_1101_v8.inc"\n'
    component+='''; Test-only flat-memory stage backend. Original bank0 is loaded at2000;
; original logical8000..9FFF pointer becomes2000..3FFF. This is not an NES
; host address grant. EOR changes no C/V/D/I; final LDA supplies original NZ.
KrEquipmentReadStage:
 lda KrState+$4d
 eor #$a0
 sta KrPointer+1
 lda KrState+$4c
 sta KrPointer
 lda (KrPointer),y
 rts
KrEquipmentFixtureEnd:
'''
    (O/'component.s').write_text(component)
    (O/'component.cfg').write_text('MEMORY{P:start=$9000,size=$3000,file=%O;}SEGMENTS{CODE:load=P,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for name in ['original','component']:
        for cmd in [[cc/'ca65.exe','-g','-I',O,'-I',HOST.parent,O/(name+'.s'),'-o',O/(name+'.o')],
                    [cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin'),'--dbgfile',O/(name+'.dbg'),'-Ln',O/(name+'.lbl')]]:
            cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True)
            commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    assert(O/'original.bin').read_bytes()==b''.join(z['data']for z in chunks)
    labels={}
    for line in(O/'component.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            z=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
            if 'val'in z:labels[z['name'].strip('"')]=int(z['val'],0)
    q=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False,
        donor_sha256=EXPECTED,original_island_bytes=sum(z['end']-z['start']for z in chunks),original_islands_reproduced=True,
        source_component_bytes=labels['KrEquipmentEnd']-0x9000,test_read_backend_bytes=labels['KrEquipmentFixtureEnd']-labels['KrEquipmentEnd'],
        spans=metadata,labels=labels,commands=commands,
        imports=['KrState','KrPointer','KrSaved0','KrSaved1','KrEquipmentReadStage','KrEquipmentScore','KrEquipmentHUD','KrEquipmentScene','KrEquipmentDraw','KrEquipmentFrameGate'],
        new_persistent_RAM=[],source_state_range=[0xc000,0xc800],borrowed_ZP=[3,4],
        read_backend='Exact source logical (C04C/C04D)+Y current-stage ROM. Standalone flat-memory backend relocates donor bank0 to2000..3FFF; native current-stage backend not admitted.',
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),HOST,ROM,R/'tools/audit/recover_karnov_actor_1101_v1.py',A/'portable_dispatch.inc',A/'original_dispatch.inc',
            *sources,O/'karnov-equipment-portable-v8.inc',O/'original.s',O/'original.cfg',O/'original.bin',O/'component.s',O/'component.cfg',O/'component.bin',O/'component.dbg']})
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','original_island_bytes','source_component_bytes','test_read_backend_bytes','code_lease_granted']}))
if __name__=='__main__':main()
