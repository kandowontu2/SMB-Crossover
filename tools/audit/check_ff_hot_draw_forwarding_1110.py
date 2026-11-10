"""Lossless hot-draw classification funding and same-public-FF forwarding.

Memory-only proposal. Frozen earlier images/checkers stay unchanged.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
from py65.disassembler import Disassembler

import check_ff_mux_unused_tail_1110 as Tail

L,W,N,Fix=Tail.L,Tail.W,Tail.N,Tail.Fix
R=W.R
SOURCE=R/'tools/reference/ff_hot_draw_forwarding_1110.s'
PARENT_PIN='a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
COUNTS=Counter();SEAMS=set()


def cfg(data,start,roots):
    memory=[0]*65536;memory[start:start+len(data)]=data
    c=N.NesMPU(memory=memory);d=Disassembler(c);todo=list(roots);seen={}
    while todo:
        pc=todo.pop()
        if not start<=pc<start+len(data) or pc in seen:continue
        size,text=d.instruction_at(pc);seen[pc]=(size,text);op=memory[pc]
        assert op,('unexpected reachable BRK',hex(pc))
        if op in (0x60,0x40):continue
        if op==0x4c:
            todo.append(memory[pc+1]+256*memory[pc+2]);continue
        assert op!=0x6c,('indirect branch',hex(pc))
        todo.append(pc+size)
        if c.disassemble[op][1]=='rel':
            delta=memory[pc+1];todo.append(pc+size+(delta if delta<128 else delta-256))
    return seen


def proposal(raw):
    image,kernel,cookie,*_=Tail.proposal(raw)
    assert sha256(image).hexdigest()==PARENT_PIN
    b=W.Symbols.bundle();start=W.address(b,'HotNewCharacterDraw');end=W.address(b,'ThSharedDrawHot')
    offset=W.location(b,'HotNewCharacterDraw');size=end-start
    assert (start,end,size)==(0xb4a4,0xb51a,118)
    data=image[offset:offset+size];seen=cfg(data,start,(start,))
    loads=[]
    for pc,(length,text) in sorted(seen.items()):
        if data[pc-start]==0xbd:
            target=int.from_bytes(data[pc-start+1:pc-start+3],'little')
            if start<=target<end:loads.append((pc,target))
    assert len(loads)==3,loads
    bases=[target for _,target in loads]
    assert bases==list(range(bases[0],bases[0]+27,9)) and bases[-1]+9==end
    tables=[data[at-start:at-start+9] for at in bases]
    assert all(z[1]==z[2] for z in tables),'Only identical legacy rows1/2 may be folded'
    expected=['RlDraw','CdNewDrawDispatch','CdNewDrawDispatch','LmDrawGate','JnDrawDispatch',
              'M3NewDrawDispatch','VvDrawDispatch','TnDraw','NrDraw']
    original_targets=[]
    for i,name in enumerate(expected):
        target=(tables[2][i],tables[0][i]+256*tables[1][i])
        assert target==(((W.location(b,name)-16)//8192)|128,W.address(b,name)),(name,target)
        original_targets.append(target)
    selected=W.address(b,'SelectedCharacter');bass_pattern=b'\xad'+selected.to_bytes(2,'little')+b'\xc9'
    bass=data[data.index(bass_pattern)+len(bass_pattern)]
    definitions={n:W.address(b,n) for n in ('SelectedCharacter','RlVariant','FmAlts',
        'FarcallJmpTarget_SMC','NextBank_SMC','SafecallA_SMC','FarCallCommon')}
    definitions['CharacterBass']=bass
    definitions.update(FfRowLo=(W.address(b,'FwServiceVeneers')+6)&255,FfRowHi=(W.address(b,'FwServiceVeneers')+6)>>8)
    for prefix,values in zip(('Lo','Hi','Bank'),tables):
        definitions.update({prefix+str(i):value for i,value in enumerate(values)})
    preamble='\n'.join(f'{n}=${v:04x}' for n,v in definitions.items())
    program=Fix.V1.Asm.assemble(preamble+'\n'+SOURCE.read_text(),{'HOT':(start,size)})
    code=program['images']['HOT'];assert len(code)<=size
    out=bytearray(image);out[offset:offset+size]=code.ljust(size,b'\xff')
    assert out[offset+size:offset+226]==image[offset+size:offset+226]
    return bytes(out),dict(entry=start,private_end=end,physical_bank=(offset-16)//8192,
        old_bytes=size,new_bytes=len(code),retained_public_leaf=end,
        original_targets=original_targets,FF_target=(190,W.address(b,'FwServiceVeneers')+6),
        source_declared_body_bytes=226,changed_span_file=[offset,offset+size],
        old_SHA256=sha256(data).hexdigest(),new_SHA256=sha256(out[offset:offset+size]).hexdigest()),program,image,kernel,cookie


def frontend_matrix(parent,image,record):
    b=W.Symbols.bundle();at=record['entry'];offset=record['changed_span_file'][0]
    memories=[[0]*65536 for _ in range(2)]
    for m,raw in zip(memories,(parent,image)):m[at:at+118]=raw[offset:offset+118]
    fields={n:W.address(b,n) for n in ('SelectedCharacter','RlVariant','FmAlts')}
    target=W.address(b,'FarcallJmpTarget_SMC');bank=W.address(b,'NextBank_SMC')+1
    stop=W.address(b,'FarCallCommon')+3;costs=Counter();cases=0
    def check(owner,alt,roll,a,p):
        nonlocal cases
        outputs=[];cycles=[]
        for m in memories:
            for name,value in (('SelectedCharacter',owner),('RlVariant',roll),('FmAlts',alt)):m[fields[name]]=value
            c=N.NesMPU(memory=m,pc=at);c.a,c.x,c.y,c.p,c.sp=a,71,37,p,224
            for _ in range(100):
                if c.pc==stop:break
                assert m[c.pc];c.step()
            else:raise AssertionError(('frontend instruction bound',owner,alt,roll,hex(c.pc)))
            assert (c.a,c.x,c.y,c.p,c.sp)==(a,71,37,p|0x30,224)
            outputs.append((m[bank],m[target+1]+256*m[target+2]))
            cycles.append(c.processorCycles)
        expected=tuple(record['FF_target']) if owner==22 else outputs[0]
        assert outputs[1]==expected,('owner routing difference',owner,alt,roll,a,p,outputs,expected)
        costs[('FF' if owner==22 else 'foreign',cycles[0]-cycles[1])]+=1;cases+=1
    for owner in range(256):
        for alt in range(256):
            for roll in (0,1):check(owner,alt,roll,83,0x31)
        if owner%64==63:print(json.dumps(dict(event='frontend_owner_alt_progress',owners=owner+1,cases=cases)),flush=True)
    COUNTS['all256_owners_all256_FmAlts_both_Roll_states_frontend']+=cases
    prior=cases
    for owner in range(256):
        for p in range(256):check(owner,(owner*73)&255,owner&1,83,p)
    COUNTS['all256_owners_all256_input_flags_frontend']+=cases-prior;prior=cases
    for owner in range(256):
        for a in range(256):check(owner,(owner*17)&255,owner&1,a,0xf5)
    COUNTS['all256_owners_all256_original_A_frontend']+=cases-prior
    assert cases==262144
    print(json.dumps(dict(event='frontend_matrix_pass',cases=cases,
        cycle_deltas=[dict(kind=k,saved=v,cases=n) for (k,v),n in sorted(costs.items())])),flush=True)


def bind(seed,image):
    m=L.clone(seed);m.bundle=dict(m.bundle,raw=image)
    for i,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(i,tag)
    return m


def application(m,c):
    return (Tail.signature(m,c),bytes(m.ram[3]))


def callbacks(seed,parent,image):
    for variant in range(4):
        for power in range(3):
            for outlines in (0,1):
                for facing in (1,2):
                    for flags in (0x31,0xf5):
                        outputs=[]
                        for raw in (parent,image):
                            m=bind(seed,raw);N.put(m,FfVariant=variant,FfPower=power,FfEarned=power,
                                PlayerOutlinesOff=outlines,PlayerFacingDir=facing,NmiDisable=255)
                            c=L.call(m,'HotNewCharacterDraw',a=83,x=0,y=0,p=flags)
                            outputs.append(application(m,c))
                        assert outputs[0]==outputs[1],('FF complete draw callback',variant,power,outlines,facing,flags)
                        COUNTS['four_role_three_tier_outline_facing_two_flag_draw_callbacks']+=1
    for field in ('GameEngineSubroutine','GamePauseStatus'):
        for value in range(256):
            outputs=[]
            for raw in (parent,image):
                m=bind(seed,raw);N.put(m,NmiDisable=255,**{field:value})
                c=L.call(m,'HotNewCharacterDraw',a=83,x=0,y=0,p=0xf1)
                outputs.append(application(m,c))
            assert outputs[0]==outputs[1],('draw callback mode difference',field,value)
            COUNTS[f'all256_{field}_whole_draw_callbacks']+=1
    for byte in range(16):
        for bit in range(8):
            outputs=[]
            for raw in (parent,image):
                m=bind(seed,raw);m.ram[3][0x1fe0+byte]^=1<<bit;N.put(m,NmiDisable=255)
                entered=[]
                def watch(q,c):
                    if c.pc>=0x8000 and q.rawtags[(c.pc-0x8000)//8192]==3:entered.append(c.pc)
                c=L.call(m,'HotNewCharacterDraw',a=83,x=0,y=0,p=0xf1,observe=watch)
                assert not entered and not c.p&1
                outputs.append(application(m,c))
            assert outputs[0]==outputs[1],('same public full-cookie rejection differs',byte,bit)
            COUNTS['all16_header_bytes_all8_bit_faults_reject_full_draw']+=1
    print(json.dumps(dict(event='FF_whole_callbacks_pass',cases=dict(COUNTS))),flush=True)


def lifecycle(seed,parent,image):
    for variant in range(4):
        for scenario in ('ready','new_life','life_award','new_area','new_world','unready'):
            outputs=[]
            for raw in (parent,image):
                m=bind(seed,raw);N.put(m,FfVariant=variant,FfPower=2,FfEarned=2,
                    FfHealCharges=3 if variant==1 else 0,Player_State=0)
                if scenario=='new_life':N.put(m,NumberofLives=1)
                elif scenario=='life_award':N.put(m,NumberofLives=3)
                elif scenario=='new_area':N.put(m,AreaAddrsLOffset=1)
                elif scenario=='new_world':N.put(m,WorldNumber=1)
                elif scenario=='unready':N.put(m,FfReady=0)
                m.controller_pad=0;c=Tail.frame(m);outputs.append(application(m,c))
            assert outputs[0]==outputs[1],('four-role lifecycle Main difference',variant,scenario)
            COUNTS['four_role_six_scenarios_whole_Main_lifecycle_pairs']+=1
    print(json.dumps(dict(event='lifecycle_Main_pass',cases=dict(COUNTS))),flush=True)


def seam(m,c,stop,key):
    if c.pc>=0x8000 and m.rawtags[(c.pc-0x8000)//8192]==194 and c.pc in SEAMS:
        token=(c.pc,key,c.p&4)
        if token not in L.SAMPLE_KEYS:
            L.SAMPLE_KEYS.add(token);q,d=L.clone(m,c)
            L.SAMPLES.append(('hot_draw_frontend',stop,q,d))


def vectors(seed,parent,image,record,program):
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    code=program['images']['HOT'];seen=cfg(code,record['entry'],(record['entry'],));SEAMS.update(seen)
    stop=W.address(seed.bundle,'FarCallCommon')+3
    for owner,alt,roll in ((0,0,0),(9,0,0),(9,0,1),(10,0,0),(10,64,0),(14,0,0),(15,0,0),(19,0,0),(20,0,0),(22,0,0),(255,255,1)):
        for flags in (0x31,0x35):
            m=bind(seed,image);N.put(m,SelectedCharacter=owner,FmAlts=alt,RlVariant=roll,NmiDisable=255)
            c=L.start(m,'HotNewCharacterDraw',p=flags)
            for _ in range(100):
                if c.pc==record['entry'] and m.rawtags[1]==194:break
                assert m[c.pc];c.step()
            else:raise AssertionError('real frontend entry transport bound')
            # The actual FarCallCommon prologue owns four stack bytes before
            # the frontend. Stop at its same tail before any foreign worker.
            goal=(stop,c.sp)
            L.finish(m,c,goal,lambda q,d:seam(q,d,goal,'unit'))
    reached={c.pc for _,_,_,c in L.SAMPLES}
    assert reached==SEAMS,('new frontend seams missing',sorted(SEAMS-reached))
    m=bind(seed,image);m.controller_pad=0;idle=W.address(m.bundle,'IdleLoop')
    W.clear_logs(m);N.consume(m);c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    L.finish(m,c,(idle+12,252),lambda q,d:seam(q,d,(idle+12,252),'genuine_Main'))
    q,d=L.clone(m,c);L.SAMPLES.append(('genuine_idle_normal_NMI',(d.pc,d.sp),q,d))
    return L.irq_checks(parent)


def main():
    image,record,program,parent,kernel,cookie=proposal(W.ROM.read_bytes())
    with patch.object(L,'sample',lambda *a,**k:None):
        old,oldcold,_=L.cold_menu(parent,0,cookie,kernel)
        new,newcold,_=L.cold_menu(image,0,cookie,kernel)
    savings=[]
    for phase,pad in (('idle',0),('walking',1)):
        for update in range(16):
            cpus=[]
            for m in (old,new):
                m.controller_pad=pad;cpus.append(Tail.frame(m))
                assert not any(N.get(m,'Enemy_Flag',i) for i in range(6))
            assert Tail.signature(old,cpus[0])==Tail.signature(new,cpus[1]),('real Main difference',phase,update,
                L.regs(cpus[0]),L.regs(cpus[1]))
            savings.append(cpus[0].processorCycles-cpus[1].processorCycles)
    print(json.dumps(dict(event='real_Main_pass',Main_pairs=32,saved=savings,new_Main=cpus[1].processorCycles)),flush=True)
    frontend_matrix(parent,image,record)
    callbacks(new,parent,image)
    lifecycle(new,parent,image)
    irq=vectors(new,parent,image,record,program)
    print(json.dumps(dict(passed=True,source_CPU_only=True,ROM_written=False,output_files=0,
        parent_SHA256=sha256(parent).hexdigest(),proposal_SHA256=sha256(image).hexdigest(),funding=record,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),kernel_unchanged=True,cookie_unchanged=True,
        cold=[oldcold,newcold],saved_mean=sum(savings)/len(savings),cases=dict(COUNTS),
        all_frontend_instruction_seams=len(SEAMS),real_vectors=irq,
        scope='Same118B private frontend inside declared226B HotNewCharacterDraw. All-owner/all-alt/all-flags/all-A frontend endpoint contracts, whole FF callbacks, lifecycle and real vectors are CPU-qualified. Same public full-cookie FF veneer2; all public entries/leaves and live Mini/Giant/Karnov tails unchanged. Fullstage/physical cadence unqualified; overwhelming lag remains.')),flush=True)


if __name__=='__main__':main()
