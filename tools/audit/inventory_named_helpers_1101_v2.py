"""Read installed helper records and run compiled admission; no emulator or edits."""
from pathlib import Path
import hashlib,json
import inventory_current_helpers_1101_v1 as A
R=A.R
ROM=R/'build/metal-storm-decline-1101-v40/candidate.nes'
O=R/'build/helper-named-inventory-1101-v2'
def main():
    O.mkdir(exist_ok=True)
    b=A.scoped_load(ROM)
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert ROM.read_bytes()==installed.read_bytes(),'Nightly changed; pin the actual new input first'
    fields=['Key','Area','XLo','XHi','Y','Width','Axis','EasyGate','HardGate']
    records=[]
    for i in range(34):
        r={f:b['raw'][A.location(b,'HpData'+f)+i] for f in fields}
        r.update(record=i,stage=f"{r['Key']//4+1}-{r['Key']%4+1}",center_x=r['XLo']+256*r['XHi'])
        r['left_x']=r['center_x']-4*r['Width']
        records.append(r)
    rows=[]
    for raw,cv in [(i,0) for i in range(37)]+[(5,i) for i in range(1,4)]:
        for mode in range(2):
            m=A.M.fresh(b)
            A.M.put(m,SelectedCharacter=raw,Cv3Variant=cv,CrossoverBehaviorVersion=mode,WorldNumber=0,LevelNumber=0,AreaType=1,AreaAddrsLOffset=5,AreaPointer=37,TimerControl=1)
            A.M.invoke(m,'HpConfigure')
            n=A.M.get(m,'HpCount')
            rows.append(dict(raw=raw,cv3=cv,mode=mode,records=[A.M.get(m,'HpRecord',i) for i in range(n)]))
    q=dict(ROM_sha256=hashlib.sha256(ROM.read_bytes()).hexdigest(),installed_bytes_identical=True,records=records,admission_11=rows,scope='Compiled HpConfigure 80 cases; placement left-edge projection follows actual HpProjectPosition width*4. No native route claim.')
    (O/'inventory.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(cases=len(rows),records=len(records),sha256=q['ROM_sha256'])))
if __name__=='__main__':main()
