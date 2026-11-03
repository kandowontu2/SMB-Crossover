"""Actual status ingress and exact private native item contract checks."""
import collections,itertools,json
from pathlib import Path
import check_dkjr_native_score_tail_1102_v55 as P
A,R,O,W,N=P.A,P.R,P.O,P.W,P.N


def fixture():
    b,m,_,_=P.fixture();q=json.loads((O/'native-items-v60-layout.json').read_text());L=q['labels']
    m.ram[3][:0x1fe0]=[255]*0x1fe0;part=(O/'native-items-v60.bin').read_bytes();m.ram[3][:len(part)]=part
    for kind,at in [('pause',0x1540),('main',0x165e),('ports',0x16a7)]:
        part=(O/f'native-items-{kind}-v60.bin').read_bytes();m.ram[2][at:at+len(part)]=part
    return b,m,L,q


def native(m):
    return list.__getitem__(m,slice(0,32768))


def differences(aa,bb,allowed=()):
    return [(i,a,b)for i,(a,b)in enumerate(zip(aa,bb))if a!=b and i not in allowed and not 0x100<=i<0x200 and not 0x2000<=i<0x5c00]


def main():
    b,seed,L,q=fixture();cases=collections.Counter();source_bytes=bytes(seed.ram[2][:0x900])
    fields=['InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi']
    for slot,flags in itertools.product(range(8),[0x30,0x31,0x71,0xf1]):
        m=N.fork(seed);N.put(m,ObjectOffset=slot)
        before=native(m);out=P.direct(m,L['DkNativePrepare'],x=slot,p=flags)
        assert out==(85,slot,91,flags&0xef,224)
        allowed=[]
        if slot<6:
            for field,value in zip(fields,[40,252,0,0,0]):
                at=W.address(b,field)+slot;allowed.append(at);assert m[at]==value
        assert not differences(before,native(m),allowed)
        assert source_bytes==bytes(m.ram[2][:0x900]);cases['prepare']+=1
    for slot,kind,state,flags in itertools.product(range(8),range(4),[0,1,127,128,255],[0x30,0xf1]):
        m=N.fork(seed);m[W.address(b,'PowerUpType')+slot]=kind;m[W.address(b,'Enemy_State')+slot]=state
        before=native(m);out=P.direct(m,L['DkNativeMature'],x=slot,p=flags)
        assert bool(out[3]&1)==bool(slot<6 and(kind>=2 or state&128)),(slot,kind,state,flags,out)
        assert not differences(before,native(m))and bytes(m.ram[2][:0x900])==source_bytes;cases['maturity']+=1
    # Direct policy30 checks all messages, arbitrary legal existing offsets,
    # full incoming flags and source/native packet byte preservation.
    name=[13,20,36,19,27,36,36];base=W.address(b,'VRAM_Buffer1')
    for text,offset,flags in itertools.product(range(6),[0,11,61,100],[0x30,0x31,0x71,0xf1]):
        m=N.fork(seed);N.put(m,VRAM_Buffer1_Offset=offset)
        m[base:base+128]=[(i*11+7)&255 for i in range(128)];before=native(m)
        out=P.direct(m,L['DkNativeStatusName'],a=text,x=19,y=91,p=flags)
        assert out==(text,19,91,(flags|1)&0xef,224)
        allowed=list(range(base+11,base+18))if text==0 else[]
        if text==0:assert list(m[base+11:base+18])==name
        assert not differences(before,native(m),allowed)and bytes(m.ram[2][:0x900])==source_bytes;cases['direct_status']+=1
    nativeCPU=N.NesMPU;counter=collections.Counter();rows=[]
    class Trace(nativeCPU):
        def step(self):
            if self.pc==L['DkNativeStatusName']and self.memory.rawtags[1]==3:counter['actual_private_status']+=1
            return super().step()
    N.NesMPU=Trace
    try:
        for text,offset in itertools.product(range(6),[0,11,61]):
            m=N.fork(seed);ref=N.fork(seed)
            for bus in [m,ref]:N.put(bus,VRAM_Buffer1_Offset=offset,CurrentPlayer=0,NumberOfPlayers=0)
            N.put(ref,SelectedCharacter=0)
            a=N.invoke(ref,'WriteGameText',a=text,x=19,y=91,p=0x31)
            start=counter['actual_private_status'];out=N.invoke(m,'WriteGameText',a=text,x=19,y=91,p=0x31)
            reached=counter['actual_private_status']-start
            allowed=list(range(base+11,base+18))if text==0 else[]
            packetdiff=[(i,a,b)for i,(a,b)in enumerate(zip(ref[base:base+160],m[base:base+160]))if a!=b and base+i not in allowed]
            rows.append(dict(message=text,initial_offset=offset,actual_private_status_calls=reached,
                outside_name_packet_differences=packetdiff[:12],resulting_name=list(m[base+11:base+18]),
                native_AXYP=[out[k]for k in['A','X','Y','P']]))
            assert reached==1,('actual status ingress missing',text,offset,rows[-1])
            assert not packetdiff and(text!=0 or list(m[base+11:base+18])==name),(text,offset,rows[-1])
            assert[a[k]for k in['A','X','Y','P']]==[out[k]for k in['A','X','Y','P']]
            cases['actual_WriteGameText']+=1
    except AssertionError as error:
        out=dict(passed=False,ROM_written=False,native_owner_admitted=False,error=repr(error),completed=dict(cases),actual_native_status_rows=rows,
            scope='Private direct item/status contracts completed as listed. Genuine WriteGameText ingress is the failing boundary; no shared gate patched or fallback claimed functional.',
            body_SHA256=A.sha((O/'native-items-v60.bin').read_bytes()))
        (O/'native-items-v61-negative.json').write_text(json.dumps(out,indent=2)+'\n');raise
    finally:N.NesMPU=nativeCPU
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,historical_v65_matching_header_fixture=True,
        checks=dict(cases),actual_native_status_rows=rows,body_bytes=q['body_bytes'],header_spare=q['header_spare'],
        scope='Native itemPrepare/regular maturity predicates have exact declared scratch-free private semantics; itemcollector24 is compiled but not yet executed/IRQqualified. Actual real WriteGameText reaches authenticated own30 exactlyonce; full ordinary header/messages/buffer byte content remain except seven DKJR name cells, including nonzero offset. No actual shared raw40 item gate/menu admission, no source powerup ability claim.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-items-v60.s',O/'native-items-v60.bin',O/'native-items-v60-layout.json',R/'src/new_roster_dispatch.s',R/'src/screen_render.s']})
    (O/'native-items-v61-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=out['checks'])))


if __name__=='__main__':main()
