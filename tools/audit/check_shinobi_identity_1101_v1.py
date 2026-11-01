"""Enumerate actual current menu resolution before allocating Shinobi identity."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
import check_hogan_current_bounded_v1 as M
O=R/'build/shinobi-identity-1101-v1'
def main():
    rom=R/'build/kirby-approach-owner-1101-v3/candidate.nes';b=scoped_load(rom)
    counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    seed=M.fresh(b);rows=[]
    for slot,count in enumerate(counts):
        m=M.fork(seed);M.put(m,CrossoverMenuIndex=slot)
        M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                M.invoke(m,'CrossoverMenuInput')
            rows.append(dict(slot=slot,variant=variant,raw=M.get(m,'SelectedCharacter'),alts=M.get(m,'FmAlts')))
    assert len(rows)==90 and all(r['raw']!=36 for r in rows)
    O.mkdir(exist_ok=True)
    result=dict(passed=True,ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        native_CPU_menu_rows=rows,proposed_raw_identity=36,current_menu_collision=False,
        scope='Actual existing menu resolution across90 identities. Does not establish new identity dispatch safety or gameplay admission.')
    (O/'identity-census.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,rows=len(rows),raw_ids=sorted({r['raw'] for r in rows}),Ryu_slot=[r for r in rows if r['slot']==10])))
if __name__=='__main__':main()
