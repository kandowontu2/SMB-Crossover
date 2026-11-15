"""Passive actual590 side-probe/branch observer, frozen04f0 controls intact."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import re
import replay_gimmick_flower_position_writes_current_1115 as Previous
import replay_smb1_alts_full11_1114 as Text
from build_prince_worldmaterial_research_1114 import assemble

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
PARENT_SOURCE='312746b4233b847e1733f8af6443ab6a08feafc95fa56ea1694200b9e543e140'
PARENT_LUA='04f0db601dfa741f67ea065aece1c9aa7ee5cd2a4b13424e99be9e30bfd439f2'
WALL_SOURCE=R/'tools/reference/arthur_side_clamp_1101_v8.s'


@lru_cache(maxsize=1)
def authority(raw):
    Previous.bindings(raw);b=dict(W.Symbols.bundle(),raw=raw)
    text=WALL_SOURCE.read_text();names=set(re.findall(r'\b[A-Za-z_]\w*\b',text))
    symbols={name:W.address(b,name)for name in names if name in b['syms']}
    pc=W.address(b,'SamusStopAtWallBanked');at=W.location(b,'SamusStopAtWallBanked')
    assert pc==0xa290 and(at-16)//8192==10
    code,labels,_=assemble(text,symbols,origin=pc,check_entries=False)
    assert len(code)==215 and raw[at:at+215]==code,'Exact current shared215B wall source'
    assert labels['LeftClamp']==0xa2e4 and raw[at+labels['LeftClamp']-pc:at+labels['LeftClamp']-pc+4]==bytes((9,15,133,117))
    return b,labels,dict(wall_source_SHA256=sha256(WALL_SOURCE.read_bytes()).hexdigest(),wall_215B_SHA256=sha256(code).hexdigest(),
        origin=pc,LeftClamp=labels['LeftClamp'],actual_native_STA=labels['LeftClamp']+2,
        R0_R7_addresses=[W.address(b,'R'+str(i))for i in range(8)])


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    q=deepcopy(Previous.bindings(raw,key));b,wall,info=authority(raw)
    for name in tuple('R'+str(i)for i in range(8))+('Local_eb','SmTempX','SmTempPage','PlayerFacingDir','Player_CollisionBits','SideCollisionTimer'):
        q['ram'][name]=W.address(b,name)
    def hook(label,at,pc):
        bank=(at-16)//8192;start=16+bank*8192
        q['hooks'][label]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,bank_SHA256=sha256(raw[start:start+8192]).hexdigest())
    for alias,name in(('GmSideProbeEnter','GmSide'),('NativeSideStop','StopPlayerMove'),('SharedWallEnter','SamusStopAtWallBanked')):
        hook(alias,W.location(b,name),W.address(b,name))
    start=W.location(b,'GmBodyProbe');pc=W.address(b,'GmBodyProbe')
    pattern=bytes((0xa2,0,0xa5,W.address(b,'R3'),0x60,8,5,11,5,5,11,11,18,32,32,22,30,22,30))
    hits=[i for i in range(160-len(pattern))if raw[start+i:start+i+len(pattern)]==pattern]
    assert len(hits)==1,('Actual Gimmick body probe RTS/tables',hits)
    delta=hits[0]+4;hook('GmSideProbeReturn',start+delta,pc+delta)
    start=W.location(b,'SamusStopAtWallBanked');pc=W.address(b,'SamusStopAtWallBanked')
    delta=wall['LeftClamp']-pc;hook('SharedLeftClamp',start+delta,pc+delta)
    return q


OBSERVER=r'''
local gmSideProbe={rows={}}
flower.side_probe_diagnostic=gmSideProbe
local function sideWindow()return gmTrajectory.start and updates<=gmTrajectory.start+6 and#gmSideProbe.rows<32 end
local function sideSnapshot(kind)
 local q=gmTravel.snapshot();local cpu=emu.getState();q.kind=kind
 q.A=cpu['cpu.a'];q.X=cpu['cpu.x'];q.Y=cpu['cpu.y'];q.P=cpu['cpu.ps']or cpu['cpu.p']
 q.native_R={};for i=0,7 do q.native_R[#q.native_R+1]=r('R'..i)end
 q.cpu_zero_to_seven={};for i=0,7 do q.cpu_zero_to_seven[#q.cpu_zero_to_seven+1]=emu.read(i,emu.memType.nesDebug)end
 q.local_eb=r('Local_eb');q.facing=r('PlayerFacingDir');q.native_vx=r('Player_X_Speed');q.native_vy=r('Player_Y_Speed')
 q.temp_X=r('SmTempX');q.temp_page=r('SmTempPage');q.collision_bits=r('Player_CollisionBits');q.side_timer=r('SideCollisionTimer')
 q.hero_x16=r('GmRam00AE')+256*r('GmRam00B8');q.hero_y16=r('GmRam009A')+256*r('GmRam00A4')
 q.pointer=r('R6')+256*r('R7');q.raw_cell=emu.read((q.pointer+r('R2'))&65535,emu.memType.nesDebug)
 return q
end
local pendingSide
hook('GmSideProbeEnter',function()
 if not sideWindow()then pendingSide=nil;return end
 local sp,ret=stackReturn();local q=sideSnapshot('actual-GmSide-entry');q.expected_return_PC=ret;q.entry_SP=sp
 local ya={18,32,32,22,30,22,30};local xa={8,5,11,5,5,11,11};local y=q.Y
 assert(y>=0 and y<=6,'Legal actual Gimmick side-probe index')
 q.requested_world_X=q.x+xa[y+1];q.requested_world_Y=q.y+ya[y+1]
 gmSideProbe.rows[#gmSideProbe.rows+1]=q;pendingSide=q
end)
hook('GmSideProbeReturn',function()
 if not pendingSide then return end
 local q=pendingSide;pendingSide=nil;local sp,ret=stackReturn()
 assert(sp==q.entry_SP and ret==q.expected_return_PC,'Actual Gimmick side query caller PC/SP')
 if sideWindow()then local out=sideSnapshot('actual-GmSide-return');out.requested_world_X=q.requested_world_X;out.requested_world_Y=q.requested_world_Y;gmSideProbe.rows[#gmSideProbe.rows+1]=out end
end)
for _,name in ipairs({'NativeSideStop','SharedWallEnter','SharedLeftClamp'})do
 hook(name,function()if sideWindow()then gmSideProbe.rows[#gmSideProbe.rows+1]=sideSnapshot(name)end end)
end
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    original=Previous.controller(raw,key);assert sha256(original.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Text.lua(Previous.bindings(raw,key))+'\n';assert original.startswith(prefix)
    body=original[len(prefix):];body=Previous.Previous.once(body,"hook('GmMovement',function()",OBSERVER+"hook('GmMovement',function()")
    assert Previous.Previous.once(body,OBSERVER,'')==original[len(prefix):]
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body;Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        actual_shared_wall_source=authority(raw)[2],maximum_probe_branch_rows=32,
        scope='Passive actual590 native side-probe/branch diagnostic: exact04f0 controls/assertions, actual named R0..R7, query coordinates/tile/pointer, shared wall/clamp. No game or gameplay qualification')
    return q
