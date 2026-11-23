"""Read effective native9587 head results on the frozen1124 Up trajectory.

Only aggregate stdout. Native function return/SP/mapping establishes R3/R4
after the leaf has executed; entry R3 is never mistaken for its result.
"""
import json
from pathlib import Path
from unittest.mock import patch

import replay_prince_oneup_up_1123 as U
import compose_prince_oneup_lift_1123 as Compose
import probe_prince_lift_swept_plane_1123 as Sweep

PIN='1124ad4219fdee26306a369092f921b9eee35728e8ab19fd66d95cc34e6d3e9c'
CONTROL='1eec698c8c4bb626a1ec2efd3f74818d0e0cbaa8b9d89fb2299f8213880a462c'
SOURCE='44b020da42b7dde8975760603b77bf657f8e563506708f75a32f100e8232f3a1'


def inspect(image,overlay):
    assert U.H(image)==PIN and U.H(Path(U.__file__).read_bytes())==SOURCE
    assert U.H(U.controller(image,overlay).encode())==CONTROL
    R,N,W=U.R,U.R.N,U.W
    bundle=dict(W.Symbols.bundle(),raw=image)
    pc=W.address(bundle,'BlockBufferColli_Head');assert pc==0x9587
    at=W.location(bundle,'BlockBufferColli_Head');tag=128+(at-16)//8192;assert tag==254
    expected=image[at:at+8]
    names=('SelectedCharacter GameEngineSubroutine Player_X_Position Player_PageLoc Player_Y_Position '
           'Player_Y_HighPos Player_Y_Speed Player_State Enemy_Flag Enemy_ID Enemy_Y_Position '
           'Enemy_Y_Speed PlatformCollisionFlag R2 R3 R4 R6 R7 GameLoop').split()
    adr={n:W.address(bundle,n)for n in names}
    main_tag=128+(W.location(bundle,'GameLoop')-16)//8192
    head_adder=W.address(bundle,'BlockBufferAdderData')+6
    counter=[0];pending=[];first=[];last=[];up_first=[];up_last=[];hist={};count=[0];all_queries=[0]
    raw_kinds={};up_count=[0]
    base=N.NesMPU

    def mapped(m,where):return m.rawtags[(where-0x8000)//8192]if where>=0x8000 else None

    def row(cpu):
        m=cpu.memory;s=m.ram[2];r=lambda n,i=0:m[adr[n]+i]
        return dict(Main=counter[0],return_PC=cpu.pc,SP=cpu.sp,A=cpu.a,P=cpu.p,
            R2=r('R2'),R3=r('R3'),R4=r('R4'),R4_low=r('R4')&15,R6=r('R6'),R7=r('R7'),
            source_C616_C617_C618=list(s[0x616:0x619]),source_Y=s[0x611],source_phase=s[0xa6],
            native_x=r('Player_X_Position')+256*r('Player_PageLoc'),native_y=r('Player_Y_Position'),
            native_y_high=r('Player_Y_HighPos'),native_y_speed=r('Player_Y_Speed'),native_state=r('Player_State'),
            slot5=dict(flag=r('Enemy_Flag',5),id=r('Enemy_ID',5),Y=r('Enemy_Y_Position',5),
                Enemy_Y_Speed=r('Enemy_Y_Speed',5),PlatformCollisionFlag=r('PlatformCollisionFlag',5)),
            C086_C087=list(s[0x86:0x88]),prior_foot=s[0x86]+256*s[0x87],current_foot=s[0x84]+256*s[0x85])

    class Spy(base):
        def step(self):
            m=self.memory
            if self.pc==adr['GameLoop']and mapped(m,self.pc)==main_tag and m[adr['GameEngineSubroutine']]==8:counter[0]+=1
            for watch in tuple(pending):
                ret,sp,physical,entry=watch
                if self.pc==ret and self.sp==sp and mapped(m,ret)==physical:
                    pending.remove(watch);all_queries[0]+=1
                    if m[adr['R3']]==96:
                        y=entry['Y'];raw_kinds[y]=raw_kinds.get(y,0)+1
                        if y!=entry['head_adder']:continue
                        q=row(self);q['entry']=entry
                        key=f"{q['source_C616_C617_C618']} carry={q['slot5']['PlatformCollisionFlag']} R4={q['R4_low']}"
                        hist[key]=hist.get(key,0)+1;count[0]+=1
                        if len(first)<6:first.append(q)
                        last.append(q)
                        if len(last)>6:last.pop(0)
                        if q['source_C616_C617_C618'][0]==28:
                            up_count[0]+=1
                            if len(up_first)<6:up_first.append(q)
                            up_last.append(q)
                            if len(up_last)>6:up_last.pop(0)
            if self.pc==pc and mapped(m,pc)==tag and m[adr['SelectedCharacter']]==38 and m[adr['GameEngineSubroutine']]==8:
                x=m[adr['Player_X_Position']]+256*m[adr['Player_PageLoc']]
                if 1000<=x<=1048:
                    assert bytes(m[pc+i]for i in range(8))==expected
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    s=m.ram[2]
                    assert m[head_adder]==51,'Current Prince native head-adder identity'
                    entry=dict(Main=counter[0],PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,head_adder=m[head_adder],
                        native_y=m[adr['Player_Y_Position']],source_C616_C617_C618=list(s[0x616:0x619]),
                        slot5_Y=m[adr['Enemy_Y_Position']+5],slot5_speed=m[adr['Enemy_Y_Speed']+5],
                        slot5_carry=m[adr['PlatformCollisionFlag']+5])
                    assert len(pending)<8,'Bounded native head leaf nesting'
                    pending.append((ret,(self.sp+2)&255,mapped(m,ret),entry))
            return super().step()

    with patch.object(N,'NesMPU',Spy):q=U.source(image,overlay)
    receipt=q['receipt'];stock=receipt.get('natural_stock',{});lift=stock.get('lift',{})
    out=dict(ROM_SHA256=PIN,controller_SHA256=q['controller_SHA256'],source_receipt=q['receipt_SHA256'],
        source_passes=q['source_passes'],reason=receipt.get('reason'),terminal=receipt.get('terminal'),
        native_head=dict(PC=pc,physical_tag=tag,bytes=expected.hex(),nearby_queries_returned=all_queries[0],
            head_adder_address=head_adder,raw60_all_adder_counts=raw_kinds,
            raw60_head_count=count[0],first=first,last=last,histogram=hist,up_head_count=up_count[0],
            up_first=up_first,up_last=up_last,unreturned=len(pending)),
        lift_admission=lift.get('admission'),reached_apex=lift.get('reached_apex'),
        immutable_controller=True,post_leaf_results=True,outputs=0,Mesen=False)
    assert out['controller_SHA256']==CONTROL and not pending
    return out


def main():
    raw=U.R.P.G.ROM.read_bytes();assert U.H(raw)==U.R.PIN
    image,overlay=Compose.compose(raw,Sweep.hold_plane_plan)
    def deny(*a,**k):raise AssertionError('Read-only head inspector attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        out=inspect(image,overlay)
    print('PRINCE_UP_HEAD '+json.dumps(out,separators=(',',':')),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
