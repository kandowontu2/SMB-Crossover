"""Actual compiled trap/contact/retirement on the exact combined83 model."""
import inspect
from pathlib import Path
import check_bub_shared_auth_lifecycle_1103_v78 as P
import check_bub_combined_auth_contracts_1103_v84 as B


def main():
    source=inspect.getsource(P.main)
    source=source.replace('P.P.build()','B.adapter()')
    replacements={
        "'shared-auth-v78-lifecycle.json'":"'combined-auth-v85-lifecycle.json'",
        "'shared-auth-v76-funding.json'":"'combined-auth-v83-measurement.json'",
        "'shared-auth-v77-contracts.json'":"'combined-auth-v84-contracts.json'",
        "'shared-auth-v76.s'":"'combined-auth-v83.s'",
        "'shared-auth-v76.bin'":"'combined-auth-v83.bin'",
        "'shared-auth-v76-extra.bin'":"'combined-auth-v83-extra.bin'",
        "'shared-auth-v76-Sh.bin'":"'combined-auth-v83-Sh.bin'",
    }
    for before,after in replacements.items():assert before in source;source=source.replace(before,after)
    source=source.replace('Path(__file__),Path(P.__file__),','Path(__file__),Path(P.__file__),Path(B.__file__),Path(LegacyLifecycle.__file__),')
    env=dict(P.__dict__,__file__=__file__,B=B,LegacyLifecycle=P)
    exec(compile(source,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
