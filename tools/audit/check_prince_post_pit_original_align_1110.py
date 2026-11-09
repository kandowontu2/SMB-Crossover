"""Compare the host landing with the real donor's two original alignment calls."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import check_prince_post_pit_landing_writer_1110 as Writer


R, Route = Writer.R, Writer.Route
ROOT = R/'build/prince-post-pit-landing-writer-1110'
WRITER_SHA = 'b02298eaf32bc8763f39691972d958c877f7f7b4e2f961cca284b8594ca91fa3'
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as Original


def donor_case(snapshot, back_material):
    c = Original.machine()
    m = c.memory
    m.switch(5)
    state = bytearray.fromhex(snapshot['ram'])
    assert (int.from_bytes(state[0x60f:0x611],'little'),state[0x611],state[0x616],state[0x617],state[0x618])==(
        1579,95,18,105,3)
    # Represent native X1504..1599 in the same donor room as the retained
    # primary support cell. CE63 reads ordinary donor tiles from this fixture.
    origin = 1280
    state[0x60f:0x611] = (1579-origin).to_bytes(2,'little')
    state[0x6cd:0x6cf] = (0x300).to_bytes(2,'little')
    state[0x300:0x31e] = bytes(30)
    state[0x312],state[0x313] = back_material,20
    list.__setitem__(m,slice(0,2048),state)
    c.a,c.x,c.y,c.p = snapshot['registers'][:4]
    c.pc,c.sp = 0xd17a,0xfd
    c.stPushWord(0x5aff)
    aligns,queries,changes = [],[],[]

    def actor():
        return [m[0x60f]+256*m[0x610],m[0x611],m[0x616],m[0x617],m[0x618]]

    for _ in range(10000):
        pc = c.pc
        if pc==0x5b00:
            break
        before = actor()
        if pc==0xc8d4:
            aligns.append(dict(actor=before,index=m[0x4b1],Y=c.y,caller=(m[0x101+c.sp]+256*m[0x102+c.sp]+1)&65535))
        if pc==0xce68:
            queries.append(dict(index=c.y,material=c.a&31,actor=before,
                                caller=(m[0x101+c.sp]+256*m[0x102+c.sp]+1)&65535))
        assert m[pc]!=0,(hex(pc),actor())
        bank = m.bank
        c.step()
        after = actor()
        if before!=after:
            changes.append(dict(bank=bank,PC=pc,before=before,after=after))
    else:
        raise AssertionError('Original D17A did not return')
    assert c.sp==0xfd
    return dict(back_material=back_material,coordinate_origin=origin,aligns=aligns,queries=queries,changes=changes,end=actor())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    result = out/'donor-align.json'
    assert out==ROOT/'donor' and not result.exists()
    previous = ROOT/'writer.json'
    assert sha256(previous.read_bytes()).hexdigest()==WRITER_SHA
    q = Writer.Pair.Second.First.Pit.Current.read(previous)
    assert q['ROM_SHA256']==Route.PIN
    host_x = [c for c in q['writer']['changes'] if c['PC'][1:3]==[2,0xc427] and c['PC'][6][0]!=c['after'][0]]
    assert [(c['PC'][6][0],c['after'][0],c['PC'][6][-1]) for c in host_x]==[(1579,1588,19),(1588,1540,19)]
    x = q['retained_D17A_inputs']['190']
    donor,control = donor_case(x,0),donor_case(x,1)
    for r in (donor,control):
        print(r['back_material'],'aligns',r['aligns'],'queries',r['queries'][:4],'end',r['end'],flush=True)
    assert [(r['caller'],r['index'],r['Y']) for r in donor['aligns']]==[(0xd637,19,20),(0xd6c3,19,4)]
    assert [(r['caller'],r['index'],r['material']) for r in donor['queries'][:3]]==[
        (0xd502,19,20),(0xd66a,18,0),(0xd67a,18,0)]
    assert (donor['end'][0],donor['end'][2])==(292,45)
    assert [(r['caller'],r['index'],r['Y']) for r in control['aligns']]==[(0xd637,19,20)]
    assert (control['end'][0],control['end'][2])==(308,47)
    refs = (Path(__file__),Path(Writer.__file__),previous,Route.ROM,Path(Original.__file__))
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,donor_SHA256=Original.SHA,
                 host_alignments=host_x,donor=donor,solid_back_control=control,
                 source_x=dict(input=1579,first_alignment_both=1588,host_second=1540,donor_translated_second=1572),
                 scope='Real donor D17A/CE63/C8D4/AE78 against an explicit original room material fixture: '
                       'support index19=wall20 and back probe18=empty, matching the host materials. '
                       'The donor keeps the same room index19 on both placements. The host resolves the second '
                       'placement relative to the just-queried native column. This is a measured extra 32px '
                       'horizontal adapter relocation, not a proposal to remove the original action45 or contact.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    out.mkdir(exist_ok=True)
    result.write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
