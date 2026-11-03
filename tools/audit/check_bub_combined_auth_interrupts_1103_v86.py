"""Actual IRQ/FF cuts across combined83, including new reject/tail paths."""
import inspect
from pathlib import Path
import check_bub_shared_auth_interrupts_1103_v79 as P
import check_bub_combined_auth_contracts_1103_v84 as B


def source_main():
    source=inspect.getsource(P.main)
    assert source.count('P.P.P.build()')==1
    source=source.replace('P.P.P.build()','B.adapter()')
    replacements={
        "'shared-auth-v79-ISR.json'":"'combined-auth-v86-ISR.json'",
        "'shared-auth-v79-initial-state-negative.json'":"'combined-auth-v86-state-negative.json'",
        "'shared-auth-v76-funding.json'":"'combined-auth-v83-measurement.json'",
        "'shared-auth-v77-contracts.json'":"'combined-auth-v84-contracts.json'",
        "'shared-auth-v78-lifecycle.json'":"'combined-auth-v85-lifecycle.json'",
        "'shared-auth-v76.s'":"'combined-auth-v83.s'",
        "'shared-auth-v76.bin'":"'combined-auth-v83.bin'",
        "'shared-auth-v76-extra.bin'":"'combined-auth-v83-extra.bin'",
        "'shared-auth-v76-Sh.bin'":"'combined-auth-v83-Sh.bin'",
        '0xab72<=pc<0xabce':'0xab72<=pc<0xabd4',
    }
    for before,after in replacements.items():assert before in source,before;source=source.replace(before,after)
    source=source.replace('Path(__file__),Path(P.__file__),Path(H.__file__),',
        'Path(__file__),Path(P.__file__),Path(H.__file__),Path(B.__file__),Path(LegacyISR.__file__),')
    anchor='    result=dict(passed=True,CPU_only=True'
    assert source.count(anchor)==1
    rejected='''    for raw_owner in [0,37,255]:
        m,_=P.P.cold(b,36)
        N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)
        N.put(m,SelectedCharacter=raw_owner,NmiDisable=255,FamilyMainCommit=1)
        P.P.C.clear(m)
        run(('Sh-reject',raw_owner),lambda m=m:P.P.public(m,0xa800))
    for bank,offset in [(3,15),(2,0)]:
        m=Q.Q.fresh(b,route,0)
        m.ram[bank][0x1fe0+offset]^=1
        N.put(m,NmiDisable=255,FamilyMainCommit=1)
        P.P.C.clear(m)
        run(('BB-header-reject',bank,offset),lambda m=m:P.P.public(m,0xb0a7))
    for raw_owner in [0,36,255]:
        N.Bus=P.P.C.cold.__globals__['C'].C.V.ControllerBus;m=N.fresh(b)
        P.P.C.fields(m,raw_owner);P.P.C.clear(m)
        run(('common-cold-reject',raw_owner),lambda m=m:P.P.public(m,0xae00))
'''
    source=source.replace(anchor,rejected+anchor)
    source=source.replace("remaining=['Deepest actual lag-handler nestedIRQ replay across all retained contexts.','Complete external caller/reference closure and pending combined-owner source rebind.']",
        "remaining=['Deepest actual lag-handler nestedIRQ replay across all retained combined contexts.','Complete external caller/reference closure and root candidate permission.']")
    return source


def main():
    env=dict(P.__dict__,__file__=__file__,B=B,LegacyISR=P)
    exec(compile(source_main(),__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
