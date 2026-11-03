"""Actual native unbanked-header reader and changed flag continuation."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_body_cold_1103_v181 as C
M,V,N,I,O=C.M,C.V,C.N,C.I,C.O


def main():
    base,q=M.image();parent=dict(base,raw=M.PARENT.read_bytes())
    reader=I.address(base,'RosterProjectileOamReady')+12
    at=I.location(base,'RosterProjectileOamReady')+12
    assert base['raw'][at:at+2]==bytes.fromhex('b103')
    e,seed,lab=C.first8(base);N.put(seed,ObjectMetasprite=0x91)
    actual=N.NesMPU;events=[]
    class NativeTrace(actual):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
            if tag==132 and self.pc==reader:
                ptr=m[3]+256*m[4]
                events.append(dict(event='actual_native_reservation_indirect_read',PC=self.pc,Amap=m.rawtags[1],Cmap=m.rawtags[2],SP=self.sp,pointer=ptr,value=m[ptr],ObjectMetasprite=N.get(m,'ObjectMetasprite')))
                assert ptr==0x6e1 and m[ptr]==0 and m.rawtags[2]!=2
            if tag==132 and self.pc==0xa229:
                raise AssertionError('Corrected native draw must skip original PlayerChrBank store')
            if tag==3 and 0xbdc3<=self.pc<0xbde1:
                assert m.rawtags[2]==2
            return super().step()
    N.NesMPU=NativeTrace
    try:out=e['run'](seed,'GameLoop',lab)
    finally:N.NesMPU=actual
    assert len(events)==1 and N.get(seed,'ObjectMetasprite')==0
    assert N.get(seed,'PlayerChrBank')==85 and seed.ram[2][0x6cf]==5
    # Full source-backed old/new leaf continuation over every aligned OAM
    # origin and both inputC/V values. Native input fixtures are explicit.
    _,old,_=C.loaded(parent);_,new,_=C.loaded(base)
    rows=json.loads((O/'measurement.json').read_text())['patches'];call=rows[0]['CPU'];cases=0;executed=0;flags=[]
    consumers={'C':{'ADC','SBC','ROL','ROR','BCC','BCS'},'V':{'BVC','BVS'}}
    writers={'C':{'ADC','SBC','ASL','LSR','ROL','ROR','CLC','SEC','CMP','CPX','CPY','PLP','RTI'},'V':{'ADC','SBC','BIT','CLV','PLP','RTI'}}
    mode='old';continuations={};active=False
    class FlagTrace(actual):
        def step(self):
            nonlocal active
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
            if tag==3 and self.pc==call+4:
                active=True;continuations[mode]={'entry_flags':self.p,'first_writer':{},'first_consumer':{}}
            if active:
                row=continuations[mode];mn=self.disassemble[m[self.pc]][0]
                for bit in ['C','V']:
                    if mn in writers[bit]and bit not in row['first_writer']:row['first_writer'][bit]=[self.pc,mn,self.p]
                    if mn in consumers[bit]and bit not in row['first_consumer']:row['first_consumer'][bit]=[self.pc,mn,(self.p&(1 if bit=='C'else 64))!=0]
                if len(row['first_consumer'])==2:active=False
            return super().step()
    for cursor in range(0,256,4):
        for p in [0x20,0x21,0x60,0x61]:
            pair=[N.fork(old),N.fork(new)];outs=[];continuations={}
            for mode,m in zip(['old','new'],pair):
                m.raw_page(2,2);N.put(m,CurrentBankC=2,CurrentOAMOffset=cursor,GuestOamRotationActive=1,RgOamRotation=0)
                m.ram[2][0x617]=15;m.ram[2][0x615]=255
                m[3:11]=old[3:11];m[0x15a:0x17b]=old[0x15a:0x17b];m[0x200:0x300]=bytes([0xf8])*256
                I.invoke(m,3,lab['PpHostProject'],(83,71,109,p))
                I.invoke(m,3,0xc383,(83,71,109,p))
                active=False;N.NesMPU=FlagTrace
                try:outs.append(I.invoke(m,3,lab['PpHostDraw'],(83,71,109,p)))
                finally:N.NesMPU=actual
            assert outs[0]['regs']==outs[1]['regs']and bytes(pair[0][0x200:0x300])==bytes(pair[1][0x200:0x300])
            assert bytes(pair[0][3:11])==bytes(pair[1][3:11])and bytes(pair[0][0x15a:0x17b])==bytes(pair[1][0x15a:0x17b])
            if continuations:
                assert set(continuations)=={'old','new'}
                assert continuations['old']['first_consumer']==continuations['new']['first_consumer'],continuations
                executed+=1
                if cursor in [0,112,116,120,124,128,232]:flags.append(dict(cursor=cursor,inputP=p,continuations=continuations))
            cases+=1
    assert cases==256 and executed>0
    result=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,memory_SHA256=q['expected_memory_only_SHA256'],
                native_unbanked_reader=events,whole_Main_minimum_SP=out['minSP'],original_late_native_bank0_store_skipped=True,
                aligned_OAM_input_CV_cases=cases,accepted_renderer_continuations=executed,exact_first_CV_consumer_flags=True,flag_samples=flags,
                table_consumer=dict(source='grid-render-labels-v37.s PhysicalHi, exact31B atBDC3..BDE2',old_direct_reader=call,new_direct_readers=0,finite_immutable_pose_index_domain=list(range(31)),original_script_bounds=[0xb400,0xbae5],original_source_scripts_and_15_command_targets_unchanged=True,new_indirect_targets=False),
                lifetime='Only authenticated Prince public route reaches GraphicsCheck; only its own draw reaches Upper. Existing overlay constructor/retire/header protocol is unchanged. Helper bytes are immutable source-backed runtime, outside all source state and immutable original-script byte bounds. ObjectMetasprite/SmPosePtr are existing native graphics interface fields. Their zeroheader target06E1 is unbanked and stays valid through actual later A4/nativeROM-C reader; nativebody branch then skips PlayerChrBank overwrite. Foreign retirement invalidatesPrinceheaders before replacement and keeps existing foreign graphics initialization.',
                required='Actual newpath IRQ/genuineFF/nested and root source/lifetime review, then real native hardware allbody validation.',
                bindings={str(p.relative_to(R)):M.B.sha(p)for p in [Path(__file__),Path(C.__file__),O/'body-manifest-v180.json',O/'measurement.json',O/'body-owner.s',V.O/'grid-render-labels-v37.s',V.O/'contact-core.s',R/'src/metasprite_engine.s',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json']})
    (O/'reader-flag-CPU-v182.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','flag_samples']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'reader-flag-negative-v182.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n');raise
