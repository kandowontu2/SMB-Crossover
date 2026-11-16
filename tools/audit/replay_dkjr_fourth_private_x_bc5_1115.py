"""Passive first private-X writer calibration over frozen e07/ed3e controls."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_fourth_first_loss_bc5_v2_1115 as V2

H = lambda value: sha256(value).hexdigest()
PIN = V2.PIN
V2_FACTORY_SHA = 'f4798c9f8ebc684f8d20dcf18b082093c68b2978e92da1b5ce922883e7e3b5fe'
V2_LUA_SHA = 'e07e07be0e84cb2b439c1786170ba80e95e233e2440443514f67c5961c853158'
WALL = "flFollow('wall',0xb061,FL.wall,function()return true end)"
SOURCE_X = 0xc213
SOURCE_X_MAPPING = 2*8192+0x213

EXTRA_VIEW = '''
 q.camera_cached=ram(2,0x435)+256*ram(2,0x436);q.camera_delta=ram(2,0x438)
 q.camera_ready=ram(2,0x437);q.native_relative_x=read(0x571)
 q.world_relative_x=x()-camera();q.anchor_source_x=x()-camera()-8
 q.anchor_world_x=ram(2,0x213)+8+camera()
'''

WRITER = '''emu.addMemoryCallback(guarded('first-loss privateXwrite',function(address,value)
 if not flFirst.first_carry or not flWatching()then return end
 local m=emu.convertAddress(address)
 if not m or m.memType~=emu.memType.nesWorkRam or m.address~=FLX.source_x_mapping then return end
 flCounts.private_x_writes=flCounts.private_x_writes+1
 local old=ram(2,0x213);value=value&255
 if flFirst.private_x_decrease or value>=old or old-value>=8 then return end
 local q=flView('first-private-source-X-decrease-write')
 q.write_address=address;q.write_mapping={memType=m.memType,address=m.address}
 q.old_source_x=old;q.new_source_x=value
 local c=emu.getState();local pc=c['cpu.pc'];q.observed_pc=pc;q.near_start=pc-6;q.near_bytes={}
 for at=pc-6,pc+4 do q.near_bytes[#q.near_bytes+1]=read(at)end
 local code=emu.convertAddress(pc-6)
 if code then q.near_mapping={memType=code.memType,address=code.address}end
 for _,known in ipairs(FLX.writers)do
  if pc==known.observed_post_pc then
   q.known_writer=known.name;q.writer_pc=known.store_pc;q.known_window_matches=true
   assert(code and code.memType==emu.memType.nesWorkRam and
    code.address==3*8192+((pc-6)&8191),'Private-X writer code mapping')
   for i,b in ipairs(known.near_bytes)do
    assert(q.near_bytes[i]==b,'Private-X known writer preimage '..pc)
   end
  end
 end
 flFirst.private_x_decrease=q
end),emu.callbackType.write,0xc213)'''


def lua(value):
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return '{'+','.join(lua(v) for v in value)+'}'
    assert isinstance(value, dict)
    return '{'+','.join(k+'='+lua(v) for k, v in sorted(value.items()))+'}'


def bindings(raw):
    _, descriptor = V2.V1.bindings(raw)
    old = V2.V1.F.Prior.Early.Old
    payload = b''.join(raw[old.CHR+p*1024:old.CHR+(p+1)*1024] for p in old.PAGES)
    # Authenticate both explicit indexed source-X writers. An unexpected
    # indirect writer remains an observation, never silently classified.
    patterns = [
        ('camera-shift-indexed', bytes.fromhex('bd03c238ed38c49d03c2'), 7),
        ('explicit-anchor-import-indexed', bytes.fromhex('bd13c2186df1c89d13c2'), 7),
    ]
    writers = []
    for name, pattern, store_offset in patterns:
        assert payload[:0x1fe0].count(pattern) == 1, name
        offset = payload.index(pattern)+store_offset
        store_pc = 0xa000+offset
        observed = store_pc+3
        start = observed-6
        window = payload[start-0xa000:start-0xa000+11]
        assert window[3:6] == pattern[store_offset:store_offset+3]
        writers.append(dict(name=name, store_pc=store_pc, observed_post_pc=observed,
                            near_bytes=list(window)))
        page, within = divmod(start-0xa000, 1024)
        descriptor.append(dict(name=name, RAM_bank=3, store_PC=store_pc,
            observed_post_PC=observed, near_start=start,
            carrier_file=old.CHR+old.PAGES[page]*1024+within,
            preimage_hex=window.hex(), SHA256=H(window)))
    assert writers[0]['store_pc'] > 0xbae5
    return dict(source_x_mapping=SOURCE_X_MAPPING, writers=writers), descriptor


def restore_v2(text, raw):
    config, _ = bindings(raw)
    declaration = 'local FLX='+lua(config)+'\n'
    text = V2.V1.one(text, declaration+'local flCounts=', 'local flCounts=')
    text = V2.V1.one(text, 'plane_candidates=0,private_x_writes=0}', 'plane_candidates=0}')
    text = V2.V1.one(text, EXTRA_VIEW+' q.source_x=', ' q.source_x=')
    return V2.V1.one(text, WRITER, WALL)


def from_probe_text(v2_text, raw):
    assert H(Path(V2.__file__).read_bytes()) == V2_FACTORY_SHA
    assert isinstance(v2_text, str) and H(v2_text.encode()) == V2_LUA_SHA
    config, descriptor = bindings(raw)
    declaration = 'local FLX='+lua(config)+'\n'
    text = V2.V1.one(v2_text, 'local flCounts=', declaration+'local flCounts=')
    text = V2.V1.one(text, 'plane_candidates=0}', 'plane_candidates=0,private_x_writes=0}')
    text = V2.V1.one(text, ' q.source_x=', EXTRA_VIEW+' q.source_x=')
    text = V2.V1.one(text, WALL, WRITER)
    assert restore_v2(text, raw) == v2_text
    assert H(V2.restore_v1(v2_text).encode()) == V2.V1_LUA_SHA
    V2.restore_base(V2.restore_v1(v2_text), raw)
    V2.V1.LuaRuntime().compile(text)
    return text, descriptor


def controller(raw):
    text, _ = V2.controller(raw)
    return from_probe_text(text, raw)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-probe', type=Path)
    args = ap.parse_args()
    raw = V2.V1.F.Prior.Early.Old.NIGHTLY.read_bytes()
    text, descriptor = (from_probe_text(args.from_probe.read_bytes().decode(), raw)
                        if args.from_probe else controller(raw))
    print('DKJR_FOURTH_PRIVATE_X '+json.dumps(dict(passed=True, ROM_SHA256=PIN,
        parent_Lua_SHA256=V2_LUA_SHA, Lua_SHA256=H(text.encode()),
        binding_preimages=descriptor, maximum_specific_witnesses=8,
        replaced_witness='wall -> private source-X decrease', controls_changed=False,
        game_writes=False, output_files=0, PNGs=0, native_claim=False), separators=(',', ':')), flush=True)
