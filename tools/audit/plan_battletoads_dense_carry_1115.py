"""Detached carry/cohort successor; eliminates cross-bank entry-table read."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import plan_battletoads_dense_resolver_1115 as Failed
import current_battletoads_carry_reference_1115 as Input

P,C,N,W,Code=Failed.Previous,Failed.C,Failed.N,Failed.W,Failed.Code
OLD_SEED=Failed.detached_seed


def router(base=0xb020,*,new=False,helper=None):
    if not new:return Failed.OLD_ROUTER(base,new=False,helper=helper)
    if helper is None:helper=0xb799
    a=Code(base)
    for _ in range(36):a.absolute(0x4c,'Router')
    a.mark('Unavailable');a.emit('1860');a.mark('Router');a.emit('08488a489848ad026038e91bc907')
    a.branch(0xb0,'No');a.emit('4a');a.branch(0xb0,'No');a.emit('a8ad6c0138e920aa8a8d6a01c003')
    a.branch(0xd0,'Common');a.emit('8a29b3c913');a.branch(0xf0,'No')
    a.emit('e033');a.branch(0xf0,'Portrait');a.emit('e04e');a.branch(0xf0,'Colors');a.emit('a2ad38')
    # CPY3 supplies C0 on non33 entry; only raw33 executes SEC. Actual SFC
    # preserves that carry until the helper BCS. Original caller P is saved.
    a.mark('Common');a.emit('a9'+bytes((helper&255,)).hex()+'8d6c01a9'+bytes((helper>>8,)).hex()+'8d6d01a9e0205a01')
    a.branch(0x90,'No');a.mark('Target');a.emit('8d620168a868aa688d6a01284c5d01')
    a.mark('No');a.emit('68a868aa688d6a01281860')
    a.mark('Portrait');a.emit('a911');a.branch(0xd0,'Cold')
    a.mark('Colors');a.emit('a991');a.mark('Cold');a.emit('8d6c01a9b08d6d01a9c8');a.branch(0xd0,'Target')
    out=a.done();assert len(out)==224,(len(out),a.labels)
    return out,a.labels


def helper(raw,base=0xb799):
    # Reuse only the exact pinned, constant-time target and group contracts.
    Failed.helper(raw,base)
    table=bytearray(raw[P.WF_AT+67:P.WF_END])
    for slot in range(36):
        lo,hi,bank=table[3*slot:3*slot+3];word=lo+256*hi
        if(bank,word)==(224,0xb799):table[3*slot:3*slot+2]=(0xb2cd).to_bytes(2,'little')
        elif(bank,word)==(224,0xb79b):table[3*slot:3*slot+2]=(0xb2cb).to_bytes(2,'little')
    a=Code(base);a.mark('Entry');a.branch(0xb0,'Fast');a.emit('88');a.branch(0xf0,'Own')
    a.mark('Foreign');a.emit('a92b8d6c01a9b28d6d01a9c34c5a01')
    a.mark('Own');a.emit('a82039b6');a.branch(0x90,'Return')
    a.absolute(0xb9,base+67);a.emit('8d6c01');a.absolute(0xb9,base+68);a.emit('8d6d01');a.absolute(0xb9,base+69)
    a.mark('Return');a.emit('60');a.mark('Fast');a.emit('a9c08d6c018e6d01a9dd205a01')
    a.branch(0x90,'Foreign');a.emit('8d6c01a9a08d6d019860');assert a.pc==base+67
    a.mark('Targets');a.code.extend(table);out=a.done();assert len(out)==175
    a.labels.update(Visible=0xb2cb,NoOp=0xb2cd)
    return out,a.labels,list(table)


def shapes(parent,image):
    assert Failed.OLD_ROUTER()[0]==image[P.ROUTER_AT:P.ROUTER_AT+224]
    r,rl=router(new=True);h,hl,_=helper(image);rows=[]
    for at,code in((P.ROUTER_AT,r),(P.WF_AT,h)):
        old=image[at:at+len(code)];rows.append(dict(file=[at,at+len(code)],old_hex=old.hex(),new_hex=code.hex(),
            old_SHA256=sha256(old).hexdigest(),new_SHA256=sha256(code).hexdigest(),changed=sum(a!=b for a,b in zip(old,code,strict=True))))
    return dict(reference_SHA256=C.CANDIDATE,detached_envelopes=rows,owned_bytes=399,
        Router_labels=rl,helper_labels=hl,fit=dict(Router=224,carry_dispatch=5,foreign=15,own=22,Fast=25,targets=108,helper=175),
        failed5b28_cross_bank_entry_table_removed=True,no_lookup_outside_own_mapped_code_page=True,
        incoming_helper_C_is_raw33_flag=True,Y_is_canonical_cohort=True,all_three_full_BtCheck_calls_retained=True,
        only_opaque_target_word_alias_difference=True,no_mounted_overlay=True,no_whole_image_composed=True)


def detached_seed(seed,new):
    m,labels=OLD_SEED(seed,new);m.carry_successor=new;m.unit_reads=Counter()
    original=type(m)
    class Bound(original):
        def __getitem__(self,at):
            if isinstance(at,int):
                if 0x4020<=at<0x4100:
                    assert self.rawtags[1]==215,('Detached Router read in wrong actual bank',at,self.rawtags)
                    self.unit_reads['Router87']+=1
                if new and 0x5099<=at<0x5148:
                    assert self.rawtags[1]==224,('Detached helper/table read in wrong actual bank',at,self.rawtags)
                    self.unit_reads['helper96']+=1
            return super().__getitem__(at)
    m.__class__=Bound
    return m,labels


def sensitivity(parent,image):
    seed=N.Bus(P.Base.symbols(image));seed.raw_page(1,215)
    N.put(seed,CurrentBank=215,CurrentBankC=seed.rawtags[2],SelectedCharacter=33,FmGroups=64)
    with patch.object(P,'router',Failed.router),patch.object(P,'helper',Failed.helper):m,_=detached_seed(seed,True)
    c=N.NesMPU(memory=m,pc=0x40c2);c.y=3
    try:c.step()
    except AssertionError as e:
        assert 'helper/table read in wrong actual bank'in str(e);negative=str(e)
    else:raise AssertionError('Mapping sensitivity failed to reject old cross-bank lookup')
    return dict(old_failed_plan_LDA_rejected_by_actual_mapped_owner_assertion=True,
        PC=0x40c2,Y=3,mapped_raw=215,error=negative,corrected_plan_has_no_entry_lookup=True)


def ordinary_cold(image,owner):
    if owner==33:return P.Base.cold(image),'RASH'
    slots={27:26,29:28,31:30};slot=slots[owner];b=P.Base.symbols(image)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in([4]*(slot//8)+[1]*(slot%8)):W.UI.key(m,bits)
    name=W.UI.menu_name(m)[0];assert N.get(m,'SelectedCharacter')==owner
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;P.Base.Frames.frame(m,cold=True)
    else:raise AssertionError(('Actual reference constructor bound',owner,name))
    assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    if owner in(27,31):assert N.invoke(m,'BwCheck'if owner==27 else'CfOrBtCheck')['P']&1,('Genuine family header absent',owner,name)
    return m,name


def contract(parent,image):
    negative=sensitivity(parent,image);seeds={};names={}
    for owner in(27,29,31,33):
        seeds[owner],names[owner]=ordinary_cold(image,owner)
        print('PROGRESS '+json.dumps(dict(genuine_reference_cold=owner,name=names[owner])),flush=True)
    cases=0;minimum=255;delta=Counter();smc=Counter();checks=Counter()
    for owner,seed in seeds.items():
        pair=[]
        for new in(False,True):
            m,labels=detached_seed(seed,new);m.flat_visible=labels['Visible']if new else-1;pair.append(m)
        for slot in range(36):
            for p in range(256):
                if not p&32:continue
                out=[]
                for m in pair:
                    list.__setitem__(m,slice(0x100,0x200),list.__getitem__(seed,slice(0x100,0x200)))
                    out.append(P.public_call(m,slot,85,173,91,p))
                assert all(out[0][k]==out[1][k]for k in('PC','A','X','Y','P','SP')),(owner,slot,p,out)
                if out[0]['PC']==0x15d:assert(out[0]['target'],out[0]['next_bank'])==(out[1]['target'],out[1]['next_bank'])
                P.Base.M.Research.compare(pair,out,('All-status actual-cohort query',owner,slot,p))
                changed=tuple(at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]);assert set(changed)<={0x162,0x16c,0x16d}
                smc[changed]+=1;delta[owner,out[0]['CPU']-out[1]['CPU']]+=1
                checks[owner,out[0]['BtCheck_calls'],out[1]['BtCheck_calls']]+=1
                minimum=min(minimum,*(r['minimum_SP']for r in out));cases+=1
        print('PROGRESS '+json.dumps(dict(owner=owner,all128P_all36services=True,cases=cases)),flush=True)
    # Actual retire API, followed by every valid status on real cold service slots.
    seed=N.fork(seeds[33]);N.invoke(seed,'BtRetire');assert seed.ram[3][0x1fe0]==0
    retired=0
    for slot in(0,2,9,15,17,18,19,26,29,34):
        for p in range(256):
            if not p&32:continue
            pair=[];out=[]
            for new in(False,True):
                m,labels=detached_seed(seed,new);m.flat_visible=labels['Visible']if new else-1;pair.append(m)
                out.append(P.public_call(m,slot,85,173,91,p))
            assert all(out[0][k]==out[1][k]for k in('PC','A','X','Y','P','SP'))
            if out[0]['PC']==0x15d:assert(out[0]['target'],out[0]['next_bank'])==(out[1]['target'],out[1]['next_bank'])
            P.Base.M.Research.compare(pair,out,('Retired cold33 all statuses',slot,p));retired+=1
    return dict(mapping_sensitivity=negative,actual_compiled_reference_cold_names=names,
        all128validP_all36services_all_four_cohorts_cases=cases,retired_cold_service_all_status_cases=retired,
        actual_retire_API=True,minimum_SP=minimum,
        cycle_savings=[dict(owner=o,cycles=c,cases=n)for(o,c),n in sorted(delta.items())],
        full_BtCheck_calls=[dict(owner=o,old=a,new=b,cases=n)for(o,a,b),n in sorted(checks.items())],
        explicit_opaque_SMC=[dict(fields=list(k),cases=n)for k,n in smc.items()],
        ordinary_cold_inputs_not_candidate_cold_claim=True,no_health_actor_terrain_or_position_seeds=True,
        no_mounted_overlay=True,no_whole_image_composed=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('shapes','public','components','contract'));args=ap.parse_args()
    parent,image,info=Input.load();base=N.NesMPU;carry=Counter()
    class Observe(base):
        def step(self):
            m=self.memory
            if getattr(m,'carry_successor',False)and self.pc==0x5099:
                owner=N.get(m,'SelectedCharacter');assert owner in(27,29,31,33)
                assert bool(self.p&1)==(owner==33),('Actual unchanged FarCall lost cohort carry',owner,self.p)
                assert self.y==(owner-27)//2
                assert self.a==m[0x16a]and self.a%3==0 and 0<=self.a<=105
                carry[owner,bool(self.p&1)]+=1
            return super().step()
    def deny(*a,**kw):raise AssertionError('Detached carry plan attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',deny),\
        patch.object(P,'router',router),patch.object(P,'helper',helper),patch.object(P,'shapes',shapes),patch.object(P,'detached_seed',detached_seed),\
        patch.object(Failed,'detached_seed',detached_seed),patch.object(N,'NesMPU',Observe):
        fn={'shapes':shapes,'public':P.public_units,'contract':contract,
            'components':lambda p,z:dict(sensitivity=sensitivity(p,z),status=Failed.status_units(p,z),WWF=P.wwf_profile(p,z))}[args.mode]
        q=fn(parent,image)
    q.update(info,mode=args.mode,helper_actual_carry_entries=[dict(owner=o,C=c,cases=n)for(o,c),n in sorted(carry.items())],
        all_detached_reads_assert_actual_mapped_PRG_owner=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
