"""Preserve private d0c negative; compare the real CHR alias before writing it."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_pit_retold_host_v1 as B

def main():
 old=B.scoped_load(B.P/'candidate.nes')
 assert B.address(old,'PlayerChrBank')==B.address(old,'CurrentCHRBank')
 before=' sta SmChrBank\n sta PlayerChrBank\n cmp CurrentCHRBank'
 after=(' sta SmChrBank\n'
        ' ; PlayerChrBank is CurrentCHRBank[0]. Compare the prior publication\n'
        ' ; before the intentional alias store in ChangeChr.\n'
        ' cmp CurrentCHRBank')
 assert B.CODE.count(before)==1
 B.CODE=B.CODE.replace(before,after)
 B.O=R/'build/pit-retold-host-v2'
 B.main()
if __name__=='__main__':main()
