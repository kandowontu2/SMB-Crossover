"""Bind a 34-page native MMC5 CHR candidate pool to the exact current ROM."""

import argparse
import hashlib
import json
from pathlib import Path

from check_mega_giant_geometry_1110_v1 import R, ROM, HOST_PIN, address, bundle, sha
from check_mega_giant_ppu_mapping_1110_v1 import CHR_START, PAGE_BYTES, chr_page
from check_tmnt_render_oa import location


PAGES=tuple(range(168,235,2))
MAP_BANKS=(119,120,125,127)
LEGACY_LEDGER=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
FINITE_DOMAINS=R/'build/dkjr-native-source-1102-v2/carrier-proposal-v13.json'


def table(b,name,count):
    start=location(b,name)
    return start,b['raw'][start:start+count]


def prg_at(bank,offset):
    return 16+8192*bank+offset


def compiled_readers(b):
    raw=b['raw']
    cases={
        'SsPhysicalBanks':(17,((60,0x1812),(60,0x192e),(60,0x1e9f))),
        'SmWeaponPhysicalBanks':(2,((10,0x10a4),)),
        'AvPhysicalBanks':(17,((61,0x199c),)),
    }
    used=set()
    reports={}
    for name,(count,sites) in cases.items():
        start,values=table(b,name,count)
        target=address(b,name).to_bytes(2,'little')
        readers=[]
        for bank,offset in sites:
            at=prg_at(bank,offset)
            code=raw[at:at+5]
            assert code in (b'\xbd'+target+b'\x09\x01',b'\xad'+target+b'\x09\x01',
                            b'\xad'+(address(b,name)+4).to_bytes(2,'little')+b'\x09\x01'),(name,hex(at),code.hex())
            readers.append(dict(bank=bank,file_offset=at,instructions=code.hex()))
        outputs=sorted({p|1 for p in values})
        used.update(outputs)
        reports[name]=dict(table_file_offset=start,bytes=values.hex(),actual_mmc5_outputs=outputs,readers=readers)
    bill=bytes.fromhex('a9e809018d067e')
    bank=25
    blob=raw[prg_at(bank,0):prg_at(bank+1,0)]
    assert blob.count(bill)==1
    used.add(233)
    reports['Bill frozen flame']=dict(bank=bank,file_offset=prg_at(bank,blob.index(bill)),
                                      instructions=bill.hex(),actual_mmc5_outputs=[233])
    assert not used.intersection(PAGES)
    return reports


def inheritance(raw):
    old=json.loads(LEGACY_LEDGER.read_text())
    prior=json.loads(FINITE_DOMAINS.read_text())
    exact_tables={}
    for name,row in old['current_table_bytes'].items():
        if not row['file'].endswith('.nes'):
            continue
        start=row['file_offset']
        expected=bytes.fromhex(row['hex'])
        assert raw[start:start+len(expected)]==expected,name
        exact_tables[name]=start

    collisions={name:sorted(set(PAGES).intersection(values)) for name,values in prior['current_finite_domains'].items()
                if set(PAGES).intersection(values)}
    assert collisions=={'SMB3 seven forms81frames':[234]}
    assert prior['current_finite_domains']['SMB3 current actual selector']==list(range(524,544))
    assert not set(PAGES).intersection(prior['proposed_code']+prior['proposed_art'])

    exact_writers=0
    changed=[]
    for row in old['unchanged_inherited_writers']:
        if not row['file'].endswith('.nes'):
            continue
        at=row['file_offset']
        want=bytes.fromhex(row['old_bytes'])
        actual=raw[at:at+len(want)]
        if actual==want:
            exact_writers+=1
        else:
            changed.append(dict(segment=row['segment'],file_offset=at,old=want.hex(),actual=actual.hex(),
                                old_source_instruction=row['source']['text']))
    assert exact_writers==797 and len(changed)==19
    return dict(exact_inherited_tables=exact_tables,exact_inherited_writers=exact_writers,
                changed_old_writer_preimages_for_review=changed,obsolete_source_table_collision=collisions)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(ROM)==HOST_PIN
    raw=ROM.read_bytes()
    b=bundle(raw)
    at,legacy=table(b,'ChrPhysicalMap',256)
    assert at==prg_at(127,0xe36) and not set(PAGES).intersection(legacy)
    mirrors=[prg_at(bank,0xe36) for bank in MAP_BANKS]
    assert all(raw[start:start+256]==legacy for start in mirrors)
    hud_at,hud=table(b,'InvHudPhysicalBanks',8)
    assert list(hud)==list(range(236,244))
    reference=chr_page(raw,2)
    assert any(reference) and all(chr_page(raw,p)==reference for p in PAGES)
    pages=[dict(physical_page=p,file_offset=CHR_START+p*PAGE_BYTES,
                preimage_SHA256=hashlib.sha256(chr_page(raw,p)).hexdigest()) for p in PAGES]
    report=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,
                host_SHA256=HOST_PIN,legacy_map_mirrors=mirrors,legacy_map_values=sorted(set(legacy)),
                legacy_HUD_table_file_offset=hud_at,legacy_HUD_pages=list(hud),
                special_readers=compiled_readers(b),pool=pages,proposed_Giant_art=list(PAGES[:22]),
                tentative_Giant_backing=list(PAGES[22:28]),remaining_unallocated=list(PAGES[28:]),
                duplicated_reference_page=2,**inheritance(raw),
                scope='Exact current MMC5 legacy map, native special selector and named prior finite-domain evidence. '
                      'Even halves are excluded by compiled ORA #1, independently of duplicate art. '
                      'Changed inherited indirect writers and newer private direct publishers require separate review '
                      'before allocation. No lease or native build.',
                bindings={str(p):sha(p) for p in (Path(__file__),ROM,LEGACY_LEDGER,FINITE_DOMAINS,
                    R/'src/chr_map_mmc5.inc',R/'src/special_weapons.s',R/'src/samus_weapons.s',
                    R/'src/remaining_weapons.s',R/'src/water_draw_proposal.inc')})
    (args.output/'chr-funding-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,candidate_pages=len(PAGES),art_pages=22,
                          tentative_backing=6,resource_granted=False)))


if __name__=='__main__':
    main()
