"""Use UTF8 for witness handoff prose; retain v1 encoding failure."""
from pathlib import Path
p=Path(__file__).with_name('freeze_goku_portrait_facing_v1.py');s=p.read_text()
s=s.replace("write_text(text,newline='\\n')","write_text(text,encoding='utf8',newline='\\n')")
s=s.replace("'freeze_goku_portrait_facing_v1.py','private_build_outputs_v1.py'","'freeze_goku_portrait_facing_v1.py','freeze_goku_portrait_facing_v2.py','private_build_outputs_v1.py'")
exec(compile(s,__file__,'exec'),globals())
