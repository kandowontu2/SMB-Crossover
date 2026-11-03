"""Compare the same raw40 native text pipeline before/after its name policy.

The reference replaces only private policy30 with the existing handled/no-op
leaf in memory. It is an explicitly isolated contract control, not a native
row admission or a replacement native game-text implementation.
"""
import inspect
from pathlib import Path
import check_dkjr_native_item_status_1102_v61 as P


def main():
    text=inspect.getsource(P.main)
    old='N.put(ref,SelectedCharacter=0)'
    new="ref.ram[3][90:93]=[0x4c,L['DkNativeHandled']&255,L['DkNativeHandled']>>8]"
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('native-items-v61-','native-items-v62-')
    old="scope='Native itemPrepare/regular maturity predicates"
    new="reference_control='Same raw40/header/caller/map/native continuation; private policy30 points to existingSEC_RTS no-name handler in isolated reference RAM only. This removes the unrelated Mario0 inventory-buffer tail difference from retained61 oracle.',scope='Native itemPrepare/regular maturity predicates"
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace("for p in[Path(__file__),Path(P.__file__)","for p in[Path(__file__),V61_PATH,Path(P.__file__)")
    text=text.replace("body_SHA256=A.sha((O/'native-items-v60.bin').read_bytes()))", "body_SHA256=A.sha((O/'native-items-v60.bin').read_bytes()),reference_control='Explicit same40 native pipeline; private no-name handled leaf only in isolated reference RAM')")
    env=dict(P.__dict__);env.update(__name__='dk_status_same_owner_reference',__file__=__file__,V61_PATH=Path(P.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
