"""Small current-byte Sonic policy witness, no CPU/item route/old builders."""
from pathlib import Path
from hashlib import sha256
import json,re,struct

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
H=lambda b:sha256(b).hexdigest()
CHR=1048592


def run(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    at=lambda bank,pc:16+8192*bank+(pc&8191)
    page=lambda p:raw[CHR+1024*p:CHR+1024*(p+1)]
    kernel=b''.join(page(p)for p in(*range(321,328),330));meta=page(328)
    assert H(kernel)=='2b727a4a7856d477af9b5051ad30541f1ec97f4854cd247cfaf617203d648936'
    assert H(meta)=='367881d827a2cb80aafe71ea45dcdf4c8791ac3a129eaea781be4e579c9067f4'
    power=struct.unpack('<H',meta[52:54])[0];wrapper=kernel[power-0xa000:power-0xa000+25]
    expected=bytes.fromhex('48a9008d1ac1688d6a01a9998d6c01a9b28d6d01a98a4c5a01')
    assert wrapper==expected
    update=raw[at(10,0xb299):at(10,0xb299)+160]
    comparisons=list(re.finditer(b'\xc9\x3c\xb0(.)',update,re.S));assert len(comparisons)==1
    hit=comparisons[0];finish=0xb299+hit.start()+4+int.from_bytes(hit.group(1),'little',signed=True)
    finish_bytes=raw[at(10,finish):at(10,finish)+48]
    assert finish_bytes[:6].hex()=='ad006c8d5b07'and bytes.fromhex('8d5907')in finish_bytes
    # Preserve the whole actual unsupported-special chain as an unexecuted
    # 1UP prerequisite lead. Never infer a gameplay fault from this scan.
    pattern=b'\xad(..)\xc9\x5f\xf0(.)\xc9\x60\xf0(.)\xc9\x67\xf0(.)\xc9\x68\xd0(.)\xa9\x07\x4c(..)'
    hits=list(re.finditer(pattern,kernel,re.S));assert len(hits)==1
    match=hits[0];pc=0xa000+match.start();reject=pc+19
    assert all(pc+offset+2+int.from_bytes(match.group(group),'little',signed=True)==reject for offset,group in((5,2),(9,3),(13,4)))
    shape_source=R/'tools/reference/sonic_sms_native_shape_contact_1110.py'
    assert ' cmp #$60\n beq UnsupportedTile'in shape_source.read_text()
    original=R/'tools/audit/replay_sonic_vol2_forms_1111.py'
    assert H(original.read_bytes())=='8d7660ea9d2788437ae8768f81f45399ecf29b48d38ea8dc39de7f5ed5ceec74'
    native=raw[at(3,0xaf71):at(3,0xaf71)+256]
    assert bytes.fromhex('a9238d9c07a9408d0101')in native
    assert bytes.fromhex('a90b9d0d0160')in native
    out=dict(passed=True,read_only=True,actual_SHA256=PIN,source_SHA256=H(Path(__file__).read_bytes()),
        powerup_row33=dict(bank=3,PC=power,hex=wrapper.hex(),native_target=dict(PRG=10,PC=0xb299),
            semantics='Clear HaveEpoch then preserve incoming A and farcall genuine GuestPowerupUpdate'),
        native_growth_finish=dict(PRG=10,age_compare_PC=0xb299+hit.start(),required_age=60,finish_PC=finish,first48=finish_bytes.hex(),
            semantics='Publish GuestPowerupTarget to native status and clear native PlayerSize; actual pickup remains unrun'),
        native_star=dict(PRG=3,entry=0xaf71,timer=35,music=64,popup=6),native_life=dict(popup=11,credit='delayed native life writer'),
        hidden60_static_lead=dict(PRG_view='loaded raw3',PC=pc,hex=match.group().hex(),reject_PC=reject,
            fail_target=int.from_bytes(match.group(6),'little'),code=7,source_SHA256=H(shape_source.read_bytes()),
            scope='Actual bytes reject special5f/60/67/68 in this shape leaf. Ordinary upward hidden60 path must be observed before any game-defect or repair claim.'),
        retained_controller_source_SHA256=H(original.read_bytes()),no_new_controller_or_seed_or_code_change=True,CPU_executed=False,outputs=0)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(run(ROM.read_bytes()),separators=(',',':')),flush=True)
