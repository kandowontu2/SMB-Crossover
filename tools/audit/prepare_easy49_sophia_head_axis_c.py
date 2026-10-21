"""Complete source corner rejection across all three actual head probes."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
P=V/'root49-sophia-head-axis-b'
D=V/'root49-sophia-head-axis-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    b=json.loads((P/'preparation.json').read_text())
    assert json.loads((P/'compiled-axis-b.json').read_text())['status']=='PASS_COMPILED_SOURCE_NORMAL_FLAT_CORNER_AXES_BOTH_MAPPERS'
    for n,h in b['source_sha256'].items():
        assert sha(P/'source'/n)==h,n
        q=D/'source'/n
        q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(P/'source'/n,q)
    shutil.copytree(P/'source/build/generated',D/'source/build/generated')
    shutil.copyfile(P/'build.py',D/'build.py')
    p=D/'source/src/sophia_source_terrain.s'
    text=p.read_text()
    a='  jsr SophiaHeadSourceAxis\n  bcc Empty'
    assert text.count(a)==1
    text=text.replace(a,'  jsr SophiaHeadSourceAxis\n  bcc Next')
    # A rejected side corner is not the end of the complete head span. Restore
    # the head query row before the existing next left/right point is sampled.
    a='No:\n  clc\n  rts\n.endproc\n.popseg\n'
    assert text.count(a)==1
    text=text.replace(a,'''No:
  lda Player_Y_Position
  clc
  adc #16
  sta RgTempY
  lda MmYFraction+1
  cmp #$80
  bcc QueryRestored
  bne QueryExtra
  lda MmYFraction
  beq QueryRestored
QueryExtra:
  inc RgTempY
QueryRestored:
  clc
  rts
.endproc
.popseg
''')
    p.write_text(text)
    record=dict(status='PREPARED_PRIVATE_COMPLETE_NORMAL_FLAT_HEAD_AXIS_C',script_sha256=sha(__file__),
                parent_preparation_sha256=sha(P/'preparation.json'),parent_compiled_sha256=sha(P/'compiled-axis-b.json'),
                source_sha256={n:sha(D/'source'/n)for n in b['source_sha256']},
                change='Reject a side corner then inspect remaining real head cells, restoring actual query Y. A separated ceiling with a one-cell gap can overlap both outer cells of the19-pixel body.',
                phase_cap_bytes=500000000,final_reserve_bytes=50000000,global_cap_bytes=70000000000,
                main_changed=False,goal_complete=False)
    (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(record['status'])


if __name__=='__main__':main()
