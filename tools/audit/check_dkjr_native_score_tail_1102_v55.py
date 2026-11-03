"""Original phase/native Main boundary parity for the local score tail."""
import collections, itertools, json
from pathlib import Path
import check_dkjr_native_service_ff_1102_v51 as C
A, R, O, W, N = C.A, C.R, C.O, C.W, C.N


def fixture(successor=True):
    b, m, L, q = C.fixture()
    if successor:
        q = json.loads((O/'native-scoretail-v54-layout.json').read_text())
        L = q['labels']
        m.ram[3][:0x1fe0] = [255]*0x1fe0
        part = (O/'native-scoretail-v54.bin').read_bytes()
        m.ram[3][:len(part)] = part
        for kind, at in [('pause',0x1540), ('main',0x165e), ('ports',0x16a7)]:
            part = (O/f'native-scoretail-{kind}-v54.bin').read_bytes()
            m.ram[2][at:at+len(part)] = part
    return b, m, L, q


def direct(m, pc, a=85, x=0, y=91, p=0x31):
    c = N.NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 224
    c.stPushWord(0x5ffe)
    for _ in range(100000):
        if c.pc == 0x5fff:
            break
        assert m[c.pc] != 0, ('score tail BRK', hex(c.pc), c.sp)
        c.step()
    else:
        raise AssertionError('score tail direct bound')
    assert c.sp == 224
    return c.a, c.x, c.y, c.p & 0xef, c.sp


def compare(m, z, label):
    # Private native packets hold service-entry snapshots at different points
    # of the same Main. They are adapter data, not original donor actor state.
    diff = [(i,a,b) for i,(a,b) in enumerate(zip(m.ram[2][:0x900],z.ram[2][:0x900]))
            if a != b and not 0x460 <= i < 0x4bb and i != 0x8f9]
    assert not diff, (label, 'source/private state', diff[:12])
    aa, bb = list.__getitem__(m,slice(0,32768)), list.__getitem__(z,slice(0,32768))
    diff = [(i,a,b) for i,(a,b) in enumerate(zip(aa,bb)) if a != b
            and not 0x100 <= i < 0x1e0 and not 0x2000 <= i < 0x5c00]
    assert not diff, (label, 'native boundary', diff[:16])
    assert m.rawtags == z.rawtags, (label, 'maps')


def main():
    old, seed, beforeL, _ = fixture(False)
    b, after, L, q = fixture(True)
    points = 0
    for player, kind, flags, offset in itertools.product([0,1], range(9), [0x30,0x31,0x71,0xf1], [0,11]):
        m, z = N.fork(seed), N.fork(after)
        for bus in [m,z]:
            N.put(bus,CurrentPlayer=player,VRAM_Buffer1_Offset=offset,ObjectOffset=3)
            bus.ram[2][0x8f9] = 0
        a = direct(m,beforeL['DkjrNativeAwardSourcePoints'],x=kind,p=flags)
        c = direct(z,L['DkjrNativeAwardSourcePoints'],x=kind,p=flags)
        assert a == c
        # The original source publication has no native side effects until
        # this within-Main flush. Its immediate AXYP and popup choice match.
        c = direct(z,L['DkScoreFlush'],a=c[0],x=c[1],y=c[2],p=c[3])
        assert a == c and z.ram[2][0x8f9] == 0
        compare(m,z,('typed-score',player,kind,flags,offset))
        points += 1
    epochs, minimum, event_max = 0, 255, 0
    cohorts = []
    native = N.NesMPU
    for player, mode in itertools.product([0,1],[0,1]):
        _, m, beforeL, _ = fixture(False)
        _, z, L, _ = fixture(True)
        for bus in [m,z]:
            N.put(bus,CurrentPlayer=player,CrossoverBehaviorVersion=mode)
        source_calls, native_calls, rows = collections.Counter(), collections.Counter(), []
        activeL = None
        class Trace(native):
            def step(self):
                bank=self.memory.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
                if bank==3 and self.pc==activeL['DkjrNativeAwardSourcePoints']:
                    source_calls[role]+=1
                    kinds[role].append(self.x)
                if bank==131 and self.pc==0xb815:
                    native_calls[role]+=1
                return super().step()
        N.NesMPU = Trace
        try:
            for epoch in range(1,63):
                kinds={'old':[],'new':[]}
                outputs=[]
                for role,bus,activeL in [('old',m,beforeL),('new',z,L)]:
                    N.put(bus,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
                    C.timers(bus)
                    outputs.append(N.invoke(bus,'GameCoreRoutine',a=85,x=0,y=0,p=0x31))
                assert [outputs[0][n]for n in ['A','X','Y','P']]==[outputs[1][n]for n in ['A','X','Y','P']],(player,mode,epoch,'publicAXYP')
                compare(m,z,(player,mode,epoch))
                assert kinds['old']==kinds['new'] and len(kinds['new'])<=1
                event_max=max(event_max,len(kinds['new']))
                assert z.ram[2][0x8f9]==0
                minimum=min(minimum,outputs[1]['minimum_SP'])
                if kinds['new']:
                    rows.append(dict(epoch=epoch,original_point_kinds=kinds['new'],pending_consumed_before_Main_return=True))
                epochs+=1
            assert source_calls['old']==source_calls['new']==2 and native_calls['old']==native_calls['new']==2
            assert z.ram[2][0x68]==z.ram[2][0x440]==0 and N.get(z,'NumberofLives')==2
            at=W.address(b,'Player1ScoreDisplay' if player==0 else 'Player2ScoreDisplay')
            score=sum(z[at+i]*10**(6-i)for i in range(6));assert score==1200
            cohorts.append(dict(player=player,mode=mode,epochs=62,score=score,source_publications=rows,actual_native_score_calls=native_calls['new']))
        finally:
            N.NesMPU=native
    # Constructor discards any stale adapter pending amount before a new life.
    _,z,L,_=fixture(True);z.ram[2][0x8f9]=0x16;direct(z,L['DkConstruct']);assert z.ram[2][0x8f9]==0
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        historical_v65_matching_header_fixture=True,exact_point_service_controls=points,
        paired_actual_Main_epochs=epochs,maximum_original_point_publications_per_earned_epoch=event_max,
        minimum_foreground_SP=minimum,cohorts=cohorts,body_bytes=q['body_bytes'],header_spare=q['header_spare'],
        scope='All valid source point kinds plus invalid7/8, both native score owners, four public flag patterns and zero/nonzeroVRAM offsets preserve original source AXYP/native score/HUD bytes exactly after local flush. Four62epoch full actual GameCore/timer comparisons preserve original donor/private state except declared adapter snapshots/pending, all native nondead-stack state/publicAXYP/maps, genuine defeat,400+800score,60D1AE/thaw. Each source publication retains its exact epoch/type; pending consumed before Main returns. Final structural multiplicity/packet lifetime/fullFF/nestedIRQ and latest-owner rebind remain pending.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(C.__file__),O/'native-scoretail-v54.s',O/'native-scoretail-v54.bin',O/'native-scoretail-v54-layout.json',O/'native-registers-v48.bin']})
    (O/'native-scoretail-v55-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','exact_point_service_controls','paired_actual_Main_epochs','minimum_foreground_SP','body_bytes','header_spare']}))


if __name__=='__main__':main()
