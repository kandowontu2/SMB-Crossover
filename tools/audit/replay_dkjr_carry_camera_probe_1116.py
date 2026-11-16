"""Passive first-support probe on6d7; unchanged frozen v2/ed3e controls."""
from pathlib import Path
import json
import compose_dkjr_carry_camera_current_1116 as C
import replay_dkjr_fourth_first_loss_bc5_v2_1115 as Frozen

C_SHA='9776402784a0b199b3055a75ab10a6f01cd382094d13d736a46ac7ee453fa5b3'
FROZEN_SHA='f4798c9f8ebc684f8d20dcf18b082093c68b2978e92da1b5ce922883e7e3b5fe'
BASE='e07e07be0e84cb2b439c1786170ba80e95e233e2440443514f67c5961c853158'

def config_lua(q):
    return 'local FL={'+','.join(name+'={'+','.join(map(str,value))+'}' for name,value in sorted(q.items()))+'}\n'

def controller(candidate):
    assert C.H(Path(C.__file__).read_bytes())==C_SHA and C.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    parent=C.inverse(candidate);reference=C.reference(parent)
    base,descriptor=Frozen.controller(reference);assert C.H(base.encode())==BASE
    old_config,_=Frozen.V1.bindings(reference);new_config=dict(old_config)
    body=C.payload(candidate)
    new_config['state_writers']=[0xa000+i for i in range(0x1fde) if body[i:i+3]==bytes.fromhex('8d6bc0')]
    new_config['origin_writers']=[0xa000+i for i in range(0x1fde) if body[i:i+3]==bytes.fromhex('8d76c0')]
    assert len(new_config['origin_writers'])==3
    for row in descriptor:
        at=row.get('carrier_file',row.get('file'))
        before=bytes.fromhex(row['preimage_hex']);assert candidate[at:at+len(before)]==before
    old_cookie=reference[534485:534501].hex();new_cookie=candidate[534485:534501].hex()
    one=Frozen.V1.one
    text=one(base,config_lua(old_config),config_lua(new_config))
    text=one(text,Frozen.PIN,C.CANDIDATE)
    text=one(text,"cookie=='"+old_cookie+"'","cookie=='"+new_cookie+"'")
    restored=one(text,C.CANDIDATE,Frozen.PIN)
    restored=one(restored,"cookie=='"+new_cookie+"'","cookie=='"+old_cookie+"'")
    restored=one(restored,config_lua(new_config),config_lua(old_config))
    assert restored==base
    Frozen.V1.LuaRuntime().compile(text)
    assert not any(s in text for s in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text,dict(candidate_SHA256=C.CANDIDATE,base_probe_Lua_SHA256=BASE,Lua_SHA256=C.H(text.encode()),
        metadata_only_rebind=True,all_hook_preimages_exact=True,state_writers_old=old_config['state_writers'],
        state_writers_new=new_config['state_writers'],origin_writers_exact=new_config['origin_writers'],
        original_v2_and_ed3e_restoration=True,controls_guards_endpoints_unchanged=True,outputs=0)

if __name__=='__main__':
    parent=C.Bowser.ROM.read_bytes();raw,composition=C.proposal(parent)
    text,q=controller(raw)
    q.update(factory_SHA256=C.H(Path(__file__).read_bytes()),composition=composition)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
