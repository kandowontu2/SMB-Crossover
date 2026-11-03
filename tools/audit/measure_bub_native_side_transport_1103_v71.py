"""Full-auth fixed native Side transport, source-funded memory proposal only."""
import inspect,json
from pathlib import Path
import profile_bub_current_bridge_1103_v69 as C
import measure_bub_resident_compaction_1102_v49 as F
O,R,N,Q,address,sha=C.O,C.R,C.N,C.Q,C.address,C.sha


def build():
    b,route,q,head,manifest,rom=C.bundle();text=inspect.getsource(F.build)
    before="_,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes'";assert text.count(before)==1
    text=text.replace(before,"b,route,layout,head,manifest,rom=C.bundle()").replace('auth-frame-v49-','native-side-v71-')
    env=dict(F.__dict__,C=C,PIN=C.PIN);exec(compile(text,str(Path(__file__)),'exec'),env)
    old,compact,layout,route,oldlabels,labels,free,refs=env['build']()
    source=(O/'native-side-v71-compact.s').read_text()
    def once(a,z):
        nonlocal source
        assert source.count(a)==1,a;source=source.replace(a,z)
    # All three factored cold imports overwrite incoming A before using it.
    worker=16+123*8192+(0xaf40&8191);assert old['raw'][worker:worker+2]==bytes.fromhex('a902')
    image=(rom.parent/'private-image.bin').read_bytes()
    retire=q['labels']['BbNativeRetire']-0xa000;restore=q['labels']['BbNativeProxyRestore']-0xa000
    assert image[retire:retire+5]==bytes([0xa2,0,0x20])+q['labels']['BbNativeProxyRestore'].to_bytes(2,'little')
    assert image[restore]==0x20
    validate=int.from_bytes(image[restore+1:restore+3],'little')-0xa000
    assert image[validate:validate+8]==bytes.fromhex('e006b0278ec0c38a') # CPX6/BCS/STX/TXA, X0 first.
    publisher=16+62*8192+0x3d;assert old['raw'][publisher:publisher+3]==bytes.fromhex('adee73')
    once('CoFarIndexed:\n sta SafecallA_SMC+1\n','CoFarIndexed:\n')
    # Zero-page indexed addition wraps at256: F8..FF plus0B addresses03..0A.
    once(' ldx #0\n:\n lda R0,x\n pha\n inx\n cpx #8\n bne :-\n',
        ' ldx #$f8\n:\n lda R0+8,x\n pha\n inx\n bne :-\n')
    once('CoSelect:\n lda SelectedCharacter\n cmp #37\n beq CoSelectEx\n cmp #39\n bne CoSelectNo\n ldx #1\n bne CoSelectOwner\nCoSelectEx:\n ldx #0\nCoSelectOwner:\n',
        'CoSelect:\n lda SelectedCharacter\n and #$fd\n cmp #37\n bne CoSelectNo\n lda SelectedCharacter\n lsr\n and #1\n tax\nCoSelectOwner:\n')
    once('CoDescriptorHiFunding:.byte $ea,$ea\n','CoDescriptorHiFunding:\n')
    stub='''CoNativeSide:
 php
 pha
 txa
 pha
 tya
 pha
 jsr CoCheckCode
 bcc CoNativeSideNo
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $958b
CoNativeSideNo:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
CoNativeSideEnd:
'''
    once('CoFundingStart:\n .res 20,$ea\n','CoFundingStart:\n'+stub)
    source+='\n.export CoNativeSide,CoNativeSideNo,CoNativeSideEnd\n'
    final=F.L.assemble('native-side-v71-final',source,(O/'native-side-v71-compact.cfg').read_text())
    owner=(O/'native-side-v71-final.bin').read_bytes();assert len(owner)==531
    assert final['CoNativeSideEnd']-final['CoNativeSide']==28 and final['CoSmc']==0xafe8
    for name in['CoCold','CoRetire','CoOwnerEnd']:assert final[name]==oldlabels[name]
    raw=bytearray(old['raw']);at=16+65*8192+0xe00;raw[at:at+531]=owner
    # Only two current real dispatcher instructions read the saved-SMC table;
    # the one auth JSR is the already established source-backed alias consumer.
    bank=bytearray(raw[16+65*8192:16+66*8192]);changes=[]
    for needle,value,want in[(bytes([0x20])+oldlabels['CoCheckCode'].to_bytes(2,'little'),final['CoCheckCode'],1),
                             (bytes([0xbc])+oldlabels['CoSmc'].to_bytes(2,'little'),final['CoSmc'],2)]:
        sites=[i for i in range(8190)if bank[i:i+3]==needle];assert len(sites)==want,(needle.hex(),sites)
        for i in sites:
            changes.append(dict(bank_offset=i,old=bank[i:i+3].hex(),new=(bytes([needle[0]])+value.to_bytes(2,'little')).hex()))
            bank[i+1:i+3]=value.to_bytes(2,'little')
    side=0xb08c+3*14;assert bank[side&8191:(side&8191)+3]==bytes.fromhex('4c40a7')
    changes.append(dict(bank_offset=side&8191,old='4c40a7',new=(bytes([76])+final['CoNativeSide'].to_bytes(2,'little')).hex()))
    bank[side&8191:(side&8191)+3]=bytes([76])+final['CoNativeSide'].to_bytes(2,'little')
    raw[16+65*8192:16+66*8192]=bank
    assert raw[at+0x1f3:at+531]==old['raw'][at+0x1f3:at+531]
    # Both immutable private vectors are proved from actual carrier bytes.
    assert image[42:45]==bytes.fromhex('4c8b95')
    ex=1048592+729*1024+0x12a;assert old['raw'][ex:ex+3]==bytes.fromhex('4cd8ae')
    leaf=1048592+731*1024+0x2d8;assert old['raw'][leaf:leaf+3]==bytes.fromhex('4c8b95')
    return old,dict(old,raw=bytes(raw)),route,q,oldlabels,final,changes


def parity(a,z,out):
    assert[out[0][k]for k in['A','X','Y','P']]==[out[1][k]for k in['A','X','Y','P']],out
    assert a.ram==z.ram and a.rawtags==z.rawtags
    assert bytes(a[3:11])==bytes(z[3:11])and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])
    assert bytes(a[0x200:0x800])==bytes(z[0x200:0x800])


def main():
    destination=O/'native-side-v71-measurement.json';assert not destination.exists()
    old,new,route,q,oldlabels,final,changes=build();cases=[];bad=0;foreign=0;direct=0
    for owner in[37,39]:
        seeds=[]
        for bb in[old,new]:
            m=F.C.ready(bb);N.put(m,SelectedCharacter=owner);assert F.C.call(m,0xae00)['P']&1;seeds.append(m)
        for y in range(256):
            pair=[N.fork(m)for m in seeds];out=[]
            for m in pair:out.append(N.invoke(m,'HuSide',a=(y*13)&255,x=7,y=y,p=0x71))
            parity(*pair,out);direct+=1
        for bank in[2,3]:
            for i in range(16):
                pair=[N.fork(m)for m in seeds];out=[]
                for m in pair:
                    m.ram[bank][0x1fe0+i]^=1;out.append(N.invoke(m,'HuSide',a=83,x=7,y=14,p=0xe1))
                parity(*pair,out);assert not out[0]['P']&1;bad+=1
    seeds=[Q.Q.fresh(bb,route,0)for bb in[old,new]]
    for raw in range(256):
        if raw in[37,39]:continue
        pair=[N.fork(m)for m in seeds];out=[]
        for m in pair:N.put(m,SelectedCharacter=raw);out.append(F.C.call(m,0xb0b6,flags=0xe1))
        parity(*pair,out);foreign+=1
    actual=N.NesMPU
    for identity in[0,1]:
        for phase,keys in[('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[Q.Q.fresh(bb,route,identity)for bb in[old,new]];traces=[];outputs=[];auth=[]
            for index,m in enumerate(pair):
                Q.L.E.main_fields(m);trace=[];count=0
                class Trace(actual):
                    def step(self):
                        nonlocal count
                        mm=self.memory;pc=self.pc;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                        if bank==193 and pc==(oldlabels if index==0 else final)['CoCheckCode']:count+=1
                        if bank==3 and 0xa100<=pc<q['labels']['BbCodeEnd']or bank==3 and 0xb540<=pc<0xbfe0 or bank==2 and 0xd320<=pc<0xd400:
                            # Ex37 and Bub39 side vector/JMP are the sole
                            # removed private instructions; source, other
                            # bridge/draw/input SP and AXYP remain exact.
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
            parity(*pair,[out[-1]for out in outputs]);assert traces[0]==traces[1],(identity,phase,'source/bridge/input/draw AXYP/SP')
            for out in zip(*outputs):assert[out[0][k]for k in['A','X','Y','P']]==[out[1][k]for k in['A','X','Y','P']]
            before=sum(out['CPU']for out in outputs[0])/12;after=sum(out['CPU']for out in outputs[1])/12
            assert auth==[156,156],auth
            row=dict(identity=identity,phase=phase,Main_updates=12,baseline_CPU=before,proposal_CPU=after,
                saving_CPU=before-after,saving_percent=100*(before-after)/before,full_auth_calls=auth,
                original_bridge_draw_input_trace_entries=len(traces[0]),AXYP_SP_SMC_R0_7_maps_native_private_exact=True)
            cases.append(row);print('Native side Main',identity,phase,before,after,before-after,flush=True)
    result=dict(passed=True,proposal_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        source_mutated=False,cache_used=False,new_RAM_used=False,base_ROM_SHA256=C.PIN,
        memory_only_SHA256=__import__('hashlib').sha256(new['raw']).hexdigest(),owner_bytes=531,
        direct_side_bytes=28,source_funding=dict(old_current_source_compaction=20,redundant_incoming_A_store=3,
            exact_zero_page_wrap_save=2,exact_37_39_owner_selection=1,retired_descriptor_hi_table=2),
        moved_saved_SMC_table=[oldlabels['CoSmc'],final['CoSmc']],current_native_Side_all_Y_cases=direct,
        header_poison_rejections=bad,foreign_public_veneer_cases=foreign,Main_cases=cases,changed_operands=changes,
        scope='Full two-header authentication retained13times/Main. Shared37/39 row14 invokes its identical immutable fixed958B getter directly, without mapping privateA3/C2 or snapshotting fiveSMC bytes around a pure getter. It returns through the existing outer farcall. Fixed getter uses only fixed tables and low native block buffers, no farcalls/SMC/header writes or SP-relative access. Source-funded28B remains within the existing531B owner frame; cold/retire public addresses and cookies fixed. No obsolete dispatcher-tail lease, no auth cache, donor timing/physics/profile change.',
        remaining=['Full whole531B private-alias/reference closure, cold/retire import ABI/readback/fault/source-trap diffs and all changed actualIRQ/FF/nested cuts before candidate grant.','Native performance and affectedEx/Bub/Bob source controls/fullstage checks after source qualification.'],
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(C.__file__),Path(F.__file__),
            O/'current-bridge-profile-v69.json',O/'native-side-v71-reproduce.s',O/'native-side-v71-reproduce.bin',
            O/'native-side-v71-final.s',O/'native-side-v71-final.bin',O/'native-side-v71-final.lbl',
            R/'src/collision.s',R/'tools/reference/excitebike_native_boundary_1101_v1.inc']})
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in['passed','direct_side_bytes','current_native_Side_all_Y_cases','header_poison_rejections','foreign_public_veneer_cases']}),flush=True)


if __name__=='__main__':main()
