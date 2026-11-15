"""Explicit private e418 earned-sword full-stage controls; frozen siblings intact."""
from hashlib import sha256
import argparse,json
import compose_prince_body_world_1114 as C
import replay_prince_body_four_caps_1114 as Four
import replay_prince_earned_current_1114 as Earned
import check_prince_earned_full_stage_1113 as Full
from check_ff_stdout_controller_source_1110 import LuaRuntime

PIN=Four.PIN


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in sorted(value.items()))+'}'
    if isinstance(value,(tuple,list)):return '{'+','.join(map(lua,value))+'}'
    if isinstance(value,str):return json.dumps(value)
    return str(value).lower()


def main_hooks(raw,parent):
    W=Earned.Frozen.W;b=dict(W.Symbols.bundle(),raw=raw);hooks={}
    pc,at=W.address(b,'GameLoop'),W.location(b,'GameLoop');lo=16+(at-16)//8192*8192
    assert raw[lo:lo+8192]==parent[lo:lo+8192]
    hooks['entry']=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]))
    idle,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop')
    jsr=b'\x20'+pc.to_bytes(2,'little');returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==jsr]
    assert len(returns)==2 and returns[0]==12
    hooks['returns']=[dict(pc=idle+d,offset=at+d-16,bytes=list(raw[at+d:at+d+8]))for d in returns]
    hooks['ram']={name:W.address(b,name)for name in('AreaType','OperMode','OperMode_Task','CheatInvincible','CheatStartLevel','StarInvincibleTimer')}
    return hooks


def controller(raw):
    assert C.digest(raw)==PIN
    parent=C.inverse(raw);typed=C.normalize_parent(parent,kind=C.parent_kind(parent))
    original,cache=Earned.inputs(typed.reference421)
    assert C.digest(cache)==Full.Fix.CANDIDATE
    text=Full.controller(cache)
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    variant="local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')"
    change(variant,variant+"\nassert(variant==3,'Full Prince route requires native variant3')")
    change("          switch('third-park',65)","          switch('third-running-approach',1)")
    change('pad=201  -- Original Up+Right+A+B pipe-approach fallback.','pad=8  -- Ordinary original Up throughout the pipe approach.')
    change('pad=age<55 and 8 or 201','pad=8')
    change('pad=201','pad=8')
    change("  if progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then", """  if progress=='third-running-approach' then
    if s.x>=744 and s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then
      late.third_running_request=s;switch('third-running-takeoff',129)
    end
  elseif progress=='third-running-takeoff' and s.action==4 then
    late.third_running_admission=s;switch('third-running-flight',1)
  elseif progress=='third-running-flight' then
    if s.x>=897 and s.pose==15 and s.mode==0 and s.lock==0 then
      late.fourth_practical_stand=s;switch('fourth-practical-up',8)
    elseif s.mode==2 or s.mode==6 then
      switch('fourth-practical-up',8)
    end
  elseif progress=='fourth-practical-up' then
    local left,right=capFeet(s,912,144)
    if left or right then
      late.fourth_practical_cap=s;late.fourth_partial=s
      switch('fourth-anchor-step',65)
    end
  elseif progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then""")
    packet=C.Build.Old.Packet
    old=cache[packet.COOKIE:packet.COOKIE+16].hex();new=raw[packet.COOKIE:packet.COOKIE+16].hex()
    assert text.count(old)==1;text=text.replace(old,new,1)
    change(f"assert(rom=='{Full.Fix.CANDIDATE}','Exact cache candidate ROM')",
           f"assert(rom=='{PIN}','Exact private e418 earned-stage replay')")
    change('local function finish(passed,reason)\n',
           'local verifiedMainEntries,verifiedMainReturns,verifiedGrounded=0,0,0\nlocal verifiedPendingMain,verifiedAnyStar=nil,false\nlocal function finish(passed,reason)\n')
    change('    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,',
           '    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Main_pending=verifiedPendingMain~=nil,grounded_1_2_completed_returns=verifiedGrounded,observed_natural_Star=verifiedAnyStar,')
    hooks=main_hooks(raw,parent)
    observer=r'''
local verifiedHooks=@HOOKS@
local function verifiedHook(h,fn)
  emu.addMemoryCallback(guarded(function()
    local a=emu.convertAddress(h.pc)
    if not a or a.memType~=emu.memType.nesPrgRom or a.address~=h.offset then return end
    for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact compiled Main witness')end
    fn()
  end),emu.callbackType.exec,h.pc)
end
verifiedHook(verifiedHooks.entry,function()
  assert(not verifiedPendingMain,'Previous complete Main returned')
  local sp=emu.getState()['cpu.sp']
  local pc=read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1
  assert(pc==verifiedHooks.returns[1].pc or pc==verifiedHooks.returns[2].pc,'Authenticated native Main caller')
  verifiedMainEntries=verifiedMainEntries+1;verifiedPendingMain={pc=pc,sp=(sp+2)&255}
end)
for _,h in ipairs(verifiedHooks.returns)do verifiedHook(h,function()
  assert(verifiedPendingMain and verifiedPendingMain.pc==h.pc and verifiedPendingMain.sp==emu.getState()['cpu.sp'],'Same Main caller/SP return')
  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1
  local s=state()
  if read(0x6002)==38 and s.engine==8 then
    assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==0,'Ordinary current no-cheat gameplay')
    verifiedAnyStar=verifiedAnyStar or read(verifiedHooks.ram.StarInvincibleTimer)>0
  end
  if ending and s.world==0 and s.level==1 and s.engine==8 and read(verifiedHooks.ram.OperMode)==1 and read(verifiedHooks.ram.OperMode_Task)==3 then
    pad=0
    assert(ending.flag and ending.castle and ending.gap and s.lives==2,'Full authored native exit chain')
    if read(verifiedHooks.ram.AreaType)==2 and s.y_high==1 and math.abs(s.y-176)<=1 and s.ground==0 and s.hp>0 and source(0xab)==0xa7 and hexHeader(2)==cookie and hexHeader(3)==cookie then
      verifiedGrounded=verifiedGrounded+1
    else verifiedGrounded=0 end
    ending.completed_grounded_1_2=verifiedGrounded
    if verifiedGrounded>=25 then
      final=s;finish(true,'Prince earned-sword full1-1 and25 living grounded completed Main returns in1-2')
    end
  end
end)end
'''.replace('@HOOKS@',lua(hooks))
    change('local ending\n','local ending\n'+observer+'\n')
    change("    final=s\n    finish(true,'Prince cleared authored 1-1 and entered underground 1-2')\n    return true",
           '    pad=0\n    return true')
    assert not any(s in text for s in('pad=201','or 201','emu.write','emu.setState','io.open','takeScreenshot'))
    LuaRuntime().compile(text)
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),required_native_variant=3,
        ordinary_controls_only=True,natural_items_and_sword=True,gameplay_seeds=0,
        qualification_pending=True,current_Downloads_replacement=False,outputs=0,Mesen=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--current-bt-f11',action='store_true');args=parser.parse_args()
    if args.current_bt_f11:import current_prince_body_research_f11_1114 as Current
    else:import current_prince_body_research_input_1114 as Current
    current=Current.load(Earned.ROM);raw,_=C.proposal(current.reference1daca)
    print(json.dumps(dict(**metadata(raw),public_input=current.metadata()),separators=(',',':')),flush=True)
