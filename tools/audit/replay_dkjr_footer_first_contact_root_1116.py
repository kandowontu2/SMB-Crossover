"""Eight passive native witnesses before the first fourth-helper attachment."""
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_pipe5_depart_defense_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Previous.C
PARENT_SHA = '8716f225c58f2848f931d836c03798012fc29382e3fc5297ec2435c27d76ac58'
H = lambda data: sha256(data).hexdigest()

DECL = 'local contactProbe,contactCounts={},{lpc=0,planes=0,positions=0}\n'
OBSERVERS = r'''local cpPending,cpHooks={},{}
local function cpWatching()
 return playing and index==4 and x()>=916 and x()<980
end
local function cpMapped(pc,kind,bank,pre)
 if not mapped(pc,kind,bank*8192+(pc&8191))then return false end
 for i,b in ipairs(pre)do assert(read(pc+i-1)==b,'Current contact hook preimage '..pc)end
 return true
end
local function cpView(kind)
 local q=snapshot();local c=emu.getState();q.kind=kind
 q.PC=c['cpu.pc'];q.SP=c['cpu.sp'];q.A=c['cpu.a'];q.X=c['cpu.x'];q.Y=c['cpu.y'];q.P=c['cpu.ps']
 q.source_y=ram(2,0x210);q.source_x=ram(2,0x213);q.prior=ram(2,0x6c)
 q.origin=ram(2,0x76);q.limit=ram(2,0x7b);q.vy=read(0x8e)
 q.camera_cache=ram(2,0x435)+256*ram(2,0x436);q.camera_delta=ram(2,0x438)
 q.player_bbox={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 q.query_kind=ram(2,0x8db);q.query={ram(2,0x3e),ram(2,0x3f),ram(2,0x40),ram(2,0x41)}
 q.window={ram(2,0x8e8),ram(2,0x8e9),ram(2,0x8ea),ram(2,0x8eb)}
 q.candidate={ram(2,0x8e4),ram(2,0x8e5),ram(2,0x8e6),ram(2,0x8e7)}
 q.contact={ram(2,0x42),ram(2,0x43),ram(2,0x44),ram(2,0x45)}
 q.WCount=ram(2,0x8dd);q.helpers={}
 for _,left in ipairs({880,944})do
  local b=births[tostring(left)]
  if b then local s=b.slot;local at=0x65c+4*s
   q.helpers[tostring(left)]={slot=s,flag=read(0x10+s),id=read(0x17+s),
    x=pos(0x76,0x5d,s),raw_y=read(0xbe+s),top=currentTop(left),passenger=read(0x566+s),
    bbox={read(at),read(at+1),read(at+2),read(at+3)}}
  end
 end
 return q
end
local function cpReturn(key,row)
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 cpPending[key]={pc=pc,sp=(sp+2)&255,row=row}
 if cpHooks[key..':'..pc]then return end
 cpHooks[key..':'..pc]=true
 emu.addMemoryCallback(guarded('contact return '..key,function()
  local p=cpPending[key];local now=emu.getState()
  if not p or now['cpu.pc']~=p.pc or now['cpu.sp']~=p.sp then return end
  cpPending[key]=nil;p.row.returned=cpView('actual-'..key..'-return')
 end),emu.callbackType.exec,pc)
end
emu.addMemoryCallback(guarded('contact LPC944',function()
 if not cpWatching()or not cpMapped(0xb453,'nesPrgRom',0,CP.lpc)then return end
 local b=births['944'];local c=emu.getState()
 if not b or c['cpu.x']~=b.slot then return end
 contactCounts.lpc=contactCounts.lpc+1
 local q=cpView('actual-LPC944-entry');local h=q.helpers['944']
 local gap=h.raw_y-q.player_bbox[4];q.footer_gap=gap
 local rows={}
 if not contactProbe.lpc_first then rows[#rows+1]='lpc_first'end
 if not contactProbe.lpc_nearest or math.abs(gap)<math.abs(contactProbe.lpc_nearest.entry.footer_gap)then
  rows[#rows+1]='lpc_nearest'
 end
 rows[#rows+1]='lpc_last'
 for _,key in ipairs(rows)do local row={entry=q};contactProbe[key]=row;cpReturn(key,row)end
end),emu.callbackType.exec,0xb453)
emu.addMemoryCallback(guarded('contact plane944',function()
 if not cpWatching()or not cpMapped(0xb5c8,'nesWorkRam',3,CP.plane)then return end
 local b=births['944'];if not b or ram(2,0x8f0)~=b.slot or ram(2,0x8db)<3 then return end
 contactCounts.planes=contactCounts.planes+1
 if not contactProbe.plane_first then
  local row={entry=cpView('actual-plane944-entry')};row.entry.plane_Y=emu.getState()['cpu.a']
  contactProbe.plane_first=row;cpReturn('plane_first',row)
 end
end),emu.callbackType.exec,0xb5c8)
emu.addMemoryCallback(guarded('contact position944',function()
 if not cpWatching()or not cpMapped(0xac29,'nesPrgRom',71,CP.position)then return end
 local b=births['944'];if not b or emu.getState()['cpu.x']~=b.slot then return end
 contactCounts.positions=contactCounts.positions+1
 if not contactProbe.position_first then contactProbe.position_first=cpView('actual-position944')end
end),emu.callbackType.exec,0xac29)
for _,address in ipairs(CP.state_writers)do local pc=address
 emu.addMemoryCallback(guarded('contact source4 writer',function()
  if not cpWatching()or contactProbe.source4 or not cpMapped(pc,'nesWorkRam',3,{0x8d,0x6b,0xc0})then return end
  if emu.getState()['cpu.a']==4 and ram(2,0x6b)~=4 then
   contactProbe.source4=cpView('actual-source4-writer')
  end
 end),emu.callbackType.exec,pc)
end
for _,address in ipairs(CP.origin_writers)do local pc=address
 emu.addMemoryCallback(guarded('contact origin writer',function()
  if not cpWatching()or contactProbe.origin or not cpMapped(pc,'nesWorkRam',3,{0x8d,0x76,0xc0})then return end
  contactProbe.origin=cpView('actual-origin-writer')
 end),emu.callbackType.exec,pc)
end
'''


def controller(raw):
    assert H(Path(Previous.__file__).read_bytes()) == PARENT_SHA and H(raw) == C.CANDIDATE
    base = Previous.controller(raw)
    body = C.Camera.payload(raw)
    config = dict(lpc=list(raw[16+0x1453:16+0x1453+4]),
                  position=list(raw[16+71*8192+0xc29:16+71*8192+0xc29+4]),
                  plane=list(body[0x15c8:0x15cc]),
                  state_writers=[0xa000+i for i in range(len(body)-2) if body[i:i+3] == bytes.fromhex('8d6bc0')],
                  origin_writers=[0xa000+i for i in range(len(body)-2) if body[i:i+3] == bytes.fromhex('8d76c0')])
    assert bytes(config['plane'][:2]) == bytes.fromhex('c920') and len(config['origin_writers']) == 3
    lua = 'local CP={' + ','.join(k+'={'+','.join(map(str,v))+'}' for k,v in sorted(config.items())) + '}\n'
    replacements = [('local function finish(ok,why)', lua+DECL+'local function finish(ok,why)'),
                    ('events=events,', 'events=events,contact_probe=contactProbe,contact_counts=contactCounts,'),
                    ("emu.addMemoryCallback(guarded('main',function()", OBSERVERS+"emu.addMemoryCallback(guarded('main',function()")]
    result = base
    for before, after in replacements:
        assert result.count(before) == 1, before
        result = result.replace(before, after, 1)
    restored = result
    for before, after in reversed(replacements):
        assert restored.count(after) == 1
        restored = restored.replace(after, before, 1)
    assert restored == base
    LuaRuntime().compile(result)
    assert not any(x in result for x in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'loadState', 'saveState'))
    return result


if __name__ == '__main__':
    parent = C.BT.ROM.read_bytes()
    raw, _ = C.proposal(parent)
    text = controller(raw)
    print(json.dumps(dict(factory_SHA256=H(Path(__file__).read_bytes()), Lua_SHA256=H(text.encode()),
                          candidate_SHA256=H(raw), unchanged_controls_and_guards=True,
                          max_witness_keys=8, game_writes=False, outputs=0)))
