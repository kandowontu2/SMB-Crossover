"""Concrete read-only SMB3 placement model on6c69, without building a ROM.

Models proposed source-declared moves, intact nine-page payload and DMC clones.
No existing file, allocation, source segment, ROM or native emulator is changed.
"""
from pathlib import Path
from collections import defaultdict,Counter
import argparse
import gzip
import hashlib
import json

from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location,Memory
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'world-firebar-padding-v2/candidate.nes'
TRACE=D/'smb3-original-music-closure-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    assert sha(BASE)=='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
    b=scoped_load(BASE);raw=b['raw'];source=Path(TRACE/'proof.json')
    assert sha(source)=='fd6d4c2dc248943b225063ce3c1ce3dacb7739221981b10abb4a849ed60f3e9e'
    proof=json.loads(source.read_text());nsf=Path(proof['source']);image=nsf.read_bytes()[128:]
    assert sha(nsf)==proof['source_sha256'] and len(image)==36864
    used=defaultdict(list)
    for seg in b['segs'].values():
        if'ooffs'not in seg:continue
        first,n=int(seg['ooffs'],0),int(seg['size'],0)
        if not 16<=first<16+128*8192 or not n:continue
        for bank in range(128):
            lo,hi=max(first,16+bank*8192),min(first+n,16+(bank+1)*8192)
            if lo<hi:used[bank].append((lo-16-bank*8192,hi-16-bank*8192,seg['name'].strip('"')))
    reserved={62:'Chip native music',63:'held TMNT',94:'Chip native music',99:'held TMNT exchange',
              123:'Mac native music',124:'not released/held TMNT',125:'CV3 mirror/held cold TMNT',126:'resident',127:'fixed/DPCM'}
    gaps=[]
    for bank in range(128):
        cursor=0
        for lo,hi,name in sorted(used[bank]):
            if lo>cursor:gaps.append(dict(bank=bank,first=cursor,end=lo,bytes=lo-cursor,excluded=reserved.get(bank)))
            cursor=max(cursor,hi)
        if cursor<8192:gaps.append(dict(bank=bank,first=cursor,end=8192,bytes=8192-cursor,excluded=reserved.get(bank)))
    def empty(bank,lo,hi):
        assert bank not in reserved
        assert any(g['bank']==bank and g['first']<=lo<hi<=g['end']for g in gaps),(bank,lo,hi)
        assert raw[16+bank*8192+lo:16+bank*8192+hi]==bytes([255])*(hi-lo)
    rawbanks=[78,86,90,93,95,96,98,118,119]
    payload=[]
    for page,bank in enumerate(rawbanks):
        empty(bank,0x1000,0x2000)
        payload.append(dict(original_page=page,bank=bank,physical_first=0x1000,bytes=4096,
                            source_payload_first=page*4096,source_payload_sha256=hashlib.sha256(image[page*4096:(page+1)*4096]).hexdigest(),
                            runtime_A_window_read_base=0xb000))
    assert b''.join(image[q['source_payload_first']:q['source_payload_first']+q['bytes']]for q in payload)==image
    empty(78,0x500,0x700);empty(95,0x340,0x6b6);empty(95,0x6c0,0xa1f);empty(85,0xbe8,0x1fe8)
    relocations=[dict(segment='Z2_GFX',old_bank=70,old_offset=0,bytes=886,new_bank=95,new_offset=0x340,
                     old_CPU=0xc000,new_CPU=0xc340,genuine_data_label_delta=0x340),
                 dict(segment='MIKE_GFX',old_bank=97,old_offset=0,bytes=863,new_bank=95,new_offset=0x6c0,
                     old_CPU=0xc000,new_CPU=0xc6c0,genuine_data_label_delta=0x6c0),
                 dict(segment='BILL_ORBIT_2',old_bank=38,old_offset=0xbe8,bytes=5120,new_bank=85,new_offset=0xbe8,
                     old_CPU=0xcbe8,new_CPU=0xcbe8,genuine_data_label_delta=0)]
    for r in relocations:
        actual=[v for v in used[r['old_bank']]if v[2]==r['segment']]
        assert actual==[(r['old_offset'],r['old_offset']+r['bytes'],r['segment'])],actual
        lo=16+r['old_bank']*8192+r['old_offset']
        r['old_complete_segment_sha256']=hashlib.sha256(raw[lo:lo+r['bytes']]).hexdigest()
    fixed=raw[16+127*8192:16+128*8192]
    assert(0x1140,0x1fc1,'BASS_DPCM')in used[127]
    # Two model clones; their byte arrays are never installed or written as ROMs.
    cloneA=bytearray(fixed);cloneB=bytearray(fixed)
    overlays=[('A',0x3980,2305,0x1140),('A',0x3000,577,0x1a80),
              ('A',0x6b40,65,0x1d00),('B',0x8800,833,0x1140)]
    for name,first,n,target in overlays:
        assert target%64==0 and 0x1140<=target<target+n<=0x1fc1
        clone=cloneA if name=='A'else cloneB
        clone[target:target+n]=image[first:first+n]
    for clone in [cloneA,cloneB]:
        assert all(x==y or 0x1140<=i<0x1fc1 for i,(x,y)in enumerate(zip(fixed,clone)))
    samples={};profiles={};source_config_count=0
    for f in TRACE.glob('*/footprint.json'):
        foot=json.loads(f.read_text())
        for row in foot['DPCM_configs']:
            source_config_count+=1
            control,dac,addr,length,cpu,n,first,last,maps=row
            name='B'if addr==0x60 else'A'
            target=0x1140 if name=='B'else 0x1140+(first-0x3980)if 0x3980<=first<=0x4280 else 0x1a80+(first-0x3000)if 0x3000<=first<=0x3240 else 0x1d00
            assert target%64==0
            clone=cloneA if name=='A'else cloneB
            assert clone[target:target+n]==image[first:first+n]
            key=f'{first:04x}-{n}'
            samples[key]=image[first:first+n]
            profiles[(control,dac,addr,length,tuple(maps))]=dict(source4010=control,source4011=dac,source4012=addr,source4013=length,
                source_page_maps=maps,source_payload_first=first,bytes=n,clone=name,physical_bank=70 if name=='A'else 97,
                new_CPU_start=0xe000+target,hardware4012=(0x2000+target)//64,hardware4013_unchanged=length,
                exact_sample_sha256=hashlib.sha256(image[first:first+n]).hexdigest())
    assert len(samples)==7
    larger_overlaps=[];containments=[]
    for k,s in samples.items():
        for h,t in samples.items():
            if k==h:continue
            for offset in range(0,max(0,len(t)-len(s))+1,64):
                if t[offset:offset+len(s)]==s:containments.append([k,h,offset])
            for n in range(65,min(len(s),len(t))+1,64):
                if s[-n:]==t[:n]:larger_overlaps.append([k,h,n])
    assert not containments and not larger_overlaps
    transitions=Counter();active_address_writes=address_writes=0;unsafe=[]
    for folder in TRACE.iterdir():
        log=folder/'calls.jsonl.gz'
        if not log.exists():continue
        enable=0;selected=pending='A'
        with gzip.open(log,'rt',encoding='utf-8')as stream:
            for line in stream:
                event=json.loads(line)
                for at,v in event['APU']:
                    if at==0x4012:
                        address_writes+=1;active_address_writes+=bool(enable&16)
                        pending='B'if v==0x60 else'A'
                        if not enable&16:
                            transitions['switch_at_address_while_disabled']+=pending!=selected;selected=pending
                    if at==0x4015:
                        if not v&16:
                            transitions['switch_after_original_source_disable']+=pending!=selected;selected=pending
                        elif pending!=selected:unsafe.append([folder.name,event['tick'],v,pending,selected])
                        enable=v
    assert not unsafe
    # Pure planned-dispatch CPU model; in-memory only, not a game ROM build.
    gate=address(b,'VgAudioDispatch');helper=0xcbe8;native=0xcc00
    selected=address(b,'SelectedCharacter');variant=address(b,'VvVariant')
    low=address(b,'LmNativeMusicGate');expanded=address(b,'ExpandedAudioTick')
    newgate=bytes([0xad,selected&255,selected>>8,0xc9,17,0x90,13,0xc9,19,0xb0,9,0x4c,helper&255,helper>>8]+[0xea]*6+[0x4c,low&255,low>>8])
    newhelper=bytes([0xc9,18,0xf0,3,0x4c,native&255,native>>8,0xad,variant&255,variant>>8,0xd0,8,0xa9,250,0x8d,0x15,0x51,0x4c,0,0xa0,0x4c,low&255,low>>8])
    assert len(newgate)==len(newhelper)==23
    flags=[0x20|(v&15)|((v&16)<<2)|((v&32)<<2)for v in range(64)]
    gatecosts=defaultdict(set)
    for char in range(20):
        for vv in range(4)if char==18 else[0]:
            for flag in flags:
                pair=[]
                for change in [False,True]:
                    m=Memory(b);m.page(2,38);m[selected]=char;m[variant]=vv
                    if change:
                        list.__setitem__(m,slice(gate,gate+23),newgate)
                        list.__setitem__(m,slice(helper,helper+23),newhelper)
                    c=NesMPU(memory=m,pc=gate);c.a,c.x,c.y,c.p,c.sp=85,3,7,flag,253
                    for _ in range(100):
                        if c.pc in [native,expanded,0xa000,0xb800]:break
                        c.step()
                    else:raise AssertionError('Dispatch model timeout')
                    pair.append((c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),c.processorCycles))
                if char!=17:assert pair[0][:-1]==pair[1][:-1],(char,vv,flag,pair)
                else:assert pair[1][0]==native
                gatecosts[f'{char}:{vv}'].add(pair[1][-1]-pair[0][-1])
    plan=dict(passed=True,proposal_only=True,allocated_nothing=True,game_files_changed=False,ROM_written=False,native_run=False,
        current_ROM_sha256=sha(BASE),current_ROM=str(BASE),compiled_used_segments=dict(used),linker_gaps=gaps,
        excluded_reservations=reserved,eligible_gap_bytes=sum(q['bytes']for q in gaps if not q['excluded']),
        intact_original_payload_pages=payload,payload_storage_bytes=36864,
        proposed_data_relocations=relocations,
        C38_live_core=dict(first=0xcbe8,end_exclusive=0xdfe8,hard_budget=5120,
            contiguous_source_execution_spans=[[0xa000,0xa6a5],[0xe2c0,0xe839]],source_span_bytes=3102,
            remaining_for_native_reencoding_readers_writers_dispatch_lifecycle=2018,
            actual_adapter_not_assembled=True,unobserved_source_payload_preserved=True),
        cold_bridge_pool=dict(bank=78,CPU_first=0xa500,bytes=512,source_original_init_bytes=30),
        E_clones=dict(A=dict(bank=70,bytes=8192,model_sha256=hashlib.sha256(cloneA).hexdigest()),
                      B=dict(bank=97,bytes=8192,model_sha256=hashlib.sha256(cloneB).hexdigest()),
                      original_fixed_source_sha256=hashlib.sha256(fixed).hexdigest(),
                      only_overwrite_pure_BASS_DPCM=[0x1140,0x1fc1],original_all_other_fixed_code_vectors_exact=True),
        full_sample_translation_profiles=list(profiles.values()),
        single_clone_rejection=dict(pure_data_capacity=3713,seven_profile_lengths_sum=sum(map(len,samples.values())),
            no_64_aligned_containment_or_overlap_at_least65=True,even_ignoring_alignment_minimum=3777,
            reason='Seven1mod64 lengths total3783; only possible overlaps are single endpoints, so even optimistic six overlaps cannot fit3713.'),
        source_DMC_address_writes=address_writes,address_writes_while_logically_enabled=active_address_writes,
        safe_deferred_clone_transitions=dict(transitions),enable_with_wrong_clone=unsafe,
        DMC_policy='Latch source4012 translation immediately; never change the active sample bank merely on4012. Change E clone only while source DMC is disabled, after the original4015 clear and before source reenable. Preserve4010/4011/4013 and original logical stores; physical source4015 clear must not be suppressed by existing GuestDmcStatus. Hardware DMA/owner/transition/native proof is still required.',
        proposed_dispatch_gate_bytes=list(newgate),proposed_C38_dispatch_helper_bytes=list(newhelper),
        dispatch_prototype_only=True,dispatch_cost_deltas={k:sorted(v)for k,v in gatecosts.items()},
        public_Vg_entry_and_Legacy_PC_retained=True,
        maximum_new_proposed_occupied_regions=65749,net_PRG_occupancy_increase_at_full_budgets=58880,
        actual_native_adapter_linked_bytes=None,
        acceptance_conditions=['Review and authorize the three explicit existing-data relocations.',
            'Assemble the real translated original core/readers/writers/lifecycle within5120C bytes plus512cold bytes; reject if exceeded.',
            'Full216012 source-call/state/store/sample and repeat-contract qualification; no source/event/song/clock omission.',
            'Requalify relocated Z2/Mike OAM/data pointers and all Bill flare vectors/caller scratch/bank restoration.',
            'Prove all existing owner lifecycle/preemption/hold/tail/physical completion and E-clone transitions.',
            'Full other-identity source/ABI/IRQ guards, ordinary builds, CHR exact and bounded native no-harm cadence.'],
        dependencies={str(q):sha(q)for q in [Path(__file__),BASE,BASE.with_suffix('.dbg'),source,TRACE/'dynamic-closure.json',nsf,
            ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']},
        limits='Capacity/identity/sample-switch and planned-gate model only. No source allocation, game linker/candidate, complete adapter-size/CPU or native qualification. Proposed reservations take effect only if reviewed/accepted; no ownership of reserved banks is claimed.')
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,plan=str(out/'plan.json'),sha256=sha(out/'plan.json'),gate_deltas=plan['dispatch_cost_deltas'],net_PRG_increase=58880),indent=2))


if __name__=='__main__':main()
