"""Run the unchanged six shared component cores on the combined art image."""
from pathlib import Path

original = Path(__file__).with_name('run_easy49_union_native_i.py')
source = original.read_text()
for old, new in [
    ("H = V / 'root49-easy-union-h'", "H = V / 'root49-easy-union-t'"),
    ("'PASS_PRIVATE_SHARED_MARIO_UNION_H_BUILD_ONLY'", "'PASS_PRIVATE_LINK_L_BILL_GROWTH_UNION_R_BUILD_ONLY'"),
    ("'union-h-'", "'union-t-'"),
]:
    assert source.count(old) == 1
    source = source.replace(old, new)
exec(compile(source, str(original), 'exec'), dict(__file__=__file__, __name__='__main__'))
