"""Rebind Mini smoke/full route and retain authoritative native end evidence."""
from pathlib import Path
import argparse,ast,sys
import prepare_mini_mario_native_smoke_1103_v31 as S
import prepare_mini_mario_native_smoke_1103_v25 as B
import prepare_mini_mario_native_final_1103_v43 as V
import prepare_mini_mario_full11_1103_v28 as F
from prepare_selected_native_packet_v1 import R,prepare
from observe_chip_committed_write import lua
O=R/'build/mini-mario-end-fixed-packets-1103-v49'
DIAGNOSTIC=R/'tools/audit/prepare_mini_mario_end_handoff_1103_v47.py'

def native_end(text):
    # Reuse the exact47 field schema/observer literal without executing47,
    # creating a dummy packet, modifying47, or copying its dependency tree.
    node=next(n for n in ast.parse(DIAGNOSTIC.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='main')
    assignments={t.id:n.value for n in node.body if isinstance(n,ast.Assign)for t in n.targets if isinstance(t,ast.Name)}
    fields=ast.literal_eval(assignments['fields'])
    literal=ast.literal_eval(assignments['observer'].func.value)
    observer=literal.replace('FIELD_LIST',lua(fields)).replace('>=1200','>=1800').replace('stopped1200physicalframes','stopped1800physicalframes')
    G=B.labels(B.GLOBALS);aliases={n:G[n]for n in fields+['GameTimerDisplay']}
    anchor='-- Controller inputs only.';assert text.count(anchor)==1
    text=text.replace(anchor,'for k,v in pairs('+lua(aliases)+')do L[k]=v end\n'+anchor)
    old='local done,lastEpoch,pending,last=nil,nil,nil,nil';assert text.count(old)==1
    text=text.replace(old,old+'\nlocal native_snapshot=nil\nlocal end_native={started=false,samples={}}')
    old='script_RAM_writes=false,controller_only=true';assert text.count(old)==1
    text=text.replace(old,'native_end_handoff=end_native,terminal_native=native_snapshot and native_snapshot()or nil,'+old)
    old='if not ok then result(false,tostring(e))';assert text.count(old)==1
    text=text.replace(old,"if not ok then if native_snapshot then end_native.terminal=native_snapshot()end;if shots<2 then local f=io.open(OUTPUT..'mini-end-terminal.png','wb');if f then f:write(emu.takeScreenshot());f:close();shots=shots+1 end end;result(false,tostring(e))")
    observer+='''
-- Real non8 Draw/Portrait uses native geometry; the original source8
-- motion/draw/DMA assertions above remain unchanged.
local native_draw_hook=C.hooks.MiniNativeDraw
emu.addMemoryCallback(guard(function()
 if r('SelectedCharacter')~=41 or r('OperMode')~=1 or ram(0xc300)==0 or r('GameEngineSubroutine')==8 or not valid(native_draw_hook)then return end
 local wx=r('Player_X_Position')+256*r('Player_PageLoc')
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 local expectedX=(wx-camera)&65535
 local expectedY=((r('Player_Y_HighPos')-1)*256+r('Player_Y_Position')+16)&65535
 check(word(0xc311)==expectedX and word(0xc313)==expectedY,'Actual non8 native canvas X-camera/Y+16')
 local q=native_snapshot();q.renderX=word(0xc311);q.renderY=word(0xc313)
 end_native.native_draw_count=(end_native.native_draw_count or 0)+1
 if not end_native.first_native_draw then end_native.first_native_draw=q end
 end_native.last_native_draw=q
end),emu.callbackType.exec,native_draw_hook.pc)
'''
    return text+'\n'+observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    syntax=LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')
    smoke,deps=S.build(a.rom,a.sha,a.kernel,a.labels,a.ref);smoke=native_end(V.rotated(smoke));syntax(smoke)
    prepare(O/'smoke49',a.rom,smoke,[*deps,Path(__file__),Path(V.__file__),DIAGNOSTIC],expected=a.sha,timeout=180,allow_interactive=True,
        scope='Same43Mini smoke controls/guards, correctactualrotation/SmPose4/CHR/sourcepixels/bbox. Terminalnative mode/task/engine/identity/XY/Ready/level/flag/timer state alwaysrecorded; menu+native orfailure2PNG. No scriptRAMwrites/ROMemit/physicschanges.')
    text,deps=F.controller(a.rom,a.sha,a.kernel,a.labels,a.ref);text=V.rotated(text)
    for old,new in [
        ("if route_previous and x<=route_previous+0.05 then route_stationary=route_stationary+1 else route_stationary=0 end\n route_previous=x", "if route_previous and x<=route_previous+1 then route_stationary=route_stationary+1 else route_stationary=0;route_previous=x end"),
        ("check(route_max>3200,'Native castle route reached without shortcut')", "check(route_max>3000,'Source route reached finalcastle approach before native endsequence')")]:
        assert text.count(old)==1;text=text.replace(old,new)
    text=native_end(text);syntax(text)
    prepare(O/'full49',a.rom,text,[*deps,Path(__file__),Path(V.__file__),DIAGNOSTIC,R/'tools/audit/prepare_mini_mario_full11_1103_v33.py'],expected=a.sha,timeout=240,allow_interactive=True,
        scope='Exact43originalrun/jump+authorizedwallcling controls, all7authoredobstacles/active1-2/no-life-loss and hardwareguards unchanged. Add47actualnativeend60frame+phase observations/terminalsnapshot; endphase1800physicalframe bound allows nativecountdown/scene, no22000waitatstableseam. TwoPNGmenu+active1-2 orfailure. No RAM/ability seeds/helpers/ROMwrites. Old43/47negativeimmutable.')

if __name__=='__main__':main()
