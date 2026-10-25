"""Use the unchanged route/CHR/scroll reviewer for the two Mac runs."""
from pathlib import Path

source=Path(__file__).with_name('review_tmnt_ny.py')
text=source.read_text();old="len(replay['runs']) == 8"
assert text.count(old)==1
# The original reviewer expects four turtles x two modes. This separate
# runner has exactly one Mac x two modes; every per-run assertion remains.
exec(compile(text.replace(old,"len(replay['runs']) == 2"),str(source),'exec'),
     dict(__name__='__main__',__file__=str(source)))
