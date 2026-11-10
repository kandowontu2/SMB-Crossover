"""Syntax/ABI/API-lifecycle mocks only; no ROM instructions or Mesen runs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

import check_ff_stdout_controller_source_1110 as Base
import check_sonic_native_effects_aligned_1110 as A

R=Base.R
LUA=R/'tools/playthroughs/sonic_original_motion_stdout_1110.lua'


def runtime(variant=0,images=False):
    rt=Base.LuaRuntime(unpack_returned_tuples=True);rt.execute(Base.MOCK)
    h=rt.globals().host;h.env['SMB_STDOUT_ROM_SHA']=Base.W.PIN
    h.env['SMB_TEST_VARIANT']=str(variant);h.env['SMB_STDOUT_IMAGES']='1'if images else'0'
    rt.execute('''
host.work={};host.work_reads=0;host.debug_private_reads=0
function emu.read(at,kind)
 if kind==3 then
  assert(at>=2*8192 and at<4*8192,'Physical source bank2/3 only')
  host.work_reads=host.work_reads+1;return host.work[at]or 0
 end
 if at>=0xc000 and at<0xc200 then host.debug_private_reads=host.debug_private_reads+1 end
 return host.mem[at]or 0
end
function emu.convertAddress(pc)
 if host.wrongMap then return{address=0,memType=2}end
 if pc>=0xa000 and pc<0xc000 then return{address=3*8192+(pc&8191),memType=3}end
 if pc>=0xd000 and pc<0xd400 then return{address=2*8192+(pc&8191),memType=3}end
 return{address=(pc>=0xc000 and 127 or 126)*8192+(pc&8191),memType=2}
end
host.mem[0x6004]=1;host.mem[0x75f]=2;host.mem[0x754]=5;host.mem[0xa4]=1
host.work[0x4000+0x119]=1
host.menu='title';host.previous={};host.edges={};host.constructed=false
function host.gameMain()
 host.stack(0x82be);host.exec(0x82d9)
 if not host.constructed then host.exec(0xbebb);host.constructed=true end
 host.exec(0xbd7a);host.exec(0xbbb0);host.exec(0xbfd2);host.exec(0xd0c3);host.exec(0xd1cf)
 if host.pad and host.pad.right then
  local x=(host.mem[0x75]or 0)+256*(host.mem[0x5c]or 0)+2
  host.mem[0x75]=x&255;host.mem[0x5c]=x>>8
 end
 host.exec(0x82be,250)
end
function host.advance()
 host.event(1);local pad=host.pad or{}
 for _,name in ipairs({'start','select','down','right'})do
  if pad[name]and not host.previous[name]then
   host.edges[#host.edges+1]=name
   if name=='start'and host.menu=='title'then host.menu='roster';host.mem[0x7307]=2
   elseif name=='start'and host.menu=='roster'then
    host.menu='game';host.mem[0x7307]=0;host.mem[0x771]=1;host.mem[0x773]=3
    host.mem[0xf]=8;host.mem[0x75]=40;host.mem[0xbd]=176
   elseif host.menu=='roster'then
    if name=='down'then host.mem[0x7309]=(host.mem[0x7309]or 0)+8
    elseif name=='right'then host.mem[0x7309]=(host.mem[0x7309]or 0)+1
    elseif name=='select'then
     host.mem[0x5ffe]=(host.mem[0x5ffe]or 0)+1
     host.mem[0x6002]=host.mem[0x5ffe]==3 and 43 or 39
    end
    if host.mem[0x7309]==25 and name~='select'then host.mem[0x6002]=26;host.mem[0x5ffe]=0 end
   end
  end
 end
 host.previous=pad;if host.menu=='game'then host.gameMain()end;host.event(2)
end
''')
    cookie=bytes.fromhex('a72b0148fc67939017476de86f7ce64f')
    for bank in(2,3):
        for i,value in enumerate(cookie):h.work[bank*8192+0x1fe0+i]=value
    rt.execute(LUA.read_text());return rt


def startup(rt):
    for _ in range(400):
        rt.execute('host.advance()')
        assert rt.globals().host.status is None,Base.result(rt)
        pad=rt.globals().host.pad
        if rt.globals().host.menu=='game'and pad and pad['right']:break
    else:raise AssertionError('Mock natural Sonic menu timeout')
    assert list(rt.globals().host.edges.values())==[
        'start','down','down','down','right','select','select','select','start','right']


def success(images=False):
    rt=runtime(images=images);startup(rt)
    for _ in range(150):
        rt.execute('host.advance()')
        if rt.globals().host.status is not None:break
    q,lines=Base.result(rt);h=rt.globals().host
    assert q['passed']and h.status==0,q
    assert q['terminal']['x']>=200 and q['calls']['SonicHostConstruct']==1
    assert q['calls']['OriginalSonicFrame']>=20 and h.work_reads>0 and h.debug_private_reads==0
    assert len([s for s in lines if s.startswith('SMB_NATIVE_IMAGE ')])==(2 if images else 0)
    old=len(lines);rt.execute('host.advance();host.gameMain()');assert len(h.prints)==old
    return dict(API_mock_only=True,images=2 if images else 0,physical_source_reads=h.work_reads,
        original_frame_callbacks=q['calls']['OriginalSonicFrame'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    assert sha256(Base.DLL.read_bytes()).hexdigest()==Base.DLL_SHA
    text=LUA.read_text()
    for forbidden in('io.open','emu.write','emu.saveState','emu.loadState','emu.reset','require(','dofile','os.execute'):
        assert forbidden not in text,forbidden
    constants=dict((k,int(v,0))for k,v in re.findall(r'(\w+)\s*=\s*(0x[0-9a-f]+)',text.split('local L={',1)[1].split('\n}',1)[0]))
    b=Base.W.Symbols.bundle()
    for name,value in constants.items():
        if name=='FmAlts':assert value==0x5ffe
        else:assert Base.W.address(b,name)==value,(name,value,Base.W.address(b,name))
    _,_,p=A.proposal()
    assert p['packet']['cookie'].hex()=='a72b0148fc67939017476de86f7ce64f'
    expected={'SonicHostMain':0xbd7a,'SonicHostConstruct':0xbebb,'SonicHostPowerup':0xbf51,
        'MetaDraw':0xd1cf,'MetaFeet':0xbfd2,'MetaBounds':0xd0c3}
    for name,value in expected.items():assert p['metadata']['symbols'][name]==value
    assert p['packet']['frame']['symbols']['SonicNativeOrdinaryFrame']==0xbbb0
    cases=[success(),success(images=True)]
    invalid=runtime(1);q,_=Base.result(invalid);assert not q['passed']and invalid.globals().host.status==1
    bad=runtime();startup(bad);bad.globals().host.mem[0x7ffb]=1
    bad.execute('host.advance()');q,lines=Base.result(bad);assert not q['passed']and'No cheats'in q['reason']
    assert len([s for s in lines if s.startswith('SMB_NATIVE_RECEIPT ')])==1
    wrong=runtime();startup(wrong);wrong.execute('for i=1,10 do host.gameMain()end')
    wrong.globals().host.work[2*8192+0x1fe0]=0
    wrong.globals().host.mem[0x75]=200;wrong.execute('host.advance()')
    q,_=Base.result(wrong);assert not q['passed']and'Authenticated Sonic headers'in q['reason'],q
    physical=runtime();startup(physical);physical.execute('for i=1,4001 do host.event(2)end')
    q,_=Base.result(physical);assert not q['passed']and'Physical frame bound'in q['reason'],q
    logical=runtime();logical.execute('for i=1,2001 do host.main()end')
    q,_=Base.result(logical);assert not q['passed']and'Main bound'in q['reason'],q
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,outputs_written=0,
        Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(),symbols=len(constants),cases=cases,
        negatives=['invalid variant','cheat latched','bad authenticated header','physical bound','logical bound'],
        scope='Lua syntax/constants, natural-menu input edges, physical source reads, mapped callbacks/return lifecycle only. No actual gameplay/physics/PPU/cadence evidence.'),sort_keys=True),flush=True)
    assert not args.output.exists()


if __name__=='__main__':main()
