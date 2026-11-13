"""Private, source-bound native Ladder composition/inverse; no output files."""

from hashlib import sha256
import json

import check_karnov_ladder_native_1113 as L

P=L.Refactor
Audit=L.Audit
Owner=Audit.Bomb
PARENT=Audit.FROZEN_PARENT
TRIAL_COOKIE=bytes.fromhex('a707011323896dcc489c8b64173f25aa')
FONT_BEFORE=bytes.fromhex('00000000000018180000000000000000929292fefe00000048486c000000fe00')
ORIGINS=dict(L.ORIGINS,LADDER_TAIL=0xcdd4)
PIPELINE_PC=0xb1fa


def digest(data):return sha256(data).hexdigest()


def actor_at(pc):return P.Scene.ACTOR+pc-0xa000


def role_at(role,pc):
    page,_,origin=Owner.OWNED[role]
    return Owner.CHR+page*1024+pc-origin


def jump(opcode,pc):return bytes((opcode,))+pc.to_bytes(2,'little')


def native_bundle(raw):return L.B.Cpu.Flower.Host.C.Start.W.bundle(raw)


def pipeline(bundle):
    return jump(0x20,0xbfcb)+b''.join(jump(0x20,L.B.M.address(bundle,name))for name in(
        'KrSourceFrame','KrSourceWeapons','KrOptionsTick'))


def old_icon(symbols):return bytes.fromhex('ae7dc8e003f026bd')+symbols['KrBombHudTiles'].to_bytes(2,'little')


def proposal(raw):
    assert digest(raw)==PARENT,'Private Ladder API remains frozen on exact aa501'
    code,labels,measure=L.measure(raw)
    assert measure['current_partition_fits'] and measure['total_bytes']<=1180
    image,refactor=P.trial(raw)
    assert refactor['cookie']==TRIAL_COOKIE
    result=bytearray(image);changes=[]
    b=native_bundle(raw);_,old_symbols=L.original_bomb_code()
    controls,new_symbols,control_report=L.equipment_controls(raw)
    def change(at,before,after,label):
        assert len(before)==len(after)and bytes(result[at:at+len(before)])==before,label
        result[at:at+len(after)]=after
        changes.append(dict(file_offset=at,bytes=len(after),role=label))
    # Each existing source lease authenticates its original full emitted body.
    originals,_=L.original_bomb_code()
    for name,body in controls.items():
        role='combat'if name.endswith('_TAIL')else'options'
        pc=Owner.ORIGINS[name]
        length=(len(body)if role=='combat'else Owner.LOAN_END[name]-pc)
        before=originals[name].ljust(length,b'\xea')
        assert len(before)==length
        change(role_at(role,pc),before,body.ljust(length,b'\xea'),name)
    # The old helpers retain their ingress; all changed symbolic references
    # are linked from the same source, including the relocated Bomb tick.
    change(role_at('options',0xdc07),jump(0x20,old_symbols['KrBombCycle']),
        jump(0x20,new_symbols['KrBombCycle']),'Select cycle target')
    change(role_at('options',0xd64b),bytes.fromhex('12d6'),
        labels['KrLadderActivate'].to_bytes(2,'little'),'Ladder option2 vector')
    for pc,name,opcode in((0xdce1,'KrBombHudStocks',0xbc),(0xdd26,'KrBombHudStocks',0xbc),
            (0xdd4b,'KrBombHudNames',0xbd)):
        change(role_at('options',pc),jump(opcode,old_symbols[name]),jump(opcode,new_symbols[name]),name)
    for pc in(0xdce7,0xdd2c):
        change(role_at('options',pc),bytes.fromhex('e003'),bytes.fromhex('c000'),'Zero stock-offset HUD test')
    icon=control_report['native_icon_prefix']
    change(icon['file_offset'],bytes.fromhex(icon['before']),bytes.fromhex(icon['after']),'Ladder name/no stock icon')
    for name,body in code.items():
        pc=ORIGINS[name];n=L.PROPOSED_CAPACITIES[name]
        role='actor'if pc<0xc000 else'combat'
        before=b'\xea'*n if role=='actor'else bytes(n)if name=='LADDER_EXTRA'else b'\xff'*n
        change(role_at(role,pc),before,body.ljust(n,b'\xea'),name)
    movement=pipeline(b);at=actor_at(PIPELINE_PC)
    change(at,movement,jump(0x20,labels['KrLadderFrame']).ljust(len(movement),b'\xea'),'Native movement source sequence')
    terrain=L.B.M.address(b,'KrTerrainCallback')
    change(actor_at(terrain),bytes.fromhex('ad00c860'),jump(0x4c,labels['KrLadderTerrain'])+b'\xea','Original terrain callback')
    scene=new_symbols['KrBombSceneClear']+5
    change(role_at('options',scene),jump(0x4c,0xafa4),jump(0x4c,labels['KrLadderSceneClear']),'Same-life object cleanup')
    snap=refactor['code']['symbols']['Kr_F62B']
    change(actor_at(snap),bytes.fromhex('ad63c029f009088d63c0'),
        jump(0x20,labels['KrLadderWorldSnap']).ljust(10,b'\xea'),'World-aligned original climb snap')
    change(244491,b'\x01',b'\x03','Exact row9 copy/verify page count')
    donor=Audit.ROM.read_bytes();assert digest(donor)==Audit.EXPECTED
    patterns=b''.join(donor[16+131072+38*1024+(tile&63)*16:
        16+131072+38*1024+(tile&63)*16+16]for tile in(0xbe,0xbf))
    font=Owner.CHR+1023*1024+0x2c*16
    assert digest(FONT_BEFORE)=='8d431612acbaebd7d4b54aa4e62a6fbf1d13726073a32d07e5466343df8f8be9'
    assert digest(patterns)=='a695f4fc2d1211572a01a2f65aa755c008f09da2d47d466010d4ddbb905e535e'
    change(font,FONT_BEFORE,patterns,'Exact original BE/BF art in private glyphs')
    payload=b''.join(result[Owner.CHR+page*1024:Owner.CHR+(page+count)*1024]
        for page,count,_ in Owner.OWNED.values())+result[244477:244477+27]
    cookie=bytes.fromhex('a7070114')+sha256(b'Karnov native Ladder1113\0'+payload).digest()[:12]
    for at in(P.Scene.RESIDENT,actor_at(0xbfe0)):
        change(at,TRIAL_COOKIE,cookie,'Complete source identity')
    image=bytes(result);assert image.count(cookie)==2
    return image,dict(parent_SHA256=PARENT,candidate_SHA256=digest(image),cookie=cookie,
        code_bytes=measure['total_bytes'],code_sizes=measure['sizes'],symbols=labels,
        controls=new_symbols,changes=changes,feature_qualified=False,native=False,output_files=0)


def _restore_owning_source(image):
    assert len(image)==2097168
    cookie=image[P.Scene.RESIDENT:P.Scene.RESIDENT+16]
    assert cookie[:4]==bytes.fromhex('a7070114')and image.count(cookie)==2
    result=bytearray(image);b=native_bundle(image)
    original,old_symbols=L.original_bomb_code()
    for name,body in original.items():
        role='combat'if name.endswith('_TAIL')else'options';pc=Owner.ORIGINS[name]
        n=len(body)if role=='combat'else Owner.LOAN_END[name]-pc
        result[role_at(role,pc):role_at(role,pc)+n]=body.ljust(n,b'\xea')
    for name in('LADDER_EXTRA','LADDER_TAIL'):
        n=L.PROPOSED_CAPACITIES[name];at=role_at('combat',ORIGINS[name])
        result[at:at+n]=bytes(n)if name=='LADDER_EXTRA'else b'\xff'*n
    compact,_=Audit.relink_core(image,compact=True,verify_baseline=False)
    for name,(lo,hi)in P.ISLANDS.items():
        at=actor_at(lo);result[at:at+hi-lo]=compact['images'][name].ljust(hi-lo,b'\xea')
    for pc,name,opcode in((0xdc07,'KrBombCycle',0x20),(0xdce1,'KrBombHudStocks',0xbc),
            (0xdd26,'KrBombHudStocks',0xbc),(0xdd4b,'KrBombHudNames',0xbd)):
        at=role_at('options',pc);result[at:at+3]=jump(opcode,old_symbols[name])
    result[role_at('options',0xd64b):role_at('options',0xd64b)+2]=bytes.fromhex('12d6')
    for pc in(0xdce7,0xdd2c):result[role_at('options',pc):role_at('options',pc)+2]=bytes.fromhex('e003')
    at=role_at('options',0xdd71);result[at:at+10]=old_icon(old_symbols)
    terrain=L.B.M.address(b,'KrTerrainCallback');result[actor_at(terrain):actor_at(terrain)+4]=bytes.fromhex('ad00c860')
    # Exact authenticated native seam; includes the current platform control
    # bridge BFCB before the three source actor/weapon/timer calls.
    assert L.B.M.address(b,'KrMovement')<PIPELINE_PC<L.B.M.address(b,'KrPostTerrain')
    at=actor_at(PIPELINE_PC)
    result[at:at+12]=pipeline(b)
    result[244491]=1
    at=Owner.CHR+1023*1024+0x2c*16;result[at:at+32]=FONT_BEFORE
    for at in(P.Scene.RESIDENT,actor_at(0xbfe0)):result[at:at+16]=TRIAL_COOKIE
    return P.inverse(bytes(result))


def inverse(image):
    parent=_restore_owning_source(image)
    assert digest(parent)==PARENT
    assert proposal(parent)[0]==image
    return parent


def proposal_current(raw):
    """Separate, explicit known AA/Steve62/Prince209 disjoint composition API."""
    frozen=Audit.frozen(raw);image,info=proposal(frozen)
    result=bytearray(raw)
    # The strict image includes the owning-source relink BEFORE its recorded
    # feature edits. Copy/authenticate complete islands, including every moved
    # branch/table and the recovered tails, before applying the feature spans.
    # Applying only post-refactor changes would overlay unrelinked live code.
    relink=[dict(file_offset=actor_at(lo),bytes=hi-lo,role='Complete qualified '+name)
        for name,(lo,hi)in P.ISLANDS.items()]
    changes=relink+info['changes']
    for change in changes:
        at=change['file_offset'];size=change['bytes']
        assert raw[at:at+size]==frozen[at:at+size],('Known successor overlaps Karnov',change)
        result[at:at+size]=image[at:at+size]
    result=bytes(result)
    if digest(raw)==PARENT:assert result==image
    info=dict(info,frozen_AA_candidate_SHA256=digest(image),parent_SHA256=digest(raw),
        candidate_SHA256=digest(result),known_successor_bytes_preserved=True,changes=changes)
    return result,info


def inverse_current(image):
    parent=_restore_owning_source(image)
    Audit.frozen(parent)
    assert proposal_current(parent)[0]==image
    return parent


if __name__=='__main__':
    raw,_=Audit.inputs();image,info=proposal(raw)
    assert inverse(image)==raw
    print(json.dumps({k:v.hex()if isinstance(v,bytes)else v for k,v in info.items()
        if k not in('symbols','controls','changes')},separators=(',',':')),flush=True)
