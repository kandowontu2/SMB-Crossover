"""Check live audio handoffs and prove copied decoder scratch stays private."""

from collections import Counter
import json
from pathlib import Path

import check_native_audio_frame_token_1110_v1 as T
from check_mini_funded_actor_1108_v3 import install, slim_fork

F,M,N,R,OUT = T.F,T.M,T.N,T.R,T.OUT
SHADOWS = ((0x6a8a,0x6a98),(0x6bea,0x6bf6),(0x71dd,0x71ef))
ZP = range(0xde,0xec)
HISTORY = range(0x7400,0x7c00)


def shadow(at):
    return any(lo<=at<hi for lo,hi in SHADOWS)


class Bus(N.Bus):
    audit = False

    def __getitem__(self,at):
        v = super().__getitem__(at)
        if self.audit and isinstance(at,int) and (at in ZP or shadow(at) or at in HISTORY and self.tag!=38):
            self.access.append(('R',self.tag,self.pc,at,v,self.x,self.y))
        return v

    def __setitem__(self,at,v):
        if self.audit and isinstance(at,int) and (at in ZP or shadow(at) or at in HISTORY and self.tag!=38):
            self.access.append(('W',self.tag,self.pc,at,v,self.x,self.y))
        super().__setitem__(at,v)


class Trace(N.NesMPU):
    def step(self):
        m = self.memory
        m.pc,m.x,m.y = self.pc,self.x,self.y
        m.tag = m.rawtags[(m.pc-0x8000)//8192]&127 if m.pc>=0x8000 else -1
        if m.tag==38 and m.pc in (0xc949,0xcaea) and self.a in (166,185):
            assert bytes(m[m.pc:m.pc+3])==b'\x8d\x15\x51'
            m.packed_map_sites.append(len(m.writes))
        return super().step()


def load_store(raw,read,write):
    # Source copies are actual adjoining LDA/STA instructions, with the
    # original absolute or indexed effective addresses checked independently.
    operands = [({0xa5:'zp',0xb5:'zpx',0xad:'abs',0xbd:'absx',0xb9:'absy'},read),
                ({0x85:'zp',0x95:'zpx',0x8d:'abs',0x9d:'absx',0x99:'absy'},write)]
    end = []
    for ops,(_,bank,pc,at,_,x,y) in operands:
        pos = F.offset(bank,pc)
        op = ops[raw[pos]]
        n = 2 if op.startswith('zp') else 3
        value = int.from_bytes(raw[pos+1:pos+n],'little')
        idx = x if op.endswith('x') else y if op.endswith('y') else 0
        assert (value+idx)&(255 if n==2 else 65535)==at,(hex(pc),op,value,at,idx)
        end.append(pc+n)
    assert read[1]==write[1] and end[0]==write[2] and read[4]==write[4],(read,write)


def observe_transfers(pair,proven,counts,sites):
    raw = pair[0].bundle['raw']
    # New decoder has a different private instruction trace. Compare the
    # full traces at all actual external history borrowers and ZP shims.
    traces = [[q for q in m.access if q[1]!=38] for m in pair]
    assert len(traces[0])==len(traces[1]),(len(traces[0]),len(traces[1]))
    for i,(a,b) in enumerate(zip(*traces)):
        rw,bank,pc,at,v,*_ = a
        assert a[:4]==b[:4] and a[5:]==b[5:],(a,b)
        if at in HISTORY:
            assert a==b,('Native driver observes borrowed LZ history',a,b)
            counts['identical_native_history_'+rw] += 1
        if v==b[4] or not shadow(at):
            continue
        if rw=='W':
            assert i>0
            source = [t[i-1] for t in traces]
            assert source[0][3]==source[1][3] and source[0][3] in ZP
            assert all(q[0]=='R' for q in source)
            load_store(raw,source[0],a)
            load_store(raw,source[1],b)
            proven[at] = source[0][3],(a[4],b[4])
        else:
            dest = [t[i+1] for t in traces]
            assert at in proven and proven[at]==(dest[0][3],(a[4],b[4]))
            assert dest[0][3]==dest[1][3] and all(q[0]=='W' for q in dest)
            load_store(raw,a,dest[0])
            load_store(raw,b,dest[1])
        sites.add((rw,bank,pc,at,proven[at][0]))
        counts['exact_derived_shadow_'+rw] += 1


def same_end(pair,proven,packed):
    # The proved staging copies can remain in dead save slots after restore.
    # Compare the entire real end-state after projecting those exact values.
    a,b = pair
    undo = []
    try:
        for lo,hi in SHADOWS:
            for at in range(lo,hi):
                aa,bb = (list.__getitem__(m,at) for m in pair)
                if aa!=bb:
                    assert at in proven and proven[at][1]==(aa,bb),(hex(at),aa,bb)
                    undo.append((at,bb))
                    list.__setitem__(b,at,aa)
        T.external_state(a,b,packed)
    finally:
        for at,value in undo:
            list.__setitem__(b,at,value)


def qualify(before,after,proof):
    original_bus = N.Bus
    N.Bus = Bus
    try:
        warmed = [M.seed(M.bundle(raw),41) for raw in (before,after)]
    finally:
        N.Bus = original_bus
    counts,sites,history_users = Counter(),set(),Counter()
    for t in range(401):
        T.frame_pair(warmed,dict(AreaMusicQueue=int(t==0),FrameCounter=t&255))
    for who in range(41):
        pair = [slim_fork(m) for m in warmed]
        proven = {}
        prior_history = counts['identical_native_history_R']
        for t in range(138):
            for m in pair:
                m.audit,m.access = True,[]
            fields = dict(SelectedCharacter=who if t<8 else 41,
                          AreaMusicQueue=4 if t==4 else int(t in (0,8)),
                          EventMusicQueue=64 if t==6 else 0,FrameCounter=t&255)
            try:
                T.frame_pair(pair,fields,Trace)
                observe_transfers(pair,proven,counts,sites)
                same_end(pair,proven,packed=t>=137)
            except AssertionError as err:
                raise AssertionError(('owner round trip',who,t,*err.args)) from err
            finally:
                for m in pair:
                    m.audit = False
            counts['whole_AudioUpdate'] += 1
            if t==7:
                history_users[who] = counts['identical_native_history_R']-prior_history
    assert counts['whole_AudioUpdate']==41*138 and counts['exact_derived_shadow_R']>0
    return dict(counts=counts,round_trips=41,known_history_borrower_reads={k:v for k,v in history_users.items() if v},
                exact_shadow_copy_restore_sites=sorted(sites),projected_shadow_half_open=SHADOWS,
                scope='AudioUpdate leaves packed Mini music for each raw owner 0..40, then reinitializes Mini through its original intro and into the first packed frame. Source-tied shadow copies and known LZ-history borrowers are checked on each actual read/write.')


def main():
    rt = OUT/'runtime-proof.json'
    vr = OUT/'vectors.json'
    proof = json.loads(rt.read_text())
    before = F.BASE.read_bytes()
    assert M.sha(before)==F.PIN==proof['parent_SHA256']
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = qualify(before,after,proof)
    q = result|dict(passed=True,parent_SHA256=F.PIN,expected_memory_only_SHA256=M.sha(after),
        bindings={f.relative_to(R).as_posix():M.sha(f.read_bytes()) for f in
                  (rt,vr,Path(__file__),R/'src/expanded_audio.s',R/'src/megaman_audio.s',
                   R/'src/samus_audio.s',R/'src/roster_audio.s',R/'src/gradius_audio.s',
                   R/'src/cv3_dmc_complete.s',R/'src/cv3_source_audio.s',R/'src/mac_native_music.s',
                   R/'src/mike_native_music.s',R/'src/dragon_power_audio.s')})
    (OUT/'lifecycle.json').write_text(json.dumps(q,indent=2)+'\n')
    print({key:val for key,val in result.items() if key!='exact_shadow_copy_restore_sites'},flush=True)


if __name__=='__main__':
    main()
