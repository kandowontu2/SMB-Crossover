"""Bind Jay's stock input to the authenticated cold path in memory."""
from collections import Counter
from itertools import product
import inspect
import json
import linecache
from unittest.mock import patch

import check_jay_silius_stock_events_1110 as Stock
import check_sonic_sms_native_prototype_1110 as Lease

J,C,H,N = Stock.J,Stock.C,Stock.H,Stock.N
SOURCE = H.ROOT/'tools/reference/jay_silius_stock_carrier_1110.s'
PAGE = 216
TAIL = 640
PAGE_PIN = '9ea83f364d32c7f4b41d437752c0c58e311d7b3308835345b98a76644e6bc030'


def current_domains(parent):
    import check_sonic_eighth_cold_owner_1110 as FfLease

    ff_old = FfLease.C.ROM.read_bytes()
    ff = FfLease.FF.proposal(ff_old)[0]
    assert C.digest(ff_old)==FfLease.C.PIN and C.digest(ff)==FfLease.PIN
    ff_begin,ff_end = C.CHR+893*1024,C.CHR+901*1024
    assert parent[ff_begin:ff_end]==ff[ff_begin:ff_end]
    start,end = C.offset(93,0xa000),C.offset(94,0xa000)
    assert parent[start:end]==ff[start:end]
    roots = [FfLease.FF.Funding.gateways(raw,FfLease.C.Current.W.bundle(raw)) for raw in (ff,parent)]
    assert roots[0]==roots[1] and len(roots[0])==37
    # These two FF pages already have a complete a5 writer rebind. Restore
    # only their old coarse hashes in the historical finite census below.
    historical = bytearray(parent)
    for page in (898,900):
        start = C.CHR+page*1024
        historical[start:start+1024] = ff_old[start:start+1024]

    old_authority = inspect.getsource(Lease.chr_authority)
    if PAGE == 234:
        # This conservative historical range includes retired SMB3 form
        # arrays. The same authority below verifies the compiled seven-form
        # reader, whose current physical outputs are 524..543.
        old_domain = "    assert not any(pages.intersection(v) for v in prior['exact_finite_domains'].values())"
        actual_domain = """    overlap = {name:sorted(pages.intersection(values))
               for name,values in prior['exact_finite_domains'].items() if pages.intersection(values)}
    assert overlap == {'SMB3 seven forms81frames':[234]}, overlap"""
        assert old_authority.count(old_domain) == 1
        old_authority = old_authority.replace(old_domain, actual_domain)
    old_line = "        name=row['name'];assert name in ('M3Form2ChrLo','M3Form3ChrLo','M3Form4ChrLo','M3Form6ChrLo'),name"
    assert old_authority.count(old_line)==1
    line = '''        if row['name']=='Z2PoseChrLo':
            assert at==fairy_at and blob==fairy_bytes and n==27,(at,fairy_at,blob.hex(),fairy_bytes.hex(),n)
            changed.append(row['name'])
            continue
'''
    source = old_authority.replace(old_line,line+old_line)
    path = H.ROOT/'docs/qa/allocations/sonic-sms-fairy-repack-1110.json'
    alias = json.loads(path.read_text())['mandatory_atomic_source_change']
    at = alias['file_offset']
    fairy_bytes = bytes.fromhex(alias['new_hex'])
    assert parent[at:at+54]==fairy_bytes+bytes([1])*27
    # Existing Zelda setter emits upper=1 for these pages; low D8 cannot
    # alias physical 216. The complete loaded low table is pinned above.
    H.carrier(parent)
    namespace = dict(vars(Lease),fairy_at=at,fairy_bytes=fairy_bytes)
    label = '<Jay current CHR selector audit>'
    linecache.cache[label] = (len(source),None,source.splitlines(keepends=True),label)
    exec(compile(source,label,'exec'),namespace)
    with patch.object(Lease.Render.S,'PAGES',(PAGE,)):
        return namespace['chr_authority'](bytes(historical))


def chr_ownership(trial):
    raw = trial['raw']
    start = C.CHR+PAGE*1024
    data = raw[start:start+1024]
    assert C.digest(data) == PAGE_PIN and data[TAIL:] == bytes(1024-TAIL)
    parent = trial['b031_source']
    assert C.digest(parent)==Stock.PARENT and parent[start:start+1024]==data
    # The earlier Jay residency relocation legitimately changes Proto
    # and Sunny table offsets. Bind historical ledgers to the pinned
    # public parent and the exact current body/slot readers below.
    domains = current_domains(parent)
    recorded = H.ROOT/'build/mike-alternate-prototypes-1110/proof-v3.json'
    proof = json.loads(recorded.read_text())
    assert proof['CPU']['CHR']['source_authority']['weapons'] == domains['weapons']
    assert proof['CPU']['CHR']['physical_1KB_pages'] == [216,220]
    body = J.W.address(trial,'JnSetPose')
    assert body == 0xa276
    # Every value of X, including stale poses beyond the valid source rows,
    # reaches the compiled Jay pose clamp before any table read.
    m = C.Common.blank(trial)
    N.put(m,SelectedCharacter=16)
    m[0x730b] = 32
    poses,tiles = set(),set()
    trials = 0
    for face,state,x in product((1,2),(0,1,2,3),range(256)):
        N.put(m,PlayerFacingDir=face,Player_State=state)
        C.Vector.call(m,'JnSetPose',x=x)
        assert N.get(m,'SmChrBank') == PAGE and N.get(m,'PlayerChrBank') == PAGE
        pointer = N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)
        poses.add(pointer)
        assert 0xc000<=pointer<0xc409
        at = C.offset(97,pointer)
        n = raw[at]
        assert n==16
        for tile in raw[at+1:at+1+n:4]:
            assert tile%2 == 0 and (tile+1)*16<TAIL
            tiles.update((tile,tile+1))
        trials += 1
    assert len(poses)==8 and tiles == set(range(32)),(poses,tiles)
    return dict(physical_CHR=PAGE,page_sha=PAGE_PIN,tail=[TAIL,1024],live_body_tiles=sorted(tiles),
                paired_pose_records=len(poses),compiled_pose_inputs=trials,
                map_mirrors=domains['native_map_mirrors'],selector_domains=domains['prior_domains'],
                current_tables_exact=domains['current_tables_exact'])


def assemble_decoder(old,runtime,copy_pc):
    assert old['used']['DECODE'] == 257
    text = old['source']
    success = ' cmp #>PackedEnd\n beq Return\nFailed:'
    assert text.count(success)==1
    text = text.replace(success,f' cmp #>PackedEnd\n bne Failed\n jmp ${copy_pc:04x}\nFailed:')
    packed = J.pack(runtime)
    size = 260+len(packed)+3
    assert size<=2048,(size,len(packed))
    text, old_size = text.split('PackedEnd=$',1)
    text += f'PackedEnd=${0xd000+size:04x}\n'+old_size.split('\n',1)[1]
    decoder = H.assemble(text,{'DECODE':(0xd000,512)})
    assert decoder['used']['DECODE']==260
    data = decoder['images']['DECODE']+packed
    split = J.BOOT-0xd000
    stage = (data[:split]+b'\x4c\x00\xd0'+data[split:]).ljust(2048,b'\xea')
    return stage,decoder,size


def proposal(resident):
    trial,program,linked,old_runtime,old_stage,old_cookie,gate,extra,old_decoder,layout = resident
    ownership = chr_ownership(trial)
    print('Jay current CHR216 readers',ownership,flush=True)
    runtime = Stock.with_fire(trial,old_runtime,extra)
    bindings, fields = Stock.bindings(linked)
    data = bindings['images']['BINDINGS']
    copy_pc = 0xd800+TAIL+len(data)
    stage,decoder,stage_size = assemble_decoder(old_decoder,runtime,copy_pc)
    constants = f'TailBytes={len(data)-256}\nDecodeReturn=${decoder["symbols"]["Return"]:04x}\n'
    copy = H.assemble(constants+SOURCE.read_text(),{'COPY':(copy_pc,0xdc00-copy_pc)})
    suffix = data+copy['images']['COPY']
    descriptor = bytes.fromhex('0300014b014c01d800')
    cookie = bytes((0xa7,16,32,4))+C.sha256(stage+runtime+descriptor+suffix).digest()[:12]
    stage_text = program['source'].split('.segment "PROTO66"',1)[0]
    for old,new in ((' ldx #6\nPushDescriptor:', ' ldx #8\nPushDescriptor:'),
                    ('SceneReturn:\n', 'SceneReturn:\n pla\n pla\n'),
                    (' .byte 2,0,1,$4b,1,$4c,1\n',' .byte 3,0,1,$4b,1,$4c,1,$d8,0\n'),
                    (','.join(map(str,old_cookie)), ','.join(map(str,cookie)))):
        assert stage_text.count(old)==1,old
        stage_text = stage_text.replace(old,new)
    resident_cold = H.assemble(stage_text,{'COLD65':(0xa696,162)})
    cold = resident_cold['images']['COLD65']
    assert len(cold)==len(program['images']['COLD65'])+4
    hot_text = gate['source']
    assert hot_text.count(','.join(map(str,old_cookie)))==1
    hot_text = hot_text.replace(','.join(map(str,old_cookie)),','.join(map(str,cookie)))
    hot_origin = int(layout['hot_entry'],16)
    hot = H.assemble(hot_text,{'HOT94':(hot_origin,124)})

    raw = trial['raw']
    image = bytearray(raw)
    edits = []

    def replace(at,old,new):
        assert len(old)==len(new) and raw[at:at+len(old)]==old
        assert all(at+len(old)<=a or a+n<=at for a,n in edits)
        image[at:at+len(old)] = new
        edits.append((at,len(old)))

    start = C.CHR+PAGE*1024+TAIL
    replace(start,bytes(1024-TAIL),suffix.ljust(1024-TAIL,b'\0'))
    replace(C.CHR+331*1024,old_stage,stage)
    replace(C.offset(65,0xa696),program['images']['COLD65'].ljust(162,b'\xea'),cold.ljust(162,b'\xea'))
    old_target = program['symbols']['JaySelect']
    new_target = resident_cold['symbols']['JaySelect']
    replace(C.offset(65,0xaf00),b'\x4c'+J.u16(old_target),b'\x4c'+J.u16(new_target))
    assert program['symbols']['JaySceneOrRetire']==resident_cold['symbols']['JaySceneOrRetire']
    replace(C.offset(94,hot_origin),gate['images']['HOT94'],hot['images']['HOT94'])
    assert C.digest(raw)==Stock.RESIDENT
    return (dict(trial,raw=bytes(image)),resident_cold,runtime,stage,bindings,fields,cookie,
        extra,decoder,copy,descriptor,dict(ownership=ownership,stage_bytes=stage_size,
        copy_address=hex(copy_pc),copy_bytes=len(copy['images']['COPY']),suffix_bytes=len(suffix),
        cold_bytes=len(cold),binding_sha=C.digest(data),image_sha=C.digest(image),cookie=cookie.hex(),edits=edits))


def cold_checks(trial,program,runtime,stage,bindings,cookie,decoder,copy,descriptor):
    data = bindings['images']['BINDINGS']
    copy_pcs = {i['pc'] for i in copy['instructions']}
    decoder_pcs = {i['pc'] for i in decoder['instructions']}
    cuts = set()
    states = Counter()

    def run(m,vectors=False):
        cpu = C.ColdVector.entry(m)
        pc = program['symbols']['JaySceneOrRetire']
        m[0x16c],m[0x16d] = pc&255,pc>>8
        reads = []

        def visit(memory,c):
            if m.rawtags[1]==251 and c.pc==0xaf40:
                addr = m[6]+256*m[7]
                assert 0x101+c.sp<=addr and addr+len(descriptor)<=0x200
                reads.append(bytes(m[addr:addr+len(descriptor)]))
                assert reads[-1]==descriptor
            if m.rawtags[2]==2 and c.pc in copy_pcs|decoder_pcs:
                assert not any(header[0] for header in C.Common.headers(m)) and c.p&4
                if c.pc in copy_pcs:
                    states['copy_instruction'] += 1
                    assert m.rawtags[1]==3
                    if vectors and c.pc not in cuts:
                        cuts.add(c.pc)
                        q,d = C.Vector.clone(m,c)
                        C.ColdVector.interrupt(d,'FF')

        C.Vector.finish(m,cpu,Stock.STOP,visit)
        assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef)==(83,71,109,0x21)
        return reads

    def seed():
        m = C.Common.blank(trial)
        C.Common.scene(m,16)
        m[0x730b] = 32
        return m

    m = seed()
    assert run(m,True)==[descriptor]
    assert m.ppu_reads==6150 and C.Common.headers(m)==(cookie,)*2
    assert bytes(m.ram[3][:len(runtime)])==runtime
    assert bytes(m.ram[2][0x1000:0x1800])==stage
    assert bytes(m.ram[3][0x1000:0x1000+len(data)])==data
    assert not any(m.ram[2][0x80:0xb5]) and m.ram[2][0x33]==0
    assert run(m)==[] and m.ppu_reads==6150
    faults = ((2,0x1a80),(2,0x1bcd),(2,0x1bce),(3,0x1000),(3,0x10ff),(3,0x1100),(3,0x114d))
    for fault in faults:
        q = seed()
        q.corrupt_at = fault
        assert run(q)==[descriptor]
        assert not any(header[0] for header in C.Common.headers(q)),fault
    for bank,index in product((2,3),range(16)):
        q = C.Vector.clone(m)
        q.ram[bank][0x1fe0+index]^=1
        assert run(q)==[descriptor] and q.ppu_reads==12300
        assert C.Common.headers(q)==(cookie,)*2
    return dict(cold_ppu_reads=6150,warm_extra_ppu_reads=0,header_reloads=32,
        transfer_faults_rejected=len(faults),copy_forced_blank_NMI=len(cuts))


def main():
    donor = C.actual_donor()
    resident = Stock.resident(donor)
    trial,program,runtime,stage,bindings,fields,cookie,extra,decoder,copy,descriptor,layout = proposal(resident)
    print('Jay carrier layout',layout,flush=True)
    opening = Stock.opening(trial,runtime,cookie,extra,bindings,fields,detached=False)
    print('Jay carrier actual Main',opening,flush=True)
    cold = cold_checks(trial,program,runtime,stage,bindings,cookie,decoder,copy,descriptor)
    print('Jay carrier cold',cold,flush=True)
    budget = Stock.packed_budget(resident[3],resident[2],resident[-1])
    print(json.dumps(dict(passed=True,layout=layout,cold=cold,opening=opening,old_budget=budget,ROM_written=False,
                          Mesen=False,generated_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
