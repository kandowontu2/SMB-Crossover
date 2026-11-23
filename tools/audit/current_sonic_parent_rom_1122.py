"""Recover exact Beans32 from installed Sonic59 in memory; no ROM outputs.

Only the reviewed Sonic motion/contact spans are restored. The original
611 motor bytes come from the retained, authenticated 5526-byte component,
not an asset copy or a second ROM. Every accepted image has a full SHA pin.
"""

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

R = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PARENT = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
CANDIDATE = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
CHR, COOKIE_AT = 1048592, 1034472
CODE_PAGES = (*range(321,328),330)
COOKIE_PAGES = CODE_PAGES+(328,333,334,224,226)
COMPONENT_SOURCE = R/'build/sonic-original-composed-frame-1110/component.s'
COMPONENT_SHA256 = 'f73192961c4fccab1cdc42c3c9ca10d05373accbd16611b7d883ddb2842a228d'
# Source labels RollingBody A283, JumpComponent A406 and RollingJump A492.
OLD_MOTION = bytes.fromhex(
    'a9008d49c0ad42c0c918f01118ad43c069088d43c0ad44c069008d44c0a9188d41c08d42c0ad20c08d10c0'
    'ad21c08d11c0ad22c08d13c0a9008d12c08d14c08d15c0ad10c00d11c00d13c0d0034c7da3a9098d31c0'
    'ad40c02904d024ad40c02902f01dad30c01008ad13c0303e4c53a3a9f08d14c0a9ff8d15c08d12c04ceca3'
    'ad40c02908d024ad40c02902f01dad30c01008ad13c010134c53a3a9108d14c0a9008d15c08d12c04ceca3'
    'a9048d14c0a9008d15c08d12c0ad13c010034ceca3a9fc8d14c0a9ff8d15c08d12c04ceca3ad30c029fc8d'
    '30c0a90a8d31c020f4a3a9ff8d12c0ad11c0d07fad30c009028d30c0a9018d31c04ceca3ad30c03021a909'
    '8d31c0ad10c0cd36c0ad11c0ed37c09057a9008d12c08d14c08d15c04ceca3a9078d31c0ad30c029fe8d30'
    'c0ad48c08d15c0ad47c08d14c0ad15c0101338a9b0ed14c08d10c0a9ffed15c08d11c0b017ad14c0d003ce'
    '15c0ce14c0ad14c08d47c0ad15c08d48c060a9018d49c04c00a038a900ed34c08d14c0a900ed35c08d15c060'
    'ad58c0d015ad56c02980f04cad56c02908d007ad57c02920f03ead57c02920d042ad58c0d00aa9108d58c0a9'
    '018d5ec0ad59c08d50c0ad5ac08d51c0a9ff8d52c0a9008d53c08d54c08d55c0ce58c0ad56c009048d56c0'
    '60ad56c029f78d56c04c71a4ad56c009088d56c0a9008d58c0ad51c03005cd5dc0b011ad5bc08d54c0ad5cc0'
    '8d55c0a9008d53c060ad56c02980f037ad56c02908d007ad57c02920f029ad57c02920d02dad56c029fe8d56c0'
    'ad5fc029f88d5fc0ad58c0d00aa9108d58c0a9018d5ec04c36a4ad56c029f78d56c04ce3a4ad56c009088d'
    '56c04c76a4')
OLD_INGRESS = bytes.fromhex(
    '0848ad0260c90df01468288d6a01a9a18d6c01a9b58d6d01a98a4c5a0168288a489848ad53078de37fade17f'
    '8d186f2027aa900668a868aa386068a868aa1860')
OLD_BODY_GATE = bytes.fromhex(
    'ad02604919f00c493ef0174c57b1eaeaeaeaeaa9158d6c01a9bb8d6d01a9f6d0dceaa9298d6c01a9b08d6d'
    '01a9c1d0cdea')


def H(raw):return sha256(raw).hexdigest()
def prg(bank,pc):return 16+bank*8192+(pc&8191)


PREIMAGES = (
    (CHR+321*1024+0x283,OLD_MOTION,'original motor functions'),
    (CHR+330*1024+0x2c8,bytes.fromhex('8d47c0'),'original constructor STA'),
    (prg(74,0xabdc),OLD_INGRESS,'native body ingress'),
    (prg(74,0xbf03),OLD_BODY_GATE,'native typed body gate'),
    (CHR+328*1024+0x121,bytes.fromhex('4ce5d0'),'original body service row'),
    (CHR+328*1024+0x37c,b'\xff'*132,'unused body tail'),
    (CHR+334*1024+0x380,b'\xff'*112,'unused slow-roll tail'),
)


@lru_cache(maxsize=1)
def inverse(raw):
    """Strict 59e1a591 -> 32eaf178 byte image; never reads or writes a path."""
    assert isinstance(raw,bytes) and len(raw)==2097168 and H(raw)==CANDIDATE, 'Exact installed Sonic59 required'
    assert len(OLD_MOTION)==0x4e6-0x283 and len(OLD_INGRESS)==64 and len(OLD_BODY_GATE)==49
    restored=bytearray(raw)
    for at,data,_ in PREIMAGES:
        restored[at:at+len(data)]=data
    pages=b''.join(restored[CHR+p*1024:CHR+(p+1)*1024]for p in COOKIE_PAGES)
    restored[COOKIE_AT:COOKIE_AT+16]=bytes.fromhex('a72b01')+sha256(pages).digest()[:13]
    result=bytes(restored)
    assert len(result)==len(raw) and H(result)==PARENT, 'Exact Beans32 reconstruction failed'
    return result


def parent32(raw):
    """Accept only exact32 or exact59; return the strict exact32 reference."""
    if isinstance(raw,bytes) and len(raw)==2097168 and H(raw)==PARENT:return raw
    return inverse(raw)


def verify(raw):
    parent=inverse(raw)
    import compose_sonic_original_motion_1122 as Motion
    import run_sonic_original_full11_1122 as Forward
    # Authenticate the compact old code against the retained assembly recipe.
    assert H(COMPONENT_SOURCE.read_bytes())==COMPONENT_SHA256
    import sonic_sms_relocated_core_1110 as Core
    original=Core.assemble(COMPONENT_SOURCE.read_text(),relocated=True)['image']
    assert original[0x283:0x4e6]==OLD_MOTION
    composition=Forward.strict(parent,raw)
    assert composition['candidate_SHA256']==CANDIDATE
    assert parent32(parent) is parent and parent32(raw)==parent
    spans=[(at,len(data),role)for at,data,role in PREIMAGES]+[(COOKIE_AT,16,'original packet cookie')]
    owned={i for at,size,_ in spans for i in range(at,at+size)}
    changed={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
    assert changed<=owned
    rejected=0
    for at in (0,prg(74,0xabdc),CHR+321*1024+0x283,COOKIE_AT,len(raw)-1):
        bad=raw[:at]+bytes((raw[at]^1,))+raw[at+1:]
        try:parent32(bad)
        except AssertionError:rejected+=1
        else:raise AssertionError('Modified image admitted')
    return dict(passed=True,input_SHA256=H(raw),parent_SHA256=H(parent),forward_roundtrip_exact=True,
                motor_preimages_source_verified=True,spans=spans,owned_bytes=len(owned),
                changed_bytes=len(changed),outside_spans_exact=True,dirty_images_rejected=rejected,
                source_SHA256=H(Path(__file__).read_bytes()),outputs=0,native=False)


def main():
    raw=ROM.read_bytes()
    def deny(*args,**kwargs):raise AssertionError('Parent reader attempted outputs or process launch')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=verify(raw)
    assert ROM.read_bytes()==raw
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('SONIC_PARENT32 '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
