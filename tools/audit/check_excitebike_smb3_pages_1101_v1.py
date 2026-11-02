"""Execute factored SMB3 selectors; retired table labels are not live readers."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
import check_hogan_current_bounded_v1 as M
O=R/'build/excitebike-pose-1101-v3'


def main():
    rom=R/'build/shinobi-camera-1101-v20/candidate.nes'
    b=scoped_load(rom);seed=M.fresh(b);pages=set();cases=0
    for form in range(7):
      for frame in range(81):
       for face in [1,2]:
        m=M.fork(seed)
        M.put(m,SelectedCharacter=17,M3RenderForm=form,PlayerFacingDir=face)
        M.invoke(m,'M3SetFrame',x=frame)
        page=M.get(m,'SmChrBank')+256*M.get(m,'M3SpritePageHi')
        assert page not in range(728,740),(form,frame,face,page)
        pages.add(page);cases+=1
    assert max(pages)<728,sorted(pages)
    result=dict(passed=True,ROM_SHA256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        actual_M3SetFrame_cases=cases,forms=7,frames=81,facings=2,pages=sorted(pages),
        scope='Actual current factored selector execution, not reads from retired M3FormNChrLo labels. No graphical or gameplay claim.')
    (O/'smb3-pages.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
