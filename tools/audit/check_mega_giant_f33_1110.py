"""Rebase Giant selection and a typed late draw onto the public f33 image."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import check_mega_giant_selection_1110 as S
from check_mini_funded_actor_1108_v3 import install


C, G, P, Rr, R, M = S.C,S.G,S.P,S.Rr,S.R,S.M
PIN = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
STAGE = R/'build/mega-giant-selection-1110/proof-v2.json'
GETSU = R/'build/getsu-loaded-stage-v2-1110/proof.json'
GETSU_ATLAS = R/'build/getsu-atlas-ownership-1110/atlas-page.json'
SPARSE = R/'build/native-sparse-world-draw-1110/combo.json'
SOURCE = R/'tools/reference/mega_giant_mario_late_draw_1110.s'
SPANS = (
    ('CHECK',4,0xbff7,'eaeaeaeaeaeaea'),
    ('MAP',4,0xbf85,'eaffffffffff'),
    ('MAA_MUX',68,0xdb09,'ff'*23),
    ('TAIL_FAST',90,0xb15c,None),
    ('TAIL_FINISH',90,0xb86b,None),
    ('RETURN',127,0xe710,'eaeaeaeaeaea'),
)


def read(path):
    return json.loads(path.read_text())


def overlap(rows, other):
    def extents(patch):
        start = patch['file_offset']
        return start,start+len(bytes.fromhex(patch['old_hex']))
    result = set()
    for a in rows:
        a0,a1 = extents(a)
        for b in other:
            b0,b1 = extents(b)
            if a0<b1 and b0<a1:
                result.add((max(a0,b0),min(a1,b1)))
    return sorted(result)


def assemble(out, b, labels, allocated):
    definitions = ''.join(f'{n}=${C.address(b,n):04x}\n' for n in ('CurrentBankC','MarioVariant','M0'))
    definitions += f'GiantDrawOwner=${labels["GiantDrawOwner"]:04x}\n'
    memory,segments,sizes = [],[],[]
    for i,(name,bank,pc,old) in enumerate(SPANS):
        if old is None:
            old = allocated[bank,pc]['old_hex']
        n = len(bytes.fromhex(old))
        sizes.append(n)
        memory.append(f'M{i}:start=${pc:04x},size=${n:x},file=%O,fill=yes,fillval=$ea;')
        segments.append(f'{name}:load=M{i},type=ro;')
    with TemporaryDirectory(dir=out,prefix='late-') as tmp:
        asm,obj,cfg,binary = (Path(tmp)/f'late.{x}' for x in ('s','o','cfg','bin'))
        asm.write_text(definitions+SOURCE.read_text())
        cfg.write_text('MEMORY{'+''.join(memory)+'} SEGMENTS{'+''.join(segments)+'}')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',asm,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        code = binary.read_bytes()
    changes=[]
    pos=0
    for (_,bank,pc,old),n in zip(SPANS,sizes,strict=True):
        changes.append((bank,pc,old or allocated[bank,pc]['old_hex'],code[pos:pos+n]))
        pos += n
    assert pos==len(code)
    return changes


def compose(out, raw):
    assert G.digest(raw)==PIN
    stage, resident, sparse, getsu = map(read,(STAGE,G.RESIDENT,SPARSE,GETSU))
    old = stage['patches']+resident['patches']
    assert stage['passed'] and resident['passed'] and getsu['passed'] and sparse['passed']
    assert sparse['expected_memory_only_SHA256']==PIN
    current = [q for rows in sparse['groups'].values() for q in rows]
    assert overlap(old,current)==[(Rr.at(4,0xa24b),Rr.at(4,0xa261))]
    assert overlap(old,getsu['patch_PRG'])==[(Rr.at(66,0xacc3),Rr.at(66,0xaccf))]
    atlas_page = read(GETSU_ATLAS)['page']
    assert atlas_page==990 and atlas_page not in (*G.ART,G.ATLAS,G.CODE)
    assert not set(range(956,969))&set((*G.ART,G.ATLAS,G.CODE))

    b = C.bundle(raw)
    resident_image = C.bundle(install(raw,resident['patches']))
    donor_bytes = C.DONOR.read_bytes()
    assert G.digest(donor_bytes)==C.DONOR_PIN
    donor,art,records,atlas_cookie = G.atlas(donor_bytes)
    render,render_labels = G.assemble(out,resident_image,atlas_cookie)
    render = render.ljust(1024,b'\xff')
    meta = (atlas_cookie+b''.join(records)).ljust(1024,b'\xff')
    cookie = bytes((0xa7,0,9,2))+hashlib.sha256(meta+render+S.SOURCE.read_bytes()).digest()[:8]+bytes((2,1,1,0xd0))
    old_art,_ = G.media(resident_image,art,meta,render)
    original_code,draw,labels = S.assemble(out,old_art,cookie)
    render = render[:0x200]+draw+render[0x280:]
    art_image,storage = G.media(resident_image,art,meta,render)
    assert stage['symbols']==labels and stage['render_symbols']==render_labels
    assert stage['physical_carriers']==storage['physical_candidate_pages']

    # Retain each frozen stage preimage except the old generic late-tail
    # ingress and the two workers it used. The assembled CHR draw row is
    # already present in art_image from the authentic donor/compiler inputs.
    allocated = {(q['physical_PRG'],q['PC']):q for q in stage['patches'] if 'PC' in q}
    skip = {(4,0xa24b),(90,0xb15c),(90,0xb86b)}
    prior = [q for q in stage['patches'] if 'PC' in q and (q['physical_PRG'],q['PC']) not in skip]
    cursor = 0
    for bank,pc,size in S.AREAS:
        assert original_code[cursor:cursor+size].hex()==allocated[bank,pc]['new_hex'],(bank,pc)
        cursor += size
    assert cursor==len(original_code)

    changes = assemble(out,b,labels,allocated)
    changes += [(126,0x85ca,'4c0bdc',bytes.fromhex('4c09db')),
                (126,0x85cd,'a9f860',bytes.fromhex('4cf7bf'))]
    tail = []
    for bank,pc,old_code,new in changes:
        at = Rr.at(bank,pc)
        assert len(bytes.fromhex(old_code))==len(new)
        tail.append(dict(physical_PRG=bank,PC=pc,file_offset=at,old_hex=old_code,new_hex=new.hex()))
    patches = resident['patches']+prior+tail
    assert not overlap(patches,current)
    assert overlap(patches,getsu['patch_PRG'])==[(Rr.at(66,0xacc3),Rr.at(66,0xaccf))]
    image = C.bundle(install(install(art_image['raw'],prior),tail))
    assert image['raw'][:16]==raw[:16]
    assert all(image['raw'][p['file_offset']:p['file_offset']+len(bytes.fromhex(p['new_hex']))].hex()==p['new_hex']
               for p in current)
    return b,image,patches,storage,labels,render_labels,cookie,meta,render,donor,records


def transport_vectors(seed):
    cuts=((132,0xbff7),(132,0xbf85),(254,0x85c4),(254,0x85c7),(254,0x85ca),
          (196,0xdb17),(196,0xdb1a),(196,0xdb1d),
          (218,0xb15c),(218,0xb87b),(218,0xb87e),(255,0xe710),(255,0xe713),
          (255,0xeb3e),(255,0xeb41),(132,0xbffb))
    pending={0x85c7:(2,0x7da1),0xdb1a:(1,0x145),0xb87e:(2,0x7da1),0xe713:(1,0x145),0xeb3e:(1,0x145)}

    def vector(cpu,kind):
        if kind!='lag_nmi' or cpu.pc not in pending:
            return C.vector(cpu,kind)
        m=cpu.memory
        checkpoint=lambda: (cpu.pc,cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p&0xef,bytes(m[0x15a:0x17b]))
        entry=checkpoint()
        tags=tuple(m.rawtags)
        win,shadow=pending[cpu.pc]
        published=tags[:win]+(m[shadow],)+tags[win+1:]
        assert tags!=published and (cpu.pc-0x8000)//8192!=win
        assert M.get(m,'NmiDisable')==255
        skipped=M.get(m,'NmiSkipped')
        cpu.nmi()
        handler=cpu.pc
        for _ in range(100000):
            if (cpu.pc,cpu.sp)==entry[:2]:
                break
            assert m[cpu.pc]
            cpu.step()
        else:
            raise AssertionError(('Giant FF return bound',entry[:2]))
        assert checkpoint()==entry and tuple(m.rawtags) in (tags,published),(entry,tuple(m.rawtags))
        assert M.get(m,'NmiSkipped')==(skipped+1)&255
        return dict(kind=kind,pc=entry[0],handler=handler,SP=entry[1],completed_pending_mapper=tuple(m.rawtags)==published)

    def draw(cut=None,kind=None):
        m=M.fork(seed)
        M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,NmiDisable=255)
        hits=[]

        def visit(cpu):
            if cut==(C.tag(m,cpu.pc),cpu.pc) and not hits:
                hits.append(vector(cpu,kind))

        cpu=G.run_cpu(m,C.address(m.bundle,'GameLoop'),p=0x31,observe=visit)
        assert len(hits)==int(cut is not None),(cut,kind,hits)
        M.consume(m)
        return (cpu.a,cpu.x,cpu.y,cpu.p&0xef,bytes(m[0x200:0x300]),bytes(m[0x73:0xd0]),
                tuple(m.rawtags),M.get(m,'CurrentBankC'),M.get(m,'CurrentBank'),tuple(m.chr_latches)),hits

    base,_=draw()
    rows=[]
    for cut in cuts:
        for kind in ('irq','lag_nmi'):
            after,hits=draw(cut,kind)
            assert base==after,(cut,kind,base[:4],after[:4])
            rows.extend(hits)
    return rows


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output
    out.mkdir(exist_ok=True)
    raw = C.HOST.read_bytes()
    old,new,patches,storage,labels,render_labels,cookie,meta,render,donor,records = compose(out,raw)
    print('Memory-only image',G.digest(new['raw']),flush=True)
    seed,selection = S.select_and_start(new,labels,cookie,meta,render)
    vectors = transport_vectors(seed)
    print('Real mapper publication vectors',len(vectors),flush=True)
    first = S.walk(seed,labels,render_labels,donor,records)
    print('Actual menu Start and first terrain/draw route',first['updates'],first['world_x'],flush=True)
    foreign = S.ordinary(old,new,labels,read(G.RESIDENT)['storage']['symbols'])
    assert max(abs(cycle) for q in foreign for cycle in q['cycles'])<=16,foreign
    print('Nine stock alternate deltas',foreign,flush=True)
    retired = S.retire(seed,labels,cookie)
    rog = S.campaign((old,new),dict(GiantRogueMux=labels['GiantAudioMux']))
    report = dict(passed=True,parent_SHA256=PIN,ROM_written=False,provisional_CHR=True,
                  expected_memory_only_SHA256=G.digest(new['raw']),patches=patches,
                  physical_carriers=storage['physical_candidate_pages'],symbols=labels,render_symbols=render_labels,
                  selection=selection,first_route=first,retirement=retired,foreign=foreign,Rogue_ordered_NMI=rog,
                  real_transport_vectors=vectors,
                  Getsu_menu_intersection=[Rr.at(66,0xacc3),Rr.at(66,0xaccf)],
                  bindings={str(p):C.sha(p) for p in (Path(__file__),SOURCE,C.HOST,C.DONOR,STAGE,G.RESIDENT,S.SOURCE,
                                                         G.SOURCE,S.RENDER,GETSU,GETSU_ATLAS,SPARSE)})
    path=out/'proof-v2.json'
    assert not path.exists()
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('Public f33 Giant rebase and foreign stock draws PASS',flush=True)


if __name__=='__main__':
    main()
