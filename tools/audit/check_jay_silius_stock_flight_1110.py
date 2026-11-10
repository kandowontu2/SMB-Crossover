"""Run Jay's stock shot flight on actual donor and crossover 6502 code."""
from collections import Counter
from itertools import product
import json
from unittest.mock import patch

import check_jay_silius_stock_carrier_1110 as Prior
import check_jay_silius_stock_events_1110 as Stock

J,C,H,N = Stock.J,Stock.C,Stock.H,Stock.N
W = J.W
SOURCE = H.ROOT/'tools/reference/jay_silius_stock_flight_1110.s'
PAGE = 218
FLIGHT = 0xb14e
SLOT = (0xd0,0xe0,0xf0)


def changed(a,b):
    return {i for i,(x,y) in enumerate(zip(a,b,strict=True)) if x!=y}


def compose_parent(resident):
    import deliver_sonic_rings_1110 as Sonic
    import deliver_dkjr_second_gap_1111 as Dk

    b031 = resident['b031_source']
    sonic,_,_,_ = Sonic.Build.proposal(b031)
    assert C.digest(sonic)==Sonic.PIN
    installed = H.ROM.read_bytes()
    installed_sha = C.digest(installed)
    if installed_sha == Dk.PIN:
        current = Dk.merge(b031,sonic)
    else:
        assert installed_sha==Sonic.PIN,(installed_sha,Sonic.PIN,Dk.PIN)
        current = sonic
    assert current==installed
    sonic_bytes, dk_bytes = changed(b031,sonic), changed(sonic,current)
    assert len(sonic_bytes)==2810 and len(dk_bytes) in (0,248)
    assert not (sonic_bytes & dk_bytes)
    jay = changed(b031,resident['raw'])
    assert len(jay)==3307 and not jay & (sonic_bytes | dk_bytes)
    with patch.object(Prior,'PAGE',PAGE):
        domains = Prior.current_domains(b031)
    assert PAGE not in {p for row in domains['weapons'].values() for p in row['actual_mmc5_outputs']}
    assert PAGE+1 in domains['weapons']['AvPhysicalBanks']['actual_mmc5_outputs']
    off = C.CHR+1024*PAGE
    assert current[off:off+1024]==b031[off:off+1024]==current[C.CHR+2048:C.CHR+3072]
    sonic_chr = sorted({(i-C.CHR)//1024 for i in sonic_bytes if i>=C.CHR})
    dk_chr = sorted({(i-C.CHR)//1024 for i in dk_bytes if i>=C.CHR})
    assert PAGE not in sonic_chr+dk_chr
    for symbol in ('AvPhysicalBanks','SmWeaponPhysicalBanks','SsPhysicalBanks','ChrPhysicalMap'):
        at = W.location(resident,symbol)
        n = 256 if symbol=='ChrPhysicalMap' else 17 if symbol!='SmWeaponPhysicalBanks' else 2
        assert current[at:at+n]==b031[at:at+n],symbol
    out = bytearray(current)
    for i in jay:
        out[i] = resident['raw'][i]
    return current,bytes(out),sonic_bytes | dk_bytes,dict(parent=installed_sha,sonic_edits=len(sonic_bytes),
        later_DK_edits=len(dk_bytes),Sonic_CHR=sonic_chr,DK_CHR=dk_chr,
        reader_domains=domains['prior_domains'],legacy_tables=domains['current_tables_exact'],
        physical_218_preimage=C.digest(current[off:off+1024]))


def code_for(linked,extra,stock):
    data = stock['images']['BINDINGS']
    assert 0xb000+len(data)==FLIGHT
    ram = linked['ram']
    aliases = dict(PublishPosition=extra['symbols']['PublishPosition'],ShotRecords=0xbfb0,
        QueryY=ram[2],QueryX=ram[3],QueryDirection=ram[2]+2,NearX=0xc0b5,
        CameraXHi=ram[0x30],CameraXLo=ram[0x31],CameraYHi=ram[0x32],CameraYLo=ram[0x33],
        JayHostTile=linked['symbols']['JayHostTile'])
    assert aliases['NearX'] not in set(ram.values())|set(Stock.EXTRA_FIELDS.values())
    definitions = ''.join(f'{key}=${v:04x}\n' for key,v in aliases.items())
    text = SOURCE.read_text()
    layout = {'PREFIX':(0xa000,96),'FLIGHT':(FLIGHT,512)}
    def assemble(n):
        return H.assemble(definitions+f'CopyPages={n//256}\nCopyTailBytes={n%256}\n'+text,layout)
    sizes = assemble(len(data))['used']
    count = len(data)+sizes['FLIGHT']
    assert 256<count<=928 and count%256
    result = assemble(count)
    assert result['used']==sizes
    payload = data+result['images']['FLIGHT']
    page = result['images']['PREFIX'].ljust(96,b'\xea')+payload
    return result,payload,page.ljust(1024,b'\xea')


def proposal(donor):
    resident,old_program,linked,runtime,old_stage,old_cookie,gate,extra,_,layout = Stock.resident(donor)
    current,base,foreign,authority = compose_parent(resident)
    stock,fields = Stock.bindings(linked)
    flight,payload,packet = code_for(linked,extra,stock)
    runtime = Stock.with_fire(resident,runtime,extra)
    publish = b'\x20'+J.u16(extra['symbols']['PublishPosition'])
    assert runtime.count(publish)==1
    runtime = runtime.replace(publish,b'\x20'+J.u16(flight['symbols']['StepAndPublish']))
    stage, decoder, sizes = J.boot_stage(runtime)
    boot = J.BOOT-0xd000
    assert stage[boot:boot+3]==bytes.fromhex('4c00d0')
    stage = stage[:boot]+bytes.fromhex('4c00a0')+stage[boot+3:]
    descriptor = bytes.fromhex('030101da004b014c01')
    cookie = bytes((0xa7,16,32,5))+C.sha256(stage+runtime+descriptor+packet).digest()[:12]
    cold_source = old_program['source'].split('.segment "PROTO66"',1)[0]
    for old,new in ((' ldx #6\nPushDescriptor:', ' ldx #8\nPushDescriptor:'),
                    ('SceneReturn:\n', 'SceneReturn:\n pla\n pla\n'),
                    (' .byte 2,0,1,$4b,1,$4c,1\n',' .byte 3,1,1,$da,0,$4b,1,$4c,1\n'),
                    (','.join(map(str,old_cookie)),','.join(map(str,cookie)))):
        assert cold_source.count(old)==1
        cold_source = cold_source.replace(old,new)
    cold = H.assemble(cold_source,{'COLD65':(0xa696,162)})
    hot_origin = int(layout['hot_entry'],16)
    hot_source = gate['source']
    assert hot_source.count(','.join(map(str,old_cookie)))==1
    hot = H.assemble(hot_source.replace(','.join(map(str,old_cookie)),','.join(map(str,cookie))),
                     {'HOT94':(hot_origin,124)})
    out = bytearray(base)
    envelopes = []

    def replace(at,old,new):
        assert len(old)==len(new) and base[at:at+len(old)]==old
        assert not set(range(at,at+len(old)))&foreign
        out[at:at+len(old)] = new
        envelopes.append([at,len(old)])

    old_cold = old_program['images']['COLD65']
    assert cold['used']['COLD65']==len(old_cold)+4==151
    replace(C.offset(65,0xa696),old_cold.ljust(162,b'\xea'),cold['images']['COLD65'].ljust(162,b'\xea'))
    replace(C.offset(65,0xaf00),b'\x4c'+J.u16(old_program['symbols']['JaySelect']),
            b'\x4c'+J.u16(cold['symbols']['JaySelect']))
    replace(C.offset(94,hot_origin),gate['images']['HOT94'],hot['images']['HOT94'])
    replace(C.CHR+331*1024,old_stage,stage)
    start = C.CHR+PAGE*1024
    replace(start,current[start:start+1024],packet)
    report = dict(**authority,carrier_edits=envelopes,resident_edits=len(changed(current,out)),
        stage=sizes,assembly=flight['used'],payload_bytes=len(payload),cookie=cookie.hex(),
        image=C.digest(out),payload_sha=C.digest(payload))
    return dict(resident,raw=bytes(out)),linked,fields,runtime,cold,stock,flight,payload,cookie,report


def slot(m,x):
    at = 0x80+x-0xd0
    return m.ram[2][at:at+16]


def natural(trial,fields,runtime,flight,payload,cookie):
    m = C.menu(trial,1,{'images':{}})
    path = []
    entries = Counter()
    seed = None
    for _ in range(650):
        active = tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
        if active and len(path)==60:
            break
        m.controller_pad = 64 if active and 4<=len(path)<20 else 0

        def observe(mem,cpu):
            nonlocal seed
            if mem.rawtags[1]!=3:
                return
            if cpu.pc==Stock.VECTOR:
                entries['stock_input'] += 1
                assert C.Common.headers(m)==(cookie,)*2
                assert bytes(m.ram[3][:len(runtime)])==runtime
                assert bytes(m.ram[3][0x1000:0x1000+len(payload)])==payload
                if seed is None:
                    seed = C.Vector.clone(m)
            if cpu.pc==flight['symbols']['StepStock']:
                entries['flight'] += 1

        C.Game.frame(m,observe)
        if active:
            assert N.get(m,'NumberofLives')==2 and not any(N.get(m,'JnShotKind',i) for i in range(6))
            x,y,xs,ys,flag = slot(m,0xf0)[0],slot(m,0xf0)[2],slot(m,0xf0)[6],slot(m,0xf0)[7],slot(m,0xf0)[9]
            path.append(dict(x=xs,y=ys,active=bool(flag),raw_x=x,raw_y=y))
    assert len(path)==60 and entries=={'stock_input':60,'flight':60},(entries,path)
    live = [(i,r['x'],r['y']) for i,r in enumerate(path) if r['active']]
    assert live[0][0]==4 and live[-1][0]<59
    assert [r[1] for r in live]==list(range(live[0][1],live[-1][1]+1,4)),live
    assert len({r[2] for r in live})==1
    assert not any(path[i]['active'] for i in range(live[-1][0]+1,len(path)))
    return seed,dict(entries=dict(entries),first=live[0],last=live[-1],steps=len(live),
                     retire_epoch=live[-1][0]+1,lives=N.get(m,'NumberofLives'))


def donor_pairs(donor,seed,linked,flight):
    fields = linked['ram']
    checked = Counter()
    host_query_pc = linked['symbols']['JayHostTile']
    values = ((64,1),(0xc0,3),(0,1))
    for (vx,flags),rel_x,sy in product(values,(-650,-96,-95,-12,-1,0,12,239,255,256,285,350,680),
            (0xa00,0xc00,0xd00,0xf00)):
        m = C.Vector.clone(seed)
        old = C.Donor.fork(donor)
        old.memory.ram[0x300:0x500] = bytes(512)
        old.memory.low_bank = 6
        camera = (0x800-rel_x*16)&0xffff
        for logical,value in ((0x30,camera>>8),(0x31,camera&255),(0x32,0),(0x33,0)):
            old.memory.ram[logical] = value
            m.ram[2][fields[logical]-0xc000] = value
        initial = bytes((8,0,sy>>8,sy&255,vx,0,0xe1,0xe2,0,flags,0,0,0,0,0,1))
        m.ram[2][0x80:0xb0] = bytes(48)
        m.ram[2][0xa0:0xb0] = initial
        old.memory.ram[0x3f0:0x400] = initial
        queries = []

        def host(c):
            if c.pc==host_query_pc:
                queries.append(tuple(c.memory[fields[2]+i] for i in range(3)))

        Stock.direct(N.NesMPU(memory=m),flight['symbols']['StepStock'],(0,0,0,0x30),host)
        tile_class = m.ram[2][0xf6]
        assert len(queries)==bool(vx)

        def original(c):
            if c.pc!=0xd002:
                return False
            assert queries and (c.memory.ram[2],c.memory.ram[3],c.x)==(*queries[0][:2],2)
            assert queries[0][2]==(4 if vx&128 else 6)
            assert tile_class in (0,1)
            c.a = tile_class if c.memory.ram[3]&1 else tile_class<<4
            c.FlagsNZ(c.a)
            c.pc = c.stPopWord()+1
            checked['real_host_tile_fed_to_donor_D002'] += 1
            checked[f'class_{tile_class}'] += 1
            return True

        Stock.direct(old,0xc49e,(0,0,0,0x30),original)
        assert old.memory.ram[0x3f0:0x400]==slot(m,0xf0),(
            rel_x,sy,vx,queries,tile_class,old.memory.ram[0x3f0:0x400].hex(),slot(m,0xf0).hex())
        checked['full_records'] += 1
    assert checked['class_0'] and checked['class_1']
    return dict(checked)


def main():
    donor = C.actual_donor()
    trial,linked,fields,runtime,cold,stock,flight,payload,cookie,report = proposal(donor)
    print('Jay stock flight image',report,flush=True)
    seed,actual = natural(trial,fields,runtime,flight,payload,cookie)
    print('Jay live stock flight',actual,flush=True)
    pairs = donor_pairs(donor,seed,linked,flight)
    print(json.dumps(dict(passed=True,proposal=report,actual=actual,donor_pairs=pairs,ROM_written=False,
                          Mesen=False,generated_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
