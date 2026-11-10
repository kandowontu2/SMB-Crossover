"""Narrow new native-policy lifetime/real-vector cases; stdout only."""
from collections import Counter
import argparse
from hashlib import sha256
import json

import check_wwf_native_powerups_1110 as P

C,W,N,L=P.C,P.W,P.N,P.L


def private_gameplay(mem):
    """Exclude only source-declared native music state and ISR save scratch."""
    q=[bytearray(z) for z in mem.ram]
    scratch=W.address(mem.bundle,'WfAudioScratch')&8191
    saved=W.address(mem.bundle,'WfAudioSavedSmc')&8191
    assert (scratch,saved,W.address(mem.bundle,'WfAudioSavedP')&8191)==(0x1fa7,0x1ff8,0x1ffd)
    q[1][scratch:scratch+10]=bytes(10);q[1][saved:saved+6]=bytes(6)
    # Original driver RAM0500..05BF is relocated to donor-owned C500..C5BF.
    # See port_wwf_audio_source_bounded_v1 and wwf_roster_native_support_v1.
    q[2][0x500:0x5c0]=bytes(0xc0)
    return tuple(bytes(z) for z in q)


def live(mem,cpu):
    return (L.regs(cpu),bytes(mem[3:11]),bytes(mem[0x15a:0x17b]),
            bytes(mem[0x101+cpu.sp:0x200]),L.body(mem),private_gameplay(mem),tuple(mem.rawtags))


def vectors(parent):
    """Actual native ISR counterfactual, with original WWF music allowed to run."""
    rows=Counter();origins=Counter();music=set()
    def interrupt(mem,cpu,kind,stop=None):
        before=live(mem,cpu);result=L.isr(mem,cpu,kind,stop)
        assert live(mem,cpu)==before,('ISR live registers/gameplay/mapper',kind,hex(cpu.pc))
        for bank,offset,value in mem.ram_writes:
            assert (bank==1 and (0x1fa7<=offset<0x1fb1 or 0x1ff8<=offset<0x1ffe)) or (
                bank==2 and 0x500<=offset<0x5c0),('ISR unexpected private write',bank,hex(offset),value)
            music.add((bank,offset))
        return result
    def hardware(mem,cpu):
        return L.app(mem),L.regs(cpu),mem.vram,mem.chr_latches,mem.upper,mem.ppu_addr,mem.toggle,mem.ppuctrl,mem.writes
    def foreground(mem,cpu):
        return L.regs(cpu),L.body(mem),private_gameplay(mem),tuple(mem.rawtags),bytes(mem[0x15a:0x17b])
    for origin,stop,state,cpu in L.SAMPLES:
        origins[origin]+=1
        for kind in ('NMI','IRQ'):
            m,c=L.clone(state,cpu);n,d=L.clone(state,cpu);n.bundle=dict(n.bundle,raw=parent)
            for page,tag in enumerate(n.rawtags):
                if tag&128:n.raw_page(page,tag)
            a=interrupt(m,c,kind,stop);z=interrupt(n,d,kind,stop)
            assert a==z and hardware(m,c)==hardware(n,d),(origin,kind,'exact unchanged-parent ISR')
            if a=='masked':rows['masked_IRQ']+=1;continue
            ref,r=L.clone(state,cpu);L.finish(ref,r,stop);L.finish(m,c,stop)
            assert foreground(m,c)==foreground(ref,r),(origin,kind,'foreground continuation')
            rows[kind+'_real_RTI_and_foreground_resume']+=1
    assert L.DEEPEST is not None
    state,cpu,outer,resume=L.DEEPEST
    m,c=L.clone(state,cpu);n,d=L.clone(state,cpu);n.bundle=dict(n.bundle,raw=parent)
    for page,tag in enumerate(n.rawtags):
        if tag&128:n.raw_page(page,tag)
    assert interrupt(m,c,'IRQ')==interrupt(n,d,'IRQ')=='returned'
    assert hardware(m,c)==hardware(n,d)
    ref,r=L.clone(state,cpu)
    L.finish(m,c,(outer[0],outer[5]));L.finish(ref,r,(outer[0],outer[5]))
    assert L.regs(c)==L.regs(r)==outer
    L.finish(m,c,resume);L.finish(ref,r,resume)
    assert foreground(m,c)==foreground(ref,r)
    rows['nested_IRQ_in_real_CLI_lag_NMI']+=1
    return dict(cases=dict(rows),sample_origins=dict(origins),actual_paired_ISR_paths=dict(L.PATHS),
        original_music_private_bytes_written=len(music),
        preserved='AXYP/SP, live stack, R0..7, SMC, native body/state, all non-audio private RAM and mappings; exact parent hardware/audio writes')


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--vectors-only',action='store_true');args=cli.parse_args()
    parent=P.Images.proposal(P.Images.Ex.proposal(P.Images.Route.A5.proposal(W.ROM.read_bytes())[0])[0])[0]
    image,record=P.proposal(parent);b=W.Symbols.bundle();b['raw']=image
    row=next(r for r in C.Starts.C.inventory(image)['rows'] if r['slot']==28 and r['cycle']==0)
    _,seed=C.cold(b,row);cases=Counter()
    death_states=[]
    if args.vectors_only:
        earned=L.clone(seed);N.put(earned,PlayerStatus=1)
        cases['explicit_directed_IRQ_only_tier_fixture_not_natural']+=1
    else:
        q,earned=P.Route.route(seed,return_arena=True,quiet=True)
        assert q['passed'] and N.get(earned,'PlayerStatus')==1
        m=L.clone(earned);N.invoke(m,'ForceInjury',a=83,x=0,y=0)
        assert (N.get(m,'NumberofLives'),N.get(m,'PlayerStatus'))==(2,0)
        for _ in range(240):m.controller_pad=0;P.Route.Frames.frame(m)
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'InjuryTimer')==0
        N.invoke(m,'ForceInjury',a=83,x=0,y=0)
        assert N.get(m,'GameEngineSubroutine')==11
        for age in range(700):
            m.controller_pad=0;P.Route.Frames.frame(m)
            state=(N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'),N.get(m,'NumberofLives'))
            if not death_states or state!=death_states[-1]:death_states.append(state)
            if state==(3,8,1):break
        else:raise AssertionError(('native respawn bound',death_states))
        assert N.get(m,'PlayerStatus')==0 and N.get(m,'SelectedCharacter')==29 and N.get(m,'FmGroups')&7==0
        cases['naturally_earned_tier_survives_hit_then_unpowered_death_respawn']+=1
    for kind,state in ((0,6),(0,128),(1,128),(2,6),(3,6)):
        t=L.clone(seed);t[W.address(b,'PowerUpType')+5]=kind;t[W.address(b,'Enemy_State')+5]=state
        c=L.call(t,'HuMature',a=83,x=5,y=46,p=0xf1)
        assert bool(c.p&1)==bool(kind>=2 or state&128) and c.x==5 and c.y==46
        cases['native_maturity_representative']+=1
    for status in (0,1,2):
        t=L.clone(seed);N.put(t,PlayerStatus=status)
        c=L.call(t,'HuInjuryStatus',a=83,x=5,y=46,p=0xf1)
        assert c.a==status and c.x==5 and c.y==46
        cases['native_status_reports_earned_armor']+=1
    t=L.clone(earned);N.put(t,GuestPowerupActive=1,GuestPowerupAge=0,GuestPowerupOld=1,
        GuestPowerupDisplay=1,GuestPowerupTarget=2,GameEngineSubroutine=9,TimerControl=255,GamePauseStatus=1)
    P.Route.Frames.frame(t);assert N.get(t,'GuestPowerupAge')==0
    N.put(t,GamePauseStatus=0);P.Route.Frames.frame(t);assert N.get(t,'GuestPowerupAge')==1
    cases['real_Main_pause_then_resume']+=1
    # Compare actual foreign public routes; no selected-owner table shortcut
    # may accidentally alter another owner's native mature/status behavior.
    for name in ('HuMature','HuInjuryStatus','HuPowerup'):
        pair=[]
        for raw in (parent,image):
            t=L.clone(seed);t.bundle=dict(t.bundle,raw=raw)
            for page,tag in enumerate(t.rawtags):
                if tag&128:t.raw_page(page,tag)
            N.put(t,SelectedCharacter=0,PlayerStatus=0)
            c=L.call(t,name,a=83,x=5,y=46,p=0x31);pair.append((L.regs(c),L.app(t)))
        assert pair[0]==pair[1]
        cases['foreign_Mario_public_routes_unchanged']+=1
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    workers={5:('HuInjury','GuestInjuryStart',0),6:('HuInjuryStatus','RemainingPower::EasyPower',0),
        23:('HuMature','NrPickupCollision::Own',2),24:('HuPickup','MarioSourcePowerupCollision',0),
        33:('HuPowerup','GuestPowerupUpdate',0)}
    for row,(public,target,delta) in workers.items():
        t=L.clone(earned);N.put(t,NmiDisable=255)
        if row==24:
            for name,value in (('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',1)):
                t[W.address(b,name)+5]=value
        if row==33:N.put(t,GuestPowerupActive=1,GuestPowerupAge=59,GuestPowerupTarget=2,
            GuestPowerupOld=1,GuestPowerupDisplay=1,GameEngineSubroutine=9,TimerControl=255)
        point=(((W.location(b,target)-16)//8192)|128,W.address(b,target)+delta);seen=[]
        c=L.start(t,public,a=83,x=5,y=46,p=0x31)
        def observe(mem,cpu):
            if cpu.pc>=0x8000 and (mem.rawtags[(cpu.pc-0x8000)//8192],cpu.pc)==point and not seen:
                seen.append(1);s,d=L.clone(mem,cpu);L.SAMPLES.append(('WWF_changed_row'+str(row),(0x5b00,224),s,d))
        L.finish(t,c,(0x5b00,224),observe);assert seen,(row,public,target)
    checked_vectors=vectors(parent)
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,output_files=0,
        proposal_ROM_SHA256=sha256(image).hexdigest(),cases=dict(cases),native_death_transitions=death_states,
        representative_vectors=checked_vectors,
        scope='Earned native armor, directed actual hit/death and ordinary native respawn, few representative maturity/status/pause/foreign routes and one actual worker entry for each changed resolver row. Not natural enemy-hit or full WWF endurance qualification.')),flush=True)


if __name__=='__main__':main()
