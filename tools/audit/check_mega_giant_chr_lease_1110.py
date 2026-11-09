"""Rebind the current Giant CHR lease to finite source domains and live menu writes."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_mega_giant_f33_1110 as Giant
from audit_mega_giant_chr_candidates_1110_v1 import compiled_readers, table
from inventory_playable_menu_1101_v3 import menu_name
from prepare_mini_lane_audio_native_1110 import verify_payload


C,G,M,P,R = Giant.C,Giant.G,Giant.M,Giant.P,Giant.R
HOST = R/'build/mega-giant-current-native-1110/candidate.nes'
BASE_PIN = 'ba3cba071547402fd81398d8b69659fa1b7d20cef9dfcda4df3fe8554ec592de'
HOST_PIN = '94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1'
AUDIT = R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
OLD = R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
WRITERS = R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
NATIVE = HOST.parent/'native-end/capture/result.json'
STAGE = R/'build/mega-giant-f33-1110/proof-v2.json'
PARSER = R/'build/native-parser-paired-shadow-1110/proof.json'
CAMERA = R/'build/helper-camera-admission-1110/proof.json'
MINI = R/'build/mini-native-injury-status-fix-1110/kernel.bin'
COPIER = AUDIT.with_name('common-v15.bin')
MAPPER = AUDIT.with_name('common-v15-map.bin')
PAGES = set(range(168,215,2))


def digest(raw):
    return sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def find(raw, sequence):
    return [i for i in range(len(raw)-len(sequence)+1) if raw.startswith(sequence,i)]


def linked_bytes(raw,bank,pc,expected):
    at = Giant.Rr.at(bank,pc)
    assert raw[at:at+len(expected)]==expected,(bank,hex(pc))


def prove_replacements(raw, evidence, offsets):
    proof = read(evidence)
    assert proof['passed']
    for offset in offsets:
        row = next(p for p in proof['patches']
                   if p['file_offset']<=offset<p['file_offset']+len(bytes.fromhex(p['new_hex'])))
        at,replacement=row['file_offset'],bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(replacement)]==replacement,(evidence,offset)


def finite(old,base,host,b):
    authority,historical = read(AUDIT),read(WRITERS)
    assert digest(old)==authority['current_ROM_SHA256']
    assert authority['passed'] and historical['passed']
    assert not historical['unresolved_inherited_writers'] and not historical['unresolved_table_symbols']
    domains = authority['exact_finite_domains']
    assert not any(PAGES.intersection(p) for p in domains.values())
    for row in authority['current_table_bindings']:
        at,size=row['offset'],row['bytes']
        assert digest(base[at:at+size])==digest(host[at:at+size])==row['SHA256'],row['name']
    for row in authority['inherited_private_writer_chunks_exact']:
        assert any(digest(P.chr_page(base,p))==digest(P.chr_page(host,p))==row['SHA256'] for p in row['pages']),row
    for row in historical['native_spans']:
        start,size=row['offset'],row['size']
        expected=bytes.fromhex(row['hex'])
        if row['name']=='MaaLagChrGuard':
            expected=bytes.fromhex('ad0260d006ad0a73c902603860a9f8b8')
        assert base[start:start+size]==host[start:start+size]==expected,row['name']
    moved = {}
    exact = 0
    for row in historical['unchanged_inherited_writers']:
        if not row['file'].endswith('.nes'):
            continue
        offset = row['file_offset']
        original = bytes.fromhex(row['old_bytes'])
        current = base[offset:offset+len(original)]
        assert host[offset:offset+len(original)]==current,offset
        if current==original:
            exact += 1
        else:
            moved[offset] = dict(old=original.hex(),current=current.hex(),segment=row['segment'])
    assert exact==794 and len(moved)==22
    parser=(17172,1036458,1036475,1036510)
    audio=(314270,)
    camera=(217802,217831)
    helper=(216014,216142,216148,216151,216157,216160,216166,216169,216175,216181,217232)
    retired=(1953144,1953403,1953411,1953416)
    actual=set(moved)
    assert actual==set(parser+audio+camera+retired+helper)
    prove_replacements(base,PARSER,parser)
    prove_replacements(base,CAMERA,camera)
    assert base[314269:314292].hex()=='c6e28a91e3e6e3d00ce6e4a5e4c97cd004a97485e48a60'
    assert C.address(b,'HpRamStart')==0x7382 and C.address(b,'HpRamEnd')<=0x73e0
    assert base[217228:217233].hex()=='a9008dc173'
    assert all(moved[at]['segment']=='CROSSOVER_HELPERS' for at in set(actual)&set(helper+camera))
    assert all(moved[at]['segment']=='ARTHUR_CACHE_EXEC' and (at-P.CHR_START)//1024==883 for at in retired)
    dk={q for q in domains['Granted DK code/art']}
    assert 883 in dk and all(P.chr_page(base,p)==P.chr_page(host,p)==P.chr_page(old,p) for p in dk)
    _,legacy=table(b,'ChrPhysicalMap',256)
    assert not PAGES&set(legacy)
    for bank in (119,120,125,127):
        linked_bytes(host,bank,0xee36,legacy)
    weapon = compiled_readers(b)
    _,hud=table(b,'InvHudPhysicalBanks',8)
    assert set(hud)==set(range(236,244))
    return dict(finite_source_domains=len(domains),exact_selector_tables=len(authority['current_table_bindings']),
                exact_private_writer_chunks=len(authority['inherited_private_writer_chunks_exact']),
                exact_inherited_writers=exact,changed=moved,weapon=weapon,Hud=list(hud),
                replacement_classes=dict(native_parser=parser,excitebike_audio=audio,helper_camera=camera,
                                         helper_state=sorted(actual&set(helper)),Arthur_retired=retired))


def current_additions(old,base,host,b):
    changed = [p for p in range(1024) if P.chr_page(base,p)!=P.chr_page(host,p)]
    assert changed==sorted(PAGES)
    stage = read(STAGE)
    for row in stage['physical_carriers']:
        p = row['page']
        assert digest(P.chr_page(base,p))==row['old_SHA256']
        assert digest(P.chr_page(host,p))==row['new_SHA256']
    addr = {0x5101,*range(0x5120,0x512c),0x5130}
    named = ('CurrentCHRBank','SmChrBank','X5ChrMode','X5SpecialChrUpper','X5WideChrActive','X5HudChrUpper',
             'SsChrActive','SsChrPhysical','InvHudActive','InvHudPhysical')
    addr.update(C.address(b,n) for n in named)

    def writes(raw):
        return {(at,raw[at:at+3].hex()) for at in range(16,P.CHR_START-2)
                if raw[at] in (0x8c,0x8d,0x8e,0x99,0x9d) and (raw[at+1]|raw[at+2]<<8) in addr}

    earlier,current,combined=map(writes,(old,base,host))
    assert current==combined
    assert earlier-current=={(1014266,'8c3051')}
    assert current-earlier=={(546188,'8dee73'),(548580,'8d067e'),(548590,'8dec73'),(548595,'8d057e')}
    linked_bytes(base,66,0xb57a,bytes.fromhex('a9018dee738d46013860'))
    linked_bytes(base,66,0xbecf,bytes.fromhex('a9c88d4b018d067ea9838de473a9038dec73a9018d057e'))
    linked_bytes(base,123,0xaf40,COPIER.read_bytes())
    linked_bytes(base,123,0xb9d6,MAPPER.read_bytes())
    # AF40 is a descriptor-driven common reader. Current public retains one
    # packet and Giant adds one typed scene packet. The old zero of $5130
    # was after the physical 5123 latch, not a different source page.
    worker=bytes.fromhex('a9408d6c01a9af8d6d01a9fb')
    assert find(base[:P.CHR_START],worker)==[535426]
    assert find(host[:P.CHR_START],worker)==[535426,695916]
    assert MAPPER.read_bytes()[-6:]==bytes.fromhex('010009d0c703')  # Mini metadata 967.
    scene=Giant.Rr.native_slice(host,84,0xbe00,256)
    assert scene.count(bytes((2,1,1,0xd0,214,0,212,0)))==1
    # The inherited common descriptor source sets each row's upper before
    # publishing its low. Variant9's two rows are the only overlap.
    verify_payload(base,MINI)
    verify_payload(host,MINI)
    mapper=Giant.Rr.native_slice(host,123,0xb9d6,23)
    assert mapper.hex()=='a5050a186905a8b1068d305188b1068d2351a0002c0220'
    assert all(not PAGES.intersection(domain) for domain in ((967,968),range(728,736),
                 (301,305,337,362,363,440,819,666,441)))
    return dict(exact_modified_pages=changed,new_public_CHR_shadow_stores=sorted(current-earlier),
                retired_hardware_write=sorted(earlier-current),Giant_only_descriptor_pages=[214,212],
                legacy_Mini_descriptor_pages=[967,962,963,964,965,966],
                additional_Giant_direct_store_sites=0)


def menu(b):
    profiles=set()
    counters=Counter()
    physical=set()
    for slot in range(32):
        m=M.fresh(b)
        M.put(m,CrossoverMenuIndex=slot,CrossoverMenuState=2)
        for entry in ('MenuResolveCharacter','QueueSelection'):
            M.invoke(m,entry)
        seen=set()
        for _ in range(32):
            name,tiles=menu_name(m)
            owner=M.get(m,'SelectedCharacter')
            state=(owner,tuple(tiles),bytes(m[0x5fe0:0x5fff]),M.get(m,'MarioVariant'))
            if state in seen:
                break
            seen.add(state)
            profiles.add((slot,owner,name))
            view=M.fork(m)
            view.writes.clear()
            M.put(view,VRAM_Buffer1_Offset=0)
            upper=view.upper
            for entry in ('DrawSelectionPreview','X5PublishChr'):
                M.invoke(view,entry)
            for address,value in view.writes:
                if address==0x5130:
                    upper=value&3
                elif 0x5120<=address<0x512c:
                    page=value|(upper<<8)
                    assert page not in PAGES,(slot,owner,name,hex(address),page)
                    physical.add(page)
                    counters['physical_store_events']+=1
            assert not set(view.chr_latches)&PAGES,(slot,owner,name,view.chr_latches)
            counters['menu_states']+=1
            M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
            M.invoke(m,'CrossoverMenuInput')
        else:
            raise AssertionError(('Native Select cycle bound',slot))
    return profiles,dict(counters,physical_pages=sorted(physical))


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--base',type=Path,default=C.HOST)
    args=cli.parse_args()
    old,base,host=(p.read_bytes() for p in (OLD,args.base,HOST))
    assert digest(base)==BASE_PIN and digest(host)==HOST_PIN
    assert host[:16]==base[:16]
    b=C.bundle(host)
    evidence=read(NATIVE)
    assert evidence['passed'] and evidence['ROM_sha256']==HOST_PIN and evidence['terminal']['lives']==2
    domains=finite(old,base,host,b)
    additions=current_additions(old,base,host,b)
    a,x=menu(C.bundle(base)); z,y=menu(b)
    assert z-a=={(0,0,'MEGA GIANT MARIO')} and not a-z,(a-z,z-a)
    assert not set(x['physical_pages']+y['physical_pages'])&PAGES
    result=dict(passed=True,ROM_written=False,release_grant=False,parent_SHA256=BASE_PIN,candidate_SHA256=HOST_PIN,
                domains=domains,additions=additions,menu=dict(base=x,candidate=y),
                native_clear_SHA256=C.sha(NATIVE),
                scope='Bounded finite authored publishers, compiled writer changes, and real menu register writes. '
                      'Physical lease decision remains with root. Native all-power and all-scene replay are separate.',
                bindings={str(p):C.sha(p) for p in (Path(__file__),args.base,HOST,OLD,AUDIT,WRITERS,NATIVE,STAGE,
                                                   PARSER,CAMERA,MINI,COPIER,MAPPER)})
    args.output.mkdir(exist_ok=True)
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(domains=domains['finite_source_domains'],exact_writers=domains['exact_inherited_writers'],
                          deltas=len(domains['changed']),menu=x['menu_states']+y['menu_states'],pages=sorted(PAGES))))


if __name__=='__main__':
    main()
