"""Source-preserving, in-memory relocation of the ordinary SMS Sonic core.

This is a test-only layout until the host grants its exclusive lifetime.
No file is written. All state is in bank2, all instructions/tables in bank3.
The source-world map is a private test fixture, not an SMB terrain adapter.
"""
import ast
from hashlib import sha256
from pathlib import Path
import re

from py65.devices.mpu6502 import MPU

R = Path(__file__).resolve().parents[2]
SOURCE = R/'build/sonic-original-composed-frame-1110/component.s'
BINARY = SOURCE.with_suffix('.bin')
SOURCE_PIN = 'f73192961c4fccab1cdc42c3c9ca10d05373accbd16611b7d883ddb2842a228d'
SOURCE_START = 0x8000
CODE_START, CODE_LIMIT = 0xa000, 0xbfe0
STATE_START, STATE_LIMIT = 0xc000, 0xc100
MAP_START, MAP_LIMIT = 0xc800, 0xd800
FLAGS_START, FLAGS_LIMIT = 0xd800, 0xd900
STATE_FIELDS = {
    'XVelocity':(0xc020,3),'YVelocity':(0xc060,3),'BounceVelocity':(0xc063,3),
    'XPosition':(0xc070,3),'YPosition':(0xc073,3),
    'Flags':(0xc030,1),'Animation':(0xc031,1),'SourceInput':(0xc040,1),
    'BodyWidth':(0xc041,1),'BodyHeight':(0xc042,1),'BodyAdjustedY':(0xc043,2),
    'CameraLook':(0xc047,2),'JumpTimer':(0xc058,1),'JumpVelocity':(0xc059,2),
    'Gravity':(0xc05b,2),'Terminal':(0xc05d,1),'SoundEvent':(0xc05e,1),
    'ShoesTimer':(0xc090,1),'LevelFlags':(0xc091,1),'GlobalTick':(0xc092,1),
    'SavedTempo':(0xc093,2),'LiveTempo':(0xc095,2),
    'PreviousAnimation':(0xc0a0,1),'AnimationFrame':(0xc0a1,1),
    'AnimationSubframe':(0xc0a2,1),'Sprite':(0xc0a3,1),'NesInput':(0xc0a8,1),
    'FlagsCopy':(0xc0a9,1),'BoredTimer':(0xc0aa,2),'LastGroundY':(0xc0b2,2),
}
BRANCH = dict(BPL=0x10,BMI=0x30,BVC=0x50,BVS=0x70,BCC=0x90,BCS=0xb0,BNE=0xd0,BEQ=0xf0)
OPCODES = {(name,mode):i for i,(name,mode) in enumerate(MPU.disassemble) if name!='???'}
SIZES = dict(imp=1,acc=1,imm=2,zpg=2,zpx=2,zpy=2,inx=2,iny=2,abs=3,abx=3,aby=3,ind=3,rel=2)
THUNKS = '''
RelocatedRead8C:
 lda $8c
 sta RelocatedRead8COperand+1
 lda $8d
 sta RelocatedRead8COperand+2
RelocatedRead8COperand:
 lda $ffff,y
 rts
RelocatedReadAE:
 lda $ae
 sta RelocatedReadAEOperand+1
 lda $af
 sta RelocatedReadAEOperand+2
RelocatedReadAEOperand:
 lda $ffff,y
 rts
'''


def parse(source):
    items=[]
    for number,line in enumerate(source.splitlines(),1):
        text=line.split(';',1)[0].strip()
        if not text:continue
        label=re.match(r'^(\w+|):(.*)$',text)
        if label:
            items.append(dict(kind='label',name=label[1],line=number))
            text=label[2].strip()
            if not text:continue
        assignment=re.match(r'^(\w+)\s*=\s*(.+)$',text)
        if assignment:
            items.append(dict(kind='constant',name=assignment[1],expr=assignment[2],line=number))
        elif text.startswith('.byte '):
            items.append(dict(kind='data',exprs=text[6:].split(','),line=number))
        elif text.startswith(('.setcpu ','.segment ','.export ')):
            continue
        else:
            op,_,operand=text.partition(' ')
            assert op.upper() in {k[0]for k in OPCODES},(number,text)
            items.append(dict(kind='instruction',op=op.upper(),operand=operand.strip(),line=number))
    return items


def expression(text,symbols):
    text=text.strip()
    if text.startswith('<'):return expression(text[1:],symbols)&255
    if text.startswith('>'):return expression(text[1:],symbols)>>8&255
    text=re.sub(r'\$([0-9a-fA-F]+)',r'0x\1',text)
    def evaluate(node):
        if isinstance(node,ast.Constant):return node.value
        if isinstance(node,ast.Name):return symbols[node.id]
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Sub)):
            a,b=evaluate(node.left),evaluate(node.right)
            return a+b if isinstance(node.op,ast.Add) else a-b
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            a=evaluate(node.operand);return a if isinstance(node.op,ast.UAdd) else -a
        raise AssertionError(('Unsupported source expression',text,ast.dump(node)))
    return evaluate(ast.parse(text,mode='eval').body)


def assemble(source,*,relocated):
    original=parse(source)
    items=[dict(x)for x in original]
    changed_indirect=[]
    if relocated:
        for index,item in enumerate(items):
            if item['kind']!='instruction':continue
            operand=item['operand'].lower().replace(' ','')
            if operand in ('($8c),y','($ae),y'):
                assert item['op']=='LDA'
                pointer=int(operand[2:4],16)
                item['op'],item['operand']='JSR',f'RelocatedRead{pointer:02X}'
                changed_indirect.append(index)
        items.extend(parse(THUNKS))
    start=CODE_START if relocated else SOURCE_START
    long_branches=set()
    symbols={}
    anonymous=[]
    addresses={}

    def operand_value(text,index,*,unknown=False):
        if text in (':+',':-'):
            choices=[(j,p)for j,p in anonymous if (j>index if text==':+'else j<index)]
            if not choices:
                if unknown:return 0xffff
                raise AssertionError(('Anonymous source label',index,text))
            return (choices[0]if text==':+'else choices[-1])[1]
        try:return expression(text,symbols)
        except KeyError:
            if unknown:return 0xffff
            raise

    def addressing(item,index,*,unknown=False):
        op,text=item['op'],item['operand'].strip()
        if op in BRANCH:return 'rel',operand_value(text,index,unknown=unknown)
        if not text:return ('imp'if(op,'imp')in OPCODES else'acc'),None
        if text.lower()=='a':return 'acc',None
        if text.startswith('#'):
            value=operand_value(text[1:],index,unknown=unknown)
            # Only this source fixture's map-base immediate is an address.
            if relocated and addresses.get(index,0)>=symbols.get('SourceWorldQuery',0xffff) and text.lower()=='#$60':
                value=MAP_START>>8
            return 'imm',value
        mode=None
        if re.fullmatch(r'\(.+\),[yY]',text):mode='iny';expr=text[1:-3]
        elif re.fullmatch(r'\(.+,[xX]\)',text):mode='inx';expr=text[1:-3]
        elif text.startswith('(')and text.endswith(')'):mode='ind';expr=text[1:-1]
        elif text.lower().endswith(',x'):mode='x';expr=text[:-2]
        elif text.lower().endswith(',y'):mode='y';expr=text[:-2]
        else:expr=text
        value=operand_value(expr,index,unknown=unknown)
        if relocated and value<256:
            value+=STATE_START
        elif relocated and 0x6000<=value<0x7000:
            value=MAP_START+value-0x6000
        elif relocated and 0x7000<=value<0x7100:
            value=FLAGS_START+value-0x7000
        if mode in ('inx','iny','ind'):return mode,value
        if mode=='x':return ('zpx'if value<256 and (op,'zpx')in OPCODES else'abx'),value
        if mode=='y':return ('zpy'if value<256 and (op,'zpy')in OPCODES else'aby'),value
        return ('zpg'if value<256 and (op,'zpg')in OPCODES else'abs'),value

    for _ in range(20):
        old_symbols=symbols.copy()
        pc=start;anonymous=[]
        for index,item in enumerate(items):
            addresses[index]=pc
            kind=item['kind']
            if kind=='label':
                if item['name']:symbols[item['name']]=pc
                else:anonymous.append((index,pc))
            elif kind=='constant':symbols[item['name']]=expression(item['expr'],symbols)
            elif kind=='data':pc+=len(item['exprs'])
            else:
                mode,_=addressing(item,index,unknown=True)
                assert (item['op'],mode)in OPCODES,(item,mode)
                pc+=5 if index in long_branches else SIZES[mode]
        added=False
        for index,item in enumerate(items):
            if item['kind']=='instruction'and item['op']in BRANCH:
                target=operand_value(item['operand'],index)
                off=target-addresses[index]-2
                if not -128<=off<=127 and index not in long_branches:
                    assert relocated,('Original source branch out of range',item,off)
                    long_branches.add(index);added=True
        if not added and symbols==old_symbols:break
    else:raise AssertionError('Source layout convergence')
    image=bytearray();boundaries={};data_cells={};indirect_sites=[];expanded=[]
    for index,item in enumerate(items):
        assert start+len(image)==addresses[index]
        kind=item['kind']
        if kind in ('label','constant'):continue
        if kind=='data':
            for offset,expr in enumerate(item['exprs']):
                data_cells[index,offset]=start+len(image)
                image.append(operand_value(expr,index)&255)
            continue
        pc=start+len(image);boundaries[index]=pc
        mode,value=addressing(item,index)
        if index in long_branches:
            image.extend((BRANCH[item['op']]^0x20,3,0x4c,value&255,value>>8))
            expanded.append(dict(source_line=item['line'],PC=pc,original_branch=item['op'],target=value))
        else:
            image.append(OPCODES[item['op'],mode])
            if mode=='rel':image.append((value-pc-2)&255)
            elif SIZES[mode]>=2:image.append(value&255)
            if SIZES[mode]==3:image.append(value>>8)
        if index in changed_indirect:indirect_sites.append(pc)
    return dict(image=bytes(image),symbols=symbols,items=items,boundaries=boundaries,
                data_cells=data_cells,long_branches=expanded,indirect_sites=indirect_sites)


def build():
    text=SOURCE.read_text()
    assert sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_PIN
    original=assemble(text,relocated=False)
    assert original['image']==BINARY.read_bytes()and len(original['image'])==4864
    target=assemble(text,relocated=True)
    assert len(target['image'])<=CODE_LIMIT-CODE_START,len(target['image'])
    source_to_target={original['boundaries'][i]:target['boundaries'][i]for i in original['boundaries']}
    source_to_target.update({at:target['data_cells'][key]for key,at in original['data_cells'].items()})
    smc=[]
    for name in ('RelocatedRead8COperand','RelocatedReadAEOperand'):
        pc=target['symbols'][name]
        smc.extend((pc+1,pc+2))
    target.update(original=original,source_to_target=source_to_target,SMC_operands=smc,
                  code_half_open=[CODE_START,CODE_START+len(target['image'])],
                  state_half_open=[STATE_START,STATE_LIMIT],fixture_world_half_open=[MAP_START,MAP_LIMIT],
                  fixture_flags_half_open=[FLAGS_START,FLAGS_LIMIT],state_fields=STATE_FIELDS,
                  state_aliases={name:STATE_START+value for name,value in original['symbols'].items()if value<256},
                  entrypoints={name:target['symbols'][name]for line in text.splitlines()if line.startswith('.export ')
                               for name in line[8:].split(',')})
    return target
