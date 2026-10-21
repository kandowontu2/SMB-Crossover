"""Close signed world-origin prior-bound and out-of-world query aliases."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-head-axis-c';D=V/'root49-sophia-head-axis-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    old=json.loads((P/'preparation.json').read_text())['source_sha256']
    for n,h in old.items():
        assert sha(P/'source'/n)==h,n
        p=D/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
    shutil.copytree(P/'source/build/generated',D/'source/build/generated')
    shutil.copyfile(P/'build.py',D/'build.py')
    p=D/'source/src/sophia_source_terrain.s';text=p.read_text()
    a='  sta SmTempPage\n  clc\n  lda SmHeadX'
    assert text.count(a)==1
    text=text.replace(a,'  sta SmTempPage\n  jcc Yes                     ; signed priorLeft<0 at world origin.\n  clc\n  lda SmHeadX')
    assert text.count('  jsr SophiaTerrainQuery')==3
    text=text.replace('  jsr SophiaTerrainQuery','  jsr SophiaTerrainBoundedQuery')
    text+='''
; A negative left body sample at the level origin has no source Ground.
; Retain native empty-query AXY/R2/R4/pointer ABI, but do not expose a tile
; from pageFF's two-page-buffer alias. No clipping on ordinary positive pages.
.pushseg
.segment "SOPHIA_TERRAIN_COLD"
.proc SophiaTerrainBoundedQuery
  lda RgTempPage
  cmp #$ff
  bne Native
  lda Player_PageLoc
  bne Native
  jsr SophiaTerrainQuery
  lda #0
  sta R3
  rts
Native:
  jmp SophiaTerrainQuery
.endproc
.popseg
'''
    p.write_text(text)
    record=dict(status='PREPARED_PRIVATE_SIGNED_ORIGIN_COMPLETE_NORMAL_FLAT_HEAD_AXIS_D',script_sha256=sha(__file__),
                parent_preparation_sha256=sha(P/'preparation.json'),source_sha256={n:sha(D/'source'/n)for n in old},
                changes=['Signed priorLeft page-underflow is direct interior after priorRight admission.',
                         'Negative left samples at real world origin return empty for all three slow head/side/foot queries.'],
                cost='Bounded-query normal positive-page tail adds11CPUcycles per actual slow query; existing grounded fast-foot pair is unchanged. Exact caller/crowd costs remain to verify.',
                phase_cap_bytes=500000000,final_reserve_bytes=50000000,global_cap_bytes=70000000000,
                main_changed=False,goal_complete=False)
    (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'])


if __name__=='__main__':main()
