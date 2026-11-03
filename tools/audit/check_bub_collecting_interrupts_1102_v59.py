"""Actual pickup ingress under real IRQ and the FF lag-NMI branch; no ROM emitted."""
from collections import Counter
import json
from pathlib import Path
import compose_bub_collecting_gate_1102_v57 as G
import prepare_bub_collecting_upgrades_1102_v56 as U
from prepare_selected_native_packet_v1 import R,sha

Q=G.Q;N=Q.N;address=Q.address
O=R/'build/bub-upgrades-root-interrupts-1102-v59'
COUNTS=Counter()

def state(m):
    native=bytearray(m[0x200:0x800]);native[0x7da-0x200]=0
    return ([bytes(z) for z in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],bytes(native))

def path(m):
    code=bytes(m[0xe000:0x10000]);hits=[]
    for i in range(len(code)-8):
        if code[i:i+4]==bytes.fromhex('ad390110') and code[i+5:i+8]==bytes.fromhex('ee3a01'):hits.append(i)
    assert len(hits)==1,hits
    i=hits[0];offset=code[i+4];offset-=256 if offset&128 else 0
    return 0xe000+i+5,0xe000+i+5+offset

def run(m,interrupt=None):
    b=m.bundle;target=address(b,'PowerUpObjHandler')
    from check_tmnt_render_oa import location
    m[address(b,'SafecallA_SMC')+1]=83
    m[address(b,'FarcallJmpTarget_SMC')+1]=target&255
    m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
    c=N.NesMPU(memory=m,pc=address(b,'FarCallCommon'))
    c.a=((location(b,'PowerUpObjHandler')-16)//8192)|128
    c.x=5;c.y=0;c.p=0x21;c.sp=224;c.stPushWord(0x5aff)
    cuts={};low=c.sp;injected=False;calls=Counter();audio_after=None
    needle=address(b,'MarioSourcePowerupCollision')
    for _ in range(100000):
        if c.pc==0x5b00:break
        low=min(low,c.sp)
        bank=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else None
        if c.pc==needle and bank==131:calls['native-collector']+=1
        # Include all reached low-stack native instructions as well as the
        # relocated source/adapter and every software farcall/auth instruction.
        if not c.p&4 and (c.sp<=180 or bank==3 or 0x15a<=c.pc<0x17b or bank==193 and 0xae00<=c.pc<0xb100):
            key=(c.pc,m.rawtags[1]);cut=(c.pc,c.sp,m.rawtags[1])
            if key not in cuts or c.sp<cuts[key][1]:cuts[key]=cut
        cut=(c.pc,c.sp,m.rawtags[1])
        if interrupt and not injected and cut==interrupt[1]:
            injected=True;assert not c.p&4
            regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);before=state(m);maps=m.rawtags[:]
            skipped=N.get(m,'NmiSkipped');lag,regular=path(m);lh=rh=0
            assert N.get(m,'NmiDisable')==255
            audio_before=m[0x7da]
            c.irq() if interrupt[0]=='IRQ' else c.nmi()
            for _ in range(200000):
                low=min(low,c.sp)
                if (c.pc,c.sp)==(regs[5],regs[4]):break
                lh+=int(c.pc==lag);rh+=int(c.pc==regular)
                assert m[c.pc]!=0,('ISR BRK',interrupt,hex(c.pc),c.sp)
                c.step()
            else:raise AssertionError(('ISR bound',interrupt))
            assert regs[:3]==(c.a,c.x,c.y) and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
            after=state(m)
            assert before[:3]==after[:3] and before[4]==after[4],dict(interrupt=interrupt,ram=before[:3]==after[:3],native=[(hex(i+0x200),x,y) for i,(x,y) in enumerate(zip(before[4],after[4])) if x!=y][:12])
            audio_after=m[0x7da]
            if interrupt[0]=='IRQ':assert lh==rh==0 and audio_before==audio_after
            else:assert lh==1 and rh==0 and N.get(m,'NmiSkipped')==(skipped+1)&255
            if maps!=m.rawtags:
                ins=bytes(m[c.pc:c.pc+3]);assert ins in [bytes.fromhex(x) for x in ['8d1551','8d1651','8e1651']],(interrupt,maps,m.rawtags)
                window=1 if ins[1]==0x15 else 2
                assert m.rawtags[window]==N.get(m,'CurrentBank' if window==1 else 'CurrentBankC')
                assert all(maps[k]==m.rawtags[k] for k in range(4) if k!=window)
            COUNTS[interrupt[0]]+=1
        assert m[c.pc]!=0,('Foreground BRK',hex(c.pc),c.sp,m.rawtags)
        c.step()
    else:raise AssertionError(('Foreground bound',hex(c.pc)))
    assert c.sp==224 and (interrupt is None or injected)
    if audio_after is not None:assert m[0x7da]==audio_after
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],minimum_SP=low,cuts=sorted(cuts.values()),calls=dict(calls))

def main():
    O.mkdir(exist_ok=True);old,b,route,q=G.bundles();rows=[];minimum=224
    proof=R/'build/bub-upgrades-root-ingress-1102-v58/receipt.json'
    p=json.loads(proof.read_text());assert p['passed'] and p['ROM_memory_SHA256']==q['expected_memory_only_ROM_SHA256']
    for identity in [0,1]:
        seed=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(seed)
        N.put(seed,NmiDisable=255,TimerControl=1,Player_Rel_XPos=64,Player_Rel_YPos=176)
        N.invoke(seed,'HuFullBox',a=83,x=0,y=0,p=0x21)
        for kind in range(4):
            m=N.fork(seed);N.put(m,ObjectOffset=5)
            for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=191,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[address(b,field)+5]=value
            baseline=N.fork(m);ref=run(baseline);expected=state(baseline)
            assert ref['calls'].get('native-collector')==1,ref
            print('Bub pickup ISR',identity,kind,len(ref['cuts']),ref['minimum_SP'],flush=True)
            for interrupt in ['IRQ','lagNMI']:
                for cut in ref['cuts']:
                    z=N.fork(m);out=run(z,(interrupt,cut));minimum=min(minimum,out['minimum_SP'])
                    assert out['regs']==ref['regs'] and state(z)==expected,(identity,kind,interrupt,cut)
            rows.append(dict(identity=identity,kind=kind,foreground_minimum_SP=ref['minimum_SP'],cuts=len(ref['cuts']),native_collector_calls=1))
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],real_interrupts=dict(COUNTS),minimum_ISR_SP=minimum,scenarios=rows,scope='Both identities/four native pickup types. Real PowerUpObjHandler and owning row24/native collector under actual IRQ and FF lag NMI at all reached deep instruction/A-bank pairs. Every lag cut reaches INC NmiSkipped once and never the regular NMI branch. Full private RAM/scratch/SMC/native0200..07FF/final maps/AXYP/SP exact except native async07DA sound duration. No nested IRQ-in-NMI, cold fault/readback, transformation completion, earned block/Mesen/stage claim.',bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),proof,G.O/'proposal.json',U.O/'proposal.json',U.O/'private-image.bin']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':
    try:main()
    except Exception as e:
        O.mkdir(exist_ok=True);(O/'negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e),real_interrupts=dict(COUNTS)),indent=2)+'\n');raise
