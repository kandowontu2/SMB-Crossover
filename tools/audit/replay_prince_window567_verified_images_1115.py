"""Separate strict cold observer over frozen5c2e controls; no input changes."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import replay_prince_window567_images_1115 as Previous

R,ROM,W,N,Frozen,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frozen,Previous.PIN,Previous.IDENTITIES
C=Previous.Compose
PREVIOUS_SHA='1700c122e4d75b4a637b15ca6663d9885c881f3a01c92bedd6803a6486c30602'
PREVIOUS_LUA='5c2ebf00970aedc17e48cc79718b7a9bae019d2a29b21cc00d8f01fddaba6ff0'


@lru_cache(maxsize=1)
def bindings(raw,key='prince'):
    assert sha256(open(Previous.__file__,'rb').read()).hexdigest()==PREVIOUS_SHA
    c=deepcopy(Previous.bindings(raw,key));parts=C.Packet.extract(raw)[1]
    # These AUDIO bytes have their own real154B cold copy. They are not a
    # negative offset into metadata, nor the state's ordinary80B down-copy.
    assert c['private_pickup']['pc']==0xc7b3
    source=0xc65f+(0xc7b3-0xc766);offset=source-0xc100
    code=parts[2][offset:offset+12];assert code[:3]==bytes.fromhex('adcfc6')and len(code)==12
    c['private_pickup']['bytes']=list(code)
    c['private_pickup']['cold_source']=dict(stream=2,staged_PC=source,stream_offset=offset,
        actual_copy_source=0xc65f,actual_copy_destination=0xc766,actual_copy_bytes=154)
    c['first_publish_checks']=[]
    for row in C.allocation()['decoded_envelopes']:
        stream=row['stream'];pc=(0xa000 if stream==0 else 0xc800)+row['offset']
        data=parts[stream][row['offset']:row['offset']+row['bytes']]
        c['first_publish_checks'].append(dict(bank=3 if stream==0 else 2,pc=pc,bytes=list(data),SHA256=sha256(data).hexdigest()))
    return c


@lru_cache(maxsize=1)
def controller(raw,key='prince'):
    config=bindings(raw,key);oldconfig=Previous.bindings(raw,key);old=Previous.controller(raw,key)
    assert sha256(old.encode()).hexdigest()==PREVIOUS_LUA
    prefix='local C='+Previous.Previous.Frozen.lua(oldconfig)+'\n';assert old.startswith(prefix)
    text='local C='+Previous.Previous.Frozen.lua(config)+'\n'+old[len(prefix):]
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a;text=text.replace(a,b,1)
    change('local pickup\n','local pickup,firstPublish\n')
    change('accepted_pickup=pickup,events=events','accepted_pickup=pickup,first_publish_readback=firstPublish,events=events')
    change('emu.addMemoryCallback(guard(function()\n local h=C.private_pickup;',r'''emu.addMemoryCallback(guard(function()
 if firstPublish then return end
 local map=emu.convertAddress(0xbbc1)
 if not map or map.memType~=emu.memType.nesWorkRam or map.address~=3*8192+(0xbbc1&8191)then return end
 for bank=2,3 do for i,v in ipairs(C.prince_cookie)do assert(source(0x1fe0+i-1,bank)==v,'FirstBBC1 complete16B cookie')end end
 local checked={}
 for _,h in ipairs(C.first_publish_checks)do
  for i,v in ipairs(h.bytes)do assert(source((h.pc&8191)+i-1,h.bank)==v,'FirstBBC1 exact static graphics extent')end
  checked[#checked+1]={bank=h.bank,pc=h.pc,bytes=#h.bytes,expected_SHA256=h.SHA256}
 end
 firstPublish={PC=0xbbc1,SP=emu.getState()['cpu.sp'],frame=frame,completed=completed,
  both16byte_cookies=true,static_graphics_extents=checked,before_first_publication=true}
end),emu.callbackType.exec,0xbbc1)
emu.addMemoryCallback(guard(function()
 local h=C.private_pickup;''')
    Frozen.LuaRuntime().compile(text)
    return text


def metadata(raw,key='prince'):
    c=bindings(raw,key);q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        frozen_controls_parent_Lua_SHA256=PREVIOUS_LUA,ordinary_inputs_unchanged=True,
        first_BBC1_fullcookie_and3174plus3plus2_readback=True,
        actual_relocated_pickup_source=c['private_pickup']['cold_source'])
    return q
