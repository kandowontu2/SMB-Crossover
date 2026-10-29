"""Read-only refinement:80B fixed-entry gates +9B same-bank cold finish.
Only the named report is written. Proposed bytes execute in a CPU arena, not ROM.
"""
from pathlib import Path
import hashlib,itertools,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import new_roster_routing_fit_v1 as V
from verify_native_relocation import NesMPU
R=V.R;OUT=R/'docs/qa/new-roster-routing-cold-fit-2026-10-28.json'

def encode(pc,s,targets,helper,admit=False):
    b=bytearray();labels={};patches=[]
    def emit(*v):b.extend(v)
    def absop(op,at):emit(op,at&255,at>>8)
    def ref(op,label,rel=False):emit(op,0)if rel else emit(op,0,0);patches.append((len(b)-(1 if rel else 2),label,rel))
    absop(0x8d,s['SafecallA_SMC']+1);emit(8)
    if admit:absop(0xcd,s['SelectedCharacter']);ref(0xd0,'Mismatch',True)
    emit(0x98,0x48);absop(0xad,s['SelectedCharacter']);emit(0x38,0xe9,20,0xc9,9);ref(0xb0,'Legacy',True);emit(0xa8)
    ref(0xb9,'Lo');absop(0x8d,s['FarcallJmpTarget_SMC']+1);ref(0xb9,'Hi');absop(0x8d,s['FarcallJmpTarget_SMC']+2);ref(0xb9,'Bank');absop(0x4c,helper)
    labels['Legacy']=pc+len(b);emit(0x68,0xa8,0x28);labels['Setup']=pc+len(b)
    at,bank=targets[9];emit(0xa9,at&255);absop(0x8d,s['FarcallJmpTarget_SMC']+1);emit(0xa9,at>>8);absop(0x8d,s['FarcallJmpTarget_SMC']+2);emit(0xa9,bank);absop(0x4c,s['FarCallCommon'])
    if admit:labels['Mismatch']=pc+len(b);emit(0x28);ref(0x4c,'Setup')
    for n,values in[('Lo',[targets[i][0]&255 for i in range(9)]),('Hi',[targets[i][0]>>8 for i in range(9)]),('Bank',[targets[i][1]for i in range(9)])]:labels[n]=pc+len(b);b.extend(values)
    for pos,label,rel in patches:
        at=labels[label]
        if rel:d=at-(pc+pos+1);assert -128<=d<128;b[pos]=d&255
        else:b[pos:pos+2]=bytes([at&255,at>>8])
    assert len(b)==(89 if admit else 80)
    finish=bytes([0x8d,(s['NextBank_SMC']+1)&255,(s['NextBank_SMC']+1)>>8,0x68,0xa8,0x28,0x4c,(s['FarCallCommon']+3)&255,(s['FarCallCommon']+3)>>8])
    return bytes(b),finish

def run(raw,bundle,pc,s,char,flags,proposal=None):
    m=bytearray(65536);m[0xa000:0xc000]=raw[16+124*8192:16+125*8192]
    g=next(g for g in bundle['segs'].values()if g['name']=='"SMCCODE"');a,o,n=[int(g[k],0)for k in['start','ooffs','size']];m[a:a+n]=raw[o:o+n]
    if proposal:
        code,finish=proposal;m[pc:pc+len(code)]=code;m[0xad9b:0xad9b+len(finish)]=finish
    m[s['SelectedCharacter']]=char;m[s['CurrentBank']]=252;m[s['CurrentBankC']]=213;m[0x1fe:0x200]=bytes([255,90])
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=91,177,93,flags,253;low=253
    for _ in range(200):
        low=min(low,c.sp)
        if c.pc==s['FarCallCommon']+6:
            return(c.a,c.x,c.y,c.p&0xcf,c.sp,low,m[s['NextBank_SMC']+1],m[s['SafecallA_SMC']+1],m[s['FarcallJmpTarget_SMC']+1]|m[s['FarcallJmpTarget_SMC']+2]<<8,bytes(m[0x1fe:0x200])),c.processorCycles
        assert m[c.pc]!=0,(hex(c.pc),'BRK');c.step()
    raise AssertionError('timeout')

def main():
    assert not OUT.exists();prior=json.loads(V.OUT.read_text());assert all(V.sha(p)==h for p,h in prior['bindings'].items())
    b=V.scoped_load(V.P);s={n:V.address(b,n)for n in['SelectedCharacter','CurrentBank','CurrentBankC','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']}
    gg=next(g for g in b['segs'].values()if g['name']=='"SMCCODE"');off=int(gg['ooffs'],0)+s['FarCallCommon']-int(gg['start'],0)
    literal=b['raw'][off:off+6];assert literal==bytes([0x8d,(s['NextBank_SMC']+1)&255,(s['NextBank_SMC']+1)>>8,0xad,s['CurrentBank']&255,s['CurrentBank']>>8])
    rows=[];count=0
    for f in prior['repeated_gates']:
        pc=f['public_PC'];targets={i:tuple(f['old_targets'][0])for i in range(10)}
        for index,t in[(0,f['old_targets'][1]),(1,f['old_targets'][2]),(3,f['old_targets'][3])]:targets[index]=tuple(t)
        # Same non-executed real API routing tokens as v1, not semantic targets.
        model=bytes.fromhex(f['proposal_byte_hex']);lo,hi,bank=[f['table_offsets'][k]for k in['Lo','Hi','Banks']]
        for i in[4,5]:targets[i]=(model[lo+i]|model[hi+i]<<8,model[bank+i])
        code,finish=encode(pc,s,targets,0xad9b);costs={};new_tags=[]
        for char,flags in itertools.product(range(256),[0x30,0x31,0x74,0xf9]):
            old,oc=run(b['raw'],b,pc,s,char,flags);new,nc=run(b['raw'],b,pc,s,char,flags,(code,finish))
            if char in[24,25]:assert new[6]==targets[char-20][1]and new[8]==targets[char-20][0];new_tags.append(nc)
            else:assert old==new,(f['name'],char,flags,old,new)
            cat='legacy0_19'if char<20 else{20:'Ice20',21:'City21',23:'Sunny23'}.get(char,'unexposed22_26_28'if char in[22,26,27,28]else'other29_255')
            if char not in[24,25]:costs.setdefault(cat,[]).append(nc-oc)
            count+=1
        rows.append(dict(name=f['name'],same_public_PC=pc,proposed_bytes=80,free_local_bytes=17,CPU_delta_to_real_first_live_LDA_boundary={k:[min(v),max(v)]for k,v in costs.items()},new24_25_modeled_CPU_to_boundary=[min(new_tags),max(new_tags)],byte_model_hex=code.hex()))
    terrain=[]
    for name in['NrAdder','NrBox']:
        pc=V.address(b,name);raw=b['raw'][V.location(b,name):V.location(b,name)+99]
        assert raw[:2]==bytes.fromhex('0848')
        # Current terrain prefix differs; its same4 farcall tails remain last80B.
        ts=[V.callback(raw[19+20*i:39+20*i])for i in range(4)];targets={i:ts[0]for i in range(10)}
        for i,t in[(0,ts[1]),(1,ts[2]),(3,ts[3])]:targets[i]=t
        code,_=encode(pc,s,targets,0xad9b,True);assert len(code)==89
        terrain.append(dict(name=name,old=99,proposed=89,local_reclaimed=10,proposal_bytes=code.hex(),explicit_ID_argument_guard=True,executable_terrain_proof_pending=True))
    result=dict(status='READ_ONLY_SAME_ENTRY_COLD_ROUTING_PROPOSAL_NOT_ASSEMBLED_OR_NATIVE',prior_report=V.sha(V.OUT),bindings=dict(prior['bindings']),
                exact_real_resident_continuation=dict(entry=s['FarCallCommon'],old_bytes=literal.hex(),skip_only_first_STA=True,common_helper=[0xad9b,0xada4],helper_bytes=finish.hex(),
                    liveness='Proposed helper sets NextBank once then restoresY/P and enters the genuine existing LDA CurrentBank at+3. A/N/Z differ there and are overwritten by that exact executed instruction before comparison at+6; allC/V/D/I/X/Y/SP/live return/SMC target/bank inputs compare strictly. This is a real continuation, not a fake alias.'),
                models=count,gates=rows,terrain=terrain,arithmetic=dict(repeated_11_old=1067,repeated_11_new=880,common_helper=9,net_reclaimed_repeated=178,original_tail_free=101,remaining_combined_gate_capacity=279,terrain_further_reclaim=20,with_terrain_total=299,contiguity='187B appears as17B in each old97B slot; remaining92B is contiguous atADA4..<AE00. Do not treat299B as one span.'),
                tradeoff='Old raw0..19 modeled +1..2CPU per visited gate, no additional A-bank mapping; Ice/City/Sunny table paths add measured10..18CPU dependinggate/owner. Stack peak remains2 saved bytes and targetSP exact. Costs exclude fullcaller/IRQs; no performance-ready claim.',
                safer_continuation_fallback='80B gates plus12B finish using the public FarCallCommon entry also fit;3B larger and8CPU slower only on cold table routes, keeping raw0..19 path unchanged.',
                still_required=prior['required_controls'],not_complete_host_fit=prior['not_complete_host_fit'])
    result['bindings'][str(Path(__file__).resolve())]=V.sha(__file__);result['bindings'][str(V.OUT.resolve())]=V.sha(V.OUT)
    OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(path=str(OUT),sha256=V.sha(OUT),models=count,capacity=result['arithmetic']),indent=2))

if __name__=='__main__':main()
