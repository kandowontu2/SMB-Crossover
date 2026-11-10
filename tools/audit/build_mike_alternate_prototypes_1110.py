"""Source-funded Jay/Steve prototypes and shared Sonic menu endpoint.

Only private patch/source receipts are written. Root emits/qualifies the ROM.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import tempfile

import compose_remaining_roster_starts_1110 as Current
import check_remaining_roster_starts_1110 as Menu
from check_tmnt_render_oa import address, location

R, I, W = Menu.R, Menu.I, Menu.W
OUT = R/'build/mike-alternate-prototypes-1110'
SOURCE = R/'tools/reference/mike_alternate_native_1110.s'
PIN = 'd1333adf3d9e62354ccfab9c21490f95bc972200c513183a309d90eed09728d8'
ART_BYTES = 1033
COMPACT_BYTES = 775
A_BYTES = 133
ALT_A = 0xa000+COMPACT_BYTES
ALT_C = 0xc000+COMPACT_BYTES+A_BYTES


def digest(raw):
    return sha256(raw).hexdigest()


def off(bank, pc):
    return 16+bank*8192+(pc&8191)


def read(path):
    return json.loads(path.read_bytes())


def source_bundle():
    base = Current.compose()[1]
    assert digest(base) == PIN
    return W.bundle(base)


def compact(bundle):
    raw = bundle['raw']
    leaf_names = sorted(name for name in bundle['syms']
        if re.fullmatch(r'Jn(?:Pose[0-6][RL]|Shot\d+_[01](?:Left)?|Item\d+|Heart|Star|BigHeart|BatNativeRecord\d+)',name))
    leaves = {}
    for name in leaf_names:
        at = location(bundle,name)
        blob = raw[at:at+raw[at]+1]
        assert blob[0]%4 == 0 and len(blob)<128
        leaves[name] = blob
    assert len(leaves)==93
    tables = []
    def pointers(lo,hi,n):
        a,b = location(bundle,lo),location(bundle,hi)
        return [raw[a+i]+256*raw[b+i] for i in range(n)]
    tables += [('Body',pointers('JnBodyRLo','JnBodyRHi',7)+pointers('JnBodyLLo','JnBodyLHi',7))]
    for stem,n in (('JnItem',14),('JnShotAll',52),('JnBatRecord',60)):
        tables.append((stem,pointers(stem+'Lo',stem+'Hi',n)))
    old_name = {address(bundle,name):name for name in leaf_names}
    assert all(pointer in old_name for _,group in tables for pointer in group)
    pool = bytearray()
    new_names, blobs = {},{}
    def add(name):
        blob = leaves[name]
        if blob not in blobs:
            blobs[blob] = 0xc000+len(pool)
            pool.extend(blob)
        new_names[name] = blobs[blob]
    for i in range(10):
        add(f'JnBatNativeRecord{i}')
    assert len(pool)==50 and max(new_names.values())<0xc100
    starts = {}
    for stem,group in tables:
        starts[stem+'Lo'] = 0xc000+len(pool)
        pool.extend(bytes(len(group)))
        if stem!='JnBatRecord':
            starts[stem+'Hi'] = 0xc000+len(pool)
            pool.extend(bytes(len(group)))
    assert len(pool)==270
    for face in ('R','L'):
        for pose in range(7):
            add(f'JnPose{pose}{face}')
    assert all(0xc100<=new_names[f'JnPose{pose}{face}']<0xc200
               for face in ('R','L') for pose in range(7))
    for name in leaf_names:
        add(name)
    assert len(pool)==COMPACT_BYTES and len(blobs)==71
    for stem,group in tables:
        for i,pointer in enumerate(group):
            value = new_names[old_name[pointer]]
            pool[starts[stem+'Lo']-0xc000+i] = value&255
            if stem=='JnBatRecord':
                assert value>>8==0xc0
            else:
                pool[starts[stem+'Hi']-0xc000+i] = value>>8
    for name,blob in leaves.items():
        at = new_names[name]-0xc000
        assert pool[at:at+len(blob)]==blob
    labels = dict(new_names)
    labels.update(CompactBodyLo=starts['BodyLo'],CompactBodyHi=starts['BodyHi'],
                  JnBodyRLo=starts['BodyLo'],JnBodyLLo=starts['BodyLo']+7,
                  JnBodyRHi=starts['BodyHi'],JnBodyLHi=starts['BodyHi']+7)
    labels.update({k:v for k,v in starts.items() if k.startswith('Jn')})
    return bytes(pool),labels,dict(leaf_records=93,unique_records=71,
        source_art_bytes=ART_BYTES,compact_bytes=len(pool),funded_bytes=ART_BYTES-len(pool),
        bat_records_single_high_page=0xc0,legacy_unused_pointer_bytes=52,
        bat_constant_high_table_bytes=60,complete_original_records_exact=True)


def encoded(text, width):
    assert len(text)<=width
    return bytes(36 if char==' ' else ord(char)-55 for char in text.ljust(width))


def assemble(bundle,labels,art):
    symbols = ('CurrentBankC','JnPose','SmChrBank','PlayerChrBank','PlayerFacingDir',
               'SmPosePtr','ObjectMetasprite','METASPRITE_SAMUS_BODY','X5SetPhysicalChr',
               'VRAM_Buffer1_Offset','VRAM_Buffer1','FmGroups','R0','MacVariant',
               'CrossoverMenuIndex','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','Player_State')
    definitions = ''.join(f'{name}=${address(bundle,name):04x}\n' for name in symbols)
    definitions += ''.join(f'{name}=${labels[name]:04x}\n' for name in ('CompactBodyLo','CompactBodyHi'))
    definitions += 'PrototypeSteveTitleC=PrototypeTitles+$2010\n'
    for key,text,width in (('JAY_TITLE','JAY MCCRAY',16),('STEVE_TITLE','STEVE HERMANN',16),
                           ('SONIC_TITLE','SONIC',16),('JAY_HUD','JAY    ',7)):
        definitions += f'.define {key} '+','.join(f'${n:02x}' for n in encoded(text,width))+'\n'
    for key,hero in (('JAY_PALETTE','jay'),('STEVE_PALETTE','steve')):
        definitions += f'.define {key} '+','.join(f'${n:02x}' for n in art['images'][hero]['player_palette'])+'\n'
    areas = [('POSE',0xa276,85),('PAL',0xa1be,54),('MENU_GATE',0xb746,42),
             ('TOGGLE_ENTRY',0xbf79,8),('TOGGLE_HEAD',0xbf65,16),('TOGGLE_TAIL',0xbefd,12),
             ('HUD_HOOK',0xa901,18),('ALT_A',ALT_A,A_BYTES),('ALT_C',ALT_C,ART_BYTES-COMPACT_BYTES-A_BYTES)]
    config = 'MEMORY{'+''.join(f'M{i}:start=${pc:04x},size=${size:x},file=%O,fill=yes,fillval=$ea;'
                              for i,(_,pc,size) in enumerate(areas))+'}SEGMENTS{'
    config += ''.join(f'{name}:load=M{i},type=ro;' for i,(name,_,_) in enumerate(areas))+'}'
    with tempfile.TemporaryDirectory(prefix='assemble-',dir=OUT) as tmp:
        root = Path(tmp)
        source, cfg, obj, binary, syms = (root/f'prototype.{suffix}' for suffix in ('s','cfg','o','bin','lbl'))
        source.write_text(definitions+SOURCE.read_text())
        cfg.write_text(config)
        cc = R/'tools/Windows/cc65/bin'
        for command in ((cc/'ca65.exe',source,'-o',obj),
                        (cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',syms)):
            result = subprocess.run(list(map(str,command)),capture_output=True,text=True)
            assert result.returncode==0,result.stderr
        linked = binary.read_bytes()
        exports = {line.split()[2][1:]:int(line.split()[1],16) for line in syms.read_text().splitlines()}
    assert len(linked)==sum(size for _,_,size in areas)
    blocks, cursor = {},0
    for name,pc,size in areas:
        blocks[name] = linked[cursor:cursor+size]
        cursor += size
    assert exports['PrototypeNamesEnd']<=ALT_A+A_BYTES
    assert exports['PrototypeAltEnd']<=0xc000+ART_BYTES
    return blocks,exports,areas


def patch_image(bundle,pool,labels,blocks,exports):
    original = bundle['raw']
    raw = bytearray(original)
    patches = []
    claimed = set()
    def put(at,new,role):
        new = bytes(new)
        before = original[at:at+len(new)]
        occupied = set(range(at,at+len(new)))
        assert not occupied&claimed and before!=new,role
        claimed.update(occupied)
        raw[at:at+len(new)] = new
        patches.append(dict(file_offset=at,old_hex=before.hex(),new_hex=new.hex(),role=role))
    for segment,bank,pc in (('POSE',96,0xa276),('PAL',96,0xa1be),('MENU_GATE',81,0xb746),
                            ('TOGGLE_ENTRY',76,0xbf79),('TOGGLE_HEAD',76,0xbf65),('TOGGLE_TAIL',76,0xbefd),
                            ('HUD_HOOK',96,0xa901)):
        put(off(bank,pc),blocks[segment],segment)
    assert original[off(76,0xbb9d):off(76,0xbba0)]==bytes.fromhex('4c11bf')
    put(off(76,0xbb9d),b'\x4c'+exports['PrototypeToggleEntry'].to_bytes(2,'little'),'Mike alternate before exact DK fallback')
    # The complete original art envelope is compacted and source-funds both
    # native CPU views. Rogue audio begins at C409 and remains byte-identical.
    whole = pool+blocks['ALT_A']+blocks['ALT_C']
    assert len(whole)==ART_BYTES
    put(off(97,0xc000),whole,'Exact Mike sprite aliases and source-funded prototype workers')
    combat_lo, combat_hi = off(98,0xa000),off(98,0xac91)
    for name in ('JnItemLo','JnItemHi','JnShotAllLo','JnShotAllHi','JnBatRecordLo','JnBatRecordHi'):
        needle = b'\xb9'+address(bundle,name).to_bytes(2,'little')
        hits = [at for at in range(combat_lo,combat_hi-2) if original[at:at+3]==needle]
        assert len(hits)==1,(name,hits)
        new = bytes((0xa9,0xc0,0xea)) if name=='JnBatRecordHi' else b'\xb9'+labels[name].to_bytes(2,'little')
        put(hits[0],new,'Retarget '+name if name!='JnBatRecordHi' else 'All60 bat high bytes are source-proven C0')
    for name in ('JnHeart','JnStar','JnBigHeart'):
        value = address(bundle,name)
        needle = bytes((0xa9,value&255,0x85,3,0xa9,value>>8))
        hits = [at for at in range(combat_lo,combat_hi-5) if original[at:at+6]==needle]
        assert len(hits)==1,(name,hits)
        value = labels[name]
        put(hits[0],bytes((0xa9,value&255,0x85,3,0xa9,value>>8)),'Retarget original '+name)
    for hero,page in (('jay',216),('steve',220)):
        blob = (OUT/f'{hero}-native.chr').read_bytes()
        assert len(blob)==1024
        put(1048592+page*1024,blob,'Authentic donor core '+hero)
    assert raw[off(97,0xc409):off(98,0xa000)]==original[off(97,0xc409):off(98,0xa000)]
    assert raw[off(76,0xbced):off(76,0xbd0d)]==original[off(76,0xbced):off(76,0xbd0d)]
    new_bundle = deepcopy(bundle)
    new_bundle['raw'] = bytes(raw)
    for name,pc in labels.items():
        if name in new_bundle['syms']:
            new_bundle['syms'][name]['val'] = hex(pc)
    return new_bundle,patches


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--compile-only',action='store_true')
    args = cli.parse_args()
    bundle = source_bundle()
    art = read(OUT/'native-art.json')
    assert art['passed'] and art['source_SHA256']==digest((R/'tools/audit/prepare_mike_alternate_art_1110.py').read_bytes())
    pool,labels,funding = compact(bundle)
    blocks,exports,areas = assemble(bundle,labels,art)
    after,patches = patch_image(bundle,pool,labels,blocks,exports)
    print('Linked prototype',digest(after['raw']),exports,flush=True)
    result = dict(prepared=True,passed=False,CPU_pending=True,native_pending=True,ROM_written=False,
                  parent_SHA256=PIN,expected_memory_only_SHA256=digest(after['raw']),
                  patches=patches,labels=labels,exports=exports,funding=funding,areas=areas,
                  source_bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in
                                   (Path(__file__),SOURCE,OUT/'native-art.json',OUT/'jay-native.chr',OUT/'steve-native.chr')},
                  selector=dict(address=0x5fe8,mask=0x60,values={'Mike':0,'Jay':0x20,'Steve':0x40}),
                  limitation='Mike host movement/attacks/lifecycle. Original Jay/Steve abilities/audio pending. '
                             'Original16x32body cores; Steve palette reduction and omitted arm/jump extension.')
    (OUT/'linked.json').write_text(json.dumps(result,indent=2)+'\n')
    if not args.compile_only:
        raise AssertionError('CPU qualifier not yet attached; use --compile-only while preparing source.')


if __name__=='__main__':
    main()
