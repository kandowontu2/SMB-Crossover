"""Bounded full native/foreign checks of the granted direct-fast successor."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
from itertools import product
import io
import json
from unittest.mock import patch

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_descending_platform_1113 as D

Q,P,H,N,W,L,C=D.Q,D.P,D.H,D.N,D.W,D.L,D.C


def entry(raw):
    at=16+0x143f
    assert raw[at]==0x20
    value=int.from_bytes(raw[at+1:at+3],'little')
    assert value in(0xb98e,T.Old.ENTRY,T.ENTRY)
    return value


def unsampled(seed,parent,candidate):
    cases=0;native_writes=0;extra_same_value_restores=0
    bases={}
    for slot,kind,speed,footer,high,timer in product((0,3,5),(36,37,40),(0,255),range(256),(0,1,2),(0,1)):
        if kind!=36 and speed!=255:continue
        C.SLOT=slot
        if slot not in bases:bases[slot]=C.setup(seed)
        base=L.clone(bases[slot]);base[0x65b]=footer
        C.field(base,'Enemy_ID',kind);C.field(base,'Enemy_Y_Speed',speed)
        N.put(base,Player_Y_HighPos=high,TimerControl=timer,ObjectOffset=slot)
        pair=[]
        for raw in(parent,candidate):
            m=Q.mounted(base,raw);events=[];in_lpc=False
            Base=type(m)
            class Bus(Base):
                def __setitem__(self,at,value):
                    if at==0x65b and self.track_footer:events.append((self.footer_pc,value&255,self.in_actual_lpc))
                    return super().__setitem__(at,value)
            m.__class__=Bus;m.track_footer=False;m.in_actual_lpc=False
            # Actual native LPC has a same-bank caller on old14 and an inner
            # FarCallCommon caller on the new worker. Observe both real exits.
            stop=None
            def watch(cpu):
                nonlocal stop
                m.track_footer=True;m.footer_pc=cpu.pc
                if cpu.pc==0xb453 and m.rawtags[1]==128:
                    assert stop is None
                    stop=(m[0x100+((cpu.sp+1)&255)]+256*m[0x100+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255)
                    m.in_actual_lpc=True
                elif stop==(cpu.pc,cpu.sp):m.in_actual_lpc=False
            r=Q.direct(m,entry(raw),x=slot,observe=watch);m.track_footer=False
            pair.append((bytes(m[:0x100]),bytes(m[0x200:0x800]),tuple(bytes(b)for b in m.ram),
                tuple(m.rawtags),r['X'],r['Y'],r['SP']))
            native_writes+=sum(inside for pc,value,inside in events)
            if raw==candidate:
                assert all(value==footer for pc,value,inside in events if not inside),('Unsampled restore clobbered native footer',slot,kind,speed,footer,high,timer,events)
                extra_same_value_restores+=sum(not inside for pc,value,inside in events)
        assert pair[0]==pair[1],('Unsampled native contract',slot,kind,speed,footer,high,timer)
        cases+=1
    return dict(cases=cases,all256_footer_three_slots_and_player_highs=True,
        actual_native_footer_writes=native_writes,extra_same_value_footer_restores=extra_same_value_restores,
        actual_original_native_fields_and_all_WRAM_maps_XYSP_exact=True,
        scope='ID24 and every tested upward ID25/28 clipping/timer path. No invented callback writer or native field repair.')


def full(seed,candidate):
    m=Q.mounted(seed,candidate);text=T.controller(candidate,full=True,departure_enemy_guard=True)
    with redirect_stdout(io.StringIO()):
        result=P.B.route(m,candidate,12000,controller_text=text)
    receipt=result.get('receipt')or{}
    row=dict(passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
        controller_SHA256=sha256(text.encode()).hexdigest(),reason=receipt.get('reason'),
        receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        crossings=receipt.get('crossings'),last_events=receipt.get('events',[])[-16:],
        birth_lefts=sorted(receipt.get('births',{})),native_gap=receipt.get('gap'),outputs_written=0)
    assert result['passed'],row
    return row


def caller(seed,candidate):
    from unittest.mock import patch
    count=0
    for slot,timer in product((0,3,5),(0,1)):
        C.SLOT=slot;base=C.setup(Q.mounted(seed,candidate))
        N.put(base,TimerControl=timer,ObjectOffset=slot)
        def run(id_flags,taint=None):
            m=L.clone(base);CPU=N.NesMPU;hits=0
            class Probe(CPU):
                def step(self):
                    nonlocal hits
                    if self.pc==0xb442 and self.memory.rawtags[1]==128:
                        hits+=1
                        if taint is not None:
                            self.a=taint[0];self.p=(self.p&~0xc3)|taint[1]
                    return CPU.step(self)
            with patch.object(N,'NesMPU',Probe):
                r=N.invoke(m,'RunLargePlatform',a=85,x=slot,y=91,p=0x31|id_flags)
            assert hits==1 and r['P']&12==id_flags
            return (bytes(m[:0x100]),bytes(m[0x15a:0x17b]),bytes(m[0x1e0:0x800]),
                tuple(bytes(b)for b in m.ram),tuple(m.rawtags),bytes(m[0x5c00:0x8000]),
                bytes(m.vram),tuple(m.chr_latches),tuple(r[k]for k in('A','X','Y','P')))
        for id_flags in(0,4,8,12):
            original=run(id_flags)
            for a,flags in product((0,1,40,255),range(16)):
                p=(flags&3)|((flags&4)<<4)|((flags&8)<<4)
                assert run(id_flags,(a,p))==original,(slot,timer,id_flags,a,p)
                count+=1
    return dict(actual_RunLargePlatform_return_PC=0xb442,A_NZCV_taints=count,
        all_four_incoming_I_D_pairs_preserved=True,
        full_return_AXYP_native_WRAM_SRAM_SMC_maps_graphics_equal=True,
        excluded='Only dead hardware stack0100..0159 and017B..01DF; all SMC and live caller stack compared.')


def nested_cost(seed,parent,candidate):
    C.SLOT=3;base=C.setup(seed);rows=[]
    for kind,speed,timer,gap in product((36,37,40),(0,1,255),(0,1),(1,-1)):
        pair=[]
        for raw in(parent,candidate):
            m=Q.mounted(base,raw);N.put(m,SelectedCharacter=40,TimerControl=timer,ObjectOffset=3)
            C.field(m,'Enemy_ID',kind);C.field(m,'Enemy_State',0);C.field(m,'Enemy_Y_Speed',speed)
            m[0x65b]=136;C.field(m,'Enemy_Y_Position',136+gap)
            N.invoke(m,'GetEnemyOffscreenBits',x=3);N.invoke(m,'RelativeEnemyPosition',x=3)
            N.invoke(m,'LargePlatformBoundBox',x=3)
            calls=[]
            def watch(c):
                if c.pc==0x15a:calls.append(c.a)
            r=Q.direct(m,entry(raw),x=3,observe=watch)
            pair.append((r,calls))
        a,b=pair
        rows.append(dict(ID=kind,speed=speed,timer=timer,footer_gap=gap,
            current14_cycles=a[0]['CPU'],candidate_cycles=b[0]['CPU'],additional_cycles=b[0]['CPU']-a[0]['CPU'],
            current14_Far_banks=a[1],candidate_Far_banks=b[1],
            current14_min_SP=a[0]['minimum_SP'],candidate_min_SP=b[0]['minimum_SP']))
    return dict(rows=rows,scope='Explicit eligible, deep, upward, balance and timer native calls; source fixtures, not physical cadence.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in('structure','incoming','components','native-ids','foreign','cost','nested-cost','unsampled','caller','first','full'):
        ap.add_argument('--'+name,action='store_true')
    a=ap.parse_args();Q.T=T;D.T=T;Q.entry=entry
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent)
    assert T.reverse(candidate)==parent and T.transform(parent)[0]==candidate
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    if a.structure:
        print('DKJR_DIRECT_STRUCTURE '+json.dumps(dict(T.transform(parent)[1],
            caller=D.caller_domain(e73)),separators=(',',':')),flush=True)
    for name,on,fn in(
        ('INCOMING',a.incoming,lambda:Q.incoming(Q.mounted(seed,candidate))),
        ('COMPONENTS',a.components,lambda:D.components(seed,candidate)),
        ('NATIVE_IDS',a.native_ids,lambda:D.native_ids(seed,e73,candidate)),
        ('UNSAMPLED',a.unsampled,lambda:unsampled(seed,parent,candidate)),
        ('CALLER',a.caller,lambda:caller(seed,candidate)),
        ('FOREIGN',a.foreign,lambda:Q.foreign(e73,candidate)),
        ('COST',a.cost,lambda:dict(versus_e73=Q.cost(seed,e73,candidate),versus_14ae=Q.cost(seed,parent,candidate))),
        ('NESTED_COST',a.nested_cost,lambda:nested_cost(seed,parent,candidate)),
        ('FIRST',a.first,lambda:Q.route(seed,candidate)),
        ('FULL',a.full,lambda:full(seed,candidate))):
        if on:print('DKJR_DIRECT_'+name+' '+json.dumps(fn(),separators=(',',':')),flush=True)
    print('DKJR_DIRECT_SCOPE '+json.dumps(dict(candidate_SHA256=T.PIN,outputs_written=0,
        physical_cadence_claim=False,native_ready=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
