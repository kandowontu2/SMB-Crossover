"""Remove only stale coming-soon glyphs proven playable by actual menu calls."""
import json,hashlib
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from inventory_playable_menu_1101_v3 import menu_name
R=Path(__file__).resolve().parents[2]
O=R/'build/playable-marker-cleanup-1102-v1'
ROM=R/'build/thomas-current-candidate-1102-v3/candidate.nes'
def main():
    raw=ROM.read_bytes();inventory=json.loads((R/'build/menu-indicators-1102-v1/inventory.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==inventory['ROM_sha256']
    patches=[]
    for row in inventory['rows']:
        if not row['confirm_starts'] or 63 not in row['tiles']:continue
        data=bytes(row['tiles']);start=raw.find(data)
        assert start>=0 and raw.find(data,start+1)<0,(row['name'],'nonunique source row')
        index=data.index(63);assert data.count(63)==1
        patches.append(dict(offset=start+index,old='3f',new='24',name=row['name'],slot=row['slot'],role='Remove stale coming-soon marker; actual Start and A both accepted'))
    assert len(patches)==9
    b=A.bundle();edited=bytearray(raw)
    for patch in patches:edited[patch['offset']]=36
    b['raw']=bytes(edited);verified=[]
    for row in inventory['rows']:
        if 63 not in row['tiles']:continue
        m=M.fresh(b);M.put(m,CrossoverMenuIndex=row['slot'])
        M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for _ in range(row['cycle']):
            M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
            M.invoke(m,'CrossoverMenuInput')
        name,cells=menu_name(m)
        assert (63 in cells)==(not row['confirm_starts']),(row['name'],name)
        for key in [16,128]:
            n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0)
            M.invoke(n,'CrossoverMenuInput')
            assert (M.get(n,'CrossoverMenuState')==0)==row['confirm_starts']
        verified.append(name)
    O.mkdir(exist_ok=True)
    (O/'patches.json').write_text(json.dumps(dict(base_ROM_SHA256=inventory['ROM_sha256'],patches=patches,locked_Prince_marker_preserved=True,actual_patched_names_and_Start_A_verified=verified,ROM_written=False),indent=2)+'\n')
    print(json.dumps(patches))
if __name__=='__main__':main()
