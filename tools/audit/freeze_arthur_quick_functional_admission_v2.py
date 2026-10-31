"""Narrow the retained over-broad unchanged-source freeze assertion.

The current constructor intentionally selects Arthur's real cold portrait
through the former DK-only preview helper. Its typed new branch is disclosed;
the original DK pixels/tables and all actual Select handlers are unchanged.
"""
from pathlib import Path
import json
p=Path(__file__).with_name('freeze_arthur_quick_functional_admission_v1.py')
s=p.read_text()
old="assert old.split(marker,1)[1]==new.split(marker,1)[1]"
new="""assert old.split('.proc FmToggle',1)[1].split('.endproc',1)[0]==new.split('.proc FmToggle',1)[1].split('.endproc',1)[0]
 assert A.sha(A.P/'src/full_roster_menu_art.inc')==A.sha(N/'src/full_roster_menu_art.inc')
 assert old.split('.proc FmDrawPreview\\n',1)[1]==new.split('.proc FmDrawPreview\\n',1)[1]"""
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("scope='Only FmPending has intended Quick/Arthur predicate changes; source tables/Select ordering remain identical to installed a7cc.'","scope='FmPending intentionally readies Quick/Arthur; typed FmDrawDkPreview additionally selects Arthur index30 for raw32. Original DK pixels/all actual Select handlers/name/portrait/color tables remain identical to installed a7cc.'")
s=s.replace("'freeze_arthur_quick_functional_admission_v1.py']","'freeze_arthur_quick_functional_admission_v1.py','freeze_arthur_quick_functional_admission_v2.py']")
# Preserve the failed assertion as a distinct receipt before final freeze.
root=Path(__file__).resolve().parents[2]/'build/arthur-quick-functional-admission-v1'
negative=root/'freeze-negative-v1.json'
assert not negative.exists()
negative.write_text(json.dumps(dict(passed=False,product_fault=False,source_unchanged=True,failed_assertion='All full_roster_menu code after FmToggle byte-identical',actual_reason='Typed FmDrawDkPreview intentionally adds CMP32 and selects genuine Arthur portrait30. Native DK branch is retained; source table/Select/preview-draw comparisons are checked separately in v2.'),indent=2)+'\n',newline='\n')
exec(compile(s,__file__,'exec'),globals())
