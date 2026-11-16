"""Passive first-loss hardware calibration; unchanged ed3e controls and guards."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import replay_dkjr_public_fourth_carried_bc5_1115 as F
from check_ff_stdout_controller_source_1110 import LuaRuntime

PIN = F.Prior.PIN
BASE = 'ed3e7206e7e2cd29f403048d4816de5c01f58768b53113eba5021f24ade6d4b1'
H = lambda data: sha256(data).hexdigest()


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


DECL = '''local flCounts={positions944=0,post_carry_entries=0,support_queries=0,wall_queries=0,plane_candidates=0}
local flFirst,flPending,flReturnHooks={},{},{}
local flSlot
'''

FUNCTIONS = '''local function flWatching()
 return playing and index==4 and x()>=916 and x()<980
end
local function flMapped(pc,kind,bank,pre)
 if not mapped(pc,kind,bank*8192+(pc&8191))then return false end
 for i,b in ipairs(pre)do assert(read(pc+i-1)==b,'First-loss hook preimage '..pc)end
 return true
end
local function flRects(offset)
 local rows={};for i=0,12,4 do
  if ram(2,offset+i)==255 then break end
  rows[#rows+1]={ram(2,offset+i),ram(2,offset+i+1),ram(2,offset+i+2),ram(2,offset+i+3)}
 end;return rows
end
local function flView(kind)
 local q=snapshot();local c=emu.getState();q.kind=kind;q.PC=c['cpu.pc'];q.SP=c['cpu.sp'];q.P=c['cpu.ps']
 q.A=c['cpu.a'];q.X=c['cpu.x'];q.Y=c['cpu.y'];q.bits=bits;q.saved=read(0xdc)
 q.source_held=ram(2,0x14);q.source_sample=ram(2,0x15);q.direction=ram(2,0x54);q.facing=ram(2,0x6d)
 q.native_direction=read(0x45);q.native_x_speed=read(0x46);q.fraction_x=ram(2,0x56)
 q.source_x=ram(2,0x213);q.source_y=ram(2,0x210);q.prior=ram(2,0x6c)
 q.origin=ram(2,0x76);q.limit=ram(2,0x7b);q.native_vy=read(0x8e)
 q.player_bbox={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 q.query_kind=ram(2,0x8db);q.query={ram(2,0x3e),ram(2,0x3f),ram(2,0x40),ram(2,0x41)}
 q.window={ram(2,0x8e8),ram(2,0x8e9),ram(2,0x8ea),ram(2,0x8eb)}
 q.candidate={ram(2,0x8e4),ram(2,0x8e5),ram(2,0x8e6),ram(2,0x8e7)}
 q.contact={ram(2,0x42),ram(2,0x43),ram(2,0x44),ram(2,0x45)}
 q.support=flRects(0x800);q.walls=flRects(0x880);q.WCount=ram(2,0x8dd)
 if flSlot then local s=flSlot;local at=0x65c+4*s
  q.helper={slot=s,flag=read(0x10+s),id=read(0x17+s),left=pos(0x76,0x5d,s),raw_top=read(0xbe+s),
   vy=read(0x8f+s),passenger=read(0x566+s),bbox={read(at),read(at+1),read(at+2),read(at+3)}}
 end
 return q
end
local function flFollow(kind,pc,pre,condition)
 emu.addMemoryCallback(guarded('first-loss '..kind..' entry',function()
  if not flFirst.first_carry or not flWatching()or not flMapped(pc,'nesWorkRam',3,pre)or not condition()then return end
  if kind=='plane'then flCounts.plane_candidates=flCounts.plane_candidates+1
  elseif kind=='support'then flCounts.support_queries=flCounts.support_queries+1
  elseif kind=='wall'then flCounts.wall_queries=flCounts.wall_queries+1 end
  if flFirst[kind]then return end
  local row={entry=flView('first-'..kind..'-entry')};flFirst[kind]=row
  if kind=='plane'then
   row.entry.plane_Y=emu.getState()['cpu.a']
   row.entry.horizontal_overlap=row.entry.candidate[3]>=row.entry.window[1]and row.entry.window[2]>=row.entry.candidate[1]
   row.entry.vertical_overlap=row.entry.plane_Y>=row.entry.window[3]and row.entry.plane_Y<=row.entry.window[4]
  end
  local c=emu.getState();local sp=c['cpu.sp']
  local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
  flPending[kind]={pc=ret,sp=(sp+2)&255}
  local key=kind..':'..ret
  if not flReturnHooks[key]then
   flReturnHooks[key]=true
   emu.addMemoryCallback(guarded('first-loss '..kind..' return',function()
    local p=flPending[kind];local c=emu.getState()
    if not p or c['cpu.pc']~=p.pc or c['cpu.sp']~=p.sp then return end
    flPending[kind]=nil
    row.returned={pc=c['cpu.pc'],sp=c['cpu.sp'],A=c['cpu.a'],P=c['cpu.ps'],WCount=ram(2,0x8dd),
     source=ram(2,0x6b),source_y=ram(2,0x210),query={ram(2,0x3e),ram(2,0x3f),ram(2,0x40),ram(2,0x41)},
     contact={ram(2,0x42),ram(2,0x43),ram(2,0x44),ram(2,0x45)},support=flRects(0x800),walls=flRects(0x880)}
    if kind=='plane'then row.returned.appended=row.returned.WCount>row.entry.WCount end
   end),emu.callbackType.exec,ret)
  end
 end),emu.callbackType.exec,pc)
end
'''

OBSERVERS = '''emu.addMemoryCallback(guarded('first-loss actual944position',function()
 if not flWatching()or not active()or not flMapped(0xac29,'nesPrgRom',71,FL.position)then return end
 local b=births['944'];local c=emu.getState()
 if not b or c['cpu.x']~=b.slot then return end
 flCounts.positions944=flCounts.positions944+1
 if flFirst.first_carry then return end
 local top=currentTop(944);local y=read(0xbd)
 if not top or y+32~=top or ram(2,0x210)~=y+15 or ram(2,0x6b)~=1 then return end
 flSlot=b.slot;flFirst.first_carry=flView('first-qualified-actual944position')
end),emu.callbackType.exec,0xac29)
emu.addMemoryCallback(guarded('first-loss nextD65Eentry',function()
 if not flFirst.first_carry or not flWatching()or not flMapped(0xd65e,'nesWorkRam',2,FL.motor)then return end
 flCounts.post_carry_entries=flCounts.post_carry_entries+1
 if not flFirst.motor_entry then flFirst.motor_entry=flView('first-D65E-entry-after-qualified-carry')end
end),emu.callbackType.exec,0xd65e)
flFollow('support',0xb065,FL.support,function()return true end)
flFollow('wall',0xb061,FL.wall,function()return true end)
flFollow('plane',0xb5c8,FL.plane,function()return ram(2,0x8f0)==flSlot and ram(2,0x8db)>=3 end)
for _,pc in ipairs(FL.state_writers)do local address=pc
 emu.addMemoryCallback(guarded('first-loss source4writer',function()
  if not flFirst.first_carry or flFirst.source4_writer or not flWatching()or
   not flMapped(address,'nesWorkRam',3,{0x8d,0x6b,0xc0})then return end
  local c=emu.getState();if c['cpu.a']==4 and ram(2,0x6b)~=4 then
   flFirst.source4_writer=flView('first-pending-source4-store');flFirst.source4_writer.writer_pc=address
  end
 end),emu.callbackType.exec,address)
end
for _,pc in ipairs(FL.origin_writers)do local address=pc
 emu.addMemoryCallback(guarded('first-loss originwriter',function()
  if not flFirst.source4_writer or flFirst.origin_writer or not flWatching()or
   not flMapped(address,'nesWorkRam',3,{0x8d,0x76,0xc0})then return end
  flFirst.origin_writer=flView('first-pending-origin-store');flFirst.origin_writer.writer_pc=address
 end),emu.callbackType.exec,address)
end
emu.addMemoryCallback(guarded('first-loss nativeXwrite',function(address,value)
 if not flFirst.first_carry or flFirst.native_x_decrease or not flWatching()then return end
 local old=read(0x75);value=value&255
 if value>=old or old-value>=8 then return end
 local q=flView('first-nativeX-decrease-write');q.write_address=address;q.old_low=old;q.new_low=value
 local c=emu.getState();local pc=c['cpu.pc'];q.observed_pc=pc;q.near_start=pc-6;q.near_bytes={}
 for at=pc-6,pc+4 do q.near_bytes[#q.near_bytes+1]=read(at)end
 local m=emu.convertAddress(pc-6)
 if m then
  q.near_mapping={memType=m.memType,address=m.address}
  if m.memType==emu.memType.nesPrgRom then
   q.near_ROM_bytes={};q.near_ROM_matches=true
   for i=0,10 do local b=emu.read(m.address+i,emu.memType.nesPrgRom)
    q.near_ROM_bytes[#q.near_ROM_bytes+1]=b;if b~=q.near_bytes[i+1]then q.near_ROM_matches=false end
   end
  end
 end
 flFirst.native_x_decrease=q
end),emu.callbackType.write,0x75)
'''

RECEIPT = 'events=events,fourth_first_loss=flFirst,fourth_first_loss_counts=flCounts,'


def bindings(raw):
    assert isinstance(raw, bytes) and H(raw) == PIN
    Old = F.Prior.Early.Old
    payload = b''.join(raw[Old.CHR+p*1024:Old.CHR+(p+1)*1024] for p in Old.PAGES)
    assert H(payload) == Old.PUBLIC_PAYLOAD and raw[Old.COOKIE_AT:Old.COOKIE_AT+16] == Old.PUBLIC_COOKIE
    for at, before in Old.PUBLIC_NATIVE:assert raw[at:at+len(before)] == before
    points = dict(support=(3,0xb065), wall=(3,0xb061), plane=(3,0xb5c8), motor=(2,0xd65e))
    result = {}
    descriptor = []
    for name, (bank, pc) in points.items():
        offset = pc-0xa000 if bank == 3 else 9*1024+pc-0xd000
        data = payload[offset:offset+4]
        result[name] = list(data)
        page, within = divmod(offset, 1024)
        descriptor.append(dict(name=name, RAM_bank=bank, PC=pc,
                               carrier_file=Old.CHR+Old.PAGES[page]*1024+within,
                               preimage_hex=data.hex(), SHA256=H(data)))
    assert bytes(result['support'][:2]) == bytes.fromhex('a903')
    assert bytes(result['wall'][:2]) == bytes.fromhex('a902')
    assert bytes(result['plane'][:2]) == bytes.fromhex('c920')
    at = 16+71*8192+0xc29
    result['position'] = list(raw[at:at+4])
    descriptor.append(dict(name='position', physical_PRG=71, PC=0xac29, file=at,
                           preimage_hex=raw[at:at+4].hex(), SHA256=H(raw[at:at+4])))
    result['state_writers'] = [0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0')]
    result['origin_writers'] = [0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d76c0')]
    assert len(result['origin_writers']) == 3
    return result, descriptor


def from_text(base, raw):
    assert isinstance(base, str) and H(base.encode()) == BASE and base.count(PIN) == 1
    config, descriptor = bindings(raw)
    lua = 'local FL={' + ','.join(name+'={'+','.join(map(str,value))+'}' for name,value in sorted(config.items()))+'}\n'
    text = one(base, 'local function finish(ok,why)', lua+DECL+FUNCTIONS+'local function finish(ok,why)')
    text = one(text, "emu.addMemoryCallback(guarded('main',function()", OBSERVERS+"emu.addMemoryCallback(guarded('main',function()")
    text = one(text, 'events=events,', RECEIPT)
    restored = one(text, lua+DECL+FUNCTIONS+'local function finish(ok,why)', 'local function finish(ok,why)')
    restored = one(restored, OBSERVERS+"emu.addMemoryCallback(guarded('main',function()", "emu.addMemoryCallback(guarded('main',function()")
    restored = one(restored, RECEIPT, 'events=events,')
    assert restored == base
    LuaRuntime().compile(text)
    return text, descriptor


def controller(raw):
    return from_text(F.controller(raw), raw)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-text', type=Path)
    args = ap.parse_args()
    raw = F.Prior.Early.Old.NIGHTLY.read_bytes()
    text, descriptor = from_text(args.from_text.read_bytes().decode(), raw) if args.from_text else controller(raw)
    print('DKJR_FOURTH_NATIVE_CALIBRATION '+json.dumps(dict(passed=True, ROM_SHA256=PIN,
        base_Lua_SHA256=BASE, Lua_SHA256=H(text.encode()), static_binding_preimages=descriptor,
        actual_source_origin_stores=3, maximum_specific_witnesses=8, generic_trajectory_arrays=0,
        exact_base_restoration=True, output_files=0, PNGs=0, game_writes=False, native_claim=False), separators=(',', ':')), flush=True)
