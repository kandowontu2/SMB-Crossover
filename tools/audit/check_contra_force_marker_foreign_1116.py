"""Same-context6a3/ffbb public foreign behavior; foreign need not be NoOp."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_p1_work_marker_model_1116 as M

C,N,W=M.C,M.N,M.W


def reimage(seed,raw):
    z=N.fork(seed);z.bundle=M.symbols(raw)
    for slot,tag in enumerate(z.rawtags):
        if tag&128:z.raw_page(slot,tag)
    carrier=raw[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
    z.ram[1][:]=carrier[:8192];z.ram[3][:]=carrier[16384:24576]
    cookie=bytearray(raw[573373:573389]);cookie[2]=(N.get(z,'FmGroups')>>3)&3
    z.ram[2][0x1fe0:0x1ff0]=cookie
    return z


def run(raw):
    parent=M.parent(raw);seed=M.cold(raw);d=C.Plan.descriptor(parent);ranges=[tuple(f['CPU_half_open'])for f in d['fragments']]
    assert seed.ram[2][0x2df]==0,'Use the same completed warm logical state, not a constructor work-bit allowance'
    base=N.NesMPU;counter=Counter();ctx={};foreign_draws=[];minimum=255
    class Observe(base):
        def step(self):
            m=self.memory
            if self.pc>=0xa000 and m.rawtags[(self.pc-0x8000)//8192]==3 and any(lo<=self.pc<hi for lo,hi in ranges):counter[ctx['case'],ctx['version']]+=1
            return super().step()
    for selected in range(256):
        if selected==31:continue
        pair=[];ctx['case']=selected
        for version,image in enumerate((parent,raw)):
            ctx['version']=version;m=reimage(seed,image);N.put(m,SelectedCharacter=selected)
            before_OAM=bytes(m[512:768]);before_CF=[bytes(m.ram[i])for i in(1,2,3)]
            with patch.object(N,'NesMPU',Observe):q=N.invoke(m,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
            minimum=min(minimum,q['minimum_SP']);assert counter[selected,version]==0,(selected,version,'Foreign entered CF code')
            # Every owning-cache byte, including code, stays at its bound
            # preimage; legitimate native/foreign OAM work is compared below.
            assert[bytes(m.ram[i])for i in(1,2,3)]==before_CF,(selected,version,'Foreign changed CF cache')
            pair.append((m,q,bytes(m[512:768])!=before_OAM))
        a,b=pair
        assert a[1]==b[1],('Foreign full public result',selected,a[1],b[1])
        assert bytes(a[0][:0x8000])==bytes(b[0][:0x8000]),('Foreign all lowRAM/stack/SMC/OAM/protocol',selected)
        assert a[0].rawtags==b[0].rawtags
        assert bytes(a[0].ram[1])==bytes(b[0].ram[1])
        assert a[0].ram[2][:0x1fe0]==b[0].ram[2][:0x1fe0]and a[0].ram[2][0x1ff0:]==b[0].ram[2][0x1ff0:]
        assert a[2]==b[2]
        if a[2]:foreign_draws.append(selected)
    # Owning cache faults, unlike foreign dispatch, must not execute CF or
    # mutate its OAM/state. Both full independent checks remain in the ROM.
    for i in range(16):
        m=N.fork(seed);m.ram[2][0x1fe0+i]^=1;ctx.update(case='header'+str(i),version=1)
        before_OAM=bytes(m[512:768]);before_CF=[bytes(m.ram[k])for k in(1,2,3)]
        with patch.object(N,'NesMPU',Observe):q=N.invoke(m,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
        assert not q['P']&1 and not counter[ctx['case'],1]
        assert bytes(m[512:768])==before_OAM and[bytes(m.ram[k])for k in(1,2,3)]==before_CF
    m=reimage(seed,parent);m.bundle=M.symbols(raw)
    for slot,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(slot,tag)
    ctx.update(case='old-warm',version=1)
    with patch.object(N,'NesMPU',Observe):q=N.invoke(m,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
    assert not q['P']&1 and not counter['old-warm',1]
    # Actual owning public draw/status invokes the real packet/CfCallA.
    m=N.fork(seed);ctx.update(case='valid',version=1)
    with patch.object(N,'NesMPU',Observe):
        draw=N.invoke(m,'NrDraw',a=0x53,x=0x17,y=0x8d,p=0x21)
        assert draw['P']&1 and counter['valid',1]>0 and m.ram[2][0x2df]&128
        status=N.invoke(m,'NrInjuryStatus',a=0x53,x=0x17,y=0x8d,p=0x20)
    assert not m.ram[2][0x2df]&128 and not any(m[514+i*4]&24 for i in range(64))
    assert m[W.address(m.bundle,'SmFreezeLastBlue')]==192
    return dict(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,foreign_selected_cases=255,
        same_genuine_completed_warm_prefix_coupled_only_code_and_full_expected_header=True,
        foreign_actual_public_AXYP_cycles_minSP_lowRAM_stack_all33SMC_OAM_protocol_all_unowned_data_exact=True,
        both_sides_zero_CF_new_instruction_entries_and_own_cache_writes=True,
        foreign_native_OAM_publication_preserved_for_selected_values=foreign_draws,minimum_SP=minimum,
        all16_own_header_faults_and_full_old_warm_code_cache_rejected=True,
        valid_owning_public_Draw_Status_actual_CfCallA_and_full_packet=True,
        native=False,outputs=0,scope='Explicit same foreign component contexts, not all natural foreign transitions')


if __name__=='__main__':
    parent=C.load_current_image();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Foreign guard proof attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
