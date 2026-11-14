"""Frozen527 controls with a separate bounded riser5/source/native observer."""
from hashlib import sha256
import json

import replay_dkjr_final_stair_takeoff_1113 as Proposal
from check_ff_stdout_controller_source_1110 import LuaRuntime

T,P=Proposal.T,Proposal.T.P
LUA_PIN='319a921e1ef75947b677ea212ff6ab5b5705754bc85a1eb98777999851ef2b82'


def controller(raw,*,with_metadata=False):
    text=Proposal.active_trace_controller(raw)
    assert sha256(text.encode()).hexdigest()==Proposal.ACTIVE_TRACE_LUA_PIN
    text=P.once(text,"x()<2938 or x()>2948",'x()<2968 or x()>2984')
    text=P.once(text,"q.event=name;q.PC=at;",'q.riser=finalRiser;q.event=name;q.PC=at;')
    text=P.once(text,'local function finalStairObserve(name,at)',
        'local function finalStairObserve(name,at,writeAt,writeValue)')
    text=P.once(text,"q.riser=finalRiser;q.event=name;q.PC=at;",'''q.riser=finalRiser;q.riser_attempt=math.min(finalRiserAttempts or 0,4);q.event=name;q.PC=at;
 q.write_address=writeAt;q.write_value=writeValue
 local mappedCode=emu.convertAddress(at);q.code_map=mappedCode and {mappedCode.memType,mappedCode.address}or nil
 q.code_bytes={read(at),read((at+1)&65535),read((at+2)&65535)}
 q.return_stack={};for i=1,8 do q.return_stack[i]=read(256+((cpu['cpu.sp']+i)&255))end
 ''')
    # Resolve current linked native locations through the already retained
    # symbol provider; no rebuilt source tree or generated image is needed.
    import check_dkjr_direct_platform_1113 as Gate
    W=Gate.W
    b=W.Symbols.bundle();b['raw']=raw
    fields={name:W.address(b,name)for name in('Player_BoundBoxCtrl','SideCollisionTimer',
        'Player_X_Speed','Player_Y_Speed','Player_CollisionBits','Local_eb',
        'Left_Right_Buttons','Player_MovingDir','PlayerFacingDir','R0','R2','R4','R6','R7')}
    extra='q.native_box={read(0x658),read(0x659),read(0x65a),read(0x65b)}\n q.native_side={'
    extra+=','.join("['"+name+"']=read("+str(at)+')'for name,at in fields.items())+'}\n'
    extra+=f" local ptr=read({fields['R6']})+256*read({fields['R7']});local cell=ptr+read({fields['R2']});q.native_queried_cell=ptr<2048 and cell<2048 and read(cell)or-1"
    text=P.once(text,'q.native_box={read(0x658),read(0x659),read(0x65a),read(0x65b)}',extra)
    pc,at=W.address(b,'ImpedePlayerMove'),W.location(b,'ImpedePlayerMove')
    original=raw[at:at+64]
    assert original[:2]==bytes.fromhex('a900')
    xfield=W.address(b,'Player_X_Position')
    pattern=bytes((0x85,xfield))if xfield<256 else bytes((0x8d,xfield&255,xfield>>8))
    writes=[i for i in range(61)if original[i:i+len(pattern)]==pattern]
    assert len(writes)==1,('Exact native X-store scope',writes,original.hex())
    info=[];maps=[]
    for name,offset in(('native-side-ingress',0),('native-side-X-store',writes[0]),
                       ('native-side-X-after',writes[0]+len(pattern))):
        point=pc+offset;physical=at-16+offset
        value=raw[at+offset:at+offset+len(pattern)if offset else at+2]
        assert value
        text+=f'''\nemu.addMemoryCallback(guarded('{name}',function()
 if mapped({point},'nesPrgRom',{physical})then finalStairObserve('{name}',{point})end
end),emu.callbackType.exec,{point})\n'''
        info.append(dict(name=name,CPU=point,file_offset=at+offset,preimage_hex=value.hex()))
        maps.append(f"(at=={point} and mapped(at,'nesPrgRom',{physical}))")
    write_fields={name:W.address(b,name)for name in('Player_X_Position','Player_Y_Position')}
    text=P.once(text,"not mapped(at,'nesWorkRam',3*8192+at-0xa000)",
        "not (mapped(at,'nesWorkRam',3*8192+at-0xa000)or"+'or'.join(maps)+
        ' or writeAt=='+str(write_fields['Player_X_Position'])+' or writeAt=='+str(write_fields['Player_Y_Position'])+')')
    for name,address in write_fields.items():
        text+=f'''\nemu.addMemoryCallback(guarded('actual {name} writer',function(_,value)
 local cpu=emu.getState();finalStairObserve('actual-{name}-write',cpu['cpu.pc'],{address},value)
end),emu.callbackType.write,{address})\n'''
    labels=P.frozen_labels()
    source_pc=labels['DkjrSupportProbe']
    body=P.T.payload(raw);source_head=body[source_pc-0xa000:source_pc-0xa000+2]
    assert source_head==bytes.fromhex('a903')
    text+=f'''\nemu.addMemoryCallback(guarded('source support probe',function()
 finalStairObserve('source-support-entry',{source_pc})
end),emu.callbackType.exec,{source_pc})\n'''
    text=P.once(text,'q.kind2_list={};',
        'q.kind3_list={};for off=0,math.min(ram(2,0x8dd),16)-1 do q.kind3_list[#q.kind3_list+1]=ram(2,0x840+off)end\n q.kind2_list={};')
    text=P.once(text,'if #finalStairTrace>=64 then table.remove(finalStairTrace,17);finalStairDropped=finalStairDropped+1 end',
        '''local same={};for i,row in ipairs(finalStairTrace)do if row.riser_attempt==q.riser_attempt then same[#same+1]=i end end
 if #same>=12 then table.remove(finalStairTrace,same[5]);finalStairDropped=finalStairDropped+1 end''')
    LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==LUA_PIN
    return(text,info)if with_metadata else text


if __name__=='__main__':
    _,raw=T.load_inputs();text,points=controller(raw,with_metadata=True)
    print('DKJR_STAIR_PROJECTION_TRACE '+json.dumps(dict(candidate_SHA256=T.PIN,
        frozen_controls_Lua_SHA256=Proposal.ACTIVE_LUA_PIN,
        Lua_SHA256=sha256(text.encode()).hexdigest(),native_points=points,
        world_X_window=[2968,2984],max_rows=60,per_attempt_first_last=[4,8],Lua_compiled=True,
        controls_unchanged=True,source_native_or_ROM_writes=False,outputs_written=0),separators=(',',':')),flush=True)
