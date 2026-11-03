"""Measure source-funded pure reject veneers, without an auth cache or ROM.

The current owner/body/header contract is unchanged for every mapped service.
Only owner39's literally CLC/RTS rows9/34 can reject in trusted resident code.
"""
from collections import Counter
import inspect,json
from pathlib import Path
import profile_bub_current_bridge_1103_v69 as C
import measure_bub_resident_compaction_1102_v49 as F
O,R,N,Q,address,sha=C.O,C.R,C.N,C.Q,C.address,C.sha


def build():
    b,route,q,head,manifest,rom=C.bundle()
    # Reuse the source-exact compaction transformations, not a stale blob.
    # Both current cookies and every original byte are reproduced first.
    text=inspect.getsource(F.build)
    before="_,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes'"
    assert text.count(before)==1
    text=text.replace(before,"b,route,layout,head,manifest,rom=C.bundle()")
    text=text.replace('auth-frame-v49-','constant-reject-v70-')
    env=dict(F.__dict__,C=C,PIN=C.PIN);exec(compile(text,str(Path(__file__)),'exec'),env)
    old,compact,layout,route,oldlabels,labels,free,refs=env['build']()
    source=(O/'constant-reject-v70-compact.s').read_text()
    stub='''CoConstantReject:
 php
 pha
 lda SelectedCharacter
 cmp #39
 bne CoConstantOther
 pla
 plp
 clc
 rts
CoConstantOther:
 pla
 plp
 jmp $a740
'''
    before='CoFundingStart:\n .res 20,$ea\n';assert source.count(before)==1
    source=source.replace(before,'CoFundingStart:\n'+stub+' .res 2,$ea\n')
    source+='\n.export CoConstantReject,CoConstantOther\n'
    cfg=(O/'constant-reject-v70-compact.cfg').read_text()
    newlabels=F.L.assemble('constant-reject-v70-final',source,cfg)
    owner=(O/'constant-reject-v70-final.bin').read_bytes();assert len(owner)==531
    assert newlabels['CoConstantReject']==labels['CoFundingStart']
    assert newlabels['CoSmc']-newlabels['CoConstantReject']==20
    raw=bytearray(compact['raw']);at=16+65*8192+0xe00;raw[at:at+531]=owner
    targets=[]
    for row in[9,34]:
        at=16+65*8192+(0xb08c+3*row&8191)
        assert raw[at:at+3]==bytes.fromhex('4c40a7')
        targets.append(dict(row=row,CPU=0xb08c+3*row,file_offset=at,old=raw[at:at+3].hex(),
            new=(bytes([76])+newlabels['CoConstantReject'].to_bytes(2,'little')).hex()))
        raw[at:at+3]=bytes([76])+newlabels['CoConstantReject'].to_bytes(2,'little')
    # The current two private implementations are identical literal pure
    # CLC/RTS, not a behavior inferred from empty-arena observations.
    image=(rom.parent/'private-image.bin').read_bytes()
    assert image[9*3:9*3+3]==image[34*3:34*3+3]==bytes.fromhex('4c7cb5')
    assert image[0x157c:0x157e]==bytes.fromhex('1860')
    return old,dict(old,raw=bytes(raw)),route,layout,oldlabels,newlabels,targets,refs


def same(a,z,outputs):
    assert[outputs[0][k]for k in['A','X','Y','P']]==[outputs[1][k]for k in['A','X','Y','P']]
    assert a.ram==z.ram and a.rawtags==z.rawtags
    assert bytes(a[3:11])==bytes(z[3:11])and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])
    assert bytes(a[0x200:0x800])==bytes(z[0x200:0x800])


def main():
    destination=O/'constant-reject-v70-measurement.json';assert not destination.exists()
    old,new,route,q,oldlabels,newlabels,targets,refs=build()
    actual=N.NesMPU;seeds={};direct=0;poisons=0;foreign=0;maincases=[]
    for identity in[0,1]:seeds[identity]=[Q.Q.fresh(bb,route,identity)for bb in[old,new]]
    # Whole public veneer/FarCallCommon inputs and every native flag bit.
    # Cold/warm identity/header state never acts as an implicit lease.
    for row in[9,34]:
        for identity in[0,1]:
            for flags in[0x20,0x21,0x22,0x61,0xa1,0xe1]:
                for a,x,y in[(0,0,0),(83,7,14),(255,255,255)]:
                    pair=[N.fork(m)for m in seeds[identity]];out=[]
                    for m in pair:out.append(F.C.call(m,0xb08c+row*3,flags=flags))
                    same(*pair,out);assert not out[0]['P']&1;direct+=1
            for bank in[2,3]:
                for offset in range(16):
                    pair=[N.fork(m)for m in seeds[identity]];out=[]
                    for m in pair:
                        m.ram[bank][0x1fe0+offset]^=1
                        out.append(F.C.call(m,0xb08c+row*3,flags=0x71))
                    same(*pair,out);assert not out[0]['P']&1;poisons+=1
        for raw in range(256):
            if raw==39:continue
            pair=[N.fork(m)for m in seeds[0]];out=[]
            for m in pair:
                N.put(m,SelectedCharacter=raw);out.append(F.C.call(m,0xb08c+row*3,flags=0xe1))
            same(*pair,out);foreign+=1
    # Genuine full Main keeps original donor/bridge/draw/input instruction
    # traces. Remove only the explicitly eliminated private vector+CLC/RTS.
    excluded={0xa01b,0xa066,0xb57c,0xb57d}
    for identity in[0,1]:
        for name,keys in[('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[Q.Q.fresh(bb,route,identity)for bb in[old,new]];traces=[];outputs=[];auth=[]
            for index,m in enumerate(pair):
                Q.L.E.main_fields(m);trace=[];count=0
                class Trace(actual):
                    def step(self):
                        nonlocal count
                        mm=self.memory;pc=self.pc;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                        if bank==193 and pc==(oldlabels if index==0 else newlabels)['CoCheckCode']:count+=1
                        if bank==3 and 0xa000<=pc<0xbfe0 and pc not in excluded or bank==2 and 0xd320<=pc<0xd400:
                            trace.append((bank,pc,self.a,self.x,self.y,self.p,self.sp))
                        return super().step()
                N.NesMPU=Trace
                try:
                    out=[]
                    for epoch in range(12):
                        held=(keys&127)|(128 if keys&128 and epoch==1 else 0)
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=held,SavedJoypad1Bits=held,VRAM_Buffer1_Offset=0)
                        out.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
                    outputs.append(out)
                finally:N.NesMPU=actual
                traces.append(trace);auth.append(count)
            same(*pair,[out[-1]for out in outputs])
            assert traces[0]==traces[1],(identity,name,'Donor/bridge/draw/input instruction AXYP/SP')
            for out in zip(*outputs):assert[out[0][k]for k in['A','X','Y','P']]==[out[1][k]for k in['A','X','Y','P']]
            before=sum(out['CPU']for out in outputs[0])/12;after=sum(out['CPU']for out in outputs[1])/12
            maincases.append(dict(identity=identity,phase=name,Main_updates=12,baseline_CPU=before,
                proposed_CPU=after,saving_CPU=before-after,saving_percent=100*(before-after)/before,
                full_auth_calls=auth,trace_entries=len(traces[0]),AXYP_SP_draw_input_private_native_R0_7_SMC_maps_exact=True))
            print('Constant reject Main',identity,name,before,after,'saving',before-after,auth,flush=True)
    result=dict(passed=True,proposal_only=True,CPU_qualified=False,candidate_allowed=False,
        ROM_written=False,source_mutated=False,cache_used=False,new_RAM_used=False,
        base_ROM_SHA256=C.PIN,memory_only_SHA256=sha_bytes(new['raw']),
        owner_bytes=531,stub_bytes=18,source_compaction_contiguous_bytes=20,remaining_contiguous=2,
        preserved_fixed_entries=['CoCold AE00','CoRetire AE0B','SMC AFE6','cookies AFF3/B003'],
        direct_public_cases=direct,all_header_byte_poison_cases=poisons,foreign_raw_cases=foreign,
        Main_cases=maincases,veneer_patches=targets,auth_JSR_operand_rebindings=refs,
        scope='Pure owner39 rows9/34 only, literal CLC/RTS both with valid headers and at auth rejection. Every real mapped service still performs full two-header authentication. No lease, new RAM, donor timing or physics change. Exact current531B manager preimage reproduced, then old49 source compaction funds18B resident stub. Memory-only resource proposal, not granted candidate.',
        remaining=['Full current resident private-alias/caller closure and all changed cold/retire/farcall paths/IRQ/lagNMI proof before candidate grant.','Root resource review and exact native performance/hardware qualification.'],
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(C.__file__),Path(F.__file__),
            O/'current-bridge-profile-v69.json',O/'constant-reject-v70-reproduce.s',O/'constant-reject-v70-reproduce.bin',
            O/'constant-reject-v70-final.s',O/'constant-reject-v70-final.bin',O/'constant-reject-v70-final.lbl']})
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in['passed','proposal_only','stub_bytes','direct_public_cases','all_header_byte_poison_cases','foreign_raw_cases']}),flush=True)


def sha_bytes(data):return __import__('hashlib').sha256(data).hexdigest()


if __name__=='__main__':
    try:main()
    except AssertionError as error:
        manifest=R/'build/bub-initial-tier-1103-v87/proposal.json';init=json.loads(manifest.read_text())
        rom=R/init['candidate'];assert sha(rom)==C.PIN
        image=(rom.parent/'private-image.bin').read_bytes()
        (O/'constant-reject-v70-negative.json').write_text(json.dumps(dict(passed=False,
            proposal_rejected=True,ROM_written=False,shared_source_mutated=False,base_ROM_SHA256=C.PIN,
            exception=repr(error),vector9=image[27:30].hex(),vector34=image[102:105].hex(),
            actual_target_B57C=image[0x157c:0x157e].hex(),expected_reject='1860',
            diagnosis='Actual current B57C is SEC/RTS, not CLC/RTS. Valid authentication claims these policies; failed authentication rejects. Therefore the proposed pre-auth pure-reject shortcut violates the current bad-header contract and is not admitted.',
            bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(C.__file__),rom,O/'current-bridge-profile-v69.json']}),indent=2)+'\n')
        raise
