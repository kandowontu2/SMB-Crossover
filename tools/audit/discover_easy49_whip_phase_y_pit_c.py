"""Fresh ordinary Pit discovery on the phase-corrected, faster shot image."""
from pathlib import Path

original = Path(__file__).with_name('discover_easy49_union_t_pit_b.py')
source = original.read_text()
for old, new in [
    ("T = V / 'root49-easy-union-t'", "T = V / 'root49-easy-whip-phase-y'"),
    ("H = V / 'root49-easy-union-t-pit-route-b'", "H = V / 'root49-easy-whip-phase-y-pit-route-c'"),
    ("'99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'", "'f0377dd12cae59749f85fe42651c113a18e67c3c8291a14b3610b8ba889821bc'"),
    ("'root49t-pit-discovery-b'", "'root49y-pit-discovery-c'"),
]:
    assert source.count(old) == 1
    source = source.replace(old, new)
exec(compile(source, str(original), 'exec'), dict(__file__=__file__, __name__='__main__'))
