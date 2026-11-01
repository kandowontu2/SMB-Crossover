"""Prepare a single original wrestler's cold controller-only native route."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_wwf_roster_package_bounded_v1 import decode
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--variant',type=int,required=True);ap.add_argument('--expected',required=True)
    a=ap.parse_args();assert 0<=a.variant<6;b=scoped_load(a.joint/'candidate.nes')
    template=R/'tools/reference/hogan_native_bounded_v1.lua';text=template.read_text()
    at=int.from_bytes((a.joint/'wf-meta-offsets.bin').read_bytes()[2*a.variant:2*a.variant+2],'little')
    _,cells=decode((a.joint/'metadata.chr').read_bytes()[at:at+1687],0,0)
    idle=[[t,r,y,x]for t,r,x,y,p in cells]
    art=R/'build/wwf-roster-package-1101-v1/body-pages.chr';body=art.read_bytes();assert len(body)==84*1024
    physical=[546+p if p<58 else 442+p-58 if p<76 else 629+p-76 for p in range(84)]
    point=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    args=dict(sha256=a.expected,main_return=point,idle=idle,chr=list(body),physical=physical,variant=a.variant,frontend_only=False)
    changes=[("local pad={}","for i=1,P.variant do plan[#plan+1]='select' end\nlocal pad={}"),
             ("if active()or lastMain or#isrs>0 then","if true then"),
             ("if#isrs>0 then local q=table.remove(isrs);local s=emu.getState()","local s=emu.getState();local q=isrs[#isrs]\n  if q and q.kind==kind and q.sp==s['cpu.sp']then table.remove(isrs)"),
             ("if active()then local sp=emu.getState()['cpu.sp']","if phase~='title'then local sp=emu.getState()['cpu.sp']"),
             ("local minSP=255","local minSP=255\nlocal bankEvents={}\nlocal apuWrites,expansionWrites=0,0\nlocal artIndex={} for i,p in ipairs(P.physical)do artIndex[p]=i-1 end\nemu.addMemoryCallback(function(reg,v)local s=emu.getState();bankEvents[#bankEvents+1]={reg=reg,value=v,pc=s['cpu.pc'],sp=s['cpu.sp'],frame=frame};if#bankEvents>32 then table.remove(bankEvents,1)end end,emu.callbackType.write,0x5115,0x5116)\nemu.addMemoryCallback(function()apuWrites=apuWrites+1 end,emu.callbackType.write,0x4000,0x4017)\nemu.addMemoryCallback(function()expansionWrites=expansionWrites+1 end,emu.callbackType.write,0x5000,0x5007)"),
             ("physical>=546 and physical<563","artIndex[physical]~=nil"),
             ("(physical-546)*1024","artIndex[physical]*1024"),
             ("size<=64","size<=68"),
             ("r('FmGroups')&7~=0","r('FmGroups')&7~=P.variant"),
             ("ROM_sha256=P.sha256","ROM_sha256=P.sha256,variant=P.variant,bank_events=bankEvents,APU_writes=apuWrites,MMC5_SFX_writes=expansionWrites,final_phase=phase,final_cpu=emu.getState()['cpu.pc'],final_bank=r('CurrentBank'),final_C=r('CurrentBankC'),final_mode=r('OperMode'),final_mode_task=r('OperMode_Task'),final_engine=r('GameEngineSubroutine'),final_screen_task=r('ScreenRoutineTask'),final_ready=r('WfHostReady')"),
             ("updates>=500","updates>=1000"),
             ("500 Main route bound","1000 Main route bound"),
             ("frame>=1800","frame>=3200"),
             ("1800 physical frame bound","3200 physical frame bound")]
    for old,new in changes:assert old in text,old;text=text.replace(old,new)
    text='HOGAN_ARGS='+lua(args)+'\n'+''.join(f'L[{json.dumps(n)}]={address(b,n)}\n'for n in['WfTagDone','WfHostReady','WfRenderBuffer','WfState','WfProxyValid','WfRawProxyCommit'])+text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text);assert ok,error
    prepare(a.output,a.joint/'candidate.nes',text,[Path(__file__),template,art,a.joint/'assembly-stage.json'],expected=a.expected,timeout=150,scope='Single WWF alternate: cold D-pad/Select/Start/lives; controller idle/jump/source attacks/Goomba defeat/camera; original pattern/OAM/display and real ISR register/SMC balance. APU/SFX write counts only; no audible or full1-1 qualification.')


if __name__=='__main__':main()
