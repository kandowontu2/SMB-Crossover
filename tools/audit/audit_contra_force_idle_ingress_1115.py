"""Current CF symbolic/vector ingress and existing real ISR SMC preservation."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_idle_dispatch_1115 as P

C,W,N=P.C,P.W,P.N
SOURCE_PINS={P.P.KERNEL/'p1-runtime.s':'e15911ff74498252b944ce25075ff80706214729197a0b0b219ab250247e2483',
    C.R/'build/contra-force-p1-kernel-v1/a2-router.s':'410d81b56f20bbff77c1732164a9879395aef8ce3d2ee6daf6c9c7be76ce56c2'}


def static(raw):
    q,labels=P.bindings(raw)
    for path,pin in SOURCE_PINS.items():assert C.H(path.read_bytes())==pin
    lines={};symbols={};segments={}
    for line in(P.P.KERNEL/'runtime.dbg').read_text().splitlines():
        if line.startswith('line\t'):
            row=P.P.fields(line);lines[int(row['id'])]=row
        elif line.startswith('seg\t'):
            row=P.P.fields(line);segments[int(row['id'])]=row
        elif line.startswith('sym\t'):
            row=P.P.fields(line)
            if'val'in row and row.get('name')in('CfP1Late','CfA2Return','CfHaveIndex','CfDivide3','CfBadCookie'):
                symbols[row['name']]=row
    refs=[]
    for name,row in symbols.items():
        allowed=15 if name=='CfP1Late'else 13
        for number in map(int,row['ref'].split('+')):
            line=lines[number];assert int(line['file'])==allowed
            refs.append(dict(symbol=name,PC=int(row['val'],0),source_file_id=allowed,source_line=int(line['line']),
                kind='instruction_or_data'if'span'in line else'export_declaration',span=line.get('span')))
    leaf=[r for r in refs if r['symbol']=='CfP1Late']
    assert len(leaf)==2 and sorted(r['kind']for r in leaf)==['export_declaration','instruction_or_data']
    old,_,_,_=P.router(raw);targets=[old[0xbf49-P.ROUTER_BASE+i]+256*old[0xbf6d-P.ROUTER_BASE+i]for i in range(36)]
    assert targets[6]==0xbe53 and not set(int(row['val'],0)for row in symbols.values()).intersection(targets)
    assert q['carrier'][8192+0x1e00:8192+0x1e6c]==bytes.fromhex('4c6ebe')*36
    words=[]
    for bank in(1,2,3):
        block=q['carrier'][(bank-1)*8192:bank*8192];at=0
        while True:
            at=block.find(bytes.fromhex('80be'),at)
            if at<0:break
            owners=[s['name']for s in segments.values()if s.get('oname')==f'ram{bank}.bin'and int(s['ooffs'])<=at<int(s['ooffs'])+int(s['size'],0)]
            words.append(dict(physical_RAM=bank,offset=at,owners=owners,preceding_hex=block[max(0,at-5):at+5].hex()));at+=1
    public=[];b=q['bundle']
    for name,pc,bank,size in(('BtServiceVeneers',0xb020,87,224),('WfResolve',0xb799,96,175),('BwBtResolve',0xb22b,67,213)):
        at=16+bank*8192+(pc&8191)
        public.append(dict(name=name,physical_PRG=bank,PC=pc,file=at,bytes=size,SHA256=C.H(raw[at:at+size]),hex=raw[at:at+size].hex()))
    return dict(owning_ROM_SHA256=C.CANDIDATE,retained_compiled_source_pins={str(k):v for k,v in SOURCE_PINS.items()},
        compiled_symbolic_moved_label_references=refs,public36_JMP_veneers_and_all36_private_targets_unchanged=True,
        actual_private_service6_target=targets[6],private_36_targets=targets,
        old_leaf_word_leads_in_three_CF_images=words,
        exact_existing_shared_resolver_preimages=public,
        symbolic_and_authoritative36vector_domain_only_not_blanket_literal_absence_claim=True)


def smc(raw):
    m=P.P.cold(raw);base=N.NesMPU;cuts={}
    class Capture(base):
        def step(self):
            if self.pc==0xbeb8 and m.rawtags[1]==2 and m[0x16c]in(0,87,102)and m[0x16c]not in cuts:
                z=N.fork(m);d=base(memory=z,pc=self.pc)
                for n in('a','x','y','p','sp','processorCycles'):setattr(d,n,getattr(self,n))
                cuts[m[0x16c]]=(z,d)
            return super().step()
    with patch.object(N,'NesMPU',Capture):
        m.controller_pad=0;P.P.Frames.frame(m,whole_pass=True)
    assert set(cuts)=={0,87,102};rows=[]
    for offset,(seed,cpu)in sorted(cuts.items()):
        assert N.get(seed,'NmiDisable')&128
        for kind in('NMI','IRQ'):
            z=N.fork(seed);d=base(memory=z,pc=cpu.pc)
            for n in('a','x','y','p','sp','processorCycles'):setattr(d,n,getattr(cpu,n))
            before=(d.pc,d.sp,d.a,d.x,d.y,d.p);code=bytes(z[0x15a:0x17b]);stack=bytes(z[0x101+d.sp:0x200])
            tags=z.rawtags[:];shadows=[N.get(z,n)for n in('CurrentBank','CurrentBankC')];payload=[bytes(z.ram[i])for i in(1,2,3)]
            start=d.processorCycles
            if kind=='NMI':d.nmi()
            else:
                assert not d.p&4,'Actual captured IRQ must be legal, not forced enabled'
                z[0x5204]=128;d.irq()
            minimum=d.sp
            for _ in range(100000):
                if(d.pc,d.sp)==before[:2]:break
                assert z[d.pc]!=0,('Existing actual ISR BRK',kind,d.pc,z.rawtags)
                minimum=min(minimum,d.sp);d.step()
            else:raise AssertionError(('Existing actual ISR bound',kind,d.pc))
            assert(d.pc,d.sp,d.a,d.x,d.y,d.p)==before
            assert bytes(z[0x15a:0x17b])==code and z[0x16c]==offset
            assert bytes(z[0x101+d.sp:0x200])==stack
            assert z.rawtags==tags and[N.get(z,n)for n in('CurrentBank','CurrentBankC')]==shadows
            assert[bytes(z.ram[i])for i in(1,2,3)]==payload
            rows.append(dict(service_offset=offset,source_PC=cpu.pc,source_SP=cpu.sp,kind=kind,cycles=d.processorCycles-start,
                minimum_SP=minimum,AXYP_SP_maps_live_stack_all33SMC_and_full_CF_RAM123_preserved=True))
    return dict(actual_unmodified_current_cf_main_cuts=rows,
        current_NMI_IRQ_cannot_change_repeated_SFC_low_source=True,
        new_opcode_ISR_proof_still_required_after_any_source_mount_lease=True,
        ordinary_NMI_midbusyMain_unreachable_not_invented=True,no_NesBus_patch_or_new_game_instruction=True)


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No mutable Nightly reread'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only ingress audit attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q=dict(static=static(raw),existing_current_SMC_vector_preservation=smc(raw),outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
