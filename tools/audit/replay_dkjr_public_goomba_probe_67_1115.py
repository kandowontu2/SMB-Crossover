"""Eight specific contact/input witnesses over unchanged cap-depart controls."""
from hashlib import sha256
import json
import replay_dkjr_public_cap_depart_67_1115 as F
import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE = '5c65a62251a0613e0c072087cc81f94716426e037c3ae9618d59e3415ddd9ffa'


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


DECL = '''local g3Counts={enemy_queries=0,injury_entries=0,source5_stores=0,jump_admissions=0}
local g3FirstNear,g3LastNear,g3Injury,g3PrivateInjury,g3First5,g3Jump
local g3InputEdges,g3LastA={},nil
'''

FUNCTIONS = '''local function g3Watching()
 return playing and index==4 and x()>=740 and x()<850
end
local function g3View(kind,slot)
 local q=snapshot();local c=emu.getState();q.kind=kind;q.PC=c['cpu.pc'];q.SP=c['cpu.sp']
 q.bits=bits;q.saved=read(0xdc);q.AB=read(0x0a);q.previousAB=read(G3.previousAB)
 q.source_held=ram(2,0x14);q.source_sample=ram(2,0x15)
 q.prior=ram(2,0x6c);q.source_y=ram(2,0x210);q.origin=ram(2,0x76);q.limit=ram(2,0x7b)
 q.age=ram(2,0x7e);q.fraction=ram(2,0x7f);q.acc=ram(2,0x82)+256*ram(2,0x83)
 q.impulse=ram(2,0x86)+256*ram(2,0x87);q.native_vy=read(0x8e)
 q.player_bbox={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 slot=slot or read(0x0d)
 if slot<6 then local at=0x65c+4*slot
  q.actor={slot=slot,flag=read(0x10+slot),id=read(0x17+slot),x=pos(0x76,0x5d,slot),y=read(0xbe+slot),
   state=read(0x1f+slot),direction=read(0x46+slot),speed=read(0x58+slot),collision=read(G3.collision+slot),
   bbox={read(at),read(at+1),read(at+2),read(at+3)}}
 end
 return q
end
'''

OBSERVERS = '''emu.addMemoryCallback(guarded('pipe3 Goomba contact ingress',function()
 if not g3Watching()or not mapped(G3.contactPC,'nesPrgRom',G3.contactAt)then return end
 local slot=read(0x0d)
 if slot>=6 or read(0x17+slot)~=6 or read(0x10+slot)~=1 then return end
 g3Counts.enemy_queries=g3Counts.enemy_queries+1
 local gap=pos(0x76,0x5d,slot)-x()
 if gap>=0 and gap<=48 then
  local q=g3View('actual-forward-Goomba-collision-query',slot)
  if not g3FirstNear then g3FirstNear=q end
  g3LastNear=q
 end
end),emu.callbackType.exec,G3.contactPC)
emu.addMemoryCallback(guarded('pipe3 native injury ingress',function()
 if not g3Watching()or not mapped(G3.injuryPC,'nesPrgRom',G3.injuryAt)then return end
 g3Counts.injury_entries=g3Counts.injury_entries+1
 if not g3Injury then
  g3Injury=g3View('first-actual-InjurePlayer-entry')
  g3Injury.stack={};local sp=emu.getState()['cpu.sp']
  for i=1,8 do g3Injury.stack[i]=read(0x100+((sp+i)&255))end
 end
end),emu.callbackType.exec,G3.injuryPC)
emu.addMemoryCallback(guarded('pipe3 original private injury ingress',function()
 if not g3Watching()or g3PrivateInjury or not mapped(0xbd93,'nesWorkRam',3*8192+0x1d93)then return end
 g3PrivateInjury=g3View('first-Dk-native-injury-entry')
end),emu.callbackType.exec,0xbd93)
for _,pc in ipairs(G3_WRITERS)do local address=pc
 emu.addMemoryCallback(guarded('pipe3 original source transition',function()
  if not g3Watching()or not mapped(address,'nesWorkRam',3*8192+(address&8191))then return end
  local a=emu.getState()['cpu.a']
  if a==3 and ram(2,0x6b)~=3 then
   g3Counts.jump_admissions=g3Counts.jump_admissions+1
   g3Jump=g3View('last-actual-original-jump-admission');g3Jump.writer_pc=address;g3Jump.pending_A=a
  elseif a==5 then
   g3Counts.source5_stores=g3Counts.source5_stores+1
   if not g3First5 then g3First5=g3View('first-original-state5-store');g3First5.writer_pc=address;g3First5.pending_A=a end
  end
 end),emu.callbackType.exec,address)
end
'''

POLL = ''' if g3Watching()then
  local a=bits&128
  if a~=g3LastA then
   if #g3InputEdges>=2 then table.remove(g3InputEdges,1)end
   g3InputEdges[#g3InputEdges+1]=g3View('last-actual-A-poll-edge')
  end
  g3LastA=a
 end
'''

RECEIPT = ('events=events,goomba3_counts=g3Counts,goomba3_first_near=g3FirstNear,'
           'goomba3_last_near=g3LastNear,goomba3_native_injury=g3Injury,'
           'goomba3_private_injury=g3PrivateInjury,goomba3_first_source5=g3First5,'
           'goomba3_jump=g3Jump,goomba3_A_edges=g3InputEdges,')


def controller(raw):
    _, payload = F.Old.identity(raw)
    base = F.controller(raw)
    assert sha256(base.encode()).hexdigest() == BASE
    bundle = W.Symbols.bundle()
    labels = dict(previousAB=W.address(bundle, 'PreviousA_B_Buttons'),
                  collision=W.address(bundle, 'Enemy_CollisionBits'))
    for prefix, name in (('contact', 'PlayerEnemyCollision'), ('injury', 'InjurePlayer')):
        labels[prefix+'PC'] = W.address(bundle, name)
        labels[prefix+'At'] = W.location(bundle, name)-16
        assert raw[labels[prefix+'At']+16] != 0
    writers = sorted(0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0'))
    config = 'local G3={'+','.join(f'{k}={v}' for k, v in sorted(labels.items()))+'}\n'
    observers = OBSERVERS.replace('G3_WRITERS', '{'+','.join(map(str, writers))+'}')
    text = one(base, 'local function finish(ok,why)', config+DECL+FUNCTIONS+'local function finish(ok,why)')
    text = one(text, "emu.addMemoryCallback(guarded('main',function()", observers+"emu.addMemoryCallback(guarded('main',function()")
    text = one(text, ' polls=polls+1\n', ' polls=polls+1\n'+POLL)
    text = one(text, 'events=events,', RECEIPT)
    restored = one(text, config+DECL+FUNCTIONS+'local function finish(ok,why)', 'local function finish(ok,why)')
    restored = one(restored, observers+"emu.addMemoryCallback(guarded('main',function()", "emu.addMemoryCallback(guarded('main',function()")
    restored = one(restored, ' polls=polls+1\n'+POLL, ' polls=polls+1\n')
    restored = one(restored, RECEIPT, 'events=events,')
    assert restored == base
    LuaRuntime().compile(text)
    return text, labels


if __name__ == '__main__':
    text, labels = controller(F.Old.NIGHTLY.read_bytes())
    print('DKJR_GOOMBA3_PROBE '+json.dumps(dict(passed=True, native_Lua_SHA256=sha256(text.encode()).hexdigest(),
        maximum_specific_witnesses=8, controls_and_assertions_byte_exact_after_removal=True,
        hook_bindings=labels, output_files=0, PNGs=0, game_writes=False), separators=(',', ':')), flush=True)
