"""Root-authorized two-span Gimmick-only empty-bounce side fix; memory only."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import re
from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU
import replay_gimmick_flower_side_probe_current_1115 as Current

R,W,N,PIN,ROM=Current.R,Current.W,Current.N,Current.PIN,Current.ROM
CANDIDATE='05fb72a3d7928c4ec5f2267e7f52a9aa739f682cb0c3629057c2342962486a96'
CURRENT_CANDIDATE='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'
SPAN=(202882,202998);SCREEN=(202998,203069)
START,WRAPPER=0xb872,0xb923
SOURCE=R/'src/gimmick_host.s'


def load590():
    actual=ROM.read_bytes();digest=sha256(actual).hexdigest()
    if digest==PIN:return actual,dict(actual_input_SHA256=digest,reference590_SHA256=PIN)
    import compose_prince_body_transition_590_1115 as Prince
    assert digest==Prince.CANDIDATE=='16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb','Expected exact590 or explicitly typed16a'
    old=Prince.inverse(actual);assert sha256(old).hexdigest()==PIN
    return old,dict(actual_input_SHA256=digest,reference590_SHA256=PIN,typed_inverse='compose_prince_body_transition_590_1115.inverse')


def assemble(text,symbols,origin):
    lines=[];repeat=None;count=0
    for raw in text.splitlines():
        line=raw.split(';',1)[0].strip()
        if not line:continue
        if line.startswith('.repeat'):repeat=[];count=int(line.split()[1]);continue
        if line=='.endrepeat':lines.extend(repeat*count);repeat=None;continue
        if repeat is not None:repeat.append(line);continue
        if line.startswith('.proc '):line=line.split()[1]+':'
        elif line.startswith('.')and not line.startswith('.byte'):continue
        match=re.match(r'^(\w+):\s*(.*)$',line)
        if match:
            lines.append(match[1]+':');line=match[2]
        if line:lines.append(line)
    labels=dict(symbols);sizes=[0 if line.endswith(':')else len(line.split(None,1)[1].split(','))if line.startswith('.byte')else 3 for line in lines]
    asm=Assembler(MPU())
    def render(line):
        line=re.sub(r'#>(\w+)',lambda m:'#'+str(labels[m[1]]>>8),line)
        line=re.sub(r'\b([A-Za-z_]\w*)\b',lambda m:f'${labels[m[1]]:04x}'if m[1]in labels else m[0],line)
        line=re.sub(r'\$([\da-fA-F]+)\+(\d+)',lambda m:f'${int(m[1],16)+int(m[2]):04x}',line)
        return re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
    for _ in range(20):
        pc=origin
        for line,size in zip(lines,sizes):
            if line.endswith(':'):labels[line[:-1]]=pc
            pc+=size
        out=bytearray();new=[]
        for line in lines:
            if line.endswith(':'):new.append(0);continue
            code=bytes(int(v.strip(),0)for v in line.split(None,1)[1].split(','))if line.startswith('.byte')else bytes(asm.assemble(render(line),pc=origin+len(out)))
            out.extend(code);new.append(len(code))
        if new==sizes:return bytes(out),labels
        sizes=new
    raise AssertionError('Gimmick source assembly did not converge')


@lru_cache(maxsize=1)
def recipe(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact frozen590 input'
    b=dict(W.Symbols.bundle(),raw=raw);text=SOURCE.read_text()
    start=text.index('.proc GmHead\n');end=text.index('.endproc',text.index('.proc GmBodyProbe\n'))+len('.endproc')
    old_source=text[start:end];tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',old_source))
    symbols={name:W.address(b,name)for name in tokens if name in b['syms']};symbols['GmEmptySide']=WRAPPER
    before,old_labels=assemble(old_source,symbols,START)
    assert len(before)==116 and raw[SPAN[0]:SPAN[1]]==before,'Exact Gimmick116B preimage'
    new_source=old_source.replace('.proc GmSide\n lda #1\n ; fall through\n.endproc','.proc GmSide\n lda #1\n jmp GmEmptySide\n.endproc')
    assert new_source!=old_source
    for old,new in(('Owned:\n tya\n pha','Owned:\n tya\n tax'),(' pla\n tay\n lda Player_Y_Position',' txa\n tay\n lda Player_Y_Position'),(' sty GmTemp2\n tay',' tay'),(' ldy GmTemp2\n pla',' txa\n tay\n pla')):
        assert new_source.count(old)==1,old;new_source=new_source.replace(old,new,1)
    after,new_labels=assemble(new_source,symbols,START)
    assert len(after)==115 and all(new_labels[n]==old_labels[n]for n in('GmHead','GmFoot','GmSide'))
    assert(new_labels['GmBodyProbe'],new_labels['XAdd'],new_labels['YAdd'])==(0xb882,old_labels['XAdd']-1,old_labels['YAdd']-1)
    wrapper,_=assemble('jsr GmBodyProbe\neor #35\nbeq Done\neor #35\nDone:\nrts',dict(symbols,**new_labels),WRAPPER)
    assert wrapper==bytes.fromhex('2082b84923f002492360'),('Wrapper',wrapper.hex())
    render=(R/'src/gimmick_render.s').read_text();a=render.index('.proc GmScreenPoint\n');z=render.index('.endproc',render.index('.proc GmCameraPoint\n'))+len('.endproc')
    old_screen=render[a:z];screen_tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',old_screen))
    screen_symbols={name:W.address(b,name)for name in screen_tokens if name in b['syms']}
    screen_before,old_screen_labels=assemble(old_screen,screen_symbols,0xb8e6)
    assert len(screen_before)==71 and raw[SCREEN[0]:SCREEN[1]]==screen_before
    new_screen=old_screen.replace('.proc GmScreenPoint\n','.proc GmScreenPoint\n tya\n pha\n',1)
    group=' .repeat 4\n lsr R5\n ror R4\n lsr R7\n ror R6\n .endrepeat\n jmp GmCameraPoint'
    replacement=' ldy #2\nScreenShift:\n .repeat 2\n lsr R5\n ror R4\n lsr R7\n ror R6\n .endrepeat\n dey\n bne ScreenShift\n pla\n tay'
    assert new_screen.count(group)==1;new_screen=new_screen.replace(group,replacement,1)
    screen_after,new_screen_labels=assemble(new_screen,screen_symbols,0xb8e6)
    assert len(screen_after)==61 and 0xb8e6+len(screen_after)==WRAPPER
    assert new_screen_labels['GmScreenPoint']==old_screen_labels['GmScreenPoint']and new_screen_labels['GmCameraPoint']==old_screen_labels['GmCameraPoint']-10
    source_refs=[line.strip()for line in text.splitlines()if'GmBodyProbe'in line and not line.lstrip().startswith(';')]
    assert source_refs[:3]==['jmp GmBodyProbe','jmp GmBodyProbe','.proc GmBodyProbe']
    assert len(source_refs)==4 and source_refs[-1].startswith('.export ')
    # Every literal old-body call in the actual Gimmick code is one of those
    # two symbolic Head/Foot jumps. Interior table consumers are within span.
    code=raw[200336:203743];refs=[];target=old_labels['GmBodyProbe'].to_bytes(2,'little')
    for i in range(len(code)-2):
        if code[i]in(0x20,0x4c)and code[i+1:i+3]==target:refs.append(200336+i)
    assert refs==[SPAN[0]+2,SPAN[0]+8],refs
    camera_target=old_screen_labels['GmCameraPoint'].to_bytes(2,'little');camera_refs=[]
    for i in range(len(code)-2):
        if code[i]in(0x20,0x4c)and code[i+1:i+3]==camera_target:camera_refs.append(200336+i)
    assert camera_refs==[203050,203357,203559]and all(raw[at]==0x20 for at in camera_refs[1:]),('Camera refs',camera_refs)
    draw_operands=[at+1 for at in camera_refs[1:]]
    assert all(W.location(b,'GmDraw')<=at<W.location(b,'GmDraw')+int(b['syms']['GmDraw']['size'],0)for at in draw_operands)
    patch=after+b'\xea';screen_patch=screen_after+wrapper
    spans=[dict(start=SPAN[0],end=SPAN[1],old=before.hex(),new=patch.hex()),dict(start=SCREEN[0],end=SCREEN[1],old=screen_before.hex(),new=screen_patch.hex())]
    spans.extend(dict(start=at,end=at+2,old=raw[at:at+2].hex(),new=new_screen_labels['GmCameraPoint'].to_bytes(2,'little').hex())for at in draw_operands)
    for span in spans:
        span.update(old_SHA256=sha256(bytes.fromhex(span['old'])).hexdigest(),new_SHA256=sha256(bytes.fromhex(span['new'])).hexdigest())
    return dict(bundle=b,before=before,after=patch,wrapper=wrapper,old_labels=old_labels,new_labels=new_labels,
        old_source=old_source,new_source=new_source,old_screen=old_screen,new_screen=new_screen,old_screen_labels=old_screen_labels,new_screen_labels=new_screen_labels,
        info=dict(parent_SHA256=PIN,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
            scope='Root source-test lease: four existing Gimmick-owned spans; no staging/native/delivery',spans=spans,
            public_anchors={name:old_labels[name]for name in('GmHead','GmFoot','GmSide')},body_old=old_labels['GmBodyProbe'],body_new=new_labels['GmBodyProbe'],
            body_call_operand_sites=[at+1 for at in refs],camera_old=old_screen_labels['GmCameraPoint'],camera_new=new_screen_labels['GmCameraPoint'],camera_call_operand_sites=draw_operands,
            ScreenPoint_public_unchanged=True,foreign_MiniLiftTick_BBCF_untouched=True,spare_claimed=0,
            material_change='Only side returnedA35 becomes0; R3/raw native cell retained; head/foot and other tiles unchanged',outputs=0))


@lru_cache(maxsize=1)
def proposal(raw):
    q=recipe(raw);out=bytearray(raw)
    for span in q['info']['spans']:
        a,z=span['start'],span['end'];assert out[a:z]==bytes.fromhex(span['old']);out[a:z]=bytes.fromhex(span['new'])
    out=bytes(out)
    assert sha256(out).hexdigest()==CANDIDATE
    changed={i for i,(a,b)in enumerate(zip(raw,out))if a!=b}
    assert changed<=set().union(*(set(range(span['start'],span['end']))for span in q['info']['spans']))
    info=dict(q['info'],candidate_SHA256=sha256(out).hexdigest(),changed_bytes=len(changed),total_owned_bytes=sum(span['end']-span['start']for span in q['info']['spans']),all_unowned_bytes_exact=True,source_only=True)
    return out,info


def inverse(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==CANDIDATE,'Expected exact Gimmick empty-side source candidate'
    b=dict(W.Symbols.bundle(),raw=raw);parent=bytearray(raw)
    for filename,first,last,origin,span in(('gimmick_host.s','GmHead','GmBodyProbe',START,SPAN),('gimmick_render.s','GmScreenPoint','GmCameraPoint',0xb8e6,SCREEN)):
        text=(R/'src'/filename).read_text();a=text.index('.proc '+first+'\n');z=text.index('.endproc',text.index('.proc '+last+'\n'))+len('.endproc');text=text[a:z]
        tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',text));symbols={name:W.address(b,name)for name in tokens if name in b['syms']}
        old,_=assemble(text,symbols,origin);assert len(old)==span[1]-span[0];parent[span[0]:span[1]]=old
    for at in(203358,203560):parent[at:at+2]=bytes.fromhex('1db9')
    parent=bytes(parent);assert sha256(parent).hexdigest()==PIN
    assert proposal(parent)[0]==raw
    return parent


@lru_cache(maxsize=1)
def current_proposal(actual16a):
    import compose_prince_body_transition_590_1115 as Prince
    assert isinstance(actual16a,bytes)and sha256(actual16a).hexdigest()==Prince.CANDIDATE
    old=Prince.inverse(actual16a);assert sha256(old).hexdigest()==PIN
    _,info=proposal(old);out=bytearray(actual16a);allowed=set()
    for span in info['spans']:
        a,z=span['start'],span['end'];assert actual16a[a:z]==old[a:z]==bytes.fromhex(span['old'])
        out[a:z]=bytes.fromhex(span['new']);allowed.update(range(a,z))
    out=bytes(out);assert all(a==b for i,(a,b)in enumerate(zip(actual16a,out))if i not in allowed)
    assert sha256(out).hexdigest()==CURRENT_CANDIDATE
    return out,dict(info,owning_current16a_SHA256=Prince.CANDIDATE,current_candidate_SHA256=sha256(out).hexdigest(),
        every_other_current16a_byte_exact=True,Prince_transition_preserved=True)


def current_inverse(raw):
    import compose_prince_body_transition_590_1115 as Prince
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==CURRENT_CANDIDATE,'Expected exact current16a plus Gimmick source candidate'
    # Source recipe preimages are derived independently, never from Downloads.
    legacy=bytearray(raw)
    b=dict(W.Symbols.bundle(),raw=raw)
    for filename,first,last,origin,span in(('gimmick_host.s','GmHead','GmBodyProbe',START,SPAN),('gimmick_render.s','GmScreenPoint','GmCameraPoint',0xb8e6,SCREEN)):
        text=(R/'src'/filename).read_text();a=text.index('.proc '+first+'\n');z=text.index('.endproc',text.index('.proc '+last+'\n'))+len('.endproc');text=text[a:z]
        tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',text));symbols={name:W.address(b,name)for name in tokens if name in b['syms']}
        old,_=assemble(text,symbols,origin);legacy[span[0]:span[1]]=old
    for at in(203358,203560):legacy[at:at+2]=bytes.fromhex('1db9')
    legacy=bytes(legacy);assert sha256(legacy).hexdigest()==Prince.CANDIDATE
    assert current_proposal(legacy)[0]==raw
    return legacy


if __name__=='__main__':
    import json
    raw,boundary=load590();print('RESULT '+json.dumps(dict(proposal(raw)[1],input_binding=boundary),separators=(',',':')),flush=True)
