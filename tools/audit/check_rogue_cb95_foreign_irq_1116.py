"""Actualcb95 Mini/Sonic public parity and focused missile IRQ smoke."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_rogue_missile_cb95_1116 as J
import current_mini_weapon_owner_a2_1116 as Mini
import current_sonic_ceiling_complete_a2d9_1116 as Sonic
import check_rogue_missile_components_54b_1116 as Old

N,W,Frames=J.N,J.W,J.Frames


def cold_family(raw,b,family):
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(dict(b,raw=raw),0)
    if family=='Mini41':
        for _ in range(8):W.UI.key(m,32)
        assert(W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'))==('MINI MARIO',41,8)
    else:
        for bits in(4,4,4,1,32,32,32):W.UI.key(m,bits)
        assert W.UI.menu_name(m)[0]=='SONIC'and N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==3
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):return m
        m.controller_pad=0;Frames.frame(m,cold=True,whole_pass=True)
    raise AssertionError(('Actual foreign compiled cold bound',family))


def foreign(raw):
    parent=J.C.inverse(raw);b=J.bindings(raw)['bundle'];qs=Sonic.bindings(J.C.Plan.Mini.inverse(parent));rows=[]
    for family in('Mini41','Sonic43'):
        a=cold_family(parent,b,family);m=cold_family(raw,b,family);Old.same(a,m)
        if family=='Mini41':
            assert bytes(m.ram[3][:5120])==raw[Mini.CODE_AT:Mini.CODE_AT+5120]
            cookie=Mini.COOKIE;points={(254,W.address(b,'GameLoop')):'Main',(3,0xa000):'MiniPublic',(3,0xa3e5):'MiniStep'}
        else:
            assert bytes(m.ram[3][:0x1fe0])==qs['kernel'][:0x1fe0]
            assert bytes(m.ram[2][0x1000:0x1400])==qs['metadata']
            cookie=qs['cookie'];h=qs['hooks']['SonicHostMain'];points={(254,W.address(b,'GameLoop')):'Main',(h['tag'],h['PC']):'SonicHostMain'}
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(cookie,)*2
        counts=Counter();pending=[];objects=[];base=N.NesMPU
        def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
        class CPU(base):
            def __init__(self,*a,**kw):super().__init__(*a,**kw);objects.append(self)
            def settle(self):
                while pending and(self.pc,self.sp,tag(self.pc))==pending[-1][1]:counts[pending.pop()[0]+'_returned']+=1
            def step(self):
                self.settle()
                if self.memory is m:
                    key=(tag(self.pc),self.pc)
                    assert key!=(249,0xaf60),'Foreign character entered changed Rogue updater'
                    name=points.get(key)
                    if name:
                        pc=(m[0x101+self.sp]+256*m[0x102+self.sp]+1)&65535
                        pending.append((name,(pc,(self.sp+2)&255,tag(pc))));counts[name+'_entered']+=1
                return super().step()
        for bits in([0]*16+[1]*8+[0]*2+[2]*8):
            a.controller_pad=m.controller_pad=bits
            Frames.frame(a,whole_pass=True)
            with patch.object(N,'NesMPU',CPU):Frames.frame(m,whole_pass=True)
            for c in objects:c.settle()
            objects.clear();assert not pending;Old.same(a,m)
        assert counts['Main_entered']==counts['Main_returned']==34
        for name in points.values():assert counts[name+'_entered']==counts[name+'_returned']and counts[name+'_returned']>=34
        rows.append(dict(family=family,counts=dict(counts),full_private_native_maps_SMC_exact_to9826=True,
            runtime_both_cookies_exact=cookie.hex(),changed_Rogue_updater_entries=0,
            terminal={n:N.get(m,n)for n in('SelectedCharacter','NumberofLives','Player_X_Position','Player_PageLoc','Player_Y_Position','GameEngineSubroutine')}))
    return rows


def irq(raw):
    import check_metal_head_bridge_1112 as Async
    seed=J.cold(raw);W.clear_logs(seed);Old.record(seed,11);seed.controller_pad=0
    base=N.NesMPU;pendingMain=None;seen=set();counts=Counter();minimum=255;cuts=[]
    def regs(c):return(c.pc,c.sp,c.a,c.x,c.y,c.p|48)
    def clone(c):
        m=N.fork(seed);d=base(memory=m,pc=c.pc);d.a,d.x,d.y,d.p,d.sp=c.a,c.x,c.y,c.p,c.sp;return m,d
    def finish(m,c):
        for _ in range(200000):
            if(c.pc,c.sp)==pendingMain:return
            assert m[c.pc];base.step(c)
        raise AssertionError('Actual combined interrupted caller bound')
    class CPU(base):
        def step(self):
            nonlocal pendingMain,minimum
            if self.memory is seed:
                tag=seed.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(254,W.address(seed.bundle,'GameLoop')):
                    pendingMain=((seed[0x101+self.sp]+256*seed[0x102+self.sp]+1)&65535,(self.sp+2)&255)
                if tag==249 and self.pc in(0xaf76,0xafe2)and self.pc not in seen:
                    seen.add(self.pc);assert pendingMain is not None
                    for kind in('IRQ','lagNMI'):
                        assert not self.p&4 and N.get(seed,'NmiDisable')==255
                        plain,cp=clone(self);m,c=clone(self);before=regs(c)
                        minimum=min(minimum,Async.inject(c,base,kind));assert regs(c)==before
                        finish(plain,cp);finish(m,c);assert regs(cp)==regs(c)
                        assert plain.rawtags==m.rawtags and plain.chr_latches==m.chr_latches
                        assert[bytes(v)for v in plain.ram]==[bytes(v)for v in m.ram]
                        assert bytes(plain[0x15a:0x17b])==bytes(m[0x15a:0x17b])
                        assert bytes(plain[0x101+cp.sp:0x200])==bytes(m[0x101+c.sp:0x200])
                        skip=W.address(seed.bundle,'NmiSkipped')
                        for at in list(range(0x100))+list(range(0x200,0x800)):
                            want=(plain[at]+1)&255 if kind=='lagNMI'and at==skip else plain[at]
                            assert m[at]==want,(kind,hex(at),m[at],want)
                        counts[kind]+=1
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,Main_return=pendingMain))
            return super().step()
    with patch.object(N,'NesMPU',CPU):Frames.frame(seed,whole_pass=True)
    assert seen=={0xaf76,0xafe2}and counts==dict(IRQ=2,lagNMI=2)
    return dict(cuts=cuts,counts=dict(counts),minimum_SP=minimum,complete_public_continuation_exact=True,
        native_exception='Only actual busyNMI skipped increment; preserve full meaningful registers/live stack/SMC/maps/private',
        declared_action11_component_not_natural_acquisition=True)


def run(raw):
    proof=J.C.proposal(J.C.inverse(raw))[1];rows=foreign(raw);interrupts=irq(raw)
    out=dict(passed=True,owning_SHA256=J.PIN,input=dict(J.INPUT),composition=proof,
        foreign=rows,focused_IRQ=interrupts,old255_510_matrices_transferred_not_repeated=True,outputs=0,native=False)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Combined foreign/IRQ source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
