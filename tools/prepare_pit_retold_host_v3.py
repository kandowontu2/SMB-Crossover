"""Separate true-Select successor; preserve the native-negative private v2."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_pit_retold_host_v1 as B

def main():
 before=' sta SmChrBank\n sta PlayerChrBank\n cmp CurrentCHRBank'
 after=(' sta SmChrBank\n'
        ' ; PlayerChrBank is CurrentCHRBank[0]. Compare the prior publication\n'
        ' ; before the intentional alias store in ChangeChr.\n'
        ' cmp CurrentCHRBank')
 assert B.CODE.count(before)==1;B.CODE=B.CODE.replace(before,after)
 before=' lda CrossoverMenuPressed\n and #4'
 assert B.CODE.count(before)==1;B.CODE=B.CODE.replace(before,' lda CrossoverMenuPressed\n and #Select_Button')
 # The standalone object does not own the unrelated memory aliases required
 # by the whole constants include. Copy its one genuine named definition;
 # bind that exact source file rather than introduce a numeric button oracle.
 constant=re.search(r'^Select_Button\s*=.*$',(R/'inc/constants.inc').read_text(),re.M).group()
 before='.include "inc/common.inc"'
 assert B.CODE.count(before)==1;B.CODE=B.CODE.replace(before,before+'\n; Exact named definition from bound inc/constants.inc.\n'+constant)
 B.O=R/'build/pit-retold-host-v3';B.main()
 old,new=[B.scoped_load(p/'candidate.nes')for p in[R/'build/pit-retold-host-v2',B.O]]
 assert B.address(new,'Select_Button')==32
 dif=[(i,a,b)for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 assert len(dif)==1 and dif[0][1:]==(4,32),dif
 assert (dif[0][0]-16)//8192==66
 proof=dict(passed=True,exact_one_operand_change_vs_frozen_v2=dif,named_actual_Select_Button=32,definition_from_bound_native_constants=constant,source_controls_v2_used_wrong_Down4=True,native_v2_negative_retained=True,bindings={str(p.resolve()):B.sha(p)for p in[Path(__file__),R/'inc/constants.inc',R/'build/pit-retold-host-v2/handoff.json',R/'build/pit-retold-host-v2/candidate.nes',B.O/'candidate.nes',B.O/'component.s']})
 (B.O/'select-correction.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(proof))
if __name__=='__main__':main()
