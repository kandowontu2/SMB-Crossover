"""Explicit legacy Luigi handoff ABI differential; disclose new farcall operand image."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address
from mario_luigi731_coefficients_v1 import make
from luigi_mario_profile731_cpu_v1 import BASE,CURRENT,PARENT
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'luigi-mario-profile731-v3';O=P/'handoffs-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(P/'candidate.nes')==CURRENT and sha(BASE)==PARENT;O.mkdir(exist_ok=False)
    old,new=load(BASE),load(P/'candidate.nes')
    smc={address(new,n)+1:n for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC']}
    smc[address(new,'FarcallJmpTarget_SMC')+2]='FarcallJmpTarget_SMC+2'
    cases=[]
    for mode,bits,(kind,seed) in itertools.product([0,1],[0,1,128],[
        ('water',dict(SwimmingFlag=1)),('climb',dict(Player_State=3)),
        ('spring',dict(JumpspringAnimCtrl=1)),('engine7',dict(GameEngineSubroutine=7)),
        ('engine9',dict(GameEngineSubroutine=9))]):
        pair=[]
        for b in [old,new]:
            q=make(b,8,mode);q.put(**seed);q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,Left_Right_Buttons=bits&3)
            c,_=q.invoke('PlayerMovementSubs');pair.append((q,c))
        q,c=pair[0];r,d=pair[1]
        at=list(range(256))+list(range(0x15a,0x17b))+list(range(0x200,0x800))+list(range(0x5c00,0x8000))
        differences=[dict(address=i,old=q.m[i],new=r.m[i],real_owner=smc.get(i)) for i in at if q.m[i]!=r.m[i]]
        assert all(z['address'] in smc for z in differences),(kind,mode,bits,differences)
        assert (c.a,c.x,c.y,c.p,c.sp,q.m.banks)==(d.a,d.x,d.y,d.p,d.sp,r.m.banks)
        cases.append(dict(kind=kind,mode=mode,input=bits,ordinary_RAM_AXYP_SP_banks_exact=True,
            full_SMC_image_old_new_equal=not differences,actual_SMC_differences=differences,
            old_cycles=c.processorCycles,new_cycles=d.processorCycles))
    proof=dict(passed=True,source_CPU_only=True,native_executed=False,ROM_sha256=CURRENT,parent_ROM_sha256=PARENT,
        cases=cases,all_actual_differences_disclosed=True,
        contract='New genuine farcalls leave their ordinary five operating operands in resident SMC; handoffs can therefore differ from old stale operands. No universal SMC-equality claim or fake callable aliases. Complete ordinary RAM/AXYP/SP/banks are exact. Separate428 actual IRQ/RTI checks preserve the new live operands; NMI/native validation remains required.',
        bindings={str(p):sha(p) for p in [Path(__file__),BASE,BASE.with_suffix('.dbg'),P/'candidate.nes',P/'candidate.dbg']})
    (O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(cases),native_executed=False,full_old_new_SMC_equality_not_claimed=True,proof_sha256=sha(O/'proof.json')),indent=2))


if __name__=='__main__':main()
