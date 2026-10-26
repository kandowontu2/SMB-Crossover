"""Source/mock final display-epoch oracle and actual compiled IRQ ownership."""
from pathlib import Path
import copy, json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory, address, location
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]


def to_lua(rt,v):
    if isinstance(v,dict):return rt.table_from({k:to_lua(rt,x)for k,x in v.items()})
    if isinstance(v,list):return rt.table_from([to_lua(rt,x)for x in v])
    return v


def phase_units(LuaRuntime):
    source=(ROOT/'tools/audit/parodius_visibility_hud_terminal_phase_v1.lua').read_text()
    pure=source.split('-- PURE_PHASE_PREDICATE_BEGIN\n')[1].split('-- PURE_PHASE_PREDICATE_END')[0]
    ram=dict(SelectedCharacter=18,VvVariant=1,CrossoverBehaviorVersion=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,InvHudActive=3,InvHudPhysical=140,X5HudChrUpper=1)
    q=dict(start=dict(ppu=dict(frame=1800,scanline=-1,cycle=0,cpu=1000),original_start=dict(frame=1800),game_generation=4,source_generation=4,publication=77,DMA=66,exact256=True,completed256=True,dma_finished_before_start=True,mask=30,font=396,visible_font=396,observed_updates=200,ram=ram),endpoint=dict(ppu=dict(frame=1800,scanline=240,cycle=0,cpu=20000),game_generation=4,visible_source_generation=4,visible_publication=77,visible_DMA=66,font=0,observed_updates=201,ram=copy.deepcopy(ram)),IRQ_entry=dict(ppu=dict(frame=1800,scanline=31,cpu=4000),depth=1,nmi_depth=0,bank=126,PC=0x8000),IRQ_font_write=dict(ppu=dict(frame=1800,scanline=31,cpu=4032),depth=1,nmi_depth=0,bank=126,PC=0x8015,value=0,upper=0,physical=0,instruction_exact=True),IRQ_return=dict(ppu=dict(frame=1800,scanline=32,cpu=4100),depth=0,nmi_depth=0,bank=126,PC=0x8043,font=0))
    expected=dict(frame=1800,generation=4,variant=1,mode=0,fresh_updates=45,HUD_font=396,world_font=0,IRQ_bank=126,IRQ_entry_PC=0x8000,IRQ_font_write_PC=0x8015,IRQ_return_PC=0x8043)
    mutations=[('correct recorded phases',None,None),('wrongHUDstartfont',('start','font'),0),('wrongVisibleHUDfont',('start','visible_font'),0),('absentIRQ',('IRQ_entry',),None),('absentFontWrite',('IRQ_font_write',),None),('absentIRQreturn',('IRQ_return',),None),('wrongIRQfont',('IRQ_return','font'),396),('wrongIRQwrite',('IRQ_font_write','value'),140),('wrongIRQupper',('IRQ_font_write','upper'),1),('wrongIRQphysical',('IRQ_font_write','physical'),256),('wrongIRQsourcePC',('IRQ_font_write','PC'),0x9000),('wrongIRQbank',('IRQ_entry','bank'),77),('wrongIRQinstruction',('IRQ_font_write','instruction_exact'),False),('wrongIRQline',('IRQ_entry','ppu','scanline'),32),('wrongIRQepoch',('IRQ_entry','ppu','frame'),1799),('wrongStartEpoch',('start','ppu','frame'),1799),('wrongOriginalStartEpoch',('start','original_start','frame'),1799),('wrongEndEpoch',('endpoint','ppu','frame'),1801),('wrongEndPhase',('endpoint','ppu','scanline'),-1),('wrongSourceGeneration',('start','source_generation'),3),('wrongCurrentGeneration',('endpoint','game_generation'),5),('wrongVisibleGeneration',('endpoint','visible_source_generation'),3),('wrongPublication',('endpoint','visible_publication'),76),('wrongDMA',('endpoint','visible_DMA'),65),('incompleteDMA',('start','completed256'),False),('wrongHardware',('start','exact256'),False),('pendingDMA',('start','dma_finished_before_start'),False),('renderingOff',('start','mask'),6),('wrongVariant',('start','ram','VvVariant'),2),('wrongMode',('endpoint','ram','CrossoverBehaviorVersion'),1),('wrongTag',('start','ram','InvHudActive'),5),('wrongPhysicalTag',('endpoint','ram','InvHudPhysical'),0),('wrongUpperTag',('endpoint','ram','X5HudChrUpper'),0),('inactiveEngine',('endpoint','ram','GameEngineSubroutine'),3),('wrongEndpointFont',('endpoint','font'),396),('noMeaningfulUpdates',('expected','fresh_updates'),44),('IRQbeforeStart',('IRQ_entry','ppu','cpu'),999),('fontWriteBeforeIRQ',('IRQ_font_write','ppu','cpu'),3999),('returnBeforeWrite',('IRQ_return','ppu','cpu'),4031),('returnAfterEnd',('IRQ_return','ppu','cpu'),20001),('unexpectedLaterFontWrite',('later',),True)]
    rows=[]
    for name,path,value in mutations:
        rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pure);v=copy.deepcopy(q);e=copy.deepcopy(expected)
        if path and path[0]not in ['later','expected']:
            target=v
            for key in path[:-1]:target=target[key]
            if value is None:target.pop(path[-1])
            else:target[path[-1]]=value
        elif path and path[0]=='expected':e[path[1]]=value
        lv=to_lua(rt,v);lv['last_font_write']=lv['IRQ_font_write']
        if path and path[0]=='later':lv['last_font_write']=to_lua(rt,dict(value=0))
        ok,why=rt.globals().PARODIUS_HUD_FINAL_PHASE_OK(lv,to_lua(rt,e))
        assert bool(ok)==(path is None),(name,ok,why)
        rows.append(dict(case=name,accepted=bool(ok),reason=why))
    return rows


def compiled_irq(rom,config):
    b=scoped_load(rom);h=config['terminal_phase'];entry=config['hooks']['IrqScrollSplit'];ret=config['hooks']['IrqReturn']
    assert entry['address']==address(b,'IrqScrollSplit') and entry['bank']==126
    at=location(b,'IrqScrollSplit');data=b['raw'][at:at+68]
    assert data[h['IRQ_font_instruction_PC']-entry['address']-2:h['IRQ_font_write_PC']-entry['address']]==bytes([0xa9,0,0x8d,0x28,0x51])
    rows=[]
    for mode in [0,1]:
        for scroll in [0,7,128,255]:
            m=Memory(b);m[address(b,'CrossoverBehaviorVersion')]=mode;m[address(b,'IrqPPUCTRL')]=1;m[address(b,'IrqNewScroll')]=scroll
            c=NesMPU(memory=m,pc=entry['address']);c.a,c.x,c.y,c.p,c.sp=0xa5,0x31,0x74,0x35,0xfd;before=(c.a,c.x,c.y,c.p,c.sp)
            c.stPushWord(0x5b00);c.stPush(c.p&~0x10);m.writes=[];fontwrites=[];atreturn=None
            for _ in range(1000):
                if c.pc==0x5b00:break
                if c.pc==ret['address']:atreturn=dict(PC=c.pc,cycles=c.processorCycles,SP=c.sp)
                pc=c.pc;count=len(m.writes);c.step()
                for address_,value in m.writes[count:]:
                    if address_==0x5128:fontwrites.append(dict(instruction_PC=pc,callback_PC=c.pc,physical_bank=m.banks[0],value=value,completed_CPU_cycles=c.processorCycles))
            else:raise AssertionError('IRQ did not return')
            assert (c.a,c.x,c.y,c.p,c.sp)==before,((c.a,c.x,c.y,c.p,c.sp),before)
            assert fontwrites==[dict(instruction_PC=h['IRQ_font_instruction_PC'],callback_PC=h['IRQ_font_write_PC'],physical_bank=126,value=0,completed_CPU_cycles=fontwrites[0]['completed_CPU_cycles'])]
            assert atreturn and atreturn['PC']==ret['address']
            rows.append(dict(mode=mode,scroll=scroll,AXYP_SP_restored=True,actual_compiled_font_write=fontwrites[0],actual_RTI_endpoint=atreturn,full_CPU_cycles=c.processorCycles,limits='Synthetic CPU state/interrupt entry, no PPU raster timing claim'))
    return rows


def observer_sequences(LuaRuntime):
    source=(ROOT/'tools/audit/parodius_visibility_hud_terminal_phase_v1.lua').read_text()
    prefix=r'''
local C={hud_ram={},terminal_phase={IRQ_font_write_PC=0x8015,IRQ_bank=126,IRQ_font_instruction_PC=0x8012,IRQ_font_instruction={0x8d,0x28,0x51}}}
local RAM={SelectedCharacter=18,VvVariant=1,CrossoverBehaviorVersion=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,InvHudActive=3,InvHudPhysical=140,X5HudChrUpper=1}
for n in pairs(RAM)do C.hud_ram[n]=n end
local S={['ppu.frameCount']=1800,['ppu.scanline']=-1,['ppu.cycle']=0,['cpu.cycleCount']=1000,['mapper.chrBanks8']=396,['cpu.pc']=0x9000}
local lifeGeneration,updates,ppuMask,irqDepth,nmiDepth,upper=4,200,30,0,0,0
local P={id=77,generation=4,oam={}};for i=1,256 do P.oam[i]=(i*17)%256 end
local visible={start={frame=1800},dma={id=66,publication=P,complete={},data_writes=256},chr_banks={[9]=396},start_hardware_exact_source=true,start_hardware=P.oam,dma_finished_before_start=true}
local bus={};local function row(f,q)f[#f+1]=q end
local function active()return true end
local function equal(a,b)return a==b end
local function bank()return 126 end
local function stamp()return{frame=S['ppu.frameCount'],scanline=S['ppu.scanline'],cycle=S['ppu.cycle'],cpu=S['cpu.cycleCount']}end
local HOOKS,STARTS,WRITES={},{},{}
local function hook(n,fn)HOOKS[n]=fn end
emu={memType={nesDebug=1},callbackType={write=1},eventType={startFrame=0},getState=function()return S end,read=function(a)if type(a)=='string'then return RAM[a]end;return({[0x8012]=0x8d,[0x8013]=0x28,[0x8014]=0x51})[a]end,addEventCallback=function(fn)STARTS[#STARTS+1]=fn end,addMemoryCallback=function(fn)WRITES[#WRITES+1]=fn end}
'''
    suffix=r'''
function TEST_RUN(which)
 STARTS[1]()
 S['cpu.pc']=0x8000;S['ppu.scanline']=31;S['cpu.cycleCount']=4000;irqDepth=1;HOOKS.IrqScrollSplit()
 S['cpu.pc']=0x8015;S['cpu.cycleCount']=4032;WRITES[1](0x5128,0);S['mapper.chrBanks8']=0
 S['cpu.pc']=0x8043;S['ppu.scanline']=32;S['cpu.cycleCount']=4100;irqDepth=0;HOOKS.IrqReturn()
 if which=='later-same-font-write'then S['cpu.pc']=0x9000;S['ppu.scanline']=40;S['cpu.cycleCount']=5000;WRITES[1](0x5128,0)end
 if which=='new-generation'then lifeGeneration=5 end
 if which=='new-displayed-publication'then visible.dma={id=67,publication={id=78,generation=4}}end
 S['cpu.pc']=0x9000;S['ppu.scanline']=240;S['cpu.cycleCount']=20000;updates=201
 local q=PARODIUS_HUD_FINAL_LEASE_EVIDENCE()
 local ok,why=PARODIUS_HUD_FINAL_PHASE_OK(q,{frame=1800,variant=1,mode=0,generation=lifeGeneration,fresh_updates=45,HUD_font=396,world_font=0,IRQ_bank=126,IRQ_entry_PC=0x8000,IRQ_return_PC=0x8043,IRQ_font_write_PC=0x8015})
 return ok,why,#STARTS,#WRITES,#bus,q.start.publication,q.endpoint.font
end
'''
    rows=[]
    for case in ['correct-observed-sequence','later-same-font-write','new-generation','new-displayed-publication']:
        rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(prefix+source+suffix)
        ok,why,starts,writes,events,pub,font=rt.globals().TEST_RUN(case)
        assert bool(ok)==(case=='correct-observed-sequence') and starts==writes==1 and pub==77 and font==0,(case,ok,why)
        rows.append(dict(case=case,accepted=bool(ok),reason=why,static_start_callbacks=starts,static_memory_callbacks=writes,logged_events=events,actual_endpoint_font_in_mock=font,limits='Host-only synthetic state/callback ordering, not native execution'))
    return rows


def check(LuaRuntime,script):
    return dict(predicate_cases=phase_units(LuaRuntime),observer_sequence_cases=observer_sequences(LuaRuntime),compiled_IRQ_cases=compiled_irq(script.with_name('candidate.nes'),json.loads(script.with_name('config.json').read_text())))
