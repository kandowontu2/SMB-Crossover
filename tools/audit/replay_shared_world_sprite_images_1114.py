"""Strict421 ordinary first-Goomba/first-Mushroom image probes, stdout only.

Root alone launches Mesen. Images diagnose the existing cartridge; no expected
graphics result is imposed on a suspected broken mapping.
"""
from functools import lru_cache
from hashlib import sha256
import json

import replay_smb1_alts_full11_1114 as Frozen
import prince_cold_packet_1111 as Prince

R,ROM,PIN,W,N=Frozen.R,Frozen.ROM,Frozen.PIN,Frozen.W,Frozen.N
TEMPLATE=R/'tools/playthroughs/shared_world_sprite_images_1114.lua'
TEMPLATE_SHA='623a075ec25b5c7df77e9a34fa6dacb08b4da9126c80fdd31435b59a0fffa00b'
IDENTITIES={
    'prince':('PRINCE PERSIA',29,1,38,-1),
    'donkey_kong':('DONKEY KONG',27,0,28,-1),
    'hogan':('HULK HOGAN',28,0,29,0),
    'dibiase':('TED DIBIASE',28,1,29,1),
    'bigelow':('BAM BAM BIGELOW',28,2,29,2),
    'honky':('HONKY TONK MAN',28,3,29,3),
    'savage':('RANDY SAVAGE',28,4,29,4),
    'andre':('ANDRE THE GIANT',28,5,29,5),
}


@lru_cache(maxsize=8)
def bindings(raw,key):
    assert key in IDENTITIES and sha256(raw).hexdigest()==PIN
    normalized=Frozen.normalize(raw)
    base=Frozen.bindings(raw,'toad')
    b=dict(W.Symbols.bundle(),raw=raw)
    name,slot,cycle,owner,role=IDENTITIES[key]
    m=W.UI.seed(b,0)
    navigation=[4]*(slot//8)+[1]*(slot%8)+[32]*cycle
    for bits in navigation:W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]==name,(key,W.UI.menu_name(m))
    assert N.get(m,'CrossoverMenuIndex')==slot and N.get(m,'SelectedCharacter')==owner
    assert role<0 or N.get(m,'FmGroups')&7==role
    names=('Player_Y_HighPos','Enemy_Y_HighPos','Enemy_SprAttrib','EnemyMetasprite',
        'PowerUpType','CurrentCHRBank','X5WideChrActive','FmGroups','Mirror_PPUCTRL')
    ram=dict(base['ram'])
    ram.update({n:W.address(b,n)for n in names})
    records={}
    for name_ in('MetaspriteData_GOOMBA_WALKING_1_LEFT','MetaspriteData_GOOMBA_WALKING_1_RIGHT',
        'MetaspriteData_GOOMBA_WALKING_2_LEFT','MetaspriteData_GOOMBA_WALKING_2_RIGHT',
        'MetaspriteData_POWERUP_MUSHROOM_RIGHT'):
        at=W.location(b,name_);length=raw[at]+1
        assert length==9,(name_,length)
        assert raw[at:at+length]==normalized.postbg[at:at+length]
        records[name_]=dict(pc=W.address(b,name_),offset=at-16,bytes=list(raw[at:at+length]))
    tables={}
    for name_,length in(('CHRBankInitValues',12),('ChrPhysicalMap',256),('GroundPaletteData',35)):
        at=W.location(b,name_)
        assert raw[at:at+length]==normalized.postbg[at:at+length]
        tables[name_]=dict(offset=at-16,bytes=list(raw[at:at+length]),SHA256=sha256(raw[at:at+length]).hexdigest())
    cookie=[];packet={}
    if key=='prince':
        head,chunks,lengths=Prince.extract(raw)
        cookie=list(raw[Prince.COOKIE:Prince.COOKIE+16])
        packet=dict(cookie=bytes(cookie).hex(),header_SHA256=sha256(head).hexdigest(),
            chunk_SHA256=[sha256(x).hexdigest()for x in chunks],compressed_lengths=list(lengths))
    return dict(sha=PIN,key=key,name=name,slot=slot,cycle=cycle,owner=owner,role=role,
        navigation=navigation,ram=ram,hooks=base['hooks'],records=records,tables=tables,
        prince_cookie=cookie,prince_packet=packet,maximum_images=2,maximum_PNG_bytes=65536)


@lru_cache(maxsize=8)
def controller(raw,key):
    config=bindings(raw,key)
    assert sha256(TEMPLATE.read_bytes()).hexdigest()==TEMPLATE_SHA
    text='local C='+Frozen.lua(config)+'\n'+TEMPLATE.read_text(encoding='utf-8')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text


def metadata(raw,key):
    c=bindings(raw,key);text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:c[k]for k in('name','slot','cycle','owner','role')},
        controller_SHA256=sha256(text.encode()).hexdigest(),
        template_SHA256=sha256(TEMPLATE.read_bytes()).hexdigest(),
        native_metasprites=c['records'],native_tables=c['tables'],prince_packet=c['prince_packet'],
        images='first live Goomba; naturally emerged kind0 Mushroom',maximum_images=2,maximum_PNG_bytes=65536,
        PPUCTRL_and_MMC5_CHR_latches=True,actual_OAM_and_physical_CHR_ROM=True,
        normal_controller_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,required=True)
    a=p.parse_args();print(json.dumps(metadata(ROM.read_bytes(),a.identity),separators=(',',':')),flush=True)
