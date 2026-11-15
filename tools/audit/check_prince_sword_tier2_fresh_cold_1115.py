"""Actual encoded40a cold: constructor survives Fresh and exact first publish."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_prince_sword_tier2_fresh_1115 as C
import check_prince_sword_tier2_earned_1115 as Previous

N,W,Frames,Game=Previous.N,Previous.W,Previous.Frames,Previous.Game

def cold(raw):
    assert C.digest(raw)==C.CANDIDATE
    def parent(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',parent):return Game.cold(raw)

def run(parent):
    raw,info=C.proposal(parent);assert C.inverse(raw)==parent
    parts=C.Packet.extract(raw)[1];rows=C.Plan.arrays(parent)[3];base=N.NesMPU;ctors=[];published=[];fresh=[]
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==0xc0b0 and m.rawtags[2]==2:
                expected=parts[2][:79];actual=bytes(m[0xc0b0:0xc0ff]);assert actual==expected
                ctors.append(dict(PC=self.pc,SP=self.sp,bytes=79,SHA256=C.digest(actual),exact=True))
            if self.pc==0xb3ef and m.rawtags[1]==3:
                assert bytes(m[0xb3f1:0xb3f9])==b'\xea'*8;fresh.append(dict(PC=self.pc,SP=self.sp))
            if self.pc==0xbbc1 and m.rawtags[1]==3 and not published:
                cookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16]
                assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
                for row in rows:
                    stream=row['stream'];lo,hi=row['decoded_half_open'];pc=row['live_CPU_half_open'][0];bank=3 if stream==0 else 2
                    assert bytes(m.ram[bank][pc&8191:(pc&8191)+hi-lo])==parts[stream][lo:hi]
                published.append(dict(PC=self.pc,SP=self.sp,both_complete_cookies=True,all166_new_static_bytes_exact=True))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        m,opening=cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(ctors)>=2 and fresh and published
    q=dict(passed=True,composition=info,opening=opening,actual_constructors=ctors,actual_Fresh=fresh,
        actual_first_publish=published,terminal=Previous.state(m),source_array_mounts=0,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Fresh cold source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
