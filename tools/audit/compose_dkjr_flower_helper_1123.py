"""Separate exactffd708 source-only Flower helper proposal; no writer.

One native vertical actor at1264/192. The unchanged restore loop finishes
X=$FF, so INX replaces LDX#0 with equal flags/cycles and funds one data byte.
"""
import ast,json
from functools import lru_cache
from pathlib import Path
import compose_dkjr_mushroom_slot_order_1123 as Previous

Old,Check,H=Previous.Old,Previous.Check,Previous.H
PIN=Previous.CANDIDATE
CANDIDATE='b9f58a5bdc97fc6a48f4fa7c3a1def3b8de7961a931246cf7989718a937848ef'
PREVIOUS_SHA='45bea71d531c5bf4197b9ab6f5b1156ef86c128fd6014e48fe05c66ca1fe1003'
LAYOUT=dict(ROWS=(0xd2c4,15),PIPE=(0xd18b,117),REFRESH=(0xb624,129))
HELPER_LEFT,HELPER_CENTER=1264,188


@lru_cache(maxsize=1)
def program():
    data=Path(Previous.__file__).read_bytes();assert H(data)==PREVIOUS_SHA
    assert H(Old.Old.GIRDER.read_bytes())==Old.GIRDER_SHA
    tree=ast.parse(data)
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='program')
    loop=next(n for n in function.body if isinstance(n,ast.For))
    source=Old.Old.GIRDER.read_text();one=Check.Replay.one
    for before,after in ast.literal_eval(loop.iter):source=one(source,before,after)
    matched=Old.M.assemble(source,Old.Old.GIRDER_LAYOUT)
    assert matched['images']==Previous.program()['images']
    for before,after in (
        ('ActorCount = 14','ActorCount = 15'),
        ('WorldColumns: .byte 21,26,30,35,39,43,47,55,59,88,','WorldColumns: .byte 21,26,30,35,39,43,47,55,59,79,88,'),
        ('    cpy #9\n    beq Horizontal','    cpy #10\n    beq Horizontal'),
        ('    ldx #0\nPopSMC:','    inx\nPopSMC:'),
        ('OscillatorY: .byte 188,128,128,177,177,169,169,161,161,0,','OscillatorY: .byte 188,128,128,177,177,169,169,161,161,188,0,')):
        source=one(source,before,after)
    p=Old.M.assemble(source,Old.Old.GIRDER_LAYOUT)
    assert p['used']['ROWS']==15 and p['used']['PIPE']==117 and p['used']['REFRESH']==129
    assert p['symbols']['DkAfterNativeConstructor']==0xd1f0 and p['symbols']['DkRefreshPlatformEnd']==0xb6a5
    assert p['images']['ROWS']==matched['images']['ROWS'][:9]+bytes((79,))+matched['images']['ROWS'][9:]
    old_y=matched['symbols']['OscillatorY']-0xb624;new_y=p['symbols']['OscillatorY']-0xb624
    assert new_y==old_y-1
    assert p['images']['REFRESH'][new_y:]==matched['images']['REFRESH'][old_y:old_y+9]+bytes((188,))+matched['images']['REFRESH'][old_y+9:]
    return p


def previous_images():
    p=Previous.program()
    return dict(ROWS=p['images']['ROWS']+b'\xa9',PIPE=p['images']['PIPE'],REFRESH=p['images']['REFRESH'])


def proposal(parent):
    assert isinstance(parent,bytes) and H(parent)==PIN
    Previous.inverse(parent)
    before=previous_images();p=program();out=bytearray(parent);owned=set()
    for name,(pc,size) in LAYOUT.items():
        a,b=before[name],p['images'][name];assert len(a)==len(b)==size
        for (at,old),(other,new) in zip(Old.chunks(pc,a),Old.chunks(pc,b),strict=True):
            assert at==other and parent[at:at+len(old)]==old
            out[at:at+len(new)]=new;owned.update(range(at,at+len(new)))
    cookie=b'\xa7\x28\x01'+bytes.fromhex(H(Old.Head.payload(out)))[:13]
    out[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16]=cookie
    owned.update(range(Old.Head.COOKIE_AT,Old.Head.COOKIE_AT+16))
    result=bytes(out);changed={i for i,(a,b) in enumerate(zip(parent,result,strict=True)) if a!=b}
    assert changed<=owned
    if CANDIDATE is not None:assert H(result)==CANDIDATE
    return result,dict(parent_SHA256=PIN,candidate_SHA256=H(result),changed_bytes=len(changed),
        helper=dict(character='Donkey Kong Jr.',stage='1-1',left=1264,center=1280,initial_top=192,
            collision_width=32,native_ID=37,oscillator_center=188),
        existing14_placements_preserved=True,horizontal_ordinal=10,constructor_return=0xd1f0,
        original_jump_head_carry_unchanged=True,SMC_save_cells_and_values_preserved=True,
        restore_ldx0_replaced_by_inx=True,used=p['used'],outputs=0,native_qualified=False)


def inverse(raw):
    assert CANDIDATE is not None and H(raw)==CANDIDATE
    out=bytearray(raw)
    for name,(pc,_) in LAYOUT.items():
        for at,data in Old.chunks(pc,previous_images()[name]):out[at:at+len(data)]=data
    out[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16]=bytes.fromhex('a72801a3ddeefa05ffa269a75de71170')
    parent=bytes(out)
    assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def full_controller(raw):
    parent=inverse(raw);text=Previous.full_controller(parent);original=text;changes=[]
    before_cookie=parent[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
    after_cookie=raw[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
    for before,after in (
        (f'local rom="{PIN}"',f'local rom="{H(raw)}"'),
        (f"assert(rom=='{PIN}'",f"assert(rom=='{H(raw)}'"),
        (f"cookie=='{before_cookie}'",f"cookie=='{after_cookie}'"),
        ('local centers={','local centers={[1264]=188,')):
        text=Check.Replay.one(text,before,after);changes.append((before,after))
    marker='ram(2,0x8fd)~=9';assert text.count(marker)==2
    text=text.replace(marker,'ram(2,0x8fd)~=10')
    restored=text.replace('ram(2,0x8fd)~=10',marker)
    for before,after in reversed(changes):restored=Check.Replay.one(restored,after,before)
    assert restored==original
    Check.LuaRuntime().compile(text)
    return text


def restore_units(parent):
    old,new=Previous.program(),program();results=[]
    body=Old.Head.payload(parent)
    for seed in range(64):
        snapshots=[]
        for p in (old,new):
            c=Previous.fixture(p)
            c.memory[0xb7ac:0xb7bb]=body[0x17ac:0x17bb]
            c.memory[0xd2f7:0xd2fc]=bytes((0x62,0x6a,0x6c,0x6d,0x79))
            for i in range(3,14):c.memory[i]=(seed*29+i*17)&255
            for i in (0x162,0x16a,0x16c,0x16d,0x179):c.memory[i]=(seed*19+i)&255
            c.memory[0xd6]=0;c.memory[0x71d]=seed%11
            c.pc,c.sp,c.a,c.x,c.y,c.p=p['symbols']['DkRefreshPlatform'],0xfd,seed,seed^0x5a,seed^0xa5,0x31
            c.memory[0x1fe],c.memory[0x1ff]=0xff,0x7f
            marker=p['symbols']['PopSMC']-(1 if p is new else 2);saw=False
            start=c.processorCycles
            for _ in range(1500):
                if c.pc==0x8000:break
                if c.pc==marker:assert c.x==255;saw=True
                c.step()
            else:raise AssertionError(('Restore fixture bound',hex(c.pc)))
            assert saw
            snapshots.append((c.a,c.x,c.y,c.p,c.sp,bytes(c.memory[:256]),bytes(c.memory[0x100:0x180]),c.processorCycles-start))
        assert snapshots[0]==snapshots[1],seed
        results.append(seed)
    return dict(passed=True,cases=len(results),complete_refresh_return_identical=True,
        native_ZP_and_SMC_and_AXYP_SP_and_cycles_identical=True,observed_restore_entry_X=255,outputs=0)


if __name__=='__main__':
    parent=Old.M.ROM.read_bytes();raw,q=proposal(parent)
    print('DK FLOWER HELPER '+json.dumps(q,separators=(',',':')),flush=True)
    print('DK FLOWER RESTORE '+json.dumps(restore_units(parent),separators=(',',':')),flush=True)
