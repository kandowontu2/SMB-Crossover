"""Exact six-operand repair of the two SMB2 DMC post-BG aliases, in memory."""
from hashlib import sha256
import json
from pathlib import Path

import replay_smb2_dmc_alias_native_1113 as Owner

R = Path(__file__).resolve().parents[2]
W, N = Owner.Terrain.W, Owner.Terrain.N
PIN = '3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
CANDIDATE = '12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
GRANT = R/'docs/qa/allocations/smb2-postbg-mirrors-1113.json'
GRANT_SHA = '51cc906ffbb81f478639425aed5d7ea446980f345797eae85b936602db153d92'
BRIDGE = 0xe5cc
OLD = bytes.fromhex('8d6a01ad02604903d00d20a4ac0848a902203792682860ad6a018d6a01a9878d6c01a9bb8d6d01a9cf4c5a01eaeaeaeaea')
CANONICAL = bytes.fromhex('8d6a01ad02604903d00d20a4ac0848a902203792682860ad6a018d6a01a9388d6c01a9b48d6d01a9c24c5a01eaeaeaeaea')
EDITS = tuple((16+bank*8192+(pc&8191), old, new)
              for bank in (119,120)
              for pc,old,new in ((0xe5ea,0x87,0x38),(0xe5ef,0xbb,0xb4),(0xe5f4,0xcf,0xc2)))


def bindings(raw):
    assert sha256(raw).hexdigest() == PIN
    grant_bytes = GRANT.read_bytes()
    assert sha256(grant_bytes).hexdigest() == GRANT_SHA
    grant = json.loads(grant_bytes)
    assert grant['parent_SHA256'] == PIN and grant['changed_operand_bytes'] == 6
    assert [(q['file_offset'],int(q['before_hex'],16),int(q['after_hex'],16))
            for q in grant['resources']] == list(EDITS)
    for bank in (119,120,125,127):
        at = 16+bank*8192+(BRIDGE&8191)
        assert raw[at:at+49] == (OLD if bank in (119,120) else CANONICAL)
    b = dict(W.Symbols.bundle(), raw=raw)
    for name,pc,bank in (('RyuSourceBodyAfterBGBridge',BRIDGE,127),
                         ('ThPostNativeHot',0xb438,66),
                         ('HuGmStatusName::Copy',0xbb80,79)):
        assert W.address(b,name) == pc and (W.location(b,name)-16)//8192 == bank
    canonical_at = W.location(b,'RyuSourceBodyAfterBGBridge')
    assert b['raw'][canonical_at:canonical_at+49] == CANONICAL
    # Exact retained source recipe names the semantic rebind. Shared src's
    # older bridge body is not silently asserted current.
    recipe = (R/'tools/audit/prepare_thomas_natural_host_1031_v3.py').read_text()
    assert "text.replace('farcall HuAfterTerrainGate,jmp','farcall ThPostNativeHot,jmp')" in recipe
    bank1 = raw[16+8192:16+2*8192]
    calls = [0xa000+i for i in range(8190) if bank1[i:i+3] == b'\x20\xcc\xe5']
    assert len(calls) == 1
    source = (R/'src/player.s').read_text()
    assert source.count('jsr RyuSourceBodyAfterBGBridge') == 1
    caller = calls[0]
    caller_at = 16+8192+(caller&8191)
    def table(name,n):
        at=W.location(b,name)
        assert raw[at:at+n] == b['raw'][at:at+n]
        return raw[at:at+n]
    banks,starts = table('S2AudioSampleBank',8),table('S2AudioSampleStart',8)
    lengths,rates = table('S2AR8349',9),table('S2AR8351',9)
    samples=[]
    for i in range(8):
        begin=0xc000+starts[i]*64;size=lengths[i+1]*16+1
        assert banks[i] in (119,120) and begin>=0xf140 and begin+size<=0x10000
        assert rates[i+1] in (14,15)
        at=16+banks[i]*8192+(begin&8191)
        samples.append(dict(request_bit=i,bank=banks[i],CPU_begin=begin,
                            CPU_end_exclusive=begin+size,file=at,bytes=size,
                            rate=rates[i+1],SHA256=sha256(raw[at:at+size]).hexdigest()))
    return dict(grant_SHA256=GRANT_SHA,canonical_bridge_SHA256=sha256(CANONICAL).hexdigest(),
                native_caller_PC=caller,native_caller_bank=1,
                native_caller_window=raw[caller_at-8:caller_at+11].hex(),
                canonical_target=dict(raw_bank=194,CPU=0xb438),
                samples=samples,extra_RAM_bytes=0,extra_ROM_bytes=0,extra_CHR_bytes=0)


def proposal(raw):
    info=bindings(raw);out=bytearray(raw)
    for at,old,new in EDITS:
        assert raw[at] == old
        out[at] = new
    image=bytes(out)
    assert sha256(image).hexdigest() == CANDIDATE and len(image)==len(raw)
    changed={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert changed == {at for at,_,_ in EDITS}
    for q in info['samples']:
        assert image[q['file']:q['file']+q['bytes']] == raw[q['file']:q['file']+q['bytes']]
    for bank in (119,120,125,127):
        at=16+bank*8192+(BRIDGE&8191)
        assert image[at:at+49] == CANONICAL
    return image,dict(**info,parent_SHA256=PIN,ROM_SHA256=CANDIDATE,
                      changed_operand_bytes=6,all_unowned_bytes_exact=True,
                      sample_payloads_unchanged=True,outputs=0,native_qualified=False)


def inverse(raw):
    assert sha256(raw).hexdigest() == CANDIDATE
    out=bytearray(raw)
    for at,old,new in EDITS:
        assert raw[at] == new
        out[at] = old
    parent=bytes(out)
    assert sha256(parent).hexdigest() == PIN and proposal(parent)[0] == raw
    return parent


reverse = inverse


if __name__ == '__main__':
    image,q=proposal(Owner.NIGHTLY.read_bytes())
    assert inverse(image)==Owner.NIGHTLY.read_bytes()
    print(json.dumps(q,separators=(',',':')),flush=True)
