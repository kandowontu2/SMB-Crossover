"""Exact bc5 Bowser stock binding with one retained packet read in memory."""
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import json,zipfile
import current_sunny_stock_live_bc5_1115 as Boundary
import check_bowser_natural_powerups_1113 as Historical

R,ROM,PIN,W,N,Frames=Boundary.R,Boundary.ROM,Boundary.PIN,Historical.W,Historical.N,Historical.Frames
ARCHIVE=R/'docs/qa/checkpoints/2026-10-31/bowser-playable-contact-jump-source/source-only.zip'
IMAGE_SHA='bb43cfb45f5b931dd1beff853825bcb1f3c3d70c63599b9e69a442959e561b2f'
COOKIE=bytes.fromhex('a71b0005bb43cfb45f5b931dd1beff85')
digest=lambda data:sha256(data).hexdigest()
reference=Boundary.reference

@lru_cache(maxsize=1)
def frozen_image():
    with zipfile.ZipFile(ARCHIVE)as archive:
        names=[n for n in archive.namelist()if n.replace('\\','/').endswith('/bowser-playable-jump-v1/joint/bowser.bin')]
        assert len(names)==1,names
        assert archive.getinfo(names[0]).file_size==8192
        raw=archive.read(names[0])
    assert len(raw)==8192 and digest(raw)==IMAGE_SHA
    return raw

def bundle(raw):reference(raw);return dict(W.Symbols.bundle(),raw=raw)

@lru_cache(maxsize=1)
def preservation(raw):
    b=bundle(raw);image=frozen_image();end=W.address(b,'BwCoreEnd')-0xa000
    assert 0<end<8192
    cookie=W.location(b,'BwCookie');assert raw[cookie:cookie+16]==COOKIE
    return dict(ROM_SHA256=PIN,inverse_reference67_SHA256=Boundary.Original.REFERENCE,
        retained_packet_SHA256=IMAGE_SHA,retained_packet_bytes=8192,decoded_executable_end=end,
        current_ROM_cookie_file=cookie,cookie=COOKIE.hex(),archive_reads='Exactly one8192-byte member; no extraction or dependency reconstruction',
        historical='7ef full/M/F native scopes remain historical; current S/L require actual current execution',outputs=0)

def cold(raw,key='smb3'):
    identity={'smb3':0,'smb1':1}[key];proof=preservation(raw)
    m,opening=Historical.cold(raw,identity)
    assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    actual=bytes(m.ram[3]);image=frozen_image();end=proof['decoded_executable_end']
    assert actual[:end]==image[:end],'Current constructor changed or loaded a different executable packet'
    assert actual[0x1fe0:0x1ff0]==COOKIE
    assert N.get(m,'SelectedCharacter')==27 and bool(N.get(m,'FmAlts')&8)==bool(identity)
    return m

def inspect_inputs(raw):
    b=bundle(raw);proof=preservation(raw);rows=[]
    for key in('smb3','smb1'):
        m=cold(raw,key)
        rows.append(dict(key=key,name=W.UI.menu_name(m)[0],x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),lives=N.get(m,'NumberofLives'),status=N.get(m,'PlayerStatus'),
            variant=m.ram[3][0x1e1c],tier=m.ram[3][0x1e28],HP=m.ram[3][0x1e29],ready=m.ram[3][0x1e26],
            executable_SHA256=digest(bytes(m.ram[3][:proof['decoded_executable_end']]))))
    q=dict(passed=True,preservation=proof,openings=rows,source_frontend='Compiled actual menu/Select/Start/parser; bus lacks real title vblank',outputs=0,Mesen=False)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q
