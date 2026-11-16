"""Read-only actual6a3 acquisition reader/call census; no proposed instructions."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json,re
import compose_bowser_life_gain_signed_1116 as Bowser
import profile_contra_force_current_costs_1115 as P

W,N,Frames=P.W,P.N,P.Frames
PIN=Bowser.CANDIDATE
SOURCE=P.KERNEL/'p1-runtime.s'
SOURCE_SHA='e15911ff74498252b944ce25075ff80706214729197a0b0b219ab250247e2483'
HOST=Bowser.R/'build/contra-force-world-roles-1031-v2/kernel/host-runtime.s'
HOST_SHA='8062a45639ab0e69190a3e602d4f3a4f6b06311c385508d7c9b08fab37156f52'

def scan_words(raw,address):
    rows=[]
    for bank in range(128):
        data=raw[16+bank*8192:16+(bank+1)*8192]
        at=0
        while True:
            at=data.find(address.to_bytes(2,'little'),at)
            if at<0:break
            rows.append(dict(physical_PRG=bank,file=16+bank*8192+at,
                offset=at,near=data[max(0,at-3):at+5].hex()))
            at+=1
    return rows

def main():
    actual=Bowser.ROM.read_bytes();assert Bowser.digest(actual)==PIN
    reference=Bowser.inverse(actual)
    q=P.bindings(reference);b=dict(q['bundle'],raw=actual)
    assert actual[P.CHR+935*1024:P.CHR+959*1024]==q['carrier']
    for path,pin in ((SOURCE,SOURCE_SHA),(HOST,HOST_SHA)):
        assert Bowser.digest(path.read_bytes())==pin
    labels={name:int(pc,16) for pc,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\w+)',(P.KERNEL/'runtime.lbl').read_text(),re.M)}
    assert labels['CfP1Acquire']==0xbf44 and labels['CfP1Heartbeat']==0xbeff
    last,pending,choice=(W.address(b,n) for n in ('SmFreezeLastBlue','SmFreezePalettePending','SmFreezePalettePacket'))
    assert (last,pending,choice)==(0x7ffa,0x7ea,0x7e0)
    acquire=q['carrier'][16384+0x1f44:16384+0x1f55]
    assert len(acquire)==17 and acquire==bytes.fromhex('a9008dea078dfa7f8df87f8dfbc24c55bf')
    # All current direct control/word candidates to Acquire in its owning RAM.
    image=q['carrier'][16384:]
    calls=[]
    for i in range(len(image)-2):
        if image[i] in (0x20,0x4c,0x6c) and image[i+1:i+3]==bytes.fromhex('44bf'):
            calls.append(dict(PC=0xa000+i,opcode=image[i]))
    assert len(calls)==1 and calls[0]['opcode']==0x20,calls
    kernel_words=[]
    for bank in (1,2,3):
        block=q['carrier'][(bank-1)*8192:bank*8192]
        for i in range(1,len(block)-1):
            if block[i:i+2]==last.to_bytes(2,'little'):
                kernel_words.append(dict(bank=bank,offset=i,opcode=block[i-1],near=block[max(0,i-3):i+5].hex()))
    base=N.NesMPU;captured=[];cut=None
    class Probe(base):
        def step(self):
            nonlocal cut
            tag=m.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
            if cut is None and tag==3 and self.pc==0xbf44:
                ret=((m[0x101+self.sp]|m[0x102+self.sp]<<8)+1)&65535
                cut=dict(seed=N.fork(m),pc=self.pc,sp=self.sp,a=self.a,x=self.x,y=self.y,p=self.p,
                    cycles=self.processorCycles,return_PC=ret,return_SP=(self.sp+2)&255,return_tag=tag,
                    busy=N.get(m,'NmiDisable'),last_before=m[last],choice_before=m.ram[2][0x2fb])
            return super().step()
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    with patch.object(N,'NesMPU',Probe):
        for pad in ([4]*3+[1]*6):W.UI.key(m,pad)
        assert W.UI.menu_name(m)[0]=='BURNS'
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if (N.get(m,'OperMode'),N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True)
        else:raise AssertionError('Actual6a3 cold constructor bound')
    assert m.bundle['raw'] is actual and cut is not None
    z=N.fork(cut['seed']);d=base(memory=z,pc=cut['pc'])
    for name in ('sp','a','x','y','p'):setattr(d,name,cut[name])
    reached=[];accesses=[];tags=Counter();pending_writes=[]
    for step in range(10000):
        tag=z.rawtags[(d.pc-0x8000)//8192] if d.pc>=0x8000 else -1
        if step and (d.pc,d.sp,tag)==(cut['return_PC'],cut['return_SP'],cut['return_tag']):break
        assert z[d.pc]!=0,('Acquisition BRK',d.pc,tag)
        op=z[d.pc];address=z[(d.pc+1)&65535]|z[(d.pc+2)&65535]<<8
        if op in (0xad,0xae,0xac,0xcd,0xcc,0xec,0x2c,0x0d,0x2d,0x4d,0x6d,0xed) and address==last:
            accesses.append(dict(PC=d.pc,bank=tag,opcode=op))
        if op==0x8d and address in (last,pending):pending_writes.append(dict(PC=d.pc,bank=tag,address=address,value=d.a))
        if op==0x20:reached.append(dict(PC=d.pc,bank=tag,target=address))
        tags[tag]+=1;d.step()
    else:raise AssertionError('Actual acquisition return bound')
    assert not accesses,accesses
    assert cut['choice_before']==0 and z[last]==0xc0 and z[pending]==0xc0
    assert pending_writes[0]['address']==pending and pending_writes[0]['value']==0
    assert pending_writes[-1]['address']==pending and pending_writes[-1]['value']==0xc0
    assert sum(row['address']==last for row in pending_writes)==2
    points={}
    for name in ('SamusFreezeRenderFinish','SamusFreezeInit','SamusFreezeDrawAll','PnPaletteScreenUpdate','NonMaskableInterrupt'):
        pc,at=W.address(b,name),W.location(b,name)
        assert at>=16 and actual[at:at+16]==reference[at:at+16]
        points[name]=dict(PC=pc,file=at,head=actual[at:at+16].hex())
    result=dict(actual_ROM_SHA256=PIN,reference_only_SHA256=Bowser.PIN,execution_raw_is_actual=True,
        carrier_SHA256=Bowser.digest(q['carrier']),acquire_hex=acquire.hex(),sole_private_Acquire_call=calls,
        last_blue_native_raw_word_candidates=scan_words(actual,last),last_blue_kernel_word_candidates=kernel_words,
        actual_acquisition=dict(incoming_busy=cut['busy'],incoming_LastBlue=cut['last_before'],incoming_Choice=cut['choice_before'],
            instructions=step,bank_steps=dict(tags),synchronous_LastBlue_readers=accesses,
            validity_and_LastBlue_stores=pending_writes,actual_JSR_targets=reached,
            final_LastBlue=z[last],final_Pending=z[pending],complete_return_PC=d.pc,complete_return_SP=d.sp),
        native_points=points,scope='Current instructions only; no dirty-marker arrays or new opcode/ISR qualification',
        source_pins={str(SOURCE):SOURCE_SHA,str(HOST):HOST_SHA},outputs=0)
    encoded=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+encoded,flush=True);print('RECEIPT_SHA256 '+Bowser.digest(encoded.encode()),flush=True)

if __name__=='__main__':main()
