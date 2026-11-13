"""Compose the same-size Karnov scene motor reset; no outputs or ROM writes."""
from hashlib import sha256
from pathlib import Path
import json
import zipfile

import compose_karnov_bomb_1112 as Bomb
from compose_metal_head_bridge_1112 import assemble_segments

R=Path(__file__).resolve().parents[2]
SOURCE=R/'tools/reference/karnov_scene_motor_1113.s'
ACTOR=Bomb.CHR+399*1024
RESIDENT=0x3bad5
PC=0xb0d4
OLD=bytes.fromhex('ad3e05c902d005a9808d62c0')
OLD_COOKIE=bytes.fromhex('a707011147d338f92c669d26e11e5b71')
BASE_ACTOR_SHA='cf90140900050afb905bb2967aed23c046cabeb8fc9e6a59de2755da070c4833'
PACKET=R/'docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/source.zip'
PACKET_SHA='ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777'


def code():
    pieces,_=assemble_segments(SOURCE.read_text(),{'SCENE_FACING':PC},
        {'PlayerFacingDir':0x53e,'KrState62':0xc062})
    result=pieces['SCENE_FACING']
    assert result==bytes.fromhex('ad3e052902f002a9808d62c0') and len(result)==len(OLD)
    return result


def source_proof():
    assert sha256(PACKET.read_bytes()).hexdigest()==PACKET_SHA
    with zipfile.ZipFile(PACKET)as z:
        source=z.read('host/kr-terrain.inc').decode()
    assert 'sta KrState+$66' in source.split('KrKeepLife:',1)[1].split('KrConstructNo:',1)[0]
    assert 'lda PlayerFacingDir\n cmp #2\n bne :+\n lda #$80\n sta KrState+$62\n:' in source


def transform(raw):
    source_proof()
    assert len(raw)==2097168
    image=raw[ACTOR:ACTOR+8192]
    assert sha256(image).hexdigest()==BASE_ACTOR_SHA
    at=ACTOR+PC-0xa000
    assert raw[at:at+len(OLD)]==OLD
    assert image[0x1fe0:0x1ff0]==raw[RESIDENT:RESIDENT+16]==OLD_COOKIE
    assert raw.count(OLD_COOKIE)==2
    result=bytearray(raw);new=code();result[at:at+len(new)]=new
    digest=sha256(b'Karnov scene motor 1113\0'+b''.join(
        result[Bomb.CHR+page*1024:Bomb.CHR+(page+count)*1024]
        for page,count,_ in Bomb.OWNED.values())).digest()[:12]
    cookie=bytes.fromhex('a7070112')+digest
    for header in (ACTOR+0x1fe0,RESIDENT):result[header:header+16]=cookie
    changed=[i for i,(a,b)in enumerate(zip(raw,result))if a!=b]
    allowed=set(range(at,at+len(OLD)))|set(range(ACTOR+0x1fe0,ACTOR+0x1ff0))|set(range(RESIDENT,RESIDENT+16))
    assert set(changed)<=allowed
    return bytes(result),dict(parent_SHA256=sha256(raw).hexdigest(),candidate_SHA256=sha256(result).hexdigest(),
        old_cookie=OLD_COOKIE.hex(),cookie=cookie.hex(),code_PC=PC,code_file=at,
        before=OLD.hex(),after=new.hex(),changed_bytes=len(changed),
        source_packet_SHA256=PACKET_SHA,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        other_roster_bytes_identical=True,allocation_growth=0)


def inverse(raw):
    at=ACTOR+PC-0xa000
    assert raw[at:at+len(OLD)]==code()
    result=bytearray(raw);result[at:at+len(OLD)]=OLD
    for header in (ACTOR+0x1fe0,RESIDENT):result[header:header+16]=OLD_COOKIE
    result=bytes(result)
    assert transform(result)[0]==raw
    return result


if __name__=='__main__':
    installed=Bomb.NIGHTLY.read_bytes()
    parent=inverse(installed)if installed[ACTOR+PC-0xa000:ACTOR+PC-0xa000+len(OLD)]==code()else installed
    candidate,report=transform(parent)
    assert inverse(candidate)==parent
    print(json.dumps(report,separators=(',',':')))

