"""Use the original Sonic standing art in the existing native portrait renderer."""
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_gimmick_frontend_1110 as Menu
import check_sonic_public_admission_1110 as Public

R, W = Menu.R, Menu.Menu.W
SOURCE = R/'tools/reference/sonic_static_portrait_1110.s'
PARENT = 'e7a30825f992d9a28c813ee7eb2571e6836b8f75c6579234f7f7a66106a6d896'


def proposal(raw):
    assert sha256(raw).hexdigest() == PARENT
    b = W.bundle(raw)
    # The sole current farcall to the root of RlPortraitDispatch is the
    # intermediate-player caller. It explicitly loads the selected owner in A.
    caller = bytes.fromhex('ad0260c90690138d6a01a9d48d6c01a9b88d6d01a9ce205a0160')
    start = Menu.offset(3,0xb37f)
    assert raw[start:start+len(caller)] == caller
    selector = bytes.fromhex('a9d48d6c01a9b88d6d01a9ce')
    assert raw[16:1048592].count(selector) == 1
    call = bytes.fromhex('8d6a01a9288d6c01a9a58d6d01a9dd4c5a01')
    slot = Menu.offset(78,0xb8dd)
    assert raw[slot:slot+len(call)] == call
    assert raw[slot-9:slot] == bytes.fromhex('08482008b8b0146828')
    end = 0xbcaa
    begin = 0xbc77
    base = Menu.offset(9,0xbc54)
    target = Menu.offset(9,begin)
    # The authored demo was retired by the Sonic cold project. The admitted
    # reject helper consumes the first35 bytes; its remaining51 are unused.
    assert raw[base:target] == bytes.fromhex('babd0f0129fe9d0f01ad0260c92bd012a9009d0d019d0e01bd0801c9f5d003fe0c0160')
    assert raw[target:target+end-begin] == b'\xea'*(end-begin)
    assert Public.LAYOUT['NATIVE_REJECT'] == (9,0xbc54,86)
    assert Menu.address(b,'METASPRITE_BIG_MARIO_STANDING') == 1
    packet = Public.Asm.assemble(SOURCE.read_text(),{'PORTRAIT':(begin,end-begin)})
    body = packet['images']['PORTRAIT']
    assert len(body) <= end-begin
    image = bytearray(raw)
    new_call = bytes.fromhex('8d6a01a9778d6c01a9bc8d6d01a9894c5a01')
    assert len(new_call) == len(call)
    image[slot:slot+len(call)] = new_call
    image[target:target+len(body)] = body
    assert image[base:target] == raw[base:target]
    return bytes(image),dict(parent_SHA256=PARENT,ROM_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),leaf_bytes=len(body),
        same_bank_hook=dict(bank=78,PC=0xb8dd,old=call.hex(),new=new_call.hex()),
        previous_retired_demo_tail=dict(bank=9,first=begin,last_exclusive=end),
        changes_only_static_menu_and_lives_portraits=True,original_Sonic_motor_unchanged=True)


def main():
    raw=(R/'build/sonic-original-native-1110/candidate.nes').read_bytes()
    image,record=proposal(raw)
    b=W.bundle(image)
    m=Menu.Menu.I.UI.seed(b,25)
    for _ in range(3):Menu.Menu.I.UI.key(m,32)
    assert Menu.Menu.menu_name(m)[0]=='SONIC'
    cells=[list(m[0x200+4*i:0x204+4*i]) for i in range(64) if m[0x200+4*i]<240]
    bank=[m[Menu.address(b,n)] for n in ('X5ChrMode','CurrentCHRBank','X5WideChrActive','ReloadCHRBank')]
    assert len(cells)==4 and sorted(c[1] for c in cells)==[0,2,32,34],cells
    assert bank[:3]==[133,16,1] and bank[3],bank
    before=W.bundle(raw)
    inventory=Menu.Menu.inventory(raw)
    parity=0
    for slot in range(32):
        pair=[Menu.Menu.I.UI.seed(bundle,slot) for bundle in (before,b)]
        rows=[row for row in inventory['rows'] if row['slot']==slot]
        for row in rows:
            assert Menu.Menu.menu_name(pair[0])[0]==Menu.Menu.menu_name(pair[1])[0]==row['name']
            if row['name']!='SONIC':
                assert Menu.application(pair[0])==Menu.application(pair[1]),(slot,row,'unchanged portrait')
                for key in (16,128):
                    copies=[Menu.Menu.I.N.fork(m) for m in pair]
                    result=[Menu.Menu.I.UI.key(m,key) for m in copies]
                    assert Menu.application(copies[0])==Menu.application(copies[1]),(slot,row,key)
                    assert all(result[0][n]==result[1][n] for n in ('A','X','Y','P'))
                parity+=1
            for m in pair:Menu.Menu.I.UI.key(m,32)
        wrapped=[list(Menu.application(m)) for m in pair]
        if slot==25:
            # MoveAllSpritesOffscreen intentionally clears only the Y byte of
            # unused OAM slots. The previous Sonic tile/X values are invisible.
            for state in wrapped:
                sprites=bytearray(state[1])
                for i in range(0,256,4):
                    if sprites[i]>=240:sprites[i+1:i+4]=bytes(3)
                state[1]=bytes(sprites)
        assert wrapped[0]==wrapped[1],(slot,'unchanged wrap')
    assert parity==100
    print(json.dumps(dict(passed=True,source_CPU_only=True,ROM_written=False,output_files=0,
        record=record,actual_menu_OAM=cells,mode_page_wide_reload=bank,
        exact_other_selector_states=parity,exact_other_Start_A=parity*2),sort_keys=True),flush=True)


if __name__=='__main__':main()
