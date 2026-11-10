"""Publish Sonic's palette through the real native GetPlayerColors entry."""
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_static_portrait_1110 as Portrait
import stage_sonic_portrait_1110 as Stage

M,W=Portrait.Menu,Portrait.W
R=M.R
SOURCE=R/'tools/reference/sonic_native_palette_1110.s'
ENTRY=bytes.fromhex('8d6a01a9da8d6c01a9b08d6d01a9c14c5a01')
BODY=bytes.fromhex(
    'ad5b07c902d002a008ad0260c9039040d011ad056cf00cad5b070a0a186998a84c3fb5'
    'ad026038e90385030a1865030a0a85038d6a01a9cb8d6c01a9a68d6d01a986205a01'
    '0a0a1865036920a84c3fb5')


def proposal(raw):
    assert sha256(raw).hexdigest()==Stage.PIN
    b=W.bundle(raw)
    begin=M.offset(3,0xb4ac)
    body=M.offset(3,0xb4be)
    assert M.location(b,'GetPlayerColors')==begin
    assert M.location(b,'ChkFiery')==body and not b['syms']['ChkFiery'].get('ref')
    assert raw[begin:body]==ENTRY and raw[body:body+len(BODY)]==BODY and len(BODY)==80
    bank=raw[M.offset(3,0xa000):M.offset(3,0xa000)+8192]
    # The live source entry is an unconditional farcall tail. Its following
    # vanilla-only start/index labels have no external entry in this build.
    for i in range(len(bank)-2):
        if bank[i] not in (0x20,0x4c):continue
        destination=int.from_bytes(bank[i+1:i+3],'little')
        assert not 0xb4be<=destination<0xb50e,(hex(0xa000+i),hex(destination))
    for name in ('ChkFiery','StartClrGet','RosterPaletteIndex'):
        pc=M.address(b,name)
        literal=bytes((0xa9,pc&255,0x8d,0x6c,1,0xa9,pc>>8,0x8d,0x6d,1,0xa9,0x83))
        assert literal not in raw[16:1048592],name
    source=(R/'src/screen_render.s').read_text()
    assert 'GetPlayerColors:\n.if ::ENABLE_MMC5_EXPANDED\n  farcall NrColors,jmp' in source
    packet=Portrait.Public.Asm.assemble(SOURCE.read_text(),{'ENTRY':(0xb4ac,18),'BODY':(0xb4be,80)})
    assert packet['used']==dict(ENTRY=14,BODY=53),packet['used']
    image=bytearray(raw)
    for name,start in [('ENTRY',begin),('BODY',body)]:
        data=packet['images'][name]
        image[start:start+len(data)]=data
    return bytes(image),dict(parent_SHA256=Stage.PIN,ROM_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),used=packet['used'],
        native_entry=0xb4ac,source_dead_range=[0xb4be,0xb50e],palette=[22,18,48],
        writes_backdrop=False,requires_private_runtime=False,new_allocations=0)


def main():
    raw=(R/'build/sonic-original-native-1110/candidate.nes').read_bytes()
    image,record=proposal(raw)
    b=W.bundle(image)
    m=M.Menu.I.UI.seed(b,25)
    for _ in range(3):M.Menu.I.UI.key(m,32)
    assert M.Menu.menu_name(m)[0]=='SONIC'
    commands=M.Calls.commands(m)
    assert sum(c['address']==0x3f11 and c['bytes']==[22,18,48] for c in commands)==1,commands
    for offset in (0,1,45,77,78,83,84,255):
        n=M.Menu.I.N.fork(m)
        n[0x4ae]=offset
        before=bytes(n[0x4ae:0x503])
        M.Calls.invoke(n,'GetPlayerColors')
        expected=bytearray(before)
        if offset<78:
            expected[0]=offset+6
            expected[offset+1:offset+8]=bytes((63,17,3,22,18,48,0))
        assert bytes(n[0x4ae:0x503])==expected,offset
    before=W.bundle(raw)
    inventory=M.Menu.inventory(raw)['rows']
    parity=0
    for slot in range(32):
        pair=[M.Menu.I.UI.seed(bundle,slot) for bundle in (before,b)]
        for row in [r for r in inventory if r['slot']==slot]:
            if row['name']!='SONIC':
                assert M.application(pair[0])==M.application(pair[1]),(slot,row)
                parity+=1
            for n in pair:M.Menu.I.UI.key(n,32)
    assert parity==100
    print(json.dumps(dict(passed=True,source_CPU_only=True,ROM_written=False,output_files=0,
        commands=commands,queue_capacity_cases=8,unchanged_foreign_menu_states=parity,record=record),sort_keys=True),flush=True)


if __name__=='__main__':main()
