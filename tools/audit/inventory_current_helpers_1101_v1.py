"""Inventory compiled helpers and actual default-family admission; no route claims."""
from pathlib import Path
import hashlib,json
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location

R=Path(__file__).resolve().parents[2]
ROM=R/'build/metal-storm-death-host-1101-v34/candidate.nes'
O=R/'build/helper-inventory-1101-v1'

def main():
    O.mkdir(exist_ok=True)
    b=scoped_load(ROM)
    fields=['Key','Area','XLo','XHi','Y','Width','Axis','EasyGate','HardGate']
    records=[]
    for i in range(34):
        r={f:b['raw'][location(b,'HpData'+f)+i] for f in fields}
        r.update(record=i,stage=f"{r['Key']//4+1}-{r['Key']%4+1}",center_x=r['XLo']+256*r['XHi'])
        records.append(r)
    admission=[]
    for character in range(36):
        for mode in range(2):
            m=M.fresh(b)
            M.put(m,SelectedCharacter=character,CrossoverBehaviorVersion=mode,
                  WorldNumber=0,LevelNumber=0,AreaType=1,AreaAddrsLOffset=5,
                  AreaPointer=37,TimerControl=1)
            M.invoke(m,'HpConfigure')
            n=M.get(m,'HpCount')
            assert n<=3,(character,mode,n)
            admission.append(dict(character=character,mode=mode,
                records=[M.get(m,'HpRecord',i) for i in range(n)]))
    q=dict(ROM_sha256=hashlib.sha256(ROM.read_bytes()).hexdigest(),records=records,
           default_family_11_admission=admission,
           scope='Actual compiled HpConfigure, zeroed alternate selectors. Separate Goku/Karnov and Thomas managers are not invoked. Not a full alternate roster, visibility or route qualification.',
           additional_source_placements=[
             dict(characters=['Goku','Karnov'],stage='1-1',center_x=x,left_x=x-16,initial_y=208,native_actor=37)
             for x in [704,888]]+[
             dict(characters=['Thomas'],stage='1-1',left_x=x,initial_y=192,native_actor=37)
             for x in [400,560,688,864]])
    (O/'inventory.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(records=len(records),admission_cases=len(admission),
        default_families_with_11_helper=[a['character'] for a in admission if a['mode']==0 and a['records']],
        first_record=records[0])))

if __name__=='__main__':main()
