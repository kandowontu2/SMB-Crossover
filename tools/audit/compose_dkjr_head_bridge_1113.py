"""In-memory DK Jr accepted-head bridge; no new ROM/RAM/carrier allocation."""
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

import check_dkjr_powerups_current_1113 as Base

R=Base.R
sys.path.insert(0,str(R/'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

SOURCE=R/'tools/reference/dkjr_head_bridge_1113.s'
FROZEN=R/'build/dkjr-native-source-1102-v2/native-entrance-v89.s'
FROZEN_SHA='82cca72d6091ca2569093e7fd35aba55f43e0d191de06224d8b2335e316c839d'
ATLAS=R/'build/dkjr-native-source-1102-v2/native-atlas-v38.json'
RECT_START,RECT_END=0xadea,0xaeef
SCORE_START,SCORE_END=0xb940,0xb9be
HOOK=0xa3b7
LAYOUT=dict(RECT=(RECT_START,RECT_END-RECT_START),SCORE=(SCORE_START,SCORE_END-SCORE_START),HEAD_HOOK=(HOOK,6))
HEAD_X,HEAD_PAGE,HEAD_TOP=0xc4b4,0xc4b5,0xc4b6
GIRDER=R/'tools/reference/dkjr_late_girder_admission_1111.s'
GIRDER_LAYOUT=dict(BOX=(0xbd3c,9),ROWS=(0xd2c4,17),PIPE=(0xd18b,117),
    REFRESH_TARGET=(0xb7b8,3),REFRESH=(0xb624,129),NATIVE_CALL=(0xb7ca,30))
OLD_ROWS=bytes.fromhex('1a1e23272b2f373b58a1a5b1bea9a9a1a1')


def offset(pc):return pc-0xa000 if pc<0xc000 else 9*1024+pc-0xd000


def payload(raw):
    return b''.join(raw[Base.CHR+p*1024:Base.CHR+(p+1)*1024]for p in Base.PAGES)


def retained(path,packet,digest):
    if path.exists():data=path.read_bytes()
    else:
        with ZipFile(R/'docs/qa/checkpoints/2026-11-03'/packet/'inputs.zip')as archive:
            names=[n for n in archive.namelist()if n==path.name or n.endswith('/'+path.name)]
            assert len(names)==1,(path,names)
            data=archive.read(names[0])
    assert sha256(data).hexdigest()==digest,path
    return data


def old_source():
    text=retained(FROZEN,'dkjr-entrance-ready-v100',FROZEN_SHA).decode().replace('\r\n','\n')
    rect=text[text.index('D_eb75:'):text.index('D_ebe3:')]
    score=text[text.index('DkScoreFlush:\n'):text.index('; Explicit constructor, after original actor init/body pose/native anchor.')]
    definitions='R0=$03\nObjectOffset=$0d\nDigitModifier=$0131\nScoreAmount=$c8f9\n'
    return text,rect,score,definitions


def linked(raw):
    carrier=payload(raw);text,rect,score,definitions=old_source()
    old_rect=assemble(f'D_ebe3=${RECT_END:x}\n.segment "OLD"\n'+rect,dict(OLD=LAYOUT['RECT']))
    assert old_rect['used']==dict(OLD=261)
    assert carrier[RECT_START-0xa000:RECT_END-0xa000]==old_rect['images']['OLD']
    staged=assemble(definitions+'DkjrNativeAddScore=$ffff\n.segment "OLD"\n'+score,dict(OLD=LAYOUT['SCORE']))
    targets=[i['pc']for i in staged['instructions']if i['op']=='JSR'and i['operand']==65535]
    assert len(targets)==1
    p=targets[0]-0xa000
    add_score=int.from_bytes(carrier[p+1:p+3],'little')
    old_score=assemble(definitions+f'DkjrNativeAddScore=${add_score:x}\n.segment "OLD"\n'+score,dict(OLD=LAYOUT['SCORE']))
    assert old_score['used']==dict(OLD=126)
    assert carrier[SCORE_START-0xa000:SCORE_END-0xa000]==old_score['images']['OLD']
    b=Base.W.Symbols.bundle();b['raw']=raw
    native={name:Base.W.address(b,name)for name in ('MTileAttribute','BlockBounceTimer','GuestHurtTicks','TimerControl')}
    head='NativeRarePlayerHeadCollisionCore'
    native.update(ScreenLeftX=Base.W.address(b,'ScreenLeft_X_Pos'),ScreenLeftPage=Base.W.address(b,'ScreenLeft_PageLoc'),
        HeadX=HEAD_X,HeadPage=HEAD_PAGE,HeadTop=HEAD_TOP,R2=5,R6=9,R7=10,SafecallA=0x16a,FarTarget=0x16c,FarCall=0x15a,
        RectPredicate=RECT_END,HeadReturn=0xaf02,NativeAddScore=add_score,NativeHeadEffect=Base.W.address(b,head),
        NativeHeadBank=((Base.W.location(b,head)-16)//8192)|128)
    prelude=definitions+''.join(f'{n}=${v:x}\n'for n,v in native.items())
    new=assemble(prelude+SOURCE.read_text(),LAYOUT)
    assert carrier[0xaf02-0xa000]==0x60 # Existing predicate's plain RTS.
    return old_rect,old_score,new


def girder_images(*,reserve_powerup_slot=False):
    source=GIRDER.read_text();new=source
    changes=(('ActorCount = 13','ActorCount = 14'),
        ('WorldColumns: .byte 26,','WorldColumns: .byte 21,26,'),
        ('    cpy #8\n    beq Horizontal','    cpy #9\n    beq Horizontal'),
        ('OscillatorY: .byte 128,','OscillatorY: .byte 128,128,'))
    for before,after in changes:
        assert new.count(before)==1,before
        new=new.replace(before,after)
    if reserve_powerup_slot:
        assert new.count('    ldx #5\nFind:')==1
        new=new.replace('    ldx #5\nFind:','    ldx #4\nFind:')
    old,linked=[assemble(text,GIRDER_LAYOUT)for text in(source,new)]
    assert old['used']['REFRESH']==128 and linked['used']['REFRESH']==129
    assert linked['used']['ROWS']==14 and linked['used']['PIPE']==117
    assert linked['symbols']['DkAfterNativeConstructor']==0xd1f0
    assert linked['symbols']['DkRefreshPlatformEnd']==0xb6a5
    return old,linked


def transform(raw,*,helper=False,reserve_powerup_slot=False):
    original=payload(raw)
    assert sha256(original).hexdigest()=='30b1118ac41a70e81c2eda030f5d93a5f56b57feb8600415f860e6007dfffc83'
    assert raw[Base.COOKIE_AT:Base.COOKIE_AT+16]==Base.COOKIE
    old_rect,old_score,new=linked(raw)
    assert original[HOOK-0xa000:HOOK-0xa000+6]==bytes.fromhex('a9048d6bc060')
    body=bytearray(original)
    for name,(pc,size)in LAYOUT.items():
        body[pc-0xa000:pc-0xa000+size]=new['images'][name].ljust(size,b'\xea')
    regions=dict(LAYOUT)
    if helper:
        old,lifts=girder_images(reserve_powerup_slot=reserve_powerup_slot)
        for name in('ROWS','PIPE','REFRESH'):
            pc,size=GIRDER_LAYOUT[name];at=offset(pc)
            expected=OLD_ROWS if name=='ROWS'else old['images'][name].ljust(size,b'\xff')
            assert original[at:at+size]==expected,name
            replacement=lifts['images'][name]
            replacement=replacement+expected[len(replacement):]if name=='ROWS'else replacement.ljust(size,b'\xff')
            body[at:at+size]=replacement;regions['GIRDER_'+name]=(pc,size)
    cookie=Base.COOKIE[:3]+sha256(body).digest()[:13]
    image=bytearray(raw);changed_pages=[]
    for i,page in enumerate(Base.PAGES):
        at=Base.CHR+page*1024;chunk=body[i*1024:(i+1)*1024]
        if image[at:at+1024]!=chunk:changed_pages.append(page);image[at:at+1024]=chunk
    image[Base.COOKIE_AT:Base.COOKIE_AT+16]=cookie
    changed=[i for i,(a,z)in enumerate(zip(raw,image))if a!=z]
    allowed={Base.COOKIE_AT+i for i in range(16)}
    for name,(pc,size)in regions.items():
        for j in range(offset(pc),offset(pc)+size):
            page,off=divmod(j,1024);allowed.add(Base.CHR+Base.PAGES[page]*1024+off)
    assert set(changed)<=allowed and len(raw)==len(image)
    return bytes(image),dict(parent_SHA256=sha256(raw).hexdigest(),candidate_SHA256=sha256(image).hexdigest(),
        cookie=cookie.hex(),changed_bytes=len(changed),changed_pages=changed_pages,
        used=new['used'],labels=new['symbols'],new_allocation_bytes=0,ROM_written=False,
        helper=dict(stage='1-1',left=336,center=352,initial_top=192,width=32,
            native_ID=37,oscillator=128,slots=list(range(5 if reserve_powerup_slot else 6)),
            native_powerup_slot5_reserved=reserve_powerup_slot,
            original_dynamic_powerup_allocator_retained=not reserve_powerup_slot,
            existing_13_rows_retained=True)if helper else None)


def inverse(raw):
    body=bytearray(payload(raw))
    assert raw[Base.COOKIE_AT:Base.COOKIE_AT+16]==Base.COOKIE[:3]+sha256(body).digest()[:13]
    _,rect,score,definitions=old_source()
    old_rect=assemble(f'D_ebe3=${RECT_END:x}\n.segment "OLD"\n'+rect,dict(OLD=LAYOUT['RECT']))['images']['OLD']
    old_score=assemble(definitions+'DkjrNativeAddScore=$bb37\n.segment "OLD"\n'+score,dict(OLD=LAYOUT['SCORE']))['images']['OLD']
    body[RECT_START-0xa000:RECT_END-0xa000]=old_rect
    body[SCORE_START-0xa000:SCORE_END-0xa000]=old_score
    body[HOOK-0xa000:HOOK-0xa000+6]=bytes.fromhex('a9048d6bc060')
    at=offset(0xd2c4);helper=body[at:at+17]!=OLD_ROWS
    reserve=False
    if helper:
        old,lifts=girder_images()
        try_pc=lifts['symbols']['DkPipeTry']
        reserve=body[offset(try_pc)+2:offset(try_pc)+4]==bytes.fromhex('a204')
        assert body[offset(try_pc)+2:offset(try_pc)+4]in(bytes.fromhex('a204'),bytes.fromhex('a205'))
        for name in('ROWS','PIPE','REFRESH'):
            pc,size=GIRDER_LAYOUT[name];at=offset(pc)
            body[at:at+size]=OLD_ROWS if name=='ROWS'else old['images'][name].ljust(size,b'\xff')
    assert sha256(body).hexdigest()=='30b1118ac41a70e81c2eda030f5d93a5f56b57feb8600415f860e6007dfffc83'
    parent=bytearray(raw)
    for i,page in enumerate(Base.PAGES):
        at=Base.CHR+page*1024;parent[at:at+1024]=body[i*1024:(i+1)*1024]
    parent[Base.COOKIE_AT:Base.COOKIE_AT+16]=Base.COOKIE
    parent=bytes(parent)
    assert transform(parent,helper=helper,reserve_powerup_slot=reserve)[0]==raw
    return parent


if __name__=='__main__':
    raw,input_info=Base.proof_parent(Base.C.ROM.read_bytes());candidate,info=transform(raw)
    print('DKJR_PROOF_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    print(json.dumps(info,separators=(',',':')),flush=True)
