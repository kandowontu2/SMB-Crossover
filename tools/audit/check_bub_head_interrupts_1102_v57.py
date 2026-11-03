"""Replay actual IRQ and FF lag-NMI through the new head handoff/bump path."""
import json
from collections import Counter
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
import check_bub_collecting_interrupts_1102_v59 as I
from check_tmnt_render_oa import location
O,Q,N,address,R,sha=H.O,H.Q,H.N,H.address,H.R,H.sha
COUNTS=Counter();AUDIO_WRITERS=Counter();AUDIO_TRANSITIONS=Counter()

def state(m):
    result=list(I.state(m));native=bytearray(result[4])
    # The retained negative proves these two real native SFX clocks advance
    # during the FF audio branch. 07DA was already owned by the root69 oracle.
    for a in[0x7d8,0x7db]:native[a-0x200]=0
    result[4]=bytes(native);return tuple(result)

def audio(m):return tuple(m[a]for a in[0x7d8,0x7da,0x7db])

def audio_sites(b):
    sites={}
    for prefix in['GuestSharedSfx::','SoundEngine::']:
        for suffix,delta,code in [('Fthrow',2,'8dd807'),('DecrementSfx1Length',0,'ced807'),('GrowItemRegs',0,'8dda07'),('GrowItemRegs',10,'8ddb07'),('ContinueGrowItems',0,'eedb07')]:
            name=prefix+suffix;pc=address(b,name)+delta;at=location(b,name)+delta
            assert b['raw'][at:at+3]==bytes.fromhex(code),(name,delta)
            sites[(((at-16)//8192)|128,pc)]=(name,delta,code)
    return sites

def run(m,p,q,interrupt=None):
    b=m.bundle;target=address(b,'GameCoreRoutine')
    m[address(b,'SafecallA_SMC')+1]=85;m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
    c=N.NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=254;c.x=c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff)
    cuts={};low=c.sp;injected=False;active=False;headreturn=None;laghits=regularhits=0;audio_after=None;sites=audio_sites(b)
    newlo=p['labels']['BbHeadBegin'];newhi=p['labels']['BbHeadEnd'];head=address(b,'PlayerHeadCollision');headcalls=0
    for _ in range(100000):
        if c.pc==0x5b00:break
        low=min(low,c.sp);bank=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
        if bank==3 and c.pc==p['labels']['BbHeadCapture']:active=True
        if bank==254 and c.pc==head:
            headcalls+=1;sp=c.sp;headreturn=(m[0x100+sp+1]+256*m[0x100+sp+2]+1,sp+2)
        if headreturn==(c.pc,c.sp):active=False
        cut=(c.pc,c.sp,m.rawtags[1],m.rawtags[2])
        if not c.p&4 and(active or bank==3 and newlo<=c.pc<newhi):
            key=(c.pc,m.rawtags[1],m.rawtags[2])
            if key not in cuts or c.sp<cuts[key][1]:cuts[key]=cut
        if interrupt and not injected and cut==interrupt[1]:
            injected=True;assert not c.p&4
            regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);before=state(m);maps=m.rawtags[:];skipped=N.get(m,'NmiSkipped');audio_before=audio(m)
            lag,regular=I.path(m);lh=rh=0;assert N.get(m,'NmiDisable')==255
            c.irq()if interrupt[0]=='IRQ'else c.nmi()
            for _ in range(200000):
                low=min(low,c.sp)
                if(c.pc,c.sp)==(regs[5],regs[4]):break
                lh+=int(c.pc==lag);rh+=int(c.pc==regular)
                assert m[c.pc]!=0,('ISR BRK',interrupt,hex(c.pc),c.sp)
                ins=bytes(m[c.pc:c.pc+3])
                if ins in[bytes.fromhex(z)for z in['8dd807','ced807','8dda07','8ddb07','eedb07']]:
                    bank=m.rawtags[(c.pc-0x8000)//8192];assert(bank,c.pc)in sites,('Unbound audio clock writer',bank,hex(c.pc),ins.hex())
                    AUDIO_WRITERS[f'{bank:02x}:{c.pc:04x}:'+sites[bank,c.pc][0]]+=1
                c.step()
            else:raise AssertionError(('ISR bound',interrupt))
            assert regs[:3]==(c.a,c.x,c.y)and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
            after=state(m)
            if before[:3]!=after[:3]or before[4]!=after[4]:
                diagnostic=dict(passed=False,interrupt=interrupt,minimum_SP=low,
                    RAM_differences=[dict(bank=k,offset=i,old=a,new=v)for k,(aa,bb)in enumerate(zip(before[0],after[0]))for i,(a,v)in enumerate(zip(aa,bb))if a!=v][:32],
                    scratch=[list(before[1]),list(after[1])],SMC=[list(before[2]),list(after[2])],
                    native_differences=[dict(address=i+0x200,old=a,new=v)for i,(a,v)in enumerate(zip(before[4],after[4]))if a!=v][:32])
                (O/'head-projection-v57-unexpected-state.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
                raise AssertionError(('ISR state',interrupt,diagnostic))
            audio_after=audio(m)
            if interrupt[0]=='IRQ':assert lh==rh==0 and audio_after==audio_before
            else:
                assert lh==1 and rh==0 and N.get(m,'NmiSkipped')==(skipped+1)&255
                assert audio_before==(0,0,0)and audio_after[0]in[0,9]and audio_after[1]in[0,16]and audio_after[2]in[0,1],('Unexpected actual first bump/grow audio clock transition',audio_before,audio_after)
                AUDIO_TRANSITIONS[str(audio_before)+'->'+str(audio_after)]+=1
            if maps!=m.rawtags:
                ins=bytes(m[c.pc:c.pc+3]);assert ins in[bytes.fromhex(x)for x in['8d1551','8d1651','8e1651']]
                window=1 if ins[1]==0x15 else 2
                assert m.rawtags[window]==N.get(m,'CurrentBank'if window==1 else'CurrentBankC')
                assert all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)
            COUNTS[interrupt[0]]+=1;laghits+=lh;regularhits+=rh
        assert m[c.pc]!=0,('Foreground BRK',hex(c.pc),c.sp,m.rawtags)
        c.step()
    else:raise AssertionError(('Foreground bound',hex(c.pc)))
    assert c.sp==224 and(interrupt is None or injected)and headcalls==1
    if audio_after is not None:assert audio(m)==audio_after,'Resumed foreground changed actual post-NMI audio clocks'
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],minimum_SP=low,cuts=sorted(cuts.values()),native_heads=headcalls,lag_hits=laghits,regular_hits=regularhits)

def seeds(b,route):
    out=[]
    for identity in[0,1]:
        m,cell=H.H.H.arena(b,route,identity)
        for epoch in range(16):
            N.put(m,FrameCounter=epoch,SavedJoypadBits=128 if epoch else 0,SavedJoypad1Bits=128 if epoch else 0,VRAM_Buffer1_Offset=0)
            N.invoke(m,'GameCoreRoutine',x=0,y=0)
        N.put(m,FrameCounter=16,SavedJoypadBits=128,SavedJoypad1Bits=128,VRAM_Buffer1_Offset=0,NmiDisable=255)
        out.append((m,cell))
    return out

def main():
    old,b,route,q,p,image=H.bundle();proof=O/'head-projection-v56-CPU.json';pr=json.loads(proof.read_text());assert pr['passed']and pr['memory_ROM_SHA256']==p['memory_ROM_SHA256']
    rows=[];minimum=224
    for identity,(m,cell)in enumerate(seeds(b,route)):
        z=N.fork(m);ref=run(z,p,q);expected=state(z)
        assert z[cell]==35 and N.get(z,'Enemy_ID',5)==46 and N.get(z,'NumberofLives')==2
        print('Head IRQ cohort',identity,len(ref['cuts']),'foregroundSP',ref['minimum_SP'],flush=True)
        for irq in['IRQ','lagNMI']:
            for index,cut in enumerate(ref['cuts']):
                z=N.fork(m);out=run(z,p,q,(irq,cut));minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and state(z)==expected,(identity,irq,cut)
                if index and index%250==0:print('Head IRQ progress',identity,irq,index,flush=True)
        rows.append(dict(identity=identity,actual_native_head_transactions=1,cuts=len(ref['cuts']),foreground_minimum_SP=ref['minimum_SP'],deepest_cut=min(ref['cuts'],key=lambda x:x[1])))
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,qualified=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],
        actual_interrupts=dict(COUNTS),minimum_ISR_SP=minimum,scenarios=rows,actual_native_audio_clock_writers=dict(AUDIO_WRITERS),actual_native_audio_clock_transitions=dict(AUDIO_TRANSITIONS),
        scope='Every reached I0 PC/A-bank/C-bank pair from source contact capture through the genuine ordinary native PlayerHeadCollision return, plus every reached new head/begin instruction. Actual IRQ and genuine NmiDisableFF lag-NMI preserve AXYP/SP, complete private RAM, R0..7, five SMC bytes, native0200..07FF and final maps; lag INC NmiSkipped once, no regular path. Three exact source-owned native sound clocks07D8/07DA/07DB advance only at bound Fthrow/DecrementSfx1Length/GrowItemRegs/ContinueGrowItems instructions. IRQ preserves all3; actual FF lag changes are tracked; resumed foreground preserves exact post-NMI values. Original source trajectory and native SetupPowerUp are real executed code.',
        remaining=['Focused nested native IRQ inside actual lag audio at deepest head contexts.','Root Mesen earned block/collection and both identities fullstage scope.'],
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(H.__file__),Path(I.__file__),proof,O/'head-projection-v55.json',O/'head-projection-v55-image.bin',O/'head-projection-v57-negative.json',R/'src/music_drivers/vanilla_sfx.s']})
    (O/'head-projection-v57-ISR.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))

if __name__=='__main__':main()
