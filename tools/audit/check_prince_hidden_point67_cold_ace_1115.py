"""Actual encoded point candidate cold, first pre-SMC readback and binding."""
from pathlib import Path
from unittest.mock import patch
import json
import current_prince_hidden_point67_ace_1115 as Current

C,N,W,Game,Frames=Current.C,Current.N,Current.W,Current.Game,Current.Frames

def run(parent):
    raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    parts=C.Packet.extract(raw)[1];base=N.NesMPU;first=[];leaf=[];ctors=[];published=[];callers={}
    cookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16]
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==0xc0b0 and m.rawtags[2]==2:
                assert bytes(m[0xc0b0:0xc0ff])==parts[2][:79]
                ctors.append(dict(PC=self.pc,SP=self.sp,constructor79_exact=True))
            if self.pc==0xb310 and m.rawtags[1]==3:
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                callers[ret]=callers.get(ret,0)+1
                if not first:
                    assert bytes(m[0xb310:0xb353])==C.NEW
                    assert bytes(m[0xb353:0xb369])==parts[0][0x1353:0x1369]
                    assert m.rawtags[0]==128+126 and m.rawtags[3]==128+127
                    assert bytes(m[0x9eca:0x9ed1])==bytes.fromhex('c95ff002c96060')
                    assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
                    first.append(dict(PC=self.pc,SP=self.sp,return_PC=ret,all67_before_first_SMC=True,
                        map=list(m.rawtags),both_complete_cookies=True,code_SHA256=C.digest(bytes(m[0xb310:0xb353])),
                        old_SMC_low=0xb33b,actual_SMC_low=0xb338,neighbor22_exact=True))
            if self.pc==0x9eca and m.rawtags[0]==128+126 and len(leaf)<4:
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                if ret==0xb33d:
                    assert m.rawtags[1]==3 and m.rawtags[3]==128+127
                    leaf.append(dict(PC=self.pc,SP=self.sp,return_PC=ret,A=self.a,map=list(m.rawtags)))
            if self.pc==0xbbc1 and m.rawtags[1]==3 and not published:
                assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
                published.append(dict(PC=self.pc,SP=self.sp,both_cookies=True,point67_seen_before_first_publish=bool(first)))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        m,opening=Current.cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert first and leaf and published and len(ctors)>=2
    # Inverse must remain portable with mutable Downloads reads rejected.
    reader=Path.read_bytes;C.inverse.cache_clear()
    def read(path,*a,**k):
        assert path.resolve()!=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').resolve()
        return reader(path,*a,**k)
    with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent
    rejected=[]
    for name,fn,image in(('parent_as_candidate',C.inverse,parent),('candidate_as_parent',C.proposal,raw),
        ('truncated',C.inverse,raw[:-1]),('dirty_unowned',C.inverse,raw[:100]+bytes((raw[100]^1,))+raw[101:])):
        try:fn(image)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('Unknown point image accepted')
    q=dict(passed=True,composition=composition,opening=opening,first_actual_PointRead=first[0],
        actual_native_leaf_calls=leaf,actual_PointRead_callers=callers,actual_constructors=ctors,first_BBC1=published[0],
        portable_inverse_without_Downloads=True,strict_rejections=rejected,source_array_mounts=0,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point cold source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
