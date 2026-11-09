"""Prepare the exact Mini peak replay with renderer and native Goomba witnesses."""

import argparse
import json
from pathlib import Path
import sys

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R / 'build/mini-final-peak-1110'
CONTROLLER = BASE / 'controller.lua'
PROFILE = BASE / 'capture/instruction-sample.json'
ROM = R / 'build/mini-box-terrain-visible-1110/candidate.nes'
PIN = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
CONTROLLER_PIN = '303c5b77ae921d8904d0c352a64d0c2dc1f9377c717a73b114a786b7d45cc09d'
REACHES = {'4:a5ba': 2, '0:bf49': 2, '0:a04e': 1, '0:a12e': 1, '0:bf7e': 1, '0:bfac': 1}

OBSERVE = '''local rendererEntries, goombaChecks = {}, {}
local goombaLabels = {[0xbf49]='page_seam_guard',[0xa04e]='native_floor',[0xa12e]='native_side',
                     [0xbf7e]='fast_floor',[0xbfac]='fast_side'}
local function captureHotEntry(bank,pc,state,key)
 local sp=state['cpu.sp']
 local a,x,y=state['cpu.a'],state['cpu.x'],state['cpu.y']
 if bank=='4' and pc==0xa5ba then
  check(#rendererEntries<8,'Bounded native renderer witnesses')
  local ptr=read(3)+256*read(4)
  local phys=emu.convertAddress(ptr)
  local header=read(ptr)
  local descriptor={header}
  for i=1,math.min(header,32) do descriptor[i+1]=read((ptr+i)&65535) end
  local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
  rendererEntries[#rendererEntries+1]={pc=key,sp=sp,entry_a=a,entry_x=x,entry_y=y,return_pc=ret,
   pointer=ptr,descriptor=descriptor,descriptor_complete=header<=32,
   descriptor_prg_offset=phys and phys.memType==emu.memType.nesPrgRom and phys.address or nil,
   attribute=read(6),x_low=read(7),x_high=read(8),y_low=read(9),y_high=read(10),
   oam_cursor=r('CurrentOAMOffset'),rotation_active=r('GuestOamRotationActive'),rotation=r('RgOamRotation')}
 elseif bank=='0' and goombaLabels[pc] then
  check(#goombaChecks<12,'Bounded native Goomba witnesses')
  -- ObjectOffset stays live through BBChk_E. The query helper may use a
  -- sprite-object index in X internally, so retain both values.
  local slot=read(0x0d)
  check(slot<6,'Reached native enemy slot')
  local item={pc=key,kind=goombaLabels[pc],sp=sp,slot=slot,cpu_x=x,cpu_y=y,a=a,
   enemy_id=read(0x17+slot),enemy_state=read(0x1f+slot),direction=read(0x053f+slot),
   world_x=read(0x76+slot)+256*read(0x5d+slot),world_y=read(0xbe+slot),y_high=read(0xa5+slot)}
  if pc==0xbf49 then
   item.seam_taken=a==0
  else
   local row=(pc==0xbf7e or pc==0xbfac) and y or read(5)
   item.tile=a
   item.cell_pointer=read(9)+256*read(10)
   item.cell_row=row
   item.cell_address=(item.cell_pointer+row)&65535
  end
  goombaChecks[#goombaChecks+1]=item
 end
end
local function validateHotEntries()
 check(#rendererEntries==2,'Exact replay reaches both generic metasprite calls')
 local counts,seam,floor,side={},nil,nil,nil
 for _,row in ipairs(goombaChecks)do
  counts[row.kind]=(counts[row.kind] or 0)+1
  if row.kind=='page_seam_guard' and row.seam_taken then
   check(not seam,'Exactly one native Goomba takes the old left-page seam')
   seam=row
  elseif row.kind=='native_floor' then floor=row
  elseif row.kind=='native_side' then side=row end
 end
 check(counts.page_seam_guard==2 and counts.native_floor==1 and counts.native_side==1 and
       counts.fast_floor==1 and counts.fast_side==1,'Exact replay reaches the incumbent Goomba paths')
 check(seam and floor and side and seam.slot==floor.slot and seam.slot==side.slot and
       seam.sp==floor.sp and seam.sp==side.sp and seam.enemy_id==6,
       'Old seam and native queries belong to the same live Goomba and call frame')
end
'''


def contract(raw):
    # All hooks read the accumulator before the exact compiled branch or
    # compare consumes it. Keep this observer pinned to the incumbent image.
    preimages = {(4, 0xa5ba): 'aede06a000b103', (0, 0xbf49): 'f00fc9f0f00b',
                 (0, 0xa04b): '20baa1d003', (0, 0xa12b): '207e95f005',
                 (0, 0xbf7c): 'b109c954d0d8', (0, 0xbfaa): 'b109d0ac'}
    for (bank, pc), hex_bytes in preimages.items():
        at = 16 + bank * 8192 + (pc & 8191)
        expected = bytes.fromhex(hex_bytes)
        assert raw[at:at + len(expected)] == expected, (bank, hex(pc), raw[at:at + len(expected)].hex())
    profile = json.loads(PROFILE.read_text())
    assert tuple(profile['scene'][k] for k in ('frame', 'x', 'y', 'keys')) == (1971, 1511, 135, 193)
    assert {row['key']: row['visits'] for row in profile['opcodes'] if row['key'] in REACHES} == REACHES


def enhance(source):
    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    # Keep all existing controller assertions and accounting. Their reports
    # share the one sample JSON, and their former CSV streams use a sink.
    replace("local csv=assert(io.open(OUTPUT..'smoke.csv','w'))",
            'local sink={write=function()end,flush=function()end,close=function()end}\n'
            'local csv=sink\nlocal diagnostic={}')
    replace("local end_csv=assert(io.open(OUTPUT..'native-end.csv','w'))", 'local end_csv=sink')
    replace("local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\\n');f:close();csv:flush();return q",
            "diagnostic.result=q\n local f=assert(io.open(OUTPUT..'instruction-sample.json','w'))\n"
            " f:write(json(diagnostic)..'\\n');f:close();return q")
    replace('local lastInstruction\nlocal function sampleInstruction()',
            OBSERVE + 'local lastInstruction\nlocal function sampleInstruction()')
    replace(" if state['cpu.sp']<minimumSampleSP.sp then",
            " if not instructionIsISR and ((bank=='4' and pc==0xa5ba) or (bank=='0' and goombaLabels[pc])) then\n"
            "  captureHotEntry(bank,pc,state,key)\n end\n if state['cpu.sp']<minimumSampleSP.sp then")
    replace("    local file=assert(io.open(OUTPUT..'instruction-sample.json','w'))\n"
            '    file:write(json({scene=call.scene,opcodes=sorted,farcall_edges=transports,minimum_sample_SP=minimumSampleSP,',
            "    check(call.scene.frame==1971 and call.scene.x==1511 and call.scene.y==135 and call.scene.keys==193,\n"
            "          'Exact controller Mini peak anchor')\n"
            '    validateHotEntries()\n'
            '    diagnostic={scene=call.scene,opcodes=sorted,farcall_edges=transports,minimum_sample_SP=minimumSampleSP,\n'
            '                     renderer_entries=rendererEntries,goomba_checks=goombaChecks,')
    replace("scope='One actual controller-reached GameLoop; elapsed cycles include interrupted work. Farcall labels record the stack return and native bank tag.'})..'\\n')\n"
            '    file:close()',
            "scope='One controller-reached GameLoop with split foreground/ISR costs and read-only native renderer and Goomba witnesses.'}")
    replace(" local file = assert(io.open(OUTPUT..'timing.json', 'w'))\n"
            ' file:write(json({ROM_sha256=C.ROM_sha256,cadence=cadence,route_by_world_x=routeCadence,routines=stats,open_calls=#stack,',
            ' diagnostic.timing={ROM_sha256=C.ROM_sha256,cadence=cadence,route_by_world_x=routeCadence,routines=stats,open_calls=#stack,')
    replace("unmatched_interrupt_returns=unmatchedReturns,open_interrupts=#interrupts})..'\\n')\n file:close()",
            'unmatched_interrupt_returns=unmatchedReturns,open_interrupts=#interrupts}')
    replace(" local file=assert(io.open(OUTPUT..'column-pairs.json','w'))\n"
            ' file:write(json({pairs=completedPairs,left=leftCount}));file:close()',
            ' diagnostic.column_pairs={pairs=completedPairs,left=leftCount}')
    assert source.count("io.open(OUTPUT..'instruction-sample.json','w')") == 1
    assert all(token not in source for token in ('emu.write(', 'emu.loadSavestate(', 'emu.reset('))
    return source


def check_lua(source):
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime

    lua = LuaRuntime()
    assert lua.eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    # Exercise the added callback and association logic without an emulator.
    test = '''local mem={[3]=0x40,[4]=0xa6,[0xa640]=4,[0xa641]=0x3c,[6]=2,[0x17]=6,[0x76]=3,[0x5d]=6}
local function read(at)return mem[at] or 0 end
local function r(n)return 0 end
local check=assert
local emu={memType={nesPrgRom=1},convertAddress=function(addr)return {memType=1,address=4*8192+(addr&8191)} end}
local state={['cpu.sp']=230,['cpu.a']=0,['cpu.x']=0,['cpu.y']=0}
'''
    calls = '''
captureHotEntry('4',0xa5ba,state,'4:a5ba')
captureHotEntry('4',0xa5ba,state,'4:a5ba')
captureHotEntry('0',0xbf49,state,'0:bf49')
mem[5]=0xb0;mem[9]=2;mem[10]=3;state['cpu.a']=0x54
captureHotEntry('0',0xa04e,state,'0:a04e')
state['cpu.a']=0
captureHotEntry('0',0xa12e,state,'0:a12e')
mem[0x0d]=1;state['cpu.a']=0x10
captureHotEntry('0',0xbf49,state,'0:bf49')
state['cpu.a']=0x54;state['cpu.y']=0xb0
captureHotEntry('0',0xbf7e,state,'0:bf7e')
state['cpu.a']=0
captureHotEntry('0',0xbfac,state,'0:bfac')
validateHotEntries()
assert(rendererEntries[1].descriptor[2]==0x3c and rendererEntries[1].descriptor_prg_offset==4*8192+0x640)
assert(goombaChecks[1].seam_taken and goombaChecks[1].world_x==1539)
assert(goombaChecks[2].tile==0x54 and goombaChecks[2].cell_address==0x3b2)
assert(not goombaChecks[4].seam_taken and goombaChecks[5].cell_row==0xb0)
'''
    lua.execute(test + OBSERVE + calls)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    assert sha(ROM) == PIN and sha(CONTROLLER) == CONTROLLER_PIN
    contract(ROM.read_bytes())
    source = enhance(CONTROLLER.read_text())
    check_lua(source)
    prepare(args.output, ROM, source, {CONTROLLER, PROFILE, Path(__file__)}, expected=PIN,
            timeout=140, allow_interactive=True,
            scope='Exact controller peak frame 1971 with read-only bank4:$A5BA descriptors and bank0 Goomba '
                  'seam, floor, and side witnesses. One aggregate controller report, inherited two-PNG cap.')


if __name__ == '__main__':
    main()
