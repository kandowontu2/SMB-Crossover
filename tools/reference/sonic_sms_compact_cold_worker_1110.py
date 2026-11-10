"""In-memory source factoring of the six-owner common cold worker.

This does not grant raw43, RAM, a cookie, or a native entry.  The spare five
bytes carry a proposed one-row descriptor only; root owns its admission.
The actual fixed-D0 source and Getsu edits are assembled before any change.
"""
from pathlib import Path
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import check_getsu_fuma_owner_1110 as Frozen
from sonic_sms_relocated_core_1110 import OPCODES,SIZES,BRANCH,expression

LAYOUT={'BB_COLD_PROPOSAL':(0xaf40,192),'BB_COLD_MAP':(0xb9d6,42)}


def one(source,old,new):
    assert source.count(old)==1,(old,source.count(old))
    return source.replace(old,new)


def assemble(source,layout):
    """Small deterministic two-pass 6502 assembler; output is memory only.

    ca65 long branches are deliberately absent from the active fixed-D0
    source.  Disabled conditional bodies are excluded using source flags.
    Every emitted instruction is checked against py65's opcode metadata.
    """
    symbols={};items=[];active=True;conditions=[]
    for number,line in enumerate(source.splitlines(),1):
        text=line.split(';',1)[0].strip()
        if not text:continue
        if text.startswith(('.ifdef ','.ifndef ')):
            directive,name=text.split()
            yes=name in symbols
            if directive=='.ifndef':yes=not yes
            conditions.append((active,yes));active=active and yes;continue
        if text=='.else':
            parent,yes=conditions[-1];active=parent and not yes;continue
        if text=='.endif':
            parent,_=conditions.pop();active=parent;continue
        if not active:continue
        assignment=re.fullmatch(r'(\w+)\s*=\s*(.+)',text)
        if assignment:
            symbols[assignment[1]]=expression(assignment[2],symbols);continue
        if text.startswith(('.setcpu ','.macpack ','.export ')):continue
        if text.startswith('.segment '):
            name=text.split('"')[1];assert name in layout
            items.append(dict(kind='segment',name=name));continue
        label=re.match(r'^(\w+):(.*)$',text)
        if label:
            items.append(dict(kind='label',name=label[1]));text=label[2].strip()
            if not text:continue
        if text.startswith(('.byte ','.word ')):
            items.append(dict(kind='data',width=1 if text.startswith('.byte')else 2,
                              exprs=text[6:].split(','),line=number));continue
        op,_,operand=text.partition(' ')
        assert op.upper() in {k[0]for k in OPCODES},(number,text)
        items.append(dict(kind='instruction',op=op.upper(),operand=operand.strip(),line=number))
    assert not conditions

    def value(text,unknown=False):
        try:return expression(text,symbols)
        except KeyError:
            if unknown:return 0xffff
            raise

    def addressing(item,unknown=False):
        op,text=item['op'],item['operand']
        if op in BRANCH:return 'rel',value(text,unknown)
        if not text:return ('imp'if(op,'imp')in OPCODES else'acc'),None
        if text.lower()=='a':return 'acc',None
        if text.startswith('#'):return 'imm',value(text[1:],unknown)
        mode=None
        if re.fullmatch(r'\(.+\),[yY]',text):mode='iny';expr=text[1:-3]
        elif re.fullmatch(r'\(.+,[xX]\)',text):mode='inx';expr=text[1:-3]
        elif text.startswith('(')and text.endswith(')'):mode='ind';expr=text[1:-1]
        elif text.lower().endswith(',x'):mode='x';expr=text[:-2]
        elif text.lower().endswith(',y'):mode='y';expr=text[:-2]
        else:expr=text
        result=value(expr,unknown)
        if mode in ('inx','iny','ind'):return mode,result
        if mode=='x':return ('zpx'if result<256 and(op,'zpx')in OPCODES else'abx'),result
        if mode=='y':return ('zpy'if result<256 and(op,'zpy')in OPCODES else'aby'),result
        return ('zpg'if result<256 and(op,'zpg')in OPCODES else'abs'),result

    for _ in range(20):
        before=dict(symbols);positions={name:start for name,(start,_)in layout.items()};segment=None
        for item in items:
            kind=item['kind']
            if kind=='segment':segment=item['name'];continue
            assert segment is not None
            item['segment'],item['pc']=segment,positions[segment]
            if kind=='label':symbols[item['name']]=item['pc']
            elif kind=='data':positions[segment]+=item['width']*len(item['exprs'])
            else:
                mode,_=addressing(item,True);assert(item['op'],mode)in OPCODES,(item,mode)
                positions[segment]+=SIZES[mode]
        if symbols==before:break
    else:raise AssertionError('Source convergence')
    images={name:bytearray()for name in layout};instructions=[]
    for item in items:
        if item['kind']in ('segment','label'):continue
        image=images[item['segment']];pc=layout[item['segment']][0]+len(image)
        assert pc==item['pc']
        if item['kind']=='data':
            for expr in item['exprs']:image.extend(value(expr).to_bytes(item['width'],'little'))
            continue
        mode,result=addressing(item);op=item['op'];image.append(OPCODES[op,mode])
        if mode=='rel':
            offset=result-pc-2;assert -128<=offset<=127,(item,offset);image.append(offset&255)
        elif result is not None:image.extend(result.to_bytes(SIZES[mode]-1,'little'))
        instructions.append(dict(pc=pc,op=op,mode=mode,operand=result,segment=item['segment']))
    used={name:len(image)for name,image in images.items()}
    for name,image in images.items():
        assert len(image)<=layout[name][1],(name,len(image),layout[name][1])
    return dict(images={name:bytes(image)for name,image in images.items()},symbols=symbols,
                instructions=instructions,used=used,source=source)


def worker_source(*,compact):
    source=Frozen.WORKER.read_text()
    inc=Frozen.INCLUDE.read_text()
    inc=one(inc,' ldy #0\n sty $5130\n bit $2002',' ldy #0\n bit $2002')
    inc=one(inc,' cmp (R0),y\n jne BbColdNo',' cmp (R0),y\n bne BbColdNo')
    inc=one(inc,' sta $2000\n lda #0\n sta R2',' sta $2000\n sty R2')
    inc=one(inc,' inc R2\n ldy #0\n lda R2',' inc R2\n lda R2')
    inc=one(inc,' bne BbColdCopyRow\n sec\n rts',' bne BbColdCopyRow\n rts')
    gf='\n.export GfColdDescriptor\nGfColdDescriptor:\n .byte 2,2,1,$d0\n .word 991,992\n'
    inc=one(inc,'BbColdDescriptors:',gf+'BbColdDescriptors:')
    mini='\n.segment "BB_COLD_MAP"\nMiniColdDescriptor:\n.byte 1,0,9,$d0\n.word 967\n'
    source=one(source,'.include "bubble_bobble_common_cold_1102_v4.inc"',inc)+mini
    if compact:
        source=one(source,' lda #0\n sta R0\n lda #$c0',' lda #$c0')
        source=one(source,' tax\n ldy #0\nBbColdZeroPage:',' tax\n ldy #0\n sty R0\nBbColdZeroPage:')
        source=one(source,' adc #5',' adc #4')
        assert source.count(',$d0')==5 # Also the disabled Sh descriptor.
        source=source.replace(',$d0','')
        source+='\n.segment "BB_COLD_PROPOSAL"\nProposedSonicColdDescriptor:\n.byte 1,0,9\n.word 328\n'
    return source


def typed_source(*,compact):
    source=Frozen.TYPED.read_text()
    source=re.sub(r'\.macro Far.+?\.endmacro','',source,flags=re.S)
    def far(match):
        target,bank,operation=match.groups()
        return f' lda #<{target}\n sta $016c\n lda #>{target}\n sta $016d\n lda #{bank}\n {operation} $015a'
    source=re.sub(r'^\s*Far\s+([^,\n]+),\s*([^,\n]+),\s*(\w+)',far,source,flags=re.M)
    if compact:
        source=one(source,'    eor #14\n    lsr a\n    bne Done','    cmp #12\n    bcc ReturnSuccess')
        source=one(source,'Done:\n    rts','ReturnSuccess:\n    sec\nDone:\n    rts')
    return source


def build():
    old=assemble(worker_source(compact=False),LAYOUT)
    new=assemble(worker_source(compact=True),LAYOUT)
    typed_layout={'TYPED':(0xb1ba,66)}
    old_typed=assemble(typed_source(compact=False),typed_layout)
    new_typed=assemble(typed_source(compact=True),typed_layout)
    assert old['used']=={'BB_COLD_PROPOSAL':191,'BB_COLD_MAP':41}
    assert new['used']=={'BB_COLD_PROPOSAL':191,'BB_COLD_MAP':40}
    assert old['symbols']['BbColdMainEnd']-0xaf40==141
    assert new['symbols']['BbColdMainEnd']-0xaf40==139
    assert new['symbols']['ProposedSonicColdDescriptor']==0xaffa
    assert old_typed['used']=={'TYPED':66}and new_typed['used']=={'TYPED':66}
    return dict(old=old,new=new,old_typed=old_typed,new_typed=new_typed)
