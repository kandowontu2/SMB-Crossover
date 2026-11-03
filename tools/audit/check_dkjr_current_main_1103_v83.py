"""Current physically cold-loaded DK movement/Main and aggregate CPU profile."""
import collections
import json
from pathlib import Path
import prepare_dkjr_current_owner_1103_v79 as P

A,R,O,C=P.A,P.R,P.O,P.C
N,W=C.N,A.W


def main():
    b,q=P.image();seed,_=C.cold(b,40)
    N.invoke(seed,'HuFresh',a=83,x=0,y=109,p=0x21)
    N.put(seed,DisableScreenFlag=0,Mirror_PPUMASK=30,TimerControl=0,AreaType=1,
        NmiDisable=255,PlayerSize=1,Player_BoundBoxCtrl=1,PlayerFacingDir=1,
        AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        at=W.address(b,name);seed[at:at+208]=bytes(208)
        for row in [11,12]:seed[at+row*16:at+row*16+16]=bytes([0x54])*16
    for i,value in enumerate([4,0,0]):seed[W.address(b,'GameTimerDisplay')+i]=value
    for slot in range(6):seed[W.address(b,'Enemy_Flag')+slot]=0
    L=json.loads((O/'native-event-v74-layout.json').read_text())['labels']
    labels=q['manager_labels'];CPU=N.NesMPU;totals=collections.Counter();calls=collections.Counter()
    class Profile(CPU):
        def step(self):
            pc=self.pc;bank=self.memory.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
            key=None
            if bank==193:
                if labels['CoCheckHeaders']<=pc<labels['CoRetireOwners']:key='shared_full_header_compare'
                elif 0xaaf7<=pc<0xab72:key='shared_transport'
                elif 0xa740<=pc<q['selector_labels']['DkCookie']:key='shared_selector'
                elif labels['CoCheckCode']<=pc<labels['CoCheckHeaders']:key='shared_auth_helper_and_selection'
            elif bank in [2,3]:key='private_component'
            if bank==3 and 0xa000<=pc<0xa072 and(pc-0xa000)%3==0:calls['row'+str((pc-0xa000)//3)]+=1
            if bank==3 and pc==L['DkjrJumpRestart']:calls['original_jump_reset']+=1
            before=self.processorCycles;z=super().step()
            if key:totals[key]+=self.processorCycles-before
            return z
    N.NesMPU=Profile;rows=[]
    try:
        for name,epochs in [('idle',60),('right',80),('left',60),('directional_jump',80)]:
            m=N.fork(seed)
            if name=='left':
                N.put(m,Player_X_Position=120)
                # Legal world transport of the already constructed actor;
                # genuine Main performs all subsequent source movement.
            initial=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            start=dict(calls);cycles=[];ys=[];xs=[];directions=[]
            for epoch in range(epochs):
                keys=0 if name=='idle'else 1 if name in ['right','directional_jump']else 2
                if name=='directional_jump':
                    if epoch==1:keys|=128
                    elif 5<=epoch<35:keys=2
                    elif epoch>=35:keys=0
                N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                z=N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
                cycles.append(z['CPU']);ys.append(N.get(m,'Player_Y_Position'))
                xs.append(N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))
                directions.append(m.ram[2][0x54])
                assert N.get(m,'NumberofLives')==2
            delta=xs[-1]-initial
            if name=='idle':assert delta==0 and min(ys)==max(ys)==176,(name,delta,min(ys),max(ys))
            elif name=='right':assert delta==50 and ys[-1]==176,(name,delta,min(ys),ys[-1])
            elif name=='left':assert delta==-37 and ys[-1]==176,(name,delta,min(ys),ys[-1])
            else:
                assert min(ys)==161 and ys[-1]==176,(name,min(ys),ys[-1])
                assert all(d==4 for d,y in zip(directions[5:35],ys[5:35])if y<176),(name,'air direction latch',directions)
            rows.append(dict(control=name,updates=epochs,initialX=initial,finalX=xs[-1],deltaX=delta,
                minY=min(ys),finalY=ys[-1],source_jump_resets=calls['original_jump_reset']-start.get('original_jump_reset',0),
                mean_Main_CPU=sum(cycles)/len(cycles),min_Main_CPU=min(cycles),max_Main_CPU=max(cycles)))
    finally:N.NesMPU=CPU
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),isolated_native_BlockBuffer_flat_floor=True,
        rows=rows,aggregate_CPU=dict(totals),actual_private_vector_entries=dict(calls),
        scope='Actual current cf7/Prince130/four-owner proposal, physically copied/readback DK payload, real constructor and complete native GameCore. Explicit legal flat floor uses native BlockBuffers; no source actor/timing outcomes seeded. Donor15px jump and latched airborne direction retained. CPU values are source-model Main costs, not native frame cadence; no Mesen/native1-1/helper/menu admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),
            O/'native-owner-proposal-v79.json',O/'native-current-cold-v81-CPU.json',O/'native-event-v74-layout.json']})
    (O/'native-current-main-v83-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','rows','aggregate_CPU','actual_private_vector_entries']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-current-main-v83-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
