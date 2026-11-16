"""Detached CF direct checked-resolver fit; explicitly not yet a fitting plan."""
from pathlib import Path
from unittest.mock import patch
import json
import profile_contra_force_service_layers_1116 as Source
from measure_battletoads_passthrough_fit_1114 import Code

C=Source.C
ROUTER_FILE,ROUTER_BASE,ROUTER_SIZE=716848,0xb020,224
GUARD_FILE,GUARD_BASE,GUARD_SIZE=573271,0xbf47,185


def router(old):
    assert len(old)==224 and C.H(old)=='bca680209849a80d2e3901070954bba08c1805024eec17682047df941d032535'
    a=Code(ROUTER_BASE)
    for _ in range(36):a.absolute(0x4c,'Router')
    a.mark('Unavailable');a.emit('1860');a.mark('Router');a.emit('08488a489848ad02604a')
    a.branch(0x90,'No');a.emit('e90dc904');a.branch(0xb0,'No');a.emit('a8')
    # All valid cohort classifiers finish C0, so ADC E0 is offset-20.
    a.emit('ad6c0169e0aa8d6a01c003');a.branch(0xd0,'Common')
    a.emit('8a29b3c913');a.branch(0xf0,'No');a.emit('e033');a.branch(0xf0,'Portrait')
    a.emit('e04e');a.branch(0xf0,'Colors');a.emit('a2ad38')
    a.mark('Common');a.emit('a9998d6c01c002');a.branch(0xd0,'Legacy')
    # Same target low99: raw31 calls the proposed public69:BF99 helper.
    a.emit('a9bf8d6d01a9c5205a01');a.branch(0xb0,'Target')
    # CF fault falls through into the complete old resolver. In particular,
    # cold/unready15/18/19 retain CmFresh/name/reset fallbacks, not NoOp.
    a.mark('Legacy');a.emit('a9b78d6d01a9e0205a01');a.branch(0xb0,'Target')
    a.mark('No');a.emit('18');a.mark('Target');a.emit('8d620168a868aa688d6a01')
    a.branch(0x90,'Failed');a.emit('284c5d01');a.mark('Failed');a.emit('281860')
    a.mark('Portrait');a.emit('a911');a.branch(0xd0,'Cold');a.mark('Colors');a.emit('a991')
    # The genuine fixed public veneers still leave target highB0 intact.
    # Neither special cold path calls another SFC before this point.
    a.mark('Cold');a.emit('8d6c01a9c8');a.branch(0xd0,'Target')
    new=a.done();assert a.labels['Unavailable']==0xb08c and a.labels['Router']==0xb08e
    return new,dict(a.labels)


def guard(old):
    assert len(old)==185 and old[:2]==bytes.fromhex('0848')
    assert old[0xbfad-GUARD_BASE:0xbfbd-GUARD_BASE]==C.OLD_COOKIE
    assert old[0xbff2-GUARD_BASE:]==bytes([255])*14
    a=Code(GUARD_BASE);prefix=bytearray(old[:0xbf90-GUARD_BASE])
    for pc in(0xbf7e,0xbf8e):
        i=pc-GUARD_BASE;assert prefix[i]==0xd0 and pc+2+prefix[i+1]==0xbf98
        prefix[i+1]=0xbfa7-(pc+2)
    a.code.extend(prefix);a.mark('Restore');a.emit('688da17d');a.absolute(0x4c,'RestoreTail')
    assert a.pc==0xbf97;a.emit('eaea');a.mark('CheckedResolver');assert a.pc==0xbf99
    a.absolute(0x20,0xbf47);a.branch(0x90,'ResolverReturn');a.emit('8d6c01ce6d01a902')
    a.mark('ResolverReturn');a.emit('60');assert a.pc==0xbfa7
    a.mark('Bad');a.emit('18');a.branch(0x90,'Restore');a.emit('eaeaea');assert a.pc==0xbfad
    a.code.extend(old[0xbfad-GUARD_BASE:0xbfe1-GUARD_BASE])
    assert a.pc==0xbfe1;a.mark('SceneRetireForeign');a.emit('0848ad0260c91f')
    a.branch(0xf0,'SceneOwn');a.branch(0xd0,'RetireShared')
    a.mark('SceneOwn');a.emit('682860');assert a.pc==0xbfef
    a.mark('RestoreTail');a.emit('8d165168aa68');a.branch(0x90,'ReturnBad');a.emit('283860')
    a.mark('ReturnBad');a.emit('281860');assert a.pc==0xbffd;a.emit('eaeaea')
    a.labels['RetireShared']=0xbfbf
    new=a.done();assert len(new)==185
    assert new[0xbfad-GUARD_BASE:0xbfe1-GUARD_BASE]==old[0xbfad-GUARD_BASE:0xbfe1-GUARD_BASE]
    return new,dict(a.labels)


def descriptor(parent):
    assert C.H(parent)==C.PIN
    rows=[]
    for name,at,base,n,fn in(('Router87',ROUTER_FILE,ROUTER_BASE,ROUTER_SIZE,router),
                           ('CF public guard/retire and requested tail',GUARD_FILE,GUARD_BASE,GUARD_SIZE,guard)):
        old=parent[at:at+n];new,labels=fn(old)
        rows.append(dict(name=name,file_half_open=[at,at+n],physical_PRG=(at-16)//8192,
            CPU_half_open=[base,base+n],old_bytes=n,new_bytes=len(new),size_deficit=max(0,len(new)-n),
            old_SHA256=C.H(old),new_SHA256=C.H(new),old_hex=old.hex(),new_hex=new.hex(),labels=labels))
    return dict(reference6a3_SHA256=C.H(parent),detached_fragments=rows,
        Router_does_NOT_fit=True,not_a_mountable_candidate=True,
        all36_public_veneers_Unavailable_and_Router_entry_PCs_anchored=True,
        same_bank_direct_CfOrBtCheck_still_all16_and_class=True,
        CF_checked_helper_BF99_14bytes=True,all14_real_services_and_inner_checks_retained=True,
        invalid_CF15_18_19_retry_whole_old_Wf_Bw_guard_and_fallback=True,
        old_full_CfRetire36_and_fixed_cookie16_exact=True,
        requested_not_granted_tail=dict(physical_PRG=69,CPU_half_open=[0xbff2,0xc000],
            file_half_open=[573442,573456],bytes=14,all_FF_is_NOT_ownership_proof=True),
        Router_funding_intent=dict(shared_return_epilogue_bytes=5,cold_redundant_high_write_bytes=5,
            offset_ADC_and_remove_TXA_bytes=2,odd_cohort_classifier_bytes=1,total=13,
            additional_CF_selection_and_fault_retry_bytes=16,remaining_deficit=3),
        additional_contracts_requiring_review=[
            'No-rejection path writes opaque NextBank0162 earlier; exact consumer/ISR closure required, not a blanket SMC mask',
            'Cold highB0 write removal requires every direct/indirect public cold entry to be one of the genuine fixed veneers',
            'CfCheck restores original P then explicitly sets only C; AXYP/SP/CVID/full native mapper and live stack parity required',
            'Public check shadow-C/mapper publication has a JMP between them; actual reached ISR plus complete continuation must converge',
            'CF helper DEC016D requires exact BF99 SFC target and selected31; no arbitrary direct private entry',
            'Shortened SceneRetire reuses CfRetire+2 with exactly its existing saved P/A stack',
            'Unknown checksum15-key fallback, all foreign cohorts and all36 public statuses unchanged',
            'Any later removal of duplicate private validation requires separate every-ingress dominating-full16 proof; not implemented here'],
        expected_benefit_scope='Only bypasses Wf96/Bw67 plus their transport on valid31; meaningful combined plan still needs private/caller layers',
        predicted_Main_or_physical_cadence_not_yet_measured=True,
        no_private_payload_or_cookie_change=True,no_whole_ROM_composition=True,no_CPU_test_or_native=True,outputs=0)


if __name__=='__main__':
    parent,pin=Source.load_reference()
    def deny(*a,**kw):raise AssertionError('Detached proposal attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=descriptor(parent)
    q['actual_input_SHA256']=pin;q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
