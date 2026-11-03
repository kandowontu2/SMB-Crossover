"""Observe the actual repeated stair contact without changing any input or ROM."""
import json,re,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2';B=R/'build/bubble-bobble-source-1101-v1'
PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    source=O/'native-landing-bub-full11-supported-stair/controller.lua';text=source.read_text()
    q=json.loads((O/'landing-v21-layout.json').read_text());image=(O/'landing-v21-image.bin').read_bytes()
    labels={name:int(value,16)for value,name in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',(B/'component.lbl').read_text(),re.M)}
    query=q['labels']['BbNativeQueryReturn'];latch=labels['BbOriginal_D371']
    def hook(pc):return dict(pc=pc,physical=3*8192+pc-0xa000,bytes=list(image[pc-0xa000:pc-0xa000+4]))
    from observe_chip_committed_write import lua
    anchor='local full_normal_actual={} '
    assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\nlocal stair_probe={jumps={},queries={},clamps={},terrain=nil,last_jump_Main=0}\nlocal stair_hooks='+lua(dict(query=hook(query),latch=hook(latch))))
    anchor='local function full_rearm_has_support(actor)'
    insertion="""local function stair_actor()
 local actor=0x2e;local a={}
 for i=0,19 do a[#a+1]=full_state(actor+i)end
 return a
end
local function stair_actual(h)
 local a=emu.convertAddress(h.pc)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.physical then return false end
 for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Pinned actual stair diagnostic')end
 return true
end
local function stair_active()
 return phase=='fullstage'and full_index==7 and full_x()>=2330 and full_x()<2432
end
emu.addMemoryCallback(function()
 if not stair_active()or not stair_actual(stair_hooks.latch)then return end
 local Main=BUB_OBSERVER.summary().completed_Main+1;stair_probe.last_jump_Main=Main
 if#stair_probe.jumps<12 then
  local row=full_support_probe();row.Main_pending=Main;row.actor=stair_actor()
  row.PlayerSize=r('PlayerSize');row.PlayerStatus=r('PlayerStatus');row.source_held=full_state(0x301)
  row.source_native_input=full_bytes(0x309,8);row.actual_latched_direction=full_state(0x33)
  stair_probe.jumps[#stair_probe.jumps+1]=row
 end
 if not stair_probe.terrain then
  local columns={}
  for wx=2352,2464,16 do
   local rows={}
   for wy=80,224,16 do local solid,tile=full_solid(wx,wy);rows[#rows+1]={y=wy,tile=tile,solid=solid}end
   columns[#columns+1]={x=wx,rows=rows}
  end
  stair_probe.terrain={Main_pending=Main,camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos'),columns=columns}
 end
end,emu.callbackType.exec,stair_hooks.latch.pc)
emu.addMemoryCallback(function()
 if not stair_active()or full_x()<2364 or full_x()>2378 or r('Player_Y_Position')>144 or#stair_probe.queries>=64 or not stair_actual(stair_hooks.query)then return end
 local s=emu.getState()
 stair_probe.queries[#stair_probe.queries+1]={Main_pending=BUB_OBSERVER.summary().completed_Main+1,
  x=full_x(),y=r('Player_Y_Position'),actor=stair_actor(),source_query=full_bytes(0x23,2),
  source_alt_query=full_bytes(0x84,2),native_query_scratch=full_bytes(0x3d0,5),
  actual_R6=ram(9),actual_R7=ram(10),actual_row=s['cpu.y'],actual_result=s['cpu.a']}
end,emu.callbackType.exec,stair_hooks.query.pc)
emu.addMemoryCallback(function(_,value)
 if not stair_active()or#stair_probe.clamps>=24 then return end
 local old=r('Player_X_Position')
 if value>=old or old-value>4 then return end
 local s=emu.getState();local a=emu.convertAddress(s['cpu.pc'])
 stair_probe.clamps[#stair_probe.clamps+1]={Main_pending=BUB_OBSERVER.summary().completed_Main+1,
  before=full_x(),new_low=value,y=r('Player_Y_Position'),source_x=full_state(0x103),
  pc=s['cpu.pc'],physical=a and a.address or-1,memory=a and a.memType or-1,
  actor=stair_actor(),native_state=r('Player_State'),native_speed=ram(142)}
end,emu.callbackType.write,L.Player_X_Position)

"""
    assert text.count(anchor)==1;text=text.replace(anchor,insertion+anchor)
    anchor='  actual_normal_pit_jump_entries=full_normal_actual,'
    assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\n  actual_stair_diagnostic=stair_probe,')
    anchor=" if full_stationary>500 then full_fail('Source route stationary500Main without a completed crossing')end"
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+"\n if#stair_probe.jumps>=3 and x<2380 and q.completed_Main-stair_probe.last_jump_Main>64 then full_fail('Diagnostic repeated actual first-stair wall')end")
    # A repeated jump every~56updates keeps last_jump_Main moving; cap the
    # diagnostic after six exact accepted starts instead of replaying500Main.
    anchor=" local actor=Q.launch.bob==1 and 0x42 or 0x2e\n if full_state(actor+3)&128~=0"
    assert text.count(anchor)==1
    text=text.replace(anchor," if#stair_probe.jumps>=6 and x<2380 then full_fail('Diagnostic six original jumps repeat at actual stair wall')end\n"+anchor)
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/'native-landing-bub-stair-diagnostic';rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,O/'landing-v21-layout.json',O/'landing-v21-image.bin',B/'component.lbl',O/'combined-landing.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Observer-only diagnosis of actualv26 X2369/Y117..160 stair wall, samecontroller/ROM. At most12actualpost-directionlatchD371 jump records,64physicallyqualified sourceTilequeryresults,24realPlayerXbackwardwritePCs and one8columnx10row native metatile neighborhood. Existinglivechecks unchanged; repeated6jumpwall intentionallyterminatesnegative with full11/observer/diagnostic. No new gameplay/control/helper changes.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,diagnostic=True,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))


if __name__=='__main__':main()
