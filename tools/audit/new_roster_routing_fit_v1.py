"""Read-only actual gate census and byte-encoded routing proposal, not a build.

No file in src/chr, ROM, linker config, native runner or frozen input is edited.
The proposed bytes run only in a Python CPU arena to FarCallCommon entry.
This does not assemble/admit a target or prove complete caller/IRQ behavior.
"""
from pathlib import Path
import hashlib,itertools,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from sunny_integrated_controls_v1 import scoped_load,address,location
from verify_native_relocation import NesMPU
import dragon_power_map_v1 as D

P=R/'build/celeste-small-chr-v2.nes'
Q=R/'build/celeste-small-v1.nes'
OUT=R/'docs/qa/new-roster-routing-fit-2026-10-28.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def kv(line):return dict(re.findall(r'(\w+)=("[^"]*"|[^,\r\n]+)',line))
def callback(raw):
    # Actual farcall tail: saved A then low/high address then physical bank.
    assert len(raw)==20 and raw[:3]==bytes.fromhex('68288d')
    assert raw[5]==0xa9 and raw[10]==0xa9 and raw[15]==0xa9 and raw[17]==0x4c
    return(raw[6]|raw[11]<<8,raw[16])
def model(start,s,targets,admission=False):
    b=bytearray();labels={};patches=[]
    def lab(n):labels[n]=start+len(b)
    def emit(*x):b.extend(x)
    def absop(op,at):emit(op,at&255,at>>8)
    def branch(op,n):emit(op,0);patches.append((len(b)-1,n,'rel'))
    def table(op,n):emit(op,0,0);patches.append((len(b)-2,n,'abs'))
    absop(0x8d,s['SafecallA_SMC']+1);emit(0x08) # original A first, then original P
    if admission: # Exact explicit-ID argument contract of NrAdder/NrBox.
        absop(0xcd,s['SelectedCharacter']);branch(0xd0,'Mismatch')
    emit(0x98,0x48);absop(0xad,s['SelectedCharacter']) # preserve Y, X untouched
    emit(0x38,0xe9,20,0xc9,9);branch(0xb0,'Legacy') # subtract-before-range includes wrap
    emit(0xa8);table(0xb9,'Lo');absop(0x8d,s['FarcallJmpTarget_SMC']+1)
    table(0xb9,'Hi');absop(0x8d,s['FarcallJmpTarget_SMC']+2)
    table(0xb9,'Banks');absop(0x8d,s['NextBank_SMC']+1)
    emit(0x68,0xa8,0x28);absop(0xad,s['NextBank_SMC']+1);absop(0x4c,s['FarCallCommon'])
    lab('Legacy');emit(0x68,0xa8,0x28);lab('LegacySetup')
    at,bank=targets[9]
    emit(0xa9,at&255);absop(0x8d,s['FarcallJmpTarget_SMC']+1)
    emit(0xa9,at>>8);absop(0x8d,s['FarcallJmpTarget_SMC']+2)
    emit(0xa9,bank);absop(0x4c,s['FarCallCommon'])
    if admission:
        lab('Mismatch');emit(0x28);table(0x4c,'LegacySetup')
    for n,seq in[('Lo',[targets[i][0]&255 for i in range(9)]),('Hi',[targets[i][0]>>8 for i in range(9)]),('Banks',[targets[i][1]for i in range(9)])]:lab(n);b.extend(seq)
    for pos,n,kind in patches:
        at=labels[n]
        if kind=='rel':d=at-(start+pos+1);assert -128<=d<128;b[pos]=d&255
        else:b[pos:pos+2]=bytes([at&255,at>>8])
    assert len(b)==(98 if admission else 89),len(b)
    return bytes(b),labels

def arena(raw,pc,s,char,a,x,y,p,bytes_override=None):
    m=bytearray(65536);m[0xa000:0xc000]=raw[16+124*8192:16+125*8192]
    if bytes_override:m[pc:pc+len(bytes_override)]=bytes_override
    m[s['SelectedCharacter']]=char
    m[s['CurrentBank']]=252;m[s['CurrentBankC']]=213
    m[s['NextBank_SMC']+1]=199;m[s['SafecallA_SMC']+1]=201
    m[0x1fe]=0xff;m[0x1ff]=0x5a
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,253;low=253;w=[]
    for _ in range(200):
        low=min(low,c.sp)
        if c.pc==s['FarCallCommon']:
            return dict(A=c.a,X=c.x,Y=c.y,P=c.p&0xcf,SP=c.sp,minSP=low,cycles=c.processorCycles,
                        original_A=m[s['SafecallA_SMC']+1],target=m[s['FarcallJmpTarget_SMC']+1]|m[s['FarcallJmpTarget_SMC']+2]<<8,
                        nextbank=m[s['NextBank_SMC']+1],live_return=list(m[0x1fe:0x200]))
        assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
    raise AssertionError('router did not reach FarCallCommon')

def main():
    assert not OUT.exists()
    b=scoped_load(P);s={n:address(b,n)for n in['SelectedCharacter','CurrentBank','CurrentBankC','NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']}
    assert sha(P)=='f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
    assert P.read_bytes()[16+124*8192:16+125*8192]==Q.read_bytes()[16+124*8192:16+125*8192]
    source=(R/'src/new_roster_dispatch.s').read_text()
    gates=re.findall(r'^NrGate (\w+),([^\r\n]+)',source,re.M);assert len(gates)==11
    scopes={x['name'].strip('"'):int(x.get('size','0'),0)for line in P.with_suffix('.dbg').read_text().splitlines()if line.startswith('scope\t')for x in[kv(line)]if 'name'in x}
    facts=[];checks=0
    # Actual exported addresses are non-executed routing tokens for new slots;
    # this is deliberately NOT a semantic API map for Portrait/Visible/etc.
    dp=R/'build/dragon-power-mixed-render-v3/component.lbl';sb=R/'build/smb2-roster-component-v1/component.lbl'
    def find(p,n):return int(re.search(r'^al ([0-9a-fA-F]+) \.'+n+r'$',p.read_text(),re.M)[1],16)
    tags={4:(find(dp,'DpMovement'),214),5:(find(sb,'S2Movement'),246)}
    for name,arguments in gates:
        pc=address(b,name);assert scopes[name]==97
        raw=b['raw'][location(b,name):location(b,name)+97]
        assert raw[:5]==bytes([8,72,173,s['SelectedCharacter']&255,s['SelectedCharacter']>>8])
        oldtargets=[callback(raw[17+20*i:37+20*i])for i in range(4)]
        targets={i:oldtargets[0]for i in range(10)}
        for i,t in[(0,oldtargets[1]),(1,oldtargets[2]),(3,oldtargets[3])]:targets[i]=t
        targets.update(tags)
        code,labels=model(pc,s,targets)
        costs={k:[]for k in['legacy0_19','Ice20','City21','Sunny23','unexposed22_26_28','other29_255']}
        for char,flags in itertools.product(range(256),[0x30,0x31,0x74,0xf9]):
            a,x,y=(char*17+91)&255,177,93
            old=arena(b['raw'],pc,s,char,a,x,y,flags)
            new=arena(b['raw'],pc,s,char,a,x,y,flags,code)
            keys=['A','X','Y','P','SP','original_A','target','live_return']
            if char not in[24,25]:assert [old[k]for k in keys]==[new[k]for k in keys],(name,char,flags,old,new)
            else:
                assert new['target']==tags[char-20][0]and new['A']==tags[char-20][1]
                assert (new['X'],new['Y'],new['SP'],new['original_A'],new['P']&0x4d)==(x,y,253,a,flags&0x4d)
            assert old['minSP']==new['minSP']==251
            if char not in[24,25]:
                cat='legacy0_19'if char<20 else {20:'Ice20',21:'City21',23:'Sunny23'}.get(char,'unexposed22_26_28'if char in[22,26,27,28]else'other29_255')
                costs[cat].append(new['cycles']-old['cycles'])
            checks+=1
        facts.append(dict(name=name,public_PC=pc,old_bytes=97,proposed_bytes=len(code),unexecuted_local_slack=97-len(code),
                          table_offsets={n:labels[n]-pc for n in['Lo','Hi','Banks']},old_targets=oldtargets,
                          proposal_byte_hex=code.hex(),estimated_CPU_delta_to_FarCallCommon={n:[min(v),max(v)]for n,v in costs.items()if v},
                          whole_target_caller_or_ISR_proof=False))
    size=next(int(z['size'],0)for z in b['segs'].values()if z['name']=='"NEW_ROSTER_GATE"')
    # Source/ROM evidence only, no full disassembly reachability claim.
    authority=D.raw();rawcalls=[]
    for bank in range(4):
        body=authority[16+bank*32768:16+(bank+1)*32768]
        for i in range(len(body)-2):
            if body[i:i+3]==bytes.fromhex('208b9a'):
                rawcalls.append(dict(bank=bank,PC=0x8000+i,preceding12=body[max(0,i-12):i].hex(),direct_immediate=body[i-1]if i>=2 and body[i-2]==0xa9 else None))
    original_sections=[(0,0x8118,0x12),(0,0x9a33,0x82),(0,0xfb33,0x6f),(0,0xfc22,0x2d),(0,0xc373,0x37),(0,0xd357,0x4b),(0,0xfde7,0x1a)]
    files=[Path(__file__),P,P.with_suffix('.dbg'),P.with_suffix('.lbl'),Q,R/'src/new_roster_dispatch.s',R/'src/mmc5.s',R/'src/hot_render_gate.s',R/'src/dragon_power_host.s',R/'src/dragon_power_contact.s',R/'src/dragon_power_native.inc',R/'tools/dragon_power_map_v1.py',R/'tools/audit/verify_native_relocation.py',dp,sb,R/'build/smb2-roster-component-v1/handoff.json',R/'build/dragon-power-mixed-render-v3/handoff.json',D.ROM]
    report=dict(status='READ_ONLY_ROUTING_LAYOUT_AND_ORIGINAL_SOURCE_FACTS_NOT_ASSEMBLED_OR_ADMITTED',
                bindings={str(p.resolve()):sha(p)for p in files},current_f56a_d52_bank124_exact=True,
                gate_segment=dict(start=0xa000,end_exclusive=0xa000+size,reserved_end_exclusive=0xae00,tail_free=0xae00-(0xa000+size)),
                repeated_gates=facts,model_checks=checks,
                proposal=dict(bytes_per_gate=89,existing_gate_size=97,reclaimed_local_bytes=8*len(gates),new_globals_or_segments=0,
                              additional_A_bank_roundtrips=0,max_stack_saved_bytes=2,all_old_public_entries_retain_their97B_slots=True,
                              future26_28='Table positions considered, remain unallocated/hidden/legacy tokens in this model; per-route safe semantics are mandatory before actual admission.',
                              new24_25='Actual DpMovement/S2Movement exported addresses are routing tokens only; targets are NOT executed. Do not copy them as Portrait/Weapons/etc semantic implementations.',
                              ordered_SMC_change='SafecallA store moves before selection, preserving original A while Y indexes; cold table paths pre-store NextBank then FarCallCommon repeats it. Full IRQ/NMI SMC/caller proof remains required.'),
                alternative99B_terrain=dict(proposed_bytes=98,old_bytes=99,exact_A_equals_SelectedCharacter_guard_preserved=True,
                    method='Insert CMP SelectedCharacter/BNE mismatch before savingY; mismatch PLP/JMP LegacySetup. Same tables and public entry, no assumed deadX/Y.'),
                not_complete_host_fit='11 repeated gates reclaim88 fragmented bytes plus existing101B tail. Terrain adds at most2B. Reset/pickup/lifecycle/UI/audio/actor/block/endFrame still need real per-owner semantics; this is NOT a claim that complete Goku+SMB2 adapters fit.',
                required_controls=['Fresh whole assembly and every old public/internal alias census; local8B slack is code space, not new global allocation.',
                    'Real caller AXYP/SP/live stack/application RAM/banks/5SMC, all64 flags/ID argument mismatch/negative/foreign cases, timing including actual table/branch page crossings.',
                    'IRQ and both lag/regularNMI at every moved earlySafecallA/NextBank publication seam; preserve exact physical/shadow bank pending-store windows, no broad mapper normalization.',
                    'No ordinary actor/world path acquires another A-bank trip; actual legacy target traces/order/cycles measured and reviewed.',
                    'Semantic host wrappers: NrDraw prepares CHR, NOT DpDrawBody/S2DrawBody OAM emission; restore bodypointer aftershots before dynamic reservation. Real health/death/head/pickup ownership must not fall through legacy raw-ID tables.'],
                original_source=dict(authority_sha256=D.SHA,raw_JSR_9A8B_occurrences=rawcalls,
                    decoded_sections=[dict(bank=bank,start=pc,end_exclusive=pc+n,text=D.disassembly(bank,pc,n))for bank,pc,n in original_sections],
                    facts=['0:9A8B accepts budgetA only when2F==0; returns0 if protected. 0:9A80 decrements budget on26&7==0, then common health debit unlessD9bit20 orHP0.',
                           '0:9A33 always services pending budget first; hunger skips whileE5!=0. Period is3 whenF9==1 OR D0>=4, else1; increments2B only27==0 then debits when it wraps to0. Scene mapping of F9/D0 is not an SMB policy.',
                           '0:9A98 food addsA, clamps150 or250 whenD9bit40, resets2B. HP crossing30 requests source audio64+65.',
                           'Incoming fixed source budgets include3/6/12/18 viaFB33/3C/45/4E,6/12/18 viaFB68/71/7A,10 viaFB93; other direct callers load5,6,10,20,30. These are source actor/contact paths, NOT an SMB enemy damage table.',
                           '0:C385 andD372 use real FC22 accepted point, cooldown050E=32, decrement actual actor050D byONE, then source-specific state/score050F consumers. D372 additionally accepts pose16hex or negative044B wave; it rejects ordinary punch. Other source HP writers/consumers remain family-specific.',
                           '0:FDEC is a distinct generic contact response/cooldown/effect/separation path; it is not universalHP--. FC22 consumes a wave on accepted point before the caller applies family eligibility; host must test actual enemy eligibility before calling it.',
                           'Original main0:8121 comparesaction2D against0D and bypasses9A2E when>=0D. Host DpHealthTick unit equivalence is not proof of whole-Main health cadence during hurt/scene/death; preserve this source caller gate when designing the integrated consumer.'],
                    remaining_policy=['Author exact SMB actor HP/armor/accepted attack kinds, outgoing damage, incoming budgets and real defeat/score/drop mapping explicitly; source oneHP per accepted hit for named consumers is not a universal SMB mapping.',
                                      'Choose source-backed hunger room classification for SMB scenes, preserving real pause/action/update admission and lowHP source cues; do not silently disable it.',
                                      'Keep source hurt/recovery/death and delayedHP timing; DpInjuryStart queues budget only and does not itself author actor-specific knockback/collision behavior.']))
    assert report['gate_segment']['tail_free']==101
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(OUT),sha256=sha(OUT),gates=len(facts),model_checks=checks,tail_free=101,reclaimed=88),indent=2))

if __name__=='__main__':main()
