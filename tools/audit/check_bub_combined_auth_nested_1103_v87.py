"""Replay exact deepest86 FF-handler IRQ witnesses, without a ROM."""
import inspect
from pathlib import Path
import check_bub_shared_auth_nested_1103_v80 as P
import check_bub_combined_auth_interrupts_1103_v86 as ISR
import check_bub_combined_auth_contracts_1103_v84 as B

O,R,sha=P.O,P.R,P.sha


def main():
    source=inspect.getsource(P.main)
    source=source.replace("O/'shared-auth-v79-ISR.json'","O/'combined-auth-v86-ISR.json'")
    source=source.replace('source=inspect.getsource(P.main)','source=ISR.source_main()')
    source=source.replace("O/'shared-auth-v80-nested.json'","O/'combined-auth-v87-nested.json'")
    source=source.replace('0xab72<=active.pc<0xabce','0xab72<=active.pc<0xabd4')
    source=source.replace('All original8127IRQ/9287FF cuts are reused by exact source/hash; only winning134foreground contexts are reconstructed, no duplicate full sweep.',
        'All parent86 IRQ/FF cuts are reused by exact source/hash; only their winning foreground contexts are reconstructed, no duplicate full sweep.')
    source=source.replace("source=source.replace(\"Path(P.__file__),Path(H.__file__),\", \"Path(P.__file__),Path(H.__file__),proof,\")",
        "source=source.replace(\"Path(P.__file__),Path(H.__file__),\", \"Path(P.__file__),Path(H.__file__),Path(ISR.__file__),Path(LegacyNested.__file__),proof,\")")
    source=source.replace('env=dict(P.__dict__,__file__=__file__,',
        'env=dict(P.__dict__,__file__=__file__,B=B,LegacyISR=P,ISR=ISR,LegacyNested=LegacyNested,')
    extra='''    source=source.replace("remaining=['Deepest actual lag-handler nestedIRQ replay across all retained combined contexts.','Complete external caller/reference closure and root candidate permission.']", "remaining=['Complete external caller/reference closure and root candidate permission.']")
'''
    source=source.replace('    env=dict(',extra+'    env=dict(')
    env=dict(P.__dict__,__file__=__file__,ISR=ISR,B=B,LegacyNested=P)
    exec(compile(source,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
