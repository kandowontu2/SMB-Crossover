"""Focused real IRQ/FF seams for the 38-byte Mini native-power bridge."""
from collections import Counter
from pathlib import Path
import json
import prepare_mini_mario_native_power_1103_v56 as P
N,O,R,address,location=P.N,P.O,P.R,P.address,P.location
SOUND=[0x7d8,0x7da,0x7db,0x7dc]

def clear(m):
    for key in ['writes','ram_writes','ppu_log']:
        if hasattr(m,key):setattr(m,key,[])

def view(m):
    native=bytearray(m[0x200:0x800])
    for a in SOUND:native[a-0x200]=0
    return ([bytes(x)for x in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(native),
        N.get(m,'SelectedCharacter'),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
        bytes(m.vram),tuple(m.chr_latches),m.upper,m.lastset,m.ppu_addr,m.toggle,m.buffer,m.ppuctrl)

def path(m):
    code=bytes(m[0xe000:0x10000]);hits=[]
    for i in range(len(code)-8):
        if code[i:i+4]==bytes.fromhex('ad390110')and code[i+5:i+8]==bytes.fromhex('ee3a01'):hits.append(i)
    assert len(hits)==1
    i=hits[0];offset=code[i+4];offset-=256 if offset&128 else 0
    return 0xe000+i+5,0xe000+i+5+offset

def main():
    dest=O/'native-power-v57-ISR.json';assert not dest.exists()
    q=json.loads((O/'mini-host-v56.json').read_text());assert q['passed']
    raw=P.P.ROM.read_bytes();after=bytearray(raw)
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);assert after[at:at+len(old)]==old
        after[at:at+len(old)]=bytes.fromhex(row['new_hex'])
    assert P.W.sha(after)==q['expected_memory_only_ROM_SHA256']
    old,b=P.bundle(raw),P.bundle(after);CPU=N.NesMPU;L=q['labels'];counts=Counter();seen=set();rows=[]
    minimum=224;foreground_minimum=224;deepest=None;pending=Counter();writers=Counter();current=None
    allowed={}
    wanted=[('Fthrow',2,'8dd807'),('DecrementSfx1Length',0,'ced807'),('GrowItemRegs',0,'8dda07'),('GrowItemRegs',10,'8ddb07'),('ContinueGrowItems',0,'eedb07'),('PlayBrickShatter',2,'8ddc07'),('DecrementSfx3Length',0,'cedc07'),('PlayPowerUpGrab',2,'8dda07'),('DecrementSfx2Length',0,'ceda07')]
    # Full nativeDBG records scoped labels separately with unqualified names.
    for line in P.B.GLOBALS.with_suffix('.dbg').read_text().splitlines():
        if not line.startswith('sym\t'):continue
        z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x);name=z.get('name','').strip('"')
        if 'val'not in z or 'seg'not in z:continue
        for suffix,delta,code in wanted:
            if name!=suffix:continue
            g=b['segs'][z['seg']];pc=int(z['val'],0)+delta;at=int(g['ooffs'],0)+pc-int(g['start'],0)
            assert b['raw'][at:at+3]==bytes.fromhex(code),(name,delta)
            allowed[(((at-16)//8192)|128,pc)]=name
    assert len(allowed)==18
    def clone(c,reference=False):
        m=N.fork(c.memory);clear(m)
        if reference:
            m.bundle=old
            for w,tag in enumerate(m.rawtags[:]):
                if tag&128:m.raw_page(w,tag)
        z=CPU(memory=m,pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z
    def finish(c,ret):
        nonlocal minimum,deepest
        for _ in range(100000):
            if(c.pc,c.sp)==ret:return
            if c.sp<minimum:minimum=c.sp;deepest=dict(scenario=current,PC=c.pc,SP=c.sp)
            assert c.memory[c.pc]!=0,('Native ISR BRK',current,hex(c.pc),c.sp)
            c.step()
        raise AssertionError(('Native ISR bound',current,ret))
    def probe(c,kind,nested=True):
        nonlocal minimum,deepest
        z=clone(c);m=z.memory;ref=clone(c,True);regs=(c.a,c.x,c.y,c.p,c.sp,c.pc)
        before=view(m);maps=m.rawtags[:];live=bytes(m[0x101+c.sp:0x200]);lag,regular=path(m)
        skipped=N.get(m,'NmiSkipped');commit=N.get(m,'FamilyMainCommit');lh=rh=0;winner=None
        assert N.get(m,'NmiDisable')==255
        ref.irq()if kind=='IRQ'else ref.nmi();finish(ref,(c.pc,c.sp))
        z.irq()if kind=='IRQ'else z.nmi()
        for _ in range(100000):
            if(z.pc,z.sp)==(c.pc,c.sp):break
            if z.sp<minimum:minimum=z.sp;deepest=dict(scenario=current,kind=kind,foreground_PC=c.pc,PC=z.pc,SP=z.sp)
            lh+=int(z.pc==lag);rh+=int(z.pc==regular)
            assert m[z.pc]!=0,('ISR BRK',current,kind,hex(z.pc),z.sp)
            if kind=='FF'and not z.p&4 and(winner is None or z.sp<winner.sp):winner=clone(z)
            ins=bytes(m[z.pc:z.pc+3])
            if ins in [bytes.fromhex(v)for v in ['8dd807','ced807','8dda07','ceda07','8ddb07','eedb07','8ddc07','cedc07']]:
                tag=m.rawtags[(z.pc-0x8000)//8192];assert(tag,z.pc)in allowed,(tag,z.pc,ins.hex(),list(allowed))
                writers[f'{tag:02x}:{z.pc:04x}:{allowed[tag,z.pc]}']+=1
            z.step()
        else:raise AssertionError(('ISR return bound',current,kind))
        assert regs[:3]==(z.a,z.x,z.y)and regs[3]&0xef==z.p&0xef and regs[4:]==(z.sp,z.pc),('ISR AXYP/SP',current,kind,c.pc)
        now=view(m);assert now[:7]==before[:7],('ISR source/native/scratch/SMC',current,kind,c.pc,[i for i in range(7)if now[i]!=before[i]])
        assert now[7:]==view(ref.memory)[7:]and tuple(m[a]for a in SOUND)==tuple(ref.memory[a]for a in SOUND),('ISR baseline PPU/audio',current,kind,c.pc)
        assert bytes(m[0x101+c.sp:0x200])==live,('Live stack',current,kind,c.pc)
        if kind=='IRQ':assert lh==rh==0 and N.get(m,'NmiSkipped')==skipped
        else:assert lh==1 and rh==0 and N.get(m,'NmiSkipped')==(skipped+1)&255
        assert N.get(m,'FamilyMainCommit')==(commit if kind=='IRQ'else commit&1)
        if maps!=m.rawtags:
            ins=bytes(m[z.pc:z.pc+3]);assert ins in[bytes.fromhex(v)for v in ['8d1551','8d1651','8e1651','8c1651']]
            w=1 if ins[1]==0x15 else 2;assert m.rawtags[w]==N.get(m,'CurrentBank'if w==1 else'CurrentBankC')
            assert all(maps[k]==m.rawtags[k]for k in range(4)if k!=w);pending[ins.hex()]+=1
        counts[kind]+=1
        if kind=='FF'and nested and winner is not None:
            # Replay actual IRQ at this lag handler's deepest reached I0.
            baseline=clone(winner);actual=clone(winner);probe(actual,'IRQ',False)
            actual.irq();finish(actual,(winner.pc,winner.sp))
            finish(actual,(c.pc,c.sp));finish(baseline,(c.pc,c.sp))
            assert view(actual.memory)[:7]==view(baseline.memory)[:7]
            assert bytes(actual.memory[0x101+c.sp:0x200])==bytes(baseline.memory[0x101+c.sp:0x200])
            assert(actual.a,actual.x,actual.y,actual.p&0xef,actual.sp)==(baseline.a,baseline.x,baseline.y,baseline.p&0xef,baseline.sp)
            counts['nested_IRQ_deepest_FF']+=1
    def live():
        m=N.fresh(b);N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
        N.invoke(m,'MiniScene')
        N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8,PlayerStatus=0,PlayerSize=1,ObjectOffset=5,Player_X_Position=162,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1)
        for name,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',0)]:m[address(b,name)+5]=v
        clear(m);return m
    class Trace(CPU):
        def step(self):
            nonlocal foreground_minimum
            foreground_minimum=min(foreground_minimum,self.sp);m=self.memory;pc=self.pc
            tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            if tag==3 and L['MiniHostPickup']<=pc<L['MiniHostEnd']or 0x15a<=pc<0x17b:
                key=(current,pc,self.sp,m.rawtags[1],m.rawtags[2],self.p&0xcf)
                if key not in seen:
                    seen.add(key)
                    if not self.p&4:probe(self,'IRQ')
                    probe(self,'FF')
            return super().step()
    def run(name,m,entry,**kw):
        nonlocal current
        current=name;before=len(seen);N.NesMPU=Trace
        try:result=N.invoke(m,entry,**kw)
        finally:N.NesMPU=CPU
        rows.append(dict(scenario=name,contexts=len(seen)-before,foreground=result));print(name,rows[-1]['contexts'],minimum,flush=True)
    m=live();run('real-native-pickup',m,'HandlePowerUpCollision',a=205,x=5,y=46,p=0x21)
    assert N.get(m,'GuestPowerupActive')==1 and m[address(b,'Enemy_Flag')+5]==0
    run('already-erased-reentry',m,'HuPickup',a=41,x=5,y=46,p=0x21)
    run('native-update-start',m,'NrNativePowerupDispatch',a=0,x=0,y=0,p=0x21)
    for _ in range(58):N.invoke(m,'NrNativePowerupDispatch',a=0,x=0,y=0,p=0x21)
    run('native-update-complete-colors',m,'NrNativePowerupDispatch',a=0,x=0,y=0,p=0x21)
    assert N.get(m,'PlayerStatus')==1 and N.get(m,'GuestPowerupActive')==0 and N.get(m,'GameEngineSubroutine')==8
    result=dict(passed=True,CPU_only=True,ROM_written=False,native_admitted=False,kernel_SHA256=q['SHA256'],ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],actual_ISR_counts=dict(counts),minimum_ISR_SP=minimum,minimum_foreground_SP=foreground_minimum,deepest=deepest,scenarios=rows,source_bound_audio_writers=dict(writers),pending_bus_writes=dict(pending),scope='Only new38B pickup/update leaves plus actual FarCallCommon/SMC contexts reached from real native pickup, erased reentry, initial update and final update/native colors. IRQ atI0; genuine FF lagNMI atbothI0/I1. ExactAXYP/SP/live stack/privateRAM/native0200..07FF/R0..7/SMC/owner/map shadows. PPU/audio equal unchanged ca90 handler fromidentical state. EachFF deepest reachedI0 additionally executes actual nestedIRQ and resumesFF suffix. Existingv48 shared/physics/cold proofs inherited unchanged; no broader native admission or original30/35 power timing claim.',bindings={p.relative_to(R).as_posix():P.W.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'mini-host-v56.json',O/'mini-host-v56.bin',R/'src/reset.s',R/'src/music_drivers/vanilla_sfx.s']})
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in['passed','actual_ISR_counts','minimum_ISR_SP','minimum_foreground_SP','deepest']}))

if __name__=='__main__':main()
