"""Abstract ExRAM/five-slot Arthur projection; does not allocate host space."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'build/arthur-source-v1';OUT=ROOT/'build/arthur-projected-leaf-v2'
BIN=ROOT/'tools/Windows/cc65/bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BRANCHES={'BCC':'jcc','BCS':'jcs','BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BVC':'jvc','BVS':'jvs'}
SLOT_EDITS={0xE045:('LDY #$11','LDY #$01'),0xE04D:('CPY #$13','CPY #$03'),0xE051:('CPY #$14','CPY #$04')}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    p=json.loads((BASE/'kernel-source-proof.json').read_text());fields=p['state']['fields']
    ptr=[k for k,v in fields.items()if v['original'] in(0x9d,0x9e)]
    scalar=[k for k,v in fields.items()if v['original']<256 and k not in ptr]
    arrays=[k for k,v in fields.items()if v['original']>=256]
    a=['; Abstract host projection. No physical PRG/CHR/host scratch lease.',
       '; Slots:0 player,1..3 shots,4 host contact/pickup.', '.macpack longbranch',
       '.export ArO_BB2D,ArO_BB3B']
    a += ['.import '+n for n in p['declared_external_owners']]
    a += ['.segment "ARTHUR_PTR": zeropage','.exportzp ArNativeZpStart,ArNativeZpEnd','ArNativeZpStart:']
    for k in ptr:a += ['.exportzp '+k,k+': .res 1']
    a += ['ArNativeZpEnd:','.segment "ARTHUR_SCALARS"','.export ArScalarStart,ArScalarEnd','ArScalarStart:']
    for k in scalar:a += ['.export '+k,k+f': .res {fields[k]["bytes"]}']
    a += ['ArScalarEnd:','.segment "ARTHUR_STATE"','.export ArNativeStateStart,ArNativeStateEnd','ArNativeStateStart:']
    for k in arrays:a += ['.export '+k,k+f': .res {5 if fields[k]["bytes"]==20 else fields[k]["bytes"]}']
    a += ['ArNativeStateEnd:','.segment "ARTHUR_NATIVE"','.export ArNativeStart,ArNativeEnd','ArNativeStart:']
    body=(BASE/'native-kernels.s').read_text().split('ArNativeStart:\n',1)[1]
    changes=[];lines=[];pc=None
    for line in body.splitlines():
        m=re.fullmatch(r'ArO_([0-9A-F]{4}):',line)
        if m:pc=int(m[1],16)
        if pc in SLOT_EDITS and line.strip()==SLOT_EDITS[pc][0]:
            old=line;line=' '+SLOT_EDITS[pc][1]
            changes.append(dict(source=pc,kind='five_slot_allocator',old=old.strip(),new=line.strip()))
        stripped=line.strip().split(' ',1)
        if len(stripped)==2 and stripped[0] in BRANCHES:
            line=' '+BRANCHES[stripped[0]]+' '+stripped[1]
            changes.append(dict(source=pc,kind='semantically_equivalent_long_branch_macro'))
        lines.append(line)
    a += lines
    (OUT/'native-kernels.s').write_text('\n'.join(a)+'\n')
    context=['; Abstract projection imports; no host address claimed.','ArNativeZpBytes=2','ArNativeStateBytes=88',
       'ArScalarBytes=42','.importzp ArNativeZpStart,ArNativeZpEnd','.import ArScalarStart,ArScalarEnd',
       '.import ArNativeStateStart,ArNativeStateEnd']
    context += [('.importzp 'if k in ptr else'.import ')+k for k in fields]
    context += ['.import '+n for n in p['exports']]
    (OUT/'native-context.inc').write_text('\n'.join(context)+'\n')
    component=(BASE/'component.s').read_text()
    start=component.index(' ldx #0\nClearPage:')
    end=component.index(' ldx #ArLeafStateEnd',start)
    component=component[:start]+''' ldx #ArNativeStateBytes-1
ClearState:sta ArNativeStateStart,x
 dex
 bpl ClearState
 ldx #ArScalarBytes-1
ClearScalar:sta ArScalarStart,x
 dex
 bpl ClearScalar
 ldx #ArNativeZpBytes-1
ClearZp:sta ArNativeZpStart,x
 dex
 bpl ClearZp
'''+component[end:]
    component=component.replace('ArR_0522+1','ArR_0522+4').replace('ArR_053B+1','ArR_053B+4')
    component=component.replace('Armor:ldx #1','Armor:ldx #4').replace(' ldx #1\n jsr ArNativeCollectWeapon',' ldx #4\n jsr ArNativeCollectWeapon')
    component=component.replace(' ldx #17\nLoop:',' ldx #1\nLoop:').replace(' cpx #20\n bcc Loop',' cpx #4\n bcc Loop')
    (OUT/'component.s').write_text(component)
    (OUT/'leaf.cfg').write_text('''# Abstract proof addresses; not a host allocation.
MEMORY {
 PTR:start=$0003,size=$0002,type=rw,file="";
 EXRAM:start=$5C00,size=$00B0,type=rw,file="";
 CODE:start=$8000,size=$4000,type=ro,file=%O,fill=yes,fillval=$FF;
}
SEGMENTS {
 ARTHUR_PTR:load=PTR,type=zp;
 ARTHUR_SCALARS:load=EXRAM,type=bss;
 ARTHUR_STATE:load=EXRAM,type=bss;
 ARTHUR_NATIVE:load=CODE,type=ro;
 ARTHUR_LEAF:load=CODE,type=ro;
}
''')
    commands=[]
    for n in('native-kernels','component'):
        args=[str(BIN/'ca65.exe'),'-g','-I',str(OUT),'-o',str(OUT/(n+'.o')),str(OUT/(n+'.s'))]
        commands.append(args);subprocess.run(args,check=True,cwd=ROOT)
    args=[str(BIN/'ld65.exe'),'-C',str(OUT/'leaf.cfg'),'-o',str(OUT/'leaf.bin'),'-Ln',str(OUT/'leaf.lbl'),
          '--dbgfile',str(OUT/'leaf.dbg'),'-m',str(OUT/'leaf.map'),str(OUT/'native-kernels.o'),str(OUT/'component.o')]
    commands.append(args);subprocess.run(args,check=True,cwd=ROOT)
    widened=[r['address']for r in p['instructions_and_data']if r['kind']=='instruction'and r['mode']in('zpg','zpx','zpy')and r.get('relocation',{}).get('symbol')in scalar]
    outfields={k:dict(original=v['original'],bytes=5 if v['bytes']==20 else v['bytes'],original_bytes=v['bytes'])for k,v in fields.items()}
    result=dict(status='ABSTRACT_SOURCE_BUILT_NOT_HOST_LINKED',source_handoff_sha256=sha(BASE/'handoff.json'),
       source_leaf_sha256=sha(BASE/'leaf.bin'),output_sha256=sha(OUT/'leaf.bin'),commands=commands,
       state=dict(pointer_ZP_bytes=2,absolute_ExRAM_scalar_bytes=42,five_slot_native_bytes=88,leaf_bytes=16,total_ExRAM_bytes=146,
          logical_slots=dict(player=0,shots=[1,2,3],target_pickup=4),fields=outfields),
       declared_transformations=dict(widened_absolute_scalar_instructions=widened,allocator_and_branch_edits=changes),
       bindings={str(q.resolve()):sha(q)for q in[Path(__file__),BASE/'handoff.json',BASE/'kernel-source-proof.json',
          BASE/'native-kernels.s',BASE/'native-context.inc',BASE/'component.s',OUT/'native-kernels.s',OUT/'native-context.inc',OUT/'component.s',OUT/'leaf.cfg',BIN/'ca65.exe',BIN/'ld65.exe']},
       limits='Abstract isolated CPU addresses only. No host leases, hooks, shared source, native gameplay or admission changed.')
    target=OUT/'projection-proof.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],widened=len(widened),state=result['state']|{'fields':'omitted'},sha256=sha(target))))
if __name__=='__main__':main()
