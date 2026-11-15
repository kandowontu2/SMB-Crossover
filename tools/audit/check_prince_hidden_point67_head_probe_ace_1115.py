"""Declared native-head and sweep primitives; never natural-item qualification."""
from pathlib import Path
from unittest.mock import patch
import json
import current_prince_hidden_point67_ace_1115 as Current

C,N,W=Current.C,Current.N,Current.W

def run(parent):
    raw,composition=C.proposal(parent);m,opening=Current.cold(raw);parts=C.Packet.extract(raw)[1]
    head=[];index=W.address(m.bundle,'BlockBufferAdderData')+6;adder=m[index];assert adder==51
    # Synthetic tile/position inputs isolate the actual compiled native query.
    # They never qualify a gameplay route, collection, health or ability state.
    for tile in(0,17,51,95,96,255):
        for x,y in((40,176),(1016,112),(1024,144),(255,176),(256,176),(511,112),(65535,112)):
            b=N.fork(m);b.__class__=W.ControllerBus
            for at in range(0x300,0x4a0):b[at]=tile
            N.put(b,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1)
            N.invoke(b,'BlockBufferColli_Head',a=83,x=0,y=adder,p=0x21)
            assert N.get(b,'R3')==tile,(tile,x,y,N.get(b,'R3'))
            head.append((tile,x,y,N.get(b,'R3')))
    def flat(code):
        a=bytearray(65536);a[:0x800]=bytes(m[:0x800])
        a[0x8000:0xa000]=raw[16+126*8192:16+127*8192]
        a[0xe000:]=raw[16+127*8192:16+128*8192]
        a[0xa000:0xc000]=m.ram[3];a[0xc000:0xe000]=m.ram[2]
        a[0xb310:0xb353]=code
        # Declared tail-call spy only: genuine native 9642 still executes.
        # This primitive checks unchanged sweep admission, not D660 effects.
        a[0xd660:0xd66b]=bytes.fromhex('0848ee005a682860eaeaea')
        return a
    arenas=(flat(C.OLD),flat(C.NEW));pairs=0;hidden=0
    def call(a,tile,x,y,p):
        a[0x300:0x4a0]=bytes((tile,))*416;a[0xb369:0xb36d]=x.to_bytes(2,'little')+y.to_bytes(2,'little');a[0x5a00]=0
        c=N.NesMPU(memory=a,pc=0xb353);c.a,c.x,c.y,c.p,c.sp=83,71,109,p,224;c.stPushWord(0x5aff)
        protected=bytes(a[0x1df:0x200])
        for _ in range(256):
            if c.pc==0x5b00:break
            assert a[c.pc];c.step()
        else:raise AssertionError('Sweep primitive return bound')
        assert c.sp==224 and bytes(a[0x1df:0x200])==protected
        return(c.a,c.x,c.y,c.p,c.sp,a[0x5a00])
    for tile in range(256):
        for x,y in((0,32),(255,239),(256,144),(65535,176)):
            for p in(0x20,0x21,0x60,0x61):
                a,b=(call(v,tile,x,y,p)for v in arenas);pairs+=1
                if tile in(95,96):
                    assert b[0]==0 and not b[3]&1 and b[-1]==0;hidden+=1
                else:assert a==b,(tile,x,y,p,a,b)
                if tile in(16,17):assert b[3]&1,'Real pipe remains a sweep wall'
    # Whole image/decoded ownership already proves these independent head
    # and live probe bytes unchanged, including both B352 return ingresses.
    prior=C.Packet.extract(parent)[1]
    assert parts[0][0x10fe:0x111b]==prior[0][0x10fe:0x111b]
    assert parts[0][0x1353:0x136e]==prior[0][0x1353:0x136e]
    q=dict(passed=True,candidate_SHA256=C.CANDIDATE,head_primitive_cases=len(head),
        actual_native_head_hidden5F60_raw_preserved=True,actual_Prince_adder_index=adder,
        head_query_PC=W.address(m.bundle,'BlockBufferColli_Head'),native_head_bridge_B0FE_unchanged=True,
        sweep_primitive_pairs=pairs,intended_hidden_empty_pairs=hidden,all_nonhidden_probe_AXYP_stack_and_tail_admission_exact=True,
        real_pipe_tiles16_17_remain_solid=True,live_probe_and_neighbors_B353_B36E_exact=True,
        declared_D660_spy_only=True,synthetic_tile_position_primitives_not_gameplay=True,
        no_natural_birth_or_collector_claim=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Head/probe primitive attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
