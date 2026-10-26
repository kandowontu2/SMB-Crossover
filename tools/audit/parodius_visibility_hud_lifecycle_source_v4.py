"""Source-only complete Lua/assembled init-owner checks. Never a native verdict."""
from pathlib import Path
import argparse, hashlib, json, sys
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import Memory, address, location
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROOT=Path(__file__).resolve().parents[2]
EXPECTED='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'


def runtime(LuaRuntime,script):
    rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={}')
    for line in script.with_name('candidate.lbl').read_text().splitlines():
        f=line.split()
        if len(f)>=3 and f[0]=='al':rt.globals().L[f[2].lstrip('.')]=int(f[1],16)
    rt.execute(script.read_text())
    assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
    rt.execute("emu.addMemoryCallback=function()error('Runtime native callback registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime native callback removal forbidden')end")
    return rt


class ObservedArena(Arena):
    """Actual linked CPU, bridge callbacks, synthetic untimed read-only APIs."""
    def __init__(self,b,rt):
        super().__init__(b,18);self.rt=rt;self.cpu=None;self.last_cpu=0;self.hardware=bytearray(256);self.hwaddr=0;self.DMA_bytes=0
        self.execs={};self.ranges=[];self.write_callbacks=[]
        for _,q in rt.globals().callbacks.items():
            lo,hi=int(q['lo']),int(q['hi'])
            if q['kind']==2:
                if lo==hi:self.execs.setdefault(lo,[]).append(q['fn'])
                else:self.ranges.append((lo,hi,q['fn']))
            elif q['kind']==1:self.write_callbacks.append((lo,hi,q['fn']))
        parent=self
        class Bus(Memory):
            def __setitem__(self,at,value):
                if isinstance(at,int) and parent.cpu:
                    parent.sync()
                    if at==0x4014:
                        # py65 exposes the operand PC inside opSTA; Mesen's
                        # write callback exposes the completed instruction PC.
                        assert self[parent.cpu.pc-1]==0x8d
                        parent.rt.globals().state['cpu.pc']=parent.cpu.pc+2
                    for lo,hi,fn in parent.write_callbacks:
                        if lo<=at<=hi:fn(at,value)
                super().__setitem__(at,value)
                if isinstance(at,int) and parent.cpu:
                    if at==0x2003:parent.hwaddr=value
                    elif at==0x4014:
                        # Explicit untimed DMA model, not native PPU evidence.
                        for i in range(256):
                            v=self[value*256+i];parent.sync()
                            parent.rt.globals().state['ppu.spriteRamAddr']=parent.hwaddr
                            for lo,hi,fn in parent.write_callbacks:
                                if lo<=0x2004<=hi:fn(0x2004,v)
                            parent.hardware[parent.hwaddr]=v;parent.hwaddr=(parent.hwaddr+1)&255;parent.DMA_bytes+=1
        old=self.m;self.m=Bus(b)
        for i in range(0x8000):list.__setitem__(self.m,i,old[i])
        def read(at,kind=1):return self.hardware[int(at)&255] if kind==3 else self.m[int(at)]
        def convert(at):
            at=int(at);z=rt.table()
            z['address']=self.m.banks[(at-0x8000)//8192]*8192+(at&8191) if at>=0x8000 else at
            return z
        rt.globals().emu['read']=read;rt.globals().emu['convertAddress']=convert
    def sync(self):
        c=self.cpu;s=self.rt.globals().state
        for n,v in [('pc',c.pc),('sp',c.sp),('a',c.a),('x',c.x),('y',c.y),('ps',c.p),('cycleCount',self.last_cpu+c.processorCycles)]:s['cpu.'+n]=v
    def invoke(self,name,a=0,x=0,y=0):
        b=self.b;at=location(b,name);bank=(at-16)//8192;pc=address(b,name);w=(pc-0x8000)//8192
        self.m.page(w,bank)
        if w in (1,2):self.set('CurrentBank' if w==1 else 'CurrentBankC',bank|128)
        c=NesMPU(memory=self.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd;c.stPushWord(0x5aff)
        self.cpu=c;self.m.writes=[];visits={}
        for steps in range(100000):
            self.sync()
            for fn in self.execs.get(c.pc,[]):fn(c.pc)
            for lo,hi,fn in self.ranges:
                if lo<=c.pc<=hi:fn(c.pc)
            if c.pc==0x5b00:break
            visits[c.pc]=visits.get(c.pc,0)+1;c.step()
        else:raise AssertionError(('CPU unbounded',name,hex(c.pc),self.m.banks))
        assert c.sp==0xfd
        self.last_cpu+=c.processorCycles;self.cpu=None
        return c,visits
    def snapshot(self):
        v,p,d=self.rt.globals().PARODIUS_PUBLICATION_SNAPSHOT()
        return v,p,d


UNIT_PREFIX=r'''
local C={character=18,variant=1,ROM_sha256='unit',output=''}
local D={Sprite_Data=512};local ram={SelectedCharacter=18,VvVariant=1}
local txid,pubid,dmaid,nmiDepth,irqDepth,ppuMask,oamAddress=0,2,3,0,0,0,0
local visible,lastPub,lastDMA={id=1,start={frame=7}},nil,nil
lastPub={id=2,generation=0,oam={}};for i=1,256 do lastPub.oam[i]=(i*17)%256 end
lastDMA={id=3,publication=lastPub};visible.dma=lastDMA
local transaction,body,bodyPending,drawOwner,dmaPending,ownerSequence={},{},nil,nil,nil,{}
local completionHooks,physical={},{};local completeMismatches=0
local bus={};local function row(f,q)f[#f+1]=q end
local function stamp()return{frame=7,scanline=120,cycle=37,cpu=800}end
local function detail()return{}end
local function r(n)return ram[n]or 0 end
local function active()return false end
local function hook()end
local function onReturn()end
local function queueReturnSlot()end
local function bank()return 127 end
local function bytes()return{}end
local function equal(a,b)return a==b end
local function json()return'{}'end
emu={memType={nesDebug=1,nesSpriteRam=3,nesPpuDebug=2},callbackType={write=1},eventType={startFrame=0},addMemoryCallback=function()end,addEventCallback=function()end}
'''


def unit_bridge(LuaRuntime,bridge):
    cases=[]
    for blocked in ['none','nmi','irq','emitter','pending-body','dma']:
        rt=LuaRuntime(unpack_returned_tuples=True)
        expose="""
TEST={bus=bus,visible=visible,pub=lastPub,dma=lastDMA}
function TEST_BLOCK(k)if k=='nmi'then nmiDepth=1 elseif k=='irq'then irqDepth=1 elseif k=='emitter'then drawOwner=0 elseif k=='pending-body'then bodyPending={} elseif k=='dma'then dmaPending={} end end
function TEST_STATE()return visible==TEST.visible,lastPub==TEST.pub,lastDMA==TEST.dma,lifeGeneration,#bus,transaction==nil end
"""
        rt.execute(UNIT_PREFIX+bridge+expose);rt.globals().TEST_BLOCK(blocked)
        ok,err=rt.eval("(function()local ok,err=pcall(function()PARODIUS_INVALIDATE_PUBLICATION('unit')end);return ok,tostring(err)end)()")
        q=rt.globals().TEST_STATE();assert all(q[:3]),('Completed/displayed images lost',blocked,q)
        if blocked=='none':assert ok and q[3:]==(1,1,True),q
        else:assert not ok and q[3:]==(0,0,False),(blocked,q,err)
        cases.append(dict(blocked=blocked,accepted=ok,retains_same_visible_and_completed_images=True,generation=q[3],logged=q[4]))
    return cases


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['packet','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'proof.json').read_text());assert z['ROM_sha256']==EXPECTED
    sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
    starts=[]
    for profile in z['profiles']:
        q=json.loads((Path(profile['packet'])/'preparation.json').read_text());script=Path(q['script']);assert sha(script)==q['script_sha256']
        rt=runtime(LuaRuntime,script);count=rt.eval('#callbacks');capture=json.loads(script.with_name('config.json').read_text())['capture_start'];limit=min(439,capture-1)
        for frame in range(1,limit+1):rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runread(0);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
        rt.execute('callbacks[#callbacks].fn(0xe007)');assert rt.eval('#callbacks')==count
        starts.append(dict(kind=profile['kind'],script_sha256=sha(script),fixed_callbacks=count,dispatcher_last=True,inactive_mock_frames=limit,runtime_API_registration_attempts=0))
    bridge_path=ROOT/'tools/audit/parodius_visibility_hud_lifecycle_bridge_v2.lua';units=unit_bridge(LuaRuntime,bridge_path.read_text())
    profile=Path(z['profiles'][0]['packet']);prep=json.loads((profile/'preparation.json').read_text());script=Path(prep['script']);b=scoped_load(script.with_name('candidate.nes'));assert sha(script.with_name('candidate.nes'))==EXPECTED
    rows=[];case=None
    try:
        for mode in [0,1]:
            rt=runtime(LuaRuntime,script);q=ObservedArena(b,rt)
            q.put(VvVariant=1,CrossoverBehaviorVersion=mode,OperMode=1,OperMode_Task=1,GameEngineSubroutine=3,ScreenLeft_PageLoc=0,Player_PageLoc=0)
            # Actual clear does NOT publish: page2 is explicitly skipped.
            image=bytes((17*i+23)&255 for i in range(256));q.array('Sprite_Data',image)
            _,trace=q.invoke('InitializeMemory',y=address(b,'SecondaryMsgCounter')&255)
            got=bytes(q.m[address(b,'Sprite_Data'):address(b,'Sprite_Data')+256]);assert got==image
            assert not any(address(b,'Sprite_Data')<=p<address(b,'Sprite_Data')+256 for p,v in q.m.writes)
            assert q.snapshot()[1] is None
            rows.append(dict(mode=mode,owner='InitializeMemory',publishes=False,page2_preserved_exact=True,steps=sum(trace.values())))
            # Restore only synthetic source setup cleared by InitializeMemory.
            q.put(SelectedCharacter=18,VvVariant=1,CrossoverBehaviorVersion=mode,OperMode=1,OperMode_Task=1,GameEngineSubroutine=3,ScreenLeft_PageLoc=0,Player_PageLoc=0)
            q.invoke('MoveAllSpritesOffscreen');v,pub,d=q.snapshot();assert pub['phase']=='init-blank' and pub['generation']==0
            assert len(pub['oam'])==256 and all(pub['oam'][i]==248 for i in range(1,257,4))
            rows.append(dict(mode=mode,owner='MoveAllSpritesOffscreen',publication=int(pub['id']),phase=pub['phase'],oam_bytes=256,all64_Y_248=True))
            q.invoke('OAMandReadJoypad');v,pub,d=q.snapshot()
            assert d['publication']['id']==pub['id'] and d['complete']['exact_source'] and d['data_writes']==256
            assert len(d['complete']['hardware'])==256 and q.DMA_bytes==256
            rows.append(dict(mode=mode,owner='OAMandReadJoypad',source_phase=pub['phase'],complete_bytes=int(d['data_writes']),completion_after_actual_next_LDX=True,exact256=True,untimed_model=True))
            before=bytes(pub['oam'][i] for i in range(1,257));q.invoke('DrawPlayer_Intermediate')
            assert bytes(q.m[address(b,'Sprite_Data'):address(b,'Sprite_Data')+256])==before,'Portrait preparation is not an OAM publication'
            q.invoke('X5PortraitRender',x=q.get('ObjectMetasprite'),y=0);v,pub,d=q.snapshot()
            assert pub['phase']=='init-portrait' and pub['body'] and pub['body']['source']['refs'][1]['variant']==1
            assert len(pub['oam'])==256 and len(pub['body']['parts'])>0
            rows.append(dict(mode=mode,owner='X5PortraitRender',publication=int(pub['id']),phase=pub['phase'],body_source=pub['body']['source']['label'],body_parts=len(pub['body']['parts']),oam_bytes=256))
            oldid=pub['id'];oldimage=bytes(pub['oam'][i] for i in range(1,257));rt.globals().PARODIUS_INVALIDATE_PUBLICATION('source-native-generation')
            assert q.snapshot()[1]['id']==oldid and q.snapshot()[1]['generation']==0
            assert bytes(q.snapshot()[1]['oam'][i] for i in range(1,257))==oldimage
            q.invoke('DrawAllMetasprites');v,pub,d=q.snapshot();assert pub['phase']=='init-draw' and pub['generation']==1
            assert pub['body'] and len(pub['oam'])==256
            rows.append(dict(mode=mode,owner='DrawAllMetasprites',engine=q.get('GameEngineSubroutine'),publication=int(pub['id']),generation=int(pub['generation']),phase=pub['phase'],body_source=pub['body']['source']['label'],body_parts=len(pub['body']['parts']),oam_bytes=256))
            q.invoke('OAMandReadJoypad');v,pub,d=q.snapshot();assert d['complete']['exact_source'] and d['data_writes']==256 and d['source_generation']==1
            rows.append(dict(mode=mode,owner='OAMandReadJoypad',source_phase=pub['phase'],generation=int(d['source_generation']),complete_bytes=int(d['data_writes']),completion_after_actual_next_LDX=True,exact256=True,untimed_model=True))
            assert rt.eval('#callbacks')==starts[0]['fixed_callbacks']
    except Exception as ex:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),completed=rows,scope='Source component/observation failure; not a game defect verdict'),indent=2)+'\n');raise
    (a.output/'owner-cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    (a.output/'bridge-cases.json').write_text(json.dumps(units,indent=2)+'\n')
    proof=dict(passed=True,native_run=False,ROM_modified=False,ROM_sha256=EXPECTED,profiles=starts,bridge_cases=units,assembled_owner_cases=len(rows),owner_cases_sha256=sha(a.output/'owner-cases.json'),preserves_original_live_guard_file=True,original_guard_sha256=sha(ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua'),bridge_sha256=sha(bridge_path),preparation_sha256=sha(a.packet/'proof.json'),tool_sha256=sha(Path(__file__)),limits='Source-only Lua startup, host generation data and actual assembled CPU init paths under synthetic APIs. Four actual OAMandReadJoypad CPU calls use an explicit untimed256-byte hardware model to exercise completion and return endpoints, not real DMA/PPU timing. No native reachability, visibility, menu/death/pipe or pending Buffer2 overlap verdict. InitializeMemory preserves page2 and cannot establish a new publication. Native lifecycle controls remain required.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
