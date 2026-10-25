"""Extract current linked legacy Hard item requirements, without claiming tests.

This intentionally covers only the ten identities using the old inventory.
Native alternate/new-family rewards and Easy's source tiers remain separate.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from check_tmnt_render_oa import load,Memory,location,address

ROOT=Path(__file__).resolve().parents[2]
IDENTITIES=[('megaman',1),('proto',1),('samus',2),('bill',3),('lance',3),('link',4),
    ('simon',5),('bass',9),('ryu',10),('sophia',11)]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=load(a.rom);m=Memory(b);bank=(location(b,'InvItemCount')-16)//8192;m.page(1,bank)
    tables={n:address(b,n)for n in ['InvItemCount','InvMushroomLo','InvMushroomHi','InvReplacementLo','InvReplacementHi',
        'InvNameLo','InvNameHi','InvAvailability','InvSelectable','InvMaxAmmo','InvCosts']}
    def get(n,i):return m[tables[n]+i]
    rows=[];disabled=[]
    for identity,char in IDENTITIES:
        count=get('InvItemCount',char);assert 0<count<16
        mushroom=get('InvMushroomLo',char)+256*get('InvMushroomHi',char)
        replacement=get('InvReplacementLo',char)+256*get('InvReplacementHi',char)
        rows.append(dict(identity=identity,mode='hard',local_id=0,name='MUSHROOM',acquisition='native mushroom transform',
            prerequisite='base player status',selectable=False,max_ammo=0,cost=0,emergence='UNVERIFIED_CURRENT_HASH',
            pickup='UNVERIFIED_CURRENT_HASH',graphics='UNVERIFIED_CURRENT_HASH',SFX='UNVERIFIED_CURRENT_HASH',
            ability_use='UNVERIFIED_CURRENT_HASH',damage_and_expiry='UNVERIFIED_CURRENT_HASH'))
        for item in range(1,count+1):
            index=char*16+item;pointer=get('InvNameLo',index)+256*get('InvNameHi',index)
            codes=[m[pointer+i]for i in range(7)]
            assert all(0<=v<=36 for v in codes),(identity,item,codes)
            name=''.join(str(v)if v<10 else chr(65+v-10)if v<36 else ' 'for v in codes).strip();assert name
            available=get('InvAvailability',index);automatic=bool(mushroom&(1<<item))
            if not available and not automatic:
                disabled.append(dict(identity=identity,local_id=item,name=name,
                    scope='Disabled in linked legacy availability and not a linked mushroom grant. Other source/native-tier paths require separate audit.'))
                continue
            acquisition='mushroom automatic grant'if automatic else 'legacy upgrade actor'
            prerequisite=('any replacement predecessor in mask '+hex(replacement)if available==254 else
                'owned local item '+str(available)if 0<available<254 else 'none')
            rows.append(dict(identity=identity,mode='hard',local_id=item,name=name,acquisition=acquisition,
                prerequisite=prerequisite,selectable=bool(get('InvSelectable',index)),max_ammo=get('InvMaxAmmo',index),
                cost=get('InvCosts',index),emergence='UNVERIFIED_CURRENT_HASH',pickup='UNVERIFIED_CURRENT_HASH',
                graphics='UNVERIFIED_CURRENT_HASH',SFX='UNVERIFIED_CURRENT_HASH',ability_use='UNVERIFIED_CURRENT_HASH',
                damage_and_expiry='UNVERIFIED_CURRENT_HASH'))
    with(a.output/'legacy-hard-requirements.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    q=dict(inventory_complete=False,goal_complete=False,ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),
        identities=len(IDENTITIES),required_rows=len(rows),requirements=rows,disabled_legacy_rows=disabled,
        tables_bank=bank,linked_names_are_NES_font_codes=True,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        linked_table_source_sha256=hashlib.sha256((ROOT/'src/inventory_data.inc').read_bytes()).hexdigest(),
        scope='Requirements extracted from actual linked tables and native names, not the potentially stale generator or guide. No coverage is inferred from a sibling or earlier hash and no execution/physical collection is claimed. All rows begin unverified. Easy/source tiers, common stars/1ups/energy, every native alternate/new family, injury/expiry rules, natural emergence, actual collection/use/SFX/graphics and final both-mapper evidence still require the full inventory and tests.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['inventory_complete','ROM_sha256','identities','required_rows']},indent=2))


if __name__=='__main__':main()
