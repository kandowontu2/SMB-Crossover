"""Compose an existing-native Jay pickup helper inside its owned worker."""

from hashlib import sha256
import json

import compose_jay_head_bridge_1113 as Head
import check_jay_silius_helpers_1111 as Helpers

B=Head.B
R=B.Current.W.R
SOURCE=R/'tools/reference/jay_pickup_helper_1113.s'
ORIGIN=0xbd20
PAGES={
    218:'eedc487ca73455425f3d15c33564ee1245069783d942a4b75e1fc77dd186bb09',
    222:'f8e5eda2bd719cd86c0a8ce4aea1b8049f88ecc0b92bde0b7c5a13e8763f36e3',
    232:'562958a0389dc647d345f31980e75ee51eefbad8a21c258c6618b92c4b469943',
    234:'552e046185c8cd7f6b7c1fdc741de41a7b283b030ef91dc26ff1d3de35f2d9dc',
    331:'fe4fcf514ac332cb7fad294fda28571c04e8f6af1e17c73eaa7dbee2557a762d',
    332:'5805d4f2300ceed8d4c2b6fb552083f644bd5c4df66f464fccd18571ef7e14f5',
}
PIN='eac09fa8805fecc96df0447516abe9b7264b9d8c6db9399cf8dc444453624baf'
COOKIE=bytes.fromhex('a810200c4dbf5b49c59d4e142de148bf')


def digest(data):return sha256(data).hexdigest()


def linked(bundle):
    old,fields=Helpers.assemble(bundle,origin=ORIGIN)
    definitions=''.join(f'{n}=${v:04x}\n'for n,v in fields.items())
    new=B.Gun.H.assemble(definitions+SOURCE.read_text(),{'HELPERS':(ORIGIN,247)})
    assert old['used']==new['used']=={'HELPERS':247}
    assert old['symbols']['StepHelpers']==new['symbols']['StepHelpers']==ORIGIN
    assert new['symbols']['ResetHelpers']==old['symbols']['ResetHelpers']-4
    return old,new,fields


def proposal(raw):
    assert len(raw)==2097168 and digest(raw)==Head.CANDIDATE_PIN
    for page,want in PAGES.items():assert digest(B.Gun.T.page(raw,page))==want,page
    old_cookie=Head.NEW_COOKIE
    assert raw.count(old_cookie)==2
    bundle=dict(B.Current.W.Symbols.bundle(),raw=raw)
    old,new,fields=linked(bundle)
    page=B.Gun.T.EXTRA_PAGE
    first=B.Gun.C.CHR+page*1024+ORIGIN-0xbc00
    before,after=(p['images']['HELPERS']for p in (old,new))
    assert raw[first:first+len(before)]==before
    motion=B.Gun.C.CHR+B.Gun.T.MOTION_PAGE*1024
    previous=b'\x20'+old['symbols']['ResetHelpers'].to_bytes(2,'little')
    replacement=b'\x20'+new['symbols']['ResetHelpers'].to_bytes(2,'little')
    row=raw[motion:motion+1024]
    assert row.count(previous)==1
    reset_at=motion+row.index(previous)
    cookie=bytes.fromhex('a810200c')+sha256(b'Jay native pickup helper 1113\0'+old_cookie+after+replacement).digest()[:12]
    cold=B.Gun.C.offset(65,B.Gun.T.COLD)
    cookie_at=raw.index(old_cookie,cold,cold+B.Gun.T.COLD_SIZE)
    edits=((first,before,after),(reset_at,previous,replacement),
           (cookie_at,old_cookie,cookie),(B.Gun.C.offset(94,0xb2ef),old_cookie,cookie))
    out=bytearray(raw)
    for at,a,b in edits:
        assert len(a)==len(b) and raw[at:at+len(a)]==a
        out[at:at+len(b)]=b
    image=bytes(out)
    assert digest(image)==PIN and cookie==COOKIE
    assert B.Gun.T.page(image,331)+B.Gun.T.page(image,332)==B.Gun.T.page(raw,331)+B.Gun.T.page(raw,332)
    return image,dict(parent_SHA256=digest(raw),candidate_SHA256=digest(image),cookie=cookie,
        edits=edits,old=old,new=new,fields=fields,allocation_growth=0,
        source_SHA256=digest(SOURCE.read_bytes()),placement=dict(stage='1-1',left=384,center=400,initial_top=192,width=32))


def inverse(raw):
    assert digest(raw)==PIN and raw.count(COOKIE)==2
    bundle=dict(B.Current.W.Symbols.bundle(),raw=raw)
    old,new,_=linked(bundle)
    out=bytearray(raw)
    first=B.Gun.C.CHR+B.Gun.T.EXTRA_PAGE*1024+ORIGIN-0xbc00
    a,b=old['images']['HELPERS'],new['images']['HELPERS']
    assert raw[first:first+len(b)]==b
    out[first:first+len(a)]=a
    motion=B.Gun.C.CHR+B.Gun.T.MOTION_PAGE*1024
    previous=b'\x20'+old['symbols']['ResetHelpers'].to_bytes(2,'little')
    changed=b'\x20'+new['symbols']['ResetHelpers'].to_bytes(2,'little')
    assert raw[motion:motion+1024].count(changed)==1
    at=motion+raw[motion:motion+1024].index(changed)
    out[at:at+3]=previous
    cold=B.Gun.C.offset(65,B.Gun.T.COLD)
    at=raw.index(COOKIE,cold,cold+B.Gun.T.COLD_SIZE)
    for at in(at,B.Gun.C.offset(94,0xb2ef)):out[at:at+16]=Head.NEW_COOKIE
    restored=bytes(out)
    assert digest(restored)==Head.CANDIDATE_PIN and proposal(restored)[0]==raw
    return restored


def frozen_head():
    installed=B.Current.ROM.read_bytes()
    if digest(installed)==Head.CANDIDATE_PIN:return installed
    if digest(installed)not in(Head.PARENT_PIN,PIN):
        import compose_quick_climb_material_1113 as Quick
        installed=Quick.inverse(installed)
    if digest(installed)==PIN:
        # Delivered Quick+Jay unwinds Quick -> helper -> head -> exact a3,
        # then repeats the original typed recipe. Strict APIs stay pinned.
        installed=Head.inverse(inverse(installed))
    assert digest(installed)==Head.PARENT_PIN
    return Head.proposal(installed)[0]


if __name__=='__main__':
    parent=frozen_head()
    image,info=proposal(parent)
    assert inverse(image)==parent
    _,loaded=Head.cold(image,COOKIE,PIN)
    at=ORIGIN-0xa000;body=info['new']['images']['HELPERS']
    assert bytes(loaded.ram[3][at:at+len(body)])==body
    print(json.dumps({k:v.hex()if isinstance(v,bytes)else v for k,v in info.items()if k not in('old','new','fields','edits')}),flush=True)
    print(json.dumps(dict(pages={p:digest(B.Gun.T.page(parent,p))for p in(218,222,B.Gun.T.MOTION_PAGE,234,331,332)},
        reset_old=info['old']['symbols']['ResetHelpers'],reset_new=info['new']['symbols']['ResetHelpers'],
        worker_size=info['new']['used'],edits=[(at,len(a))for at,a,b in info['edits']])),flush=True)
