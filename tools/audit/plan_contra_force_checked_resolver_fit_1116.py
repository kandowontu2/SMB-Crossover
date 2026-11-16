"""Detached fitting successor; needs exact source resource/caller review."""
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_checked_resolver_1116 as Rejected

C,Code=Rejected.C,Rejected.Code
REJECTED_SHA='c36c0e6ae3339e18d8628e7883f8ba5687b83bcc0b9c7ca8acaa26de1cdceabd'
WF_FILE,WF_BASE,WF_SIZE=792486,0xb796,178


def router(old):
    class Fitting(Code):
        def emit(self,value):
            if value=='a2ad38':return # New CPY2 supplies C1; helper now loads AD itself.
            if value=='a9998d6c01c002':value='a9978d6c01c002'
            return super().emit(value)
    with patch.object(Rejected,'Code',Fitting):new,labels=Rejected.router(old)
    assert len(new)==224 and labels['Common']==0xb0bd
    return new,labels


def guard(old):
    a=Code(0xbf47);prefix=bytearray(old[:0xbf90-0xbf47])
    for pc in(0xbf7e,0xbf8e):prefix[pc-0xbf47+1]=0xbfa5-(pc+2)
    a.code.extend(prefix);a.mark('Restore');a.emit('68');a.absolute(0x4c,'RestoreTail')
    a.emit('eaeaea');assert a.pc==0xbf97;a.mark('CheckedResolver')
    a.absolute(0x20,0xbf47);a.branch(0x90,'ResolverReturn');a.emit('8d6c01ce6d01a902')
    a.mark('ResolverReturn');a.emit('60');assert a.pc==0xbfa5
    a.mark('Bad');a.emit('18');a.branch(0x90,'Restore');a.emit('eaeaeaeaea');assert a.pc==0xbfad
    a.code.extend(old[0xbfad-0xbf47:0xbfe1-0xbf47]);assert a.pc==0xbfe1
    a.mark('SceneRetireForeign');a.emit('0848ad0260c91f');a.branch(0xf0,'SceneOwn');a.branch(0xd0,'RetireShared')
    a.mark('SceneOwn');a.emit('682860');assert a.pc==0xbfef
    # Both mapper publications are adjacent, after the shared jump.
    a.mark('RestoreTail');a.emit('8da17d8d165168aa68');a.branch(0x90,'ReturnBad');a.emit('283860')
    a.mark('ReturnBad');a.emit('281860');assert a.pc==0xc000
    a.labels['RetireShared']=0xbfbf;new=a.done();assert len(new)==185
    assert new[0xbfad-0xbf47:0xbfe1-0xbf47]==old[0xbfad-0xbf47:0xbfe1-0xbf47]
    return new,dict(a.labels)


def wf(old):
    assert len(old)==178 and old[:3]==bytes.fromhex('a90060')
    assert C.H(old[3:])=='1db29ae7f1b6ecc475f5282287b4e0aba1865fe4892bf8e54cd2a63abfbb8119'
    a=Code(0xb797);a.mark('Entry');a.branch(0xb0,'Fast');a.emit('88');a.branch(0xf0,'Own')
    a.mark('Foreign');a.emit('a92b8d6c01a9b28d6d01a9c34c5a01')
    a.mark('Own');a.emit('a82039b6');a.branch(0x90,'Return')
    for delta,store in((0,'8d6c01'),(1,'8d6d01'),(2,'')):
        a.absolute(0xb9,0xb7dc+delta);a.emit(store)
    a.mark('Return');a.emit('60');a.mark('Fast');a.emit('a9c08d6c01a9ad8d6d01a9dd205a01')
    a.branch(0x90,'Foreign');a.emit('8d6c01a9a08d6d019860');assert a.pc==0xb7dc
    a.mark('Targets');a.code.extend(old[3+67:]);assert a.pc==0xb848
    new=bytes([0xea])+a.done();assert len(new)==178 and new[70:]==old[70:]
    return new,dict(a.labels)


def descriptor(parent):
    assert C.H(Path(Rejected.__file__).read_bytes())==REJECTED_SHA
    assert C.H(parent)==C.PIN
    # Pin both old public regions through the rejected descriptor without
    # composing its overlong227-byte fragment into any ROM or CPU image.
    before=Rejected.descriptor(parent);rows=[]
    items=(('Router87',716848,0xb020,224,router),
           ('CF checked guard/retire/tail',573271,0xbf47,185,guard),
           ('Wf helper and retired local status',WF_FILE,WF_BASE,WF_SIZE,wf))
    for name,at,pc,n,fn in items:
        old=parent[at:at+n];new,labels=fn(old)
        assert len(new)==n
        rows.append(dict(name=name,file_half_open=[at,at+n],physical_PRG=(at-16)//8192,
            CPU_half_open=[pc,pc+n],old_SHA256=C.H(old),new_SHA256=C.H(new),
            old_hex=old.hex(),new_hex=new.hex(),changed_bytes=sum(a!=b for a,b in zip(old,new,strict=True)),labels=labels))
    return dict(reference6a3_SHA256=C.H(parent),detached_fragments=rows,exact_sizes=[224,185,178],
        owned_bytes_if_granted=587,all_arrays_fit_exactly=True,no_whole_ROM_composition=True,
        new_resource_requests=[dict(role='source-declared unloaded CF tail14',file_half_open=[573442,573456]),
            dict(role='retired local WfOneLifeStatus3',file_half_open=[792486,792489])],
        old_rejected_227byte_fragment_preserved=True,SEC_removed_only_because_new_CPY2_supplies_cohort3_C1=True,
        old_live_X_AD_not_assumed_dead=True,new_helper_explicitly_loads_AD_high_before_full_BtCheck=True,
        current_helper_table_B7DC_and_all108bytes_and_endB848_exact=True,
        source_helper_entry_B799_to_B797_requires_all_consumers_rebound=True,
        opaque_rejection_NextBank_publication_and_all_rejected_plan_obligations_still_pending=True,
        guarded_CF_service_target_BF_to_BE_DEC_requires_exact_BF97_ingress=True,
        failure15_18_19_legacy_retry_and_every_fullcheck_retained=True,
        no_private_payload_cookie_art_audio_input_timer_or_service_change=True,
        foreign_weighted_cycle_measurement_and_full_AXYP_SMC_stack_ISR_proof_pending=True,
        private_and_caller_optimization_not_joined=True,native_cadence_gain_not_claimed=True,
        no_CPU_test_allocation_mount_native_or_delivery=True,outputs=0)


if __name__=='__main__':
    parent,pin=Rejected.Source.load_reference()
    def deny(*a,**kw):raise AssertionError('Detached fitting proposal attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(parent)
    q['actual_input_SHA256']=pin;q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
