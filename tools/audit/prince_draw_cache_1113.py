"""Private exact-parent repair of Prince's original pre-animation X cache.

No output or installation. Two already retired Prince instruction spans fund
the donor's four save instructions; the recovered animation entry is retained.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
import re
from unittest.mock import patch

import prince_cold_packet_1111 as Packet

PARENT = '62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639'
CANDIDATE = '209abc2fd6144d59720e54352ed6f9f7384e2fa9ede0fbb1fb37f9e02d385008'
EDITS = (
    # Native material adapter retired C801..C80B comparisons. Its ordinary
    # fallthrough skips the helper and rejoins the unchanged C80D increment.
    (0xa4c1, bytes([234])*12, bytes.fromhex('4ccda4ad0fc68ddbc44c70a9')),
    # Existing unconditional WorldAlign jump at A96D makes this old tail dead;
    # D5FB's public RTS at A979 remains byte exact.
    (0xa970, bytes([234])*9, bytes.fromhex('ad10c68ddcc44c3fac')),
    # Only phase0, after actor-index initialization and before original F158.
    (0xb396, bytes.fromhex('203fac'), bytes.fromhex('20c4a4')),
)


def _replace(raw, inverse=False):
    def mutate(runtime, metadata, state):
        assert runtime[0xa96d-0xa000:0xa97a-0xa000] == (
            bytes.fromhex('4c0bc4') + (EDITS[1][2] if inverse else bytes([234])*9) + b'\x60')
        for address, old, new in EDITS:
            if inverse:
                old, new = new, old
            offset = address-0xa000
            assert runtime[offset:offset+len(old)] == old, hex(address)
            runtime[offset:offset+len(old)] = new
        return runtime, metadata, state
    result, layout = Packet.rebuild(raw, mutate)
    layout.update(parent_SHA256=PARENT, image_SHA256=sha256(result).hexdigest(),
                  edits=[dict(address=hex(pc), old=old.hex(), new=new.hex())
                         for pc, old, new in EDITS],
                  new_RAM_or_CHR_pages=0, decoded_lengths_changed=False)
    # Preserve the real decoder's staging bounds as well as aggregate capacity.
    # The delivered450B loader wraps DC00 to C280, granting6528 bytes.
    assert len(Packet.extract(result)[0]) == Packet.LOADER+450
    assert layout['packed_bytes'][0] <= 6528, layout
    assert 0xe100-layout['packed_bytes'][1] >= 0xc900, layout
    return result, layout


def proposal(raw):
    assert sha256(raw).hexdigest() == PARENT
    image,layout=_replace(raw)
    assert sha256(image).hexdigest()==CANDIDATE
    return image,layout


def reverse(raw):
    result, _ = _replace(raw, inverse=True)
    assert sha256(result).hexdigest() == PARENT
    assert proposal(result)[0] == raw
    return result


def funding(raw):
    """Authenticate the retired source spans, entries and exact save ABI."""
    from verify_native_relocation import NesMPU
    import compose_prince_native_flag_1111 as Flag
    import check_prince_original_position_cache_1113 as Oracle
    _, chunks, _ = Packet.extract(raw)
    runtime = chunks[0]
    assert (0xa4c1, bytes.fromhex('c909f0eac90cf0e6c907f0e3')) in Flag.IMPOSSIBLE_MATERIAL_PATHS
    root = Packet.R/'build/prince-actor-1101-v1'
    source = (root/'contact-core.s').read_text()
    # Original interior entries have definitions/exports only. No recovered
    # source branch, JSR, JMP, data pointer or animation dispatch names them.
    retired = ('PpN_7_D5F0','PpN_7_D5F3','PpN_7_D5F5','PpN_7_D5F8')
    for name in retired:
        assert not re.search(r'^\s*(?:b\w+|j\w+|\.word)\s+'+name+r'\b',source,re.M),name
    # Every literal word in every authenticated decoded stream is considered,
    # so immutable dispatch tables are included in this exclusion as well.
    for data in chunks:
        for i in range(len(data)-1):
            word=int.from_bytes(data[i:i+2],'little')
            assert not 0xa970<=word<0xa979,(i,hex(word))
            assert not 0xa4c2<=word<0xa4cd,(i,hex(word))
    labels={int(pc,16) for pc in re.findall(r'^al ([0-9A-Fa-f]+) ',(root/'contact-core.lbl').read_text(),re.M)}
    branches=0
    for pc in labels:
        if not 0xa000<=pc<0xbfff:
            continue
        op=runtime[pc-0xa000]
        if op&31==16:
            rel=runtime[pc+1-0xa000]
            target=pc+2+rel-(256 if rel&128 else 0)
            assert not 0xa970<=target<0xa979,(hex(pc),hex(target))
            assert not 0xa4c2<=target<0xa4cd,(hex(pc),hex(target))
            branches+=1
    assert runtime[0xc3f:0xc42] == bytes.fromhex('bd13c6')
    image,layout=proposal(raw)
    assert reverse(image)==raw
    _,after,_=Packet.extract(image)
    assert after[1:]==chunks[1:]
    assert {i for i,(a,b) in enumerate(zip(runtime,after[0])) if a!=b} <= {
        pc-0xa000+i for pc,old,_new in EDITS for i in range(len(old))}
    memory=bytearray(65536)
    memory[0xa000:0xa000+len(after[0])]=after[0]
    cpu=NesMPU(memory=memory)
    for value in range(65536):
        lo,hi=value&255,value>>8
        memory[0xc60f:0xc611]=value.to_bytes(2,'little')
        cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=0xa4c4,85,lo,hi,(lo^hi)&255,224
        flags=cpu.p
        for _ in range(6):cpu.step()
        assert cpu.pc==0xac3f and memory[0xc4db:0xc4dd]==value.to_bytes(2,'little')
        assert (cpu.a,cpu.x,cpu.y,cpu.sp)==(hi,lo,hi,224)
        assert cpu.p&~130==flags&~130
        # The normal retired-material fallthrough is an AXYP/SP identity.
        cpu.pc=0xa4c1
        registers=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)
        cpu.step()
        assert cpu.pc==0xa4cd and (cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)==registers
    oracle=Oracle.check()
    assert oracle['passed']
    return dict(passed=True,layout=layout,exact_reverse=True,source_branch_sites=branches,
                cached_coordinate_cases=65536,ordinary_material_ABI_cases=65536,
                donor_oracle_cases=oracle['all_16bit_coordinate_cases'],
                added_phase0_cycles=22,ordinary_material_cycles_saved=21,
                runtime_capacity=6528,runtime_staging_spare=6528-layout['packed_bytes'][0],
                other_decoded_streams_exact=True,output_files=0,Mesen=False)


def qualify_cold(raw):
    """Reuse the actual450B read/reread/decode/constructor and ISR audit."""
    import prince_pickup_reach_1112 as Reach
    import check_prince_pickup_reach_1112 as Check
    head,_,_=Packet.extract(raw)
    _,loader_layout=Reach.relocate_loader(Reach.unrelocate_loader(head[Packet.LOADER:]))
    def transform(image):
        result,layout=proposal(image)
        _,chunks,_=Packet.extract(result)
        layout.update(loader_layout, metadata_input=0xe100-layout['packed_bytes'][1])
        return result,chunks,layout
    with patch.object(Reach,'transform',transform),patch.object(Reach,'reverse',reverse):
        return Check.full_cold(raw,True)


def qualify_interrupts(raw):
    """Declared phase0 call fixtures from actual typed cold, with no item seeds."""
    import check_prince_brick_support_1111 as B
    changed,_=proposal(raw)
    model,_=B.cold(changed)
    B.N.put(model,GameEngineSubroutine=8,OperMode=1,NmiDisable=255,
            DisableScreenFlag=0,Mirror_PPUMASK=30)
    assert model.ram[2][0xa6]==0
    for pc,_old,new in EDITS:
        assert bytes(model.ram[3][pc-0xa000:pc-0xa000+len(new)])==new
    cuts=B.Async.stress('actual phase0 donor cache and animation',model,
        lambda m:B.I.invoke(m,3,0xb36e,(83,71,109,0x61))['regs'],
        [(3,0xb38e,0xb39f),(3,0xa4c1,0xa4cd),(3,0xa970,0xa979)])
    rejected=0
    for bank in (2,3):
        for index in range(16):
            fixture=B.N.fork(model)
            fixture.ram[bank][0x1fe0+index]^=1
            original=tuple(map(bytes,fixture.ram))
            result=B.Q.Sonic.C.invoke(fixture,B.Q.Sonic.O.AUTH)
            assert not result['P']&1 and tuple(map(bytes,fixture.ram))==original
            rejected+=1
    return dict(passed=True,scenarios=cuts,corrupt_header_bytes_rejected=rejected,
                fixture_scope='Actual source constructor followed by declared phase0 call; native engine/lag-NMI envelope only. No source actor, inventory, position, health or outcome seeds.',
                output_files=0,Mesen=False)


def qualify_lifecycle(raw):
    """Current common readback faults and actual neighboring owner reloads."""
    import check_prince_brick_support_1111 as B
    changed,layout=proposal(raw)
    bundle=B.C.Start.W.bundle(changed)
    cold,owner,blank=B.Q.Sonic.C.cold,B.Q.Sonic.O,B.Q.Sonic.O.blank
    canonical,_=B.cold(changed)
    _,chunks,_=Packet.extract(changed)
    def exact(model):
        assert owner.headers(model)==(bytes.fromhex(layout['cookie']),)*2
        assert bytes(model.ram[2][0x800:0x1fe0])==chunks[1]
        for pc,_old,new in EDITS:
            assert bytes(model.ram[3][pc-0xa000:pc-0xa000+len(new)])==new
    warm=B.N.fork(canonical)
    assert cold(warm,38,None)['PPU_reads']==0
    exact(warm)
    faults=[]
    for fault in ('write-protection',(2,0),(3,0),(2,0x100),(2,0x200)):
        model=blank(bundle)
        protection=model.protection[:]
        if fault=='write-protection':
            model.protection=[0,0]
        else:
            model.corrupt_at=fault
        failed=cold(model,38,None,expect_success=False)
        assert all(header[0]==0 for header in owner.headers(model))
        assert not B.Q.Sonic.C.invoke(model,owner.AUTH)['P']&1
        model.protection=protection
        model.corrupt_at=None
        retry=cold(model,38,None)
        exact(model)
        faults.append(dict(fault=fault,rejected=True,retry_PPU_reads=retry['PPU_reads'],
                           failed_PPU_reads=failed['PPU_reads']))
    transitions=[]
    model=B.N.fork(canonical)
    for other in (37,39):
        foreign=cold(model,other,None)
        assert owner.headers(model)!=(bytes.fromhex(layout['cookie']),)*2
        reloaded=cold(model,38,None)
        exact(model)
        transitions.append(dict(route=[38,other,38],foreign_PPU_reads=foreign['PPU_reads'],
                                Prince_PPU_reads=reloaded['PPU_reads']))
    return dict(passed=True,warm_PPU_reads=0,faults=faults,transitions=transitions,
                output_files=0,Mesen=False,
                scope='Complete installed common cold readback failures, unpublished headers, clean retry, and Ex37/Bub39 foreign retirement/reload. These five faults do not claim arbitrary faults on every decoded runtime store.')


@contextmanager
def current_binding(raw):
    """Use the frozen controller against the exactly authenticated private ROM.

    The old-parent recipe is reconstructed, and only its literal Prince cookie
    is rebound. Gameplay RAM, input decisions and all controller assertions stay
    untouched. This never loosens the root's frozen parent API.
    """
    import check_prince_natural_sword_1113 as P
    original_proof, original_recovery = P.proof_parent, P.recovery_controller
    if sha256(raw).hexdigest() == PARENT:
        yield
        return
    parent = reverse(raw)
    old_cookie = parent[Packet.COOKIE:Packet.COOKIE+16]
    new_cookie = raw[Packet.COOKIE:Packet.COOKIE+16]
    text = original_recovery(parent)
    before, after = old_cookie.hex(), new_cookie.hex()
    assert text.count(before) == 1, (old_cookie.hex(), text.count(before))
    rebound = text.replace(before, after)
    def proof(image):
        assert image == raw
        return original_proof(parent)
    def recovery(image):
        assert image == raw
        return rebound
    with patch.object(P, 'proof_parent', proof), patch.object(P, 'recovery_controller', recovery):
        yield


if __name__=='__main__':
    import argparse
    import check_prince_natural_sword_1113 as P
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cold',action='store_true')
    parser.add_argument('--interrupts',action='store_true')
    parser.add_argument('--lifecycle',action='store_true')
    args=parser.parse_args()
    raw=P.Base.C.ROM.read_bytes()
    print(json.dumps(qualify_cold(raw) if args.cold else qualify_interrupts(raw) if args.interrupts
                     else qualify_lifecycle(raw) if args.lifecycle else funding(raw),sort_keys=True),flush=True)
