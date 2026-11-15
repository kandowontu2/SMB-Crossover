"""Read-only current owner/reference and post-NoOp SMC reader observation."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,re
import plan_battletoads_dense_resolver_1115 as Dense

P,C,N,W=Dense.Previous,Dense.C,Dense.N,Dense.W


def source_owners(parent,image):
    q=P.ingress(parent,image);b=P.Base.symbols(image);at=lambda pc:16+96*8192+(pc&8191)
    source=C.R/'build/wwf-roster-native-1101-v1/runtime.s';listing=source.with_suffix('.lst')
    text=source.read_text();lst=listing.read_text();references=[]
    for number,line in enumerate(lst.splitlines(),1):
        if any(n in line for n in('WfNoop','WfVisible','WfResolve')):
            if'.export'in line:kind='published symbol only'
            elif re.search(r'Wf(?:Noop|Visible|Resolve|ResolveTargets):',line):kind='definition'
            elif'Target Wf'in line:kind='three-byte descriptor, current table rebound separately'
            elif'lda WfResolveTargets'in line:kind='the three internal table-plane readers'
            else:raise AssertionError(('Unclassified retained Wf compiler-source reference',number,line))
            references.append(dict(line=number,kind=kind,text=line.strip()))
    direct=[];words=[]
    for bank in range(128):
        data=image[16+bank*8192:16+(bank+1)*8192]
        for target in(0xb799,0xb79b,0xb79d):
            cursor=0
            while(cursor:=data.find(target.to_bytes(2,'little'),cursor))>=0:
                op=data[cursor-1]if cursor else None
                row=dict(bank=bank,offset=cursor,file=16+bank*8192+cursor,target=target,preceding=op)
                if bank==96 or bank in(126,127):words.append(row)
                if op in(0x20,0x4c,0x6c):direct.append(row)
                cursor+=1
    for row in direct:
        # All three are genuine/possible near JMPs in OTHER mapped PRG pages.
        # Execute the actual opcode: an absolute JMP cannot select PRG96.
        assert row['bank']not in(96,126,127),('Unclassified Wf-capable direct control',row)
        probe=N.Bus(b);tag=row['bank']|128;probe.raw_page(1,tag)
        pc=0xa000+row['offset']-1;c=N.NesMPU(memory=probe,pc=pc);before=tuple(probe.rawtags);c.step()
        assert c.pc==row['target']and tuple(probe.rawtags)==before and probe.rawtags[1]==tag
        row.update(classification='near JMP stays in its own non96 mapped page',actual_opcode_executed=True,
            target_physical_file=16+row['bank']*8192+(row['target']&8191))
    near=[r for r in words if r['bank']==96]
    table_noops={P.WF_AT+67+3*i for i in range(36)if image[P.WF_AT+69+3*i]==224 and int.from_bytes(image[P.WF_AT+67+3*i:P.WF_AT+69+3*i],'little')in(0xb799,0xb79b)}
    assert {r['file']for r in near}==table_noops
    assert image[at(0xb798)]==0x60,'Preceding WfOneLifeStatus RTS forbids fallthrough'
    # Bind the exact unchanged suffix and leaf opcodes to their retained source.
    assert 'WfColdIdentity:\n lda SelectedCharacter\n cmp #29\n bne ColdNo\n lda FmGroups\n and #7\n cmp #6\n bcs ColdNo\n sec\n rts\nColdNo:clc\n rts' in text
    assert image[at(0xb632):at(0xb646)]==bytes.fromhex('ad0260c91dd00bade85f2907c906b00238601860')
    assert image[at(0xb2cb):at(0xb2cf)]==bytes.fromhex('38601860')
    return dict(structured_domains_and_carrier_macros=q,
        retained_source=dict(path=str(source.relative_to(C.R)),SHA256=sha256(source.read_bytes()).hexdigest(),listing_SHA256=sha256(listing.read_bytes()).hexdigest(),references=references),
        old_entries_direct_control_leads=direct,same_bank_and_fixed_target_words=words,
        every_same_bank_old_NoOp_Visible_word_is_a_declared_current_descriptor=True,
        old_Resolve_standard_farcall_is_only_Router=True,
        ColdIdentity_exact_whole20bytes=True,new_group_suffix_preserves_X_Y_and_only_computes_group_C_N_Z=True,
        existing_leaf_aliases_have_no_cache_private_RAM_or_header_access=True,
        fixed_bank_word_aliases_need_final_classification=any(r['bank']in(126,127)for r in words),
        invalid_arbitrary_computed_private_addresses_not_legal_public_roots=True)


def smc_observe(parent,image):
    reads=Counter();writes=Counter();leaves=Counter();ctx=dict(active=False,PC=-1,tag=-1)
    bus=W.ControllerBus;cpu=N.NesMPU
    class Observed(bus):
        def __getitem__(self,at):
            if isinstance(at,int)and ctx['active']and at in getattr(self,'opaque_watch',()):
                reads[ctx['tag'],ctx['PC'],at]+=1
                assert len(reads)<=64,'Bounded SMC reader identities'
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if isinstance(at,int)and ctx['active']and at in getattr(self,'opaque_watch',()):
                writes[ctx['tag'],ctx['PC'],at]+=1;self.opaque_watch.remove(at)
            return super().__setitem__(at,value)
    class CPU(cpu):
        def step(self):
            m=self.memory;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            if not getattr(m,'flat_unit',False)and(tag,pc)in((224,0xb799),(224,0xb79b)):
                assert N.get(m,'SelectedCharacter')==29
                m.opaque_watch={0x16c,0x16d};leaves[pc]+=1
            ctx.update(active=not getattr(m,'flat_unit',False),PC=pc,tag=tag)
            try:return super().step()
            finally:ctx['active']=False
    with patch.object(W,'ControllerBus',Observed),patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU),\
        patch.object(P,'router',Dense.router),patch.object(P,'helper',Dense.helper),patch.object(P,'shapes',Dense.shapes),patch.object(P,'detached_seed',Dense.detached_seed):
        observed=P.wwf_profile(parent,image)
    return dict(actual_six_family_original_lifecycle=observed,actual_NoOp_Visible_entries=dict(leaves),
        watched_fields=[0x16c,0x16d],reads_before_first_write=[dict(tag=t,PC=p,address=a,count=n)for(t,p,a),n in sorted(reads.items())],
        first_writes=[dict(tag=t,PC=p,address=a,count=n)for(t,p,a),n in sorted(writes.items())],
        source_is_original_a90_not_mounted_proposal=True,
        opaque_snapshot_or_restore_writes_require_protocol_classification=True,no_blanket_invalid_or_private_RAM_mask=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('owners','smc','all'));args=ap.parse_args()
    parent,image,info=Dense.Input.load()
    def deny(*a,**kw):raise AssertionError('Read-only consumer audit attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',deny):
        if args.mode=='all':q=dict(owners=source_owners(parent,image),SMC=smc_observe(parent,image))
        else:q=(source_owners if args.mode=='owners'else smc_observe)(parent,image)
    q.update(info,mode=args.mode,outputs=0,Mesen_run=False,no_overlay=True)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
