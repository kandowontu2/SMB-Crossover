"""Verify the Getsu lag repair against the delivered Mega Giant successor."""

import argparse
import json
from pathlib import Path

import check_getsu_empty_special_1110 as Getsu
import check_mega_giant_crush_side_1110 as GiantSide
import prepare_getsu_giant_native_1110 as Native

R, SHA = Getsu.R,Getsu.SHA
Public, Rebase = Getsu.Public,Native.Rebase
BASE = R/'build/giant-impact-side-native-1110/candidate.nes'
PIN = '12f3e4163631887e134cbce7f1caa015bfe4b3786c2ee3d71217c80c1f677a6c'
GETSU = R/'build/getsu-empty-special-1110/proof.json'
GETSU_PIN = 'bc58d8165c93cec7350616b73541f7758833a2dce06f0a3ffaf6cc5039173c0a'
GIANT = R/'build/giant-impact-side-compose-1110/proof.json'
SIDE = R/'build/mega-giant-crush-side-1110/proof.json'
DELIVERY = R/'build/giant-impact-delivery-1110/verified-delivery.json'


def compose(output):
    raw = Getsu.CURRENT.read_bytes()
    parent = BASE.read_bytes()
    giant, side, getsu, delivery = map(Public.read,(GIANT,SIDE,GETSU,DELIVERY))
    assert all(q['passed'] for q in (giant,side,getsu))
    assert SHA(raw)==giant['parent_SHA256']==getsu['parent_SHA256']==Getsu.CURRENT_PIN
    assert SHA(parent)==giant['expected_memory_only_SHA256']==side['expected_memory_only_SHA256']==PIN
    assert delivery['installed'] and delivery['Downloads_launch_verified'] and delivery['ROM_SHA256']==PIN
    assert delivery['proof_SHA256']==SHA(GIANT.read_bytes())
    for q in (giant,side,getsu):
        Public.check_paths(q['bindings'])
    prior_giant = GiantSide.source_image()
    assert Public.apply(prior_giant,side['patches'])==Public.apply(raw,giant['patches'])==parent

    originals, rows, _ = Getsu.build(output)
    assert rows==getsu['patches'] and SHA(originals[-1]['raw'])==getsu['expected_memory_only_SHA256']==GETSU_PIN
    rebased = [Getsu.W.bundle(Public.apply(q['raw'],giant['patches'])) for q in originals]
    final = rebased[-1]['raw']
    assert Public.apply(parent,rows)==Public.apply(raw,giant['patches']+rows)==final
    assert len(rows)==60 and len(giant['patches'])==12
    assert all(final[q['file_offset']:q['file_offset']+len(bytes.fromhex(q['new_hex']))].hex()==q['new_hex']
               for q in giant['patches'])
    final_minus_side = Public.apply(prior_giant,rows)
    assert Public.apply(final_minus_side,side['patches'])==final
    return parent,rebased,rows,getsu,final_minus_side,side


def verify(output):
    parent, rebased, rows, getsu, minus_side, side = compose(output)
    before, with_sword, final = rebased
    print('Exact memory-only successor',SHA(final['raw']),flush=True)

    menus, vector_seeds = Rebase.menu(Getsu.W.bundle(parent),final)
    menu_vectors = Rebase.menu_interrupts(vector_seeds)
    print('Complete menu and vectors',menus['existing_profiles'],menus['combined_profiles'],menu_vectors,flush=True)
    seeds, cold = Getsu.cold(with_sword,final)
    giant = Public.read(Rebase.GIANT)
    # The historical cold comparison expected both the original $A7E4 and
    # relocated $ABC7 reader on two different historical layouts. The current
    # cold oracle above compares two current layouts, and adds real vectors.
    # Feed its measured transactions into the unchanged native transitions.
    empty = Rebase.Getsu.Empty
    assert empty is Getsu.EMPTY
    incumbent, transactions = empty.parent,empty.transactions
    def current_transactions(images):
        assert tuple(b['raw'] for b in images)==(with_sword['raw'],final['raw'])
        return seeds,cold
    try:
        empty.parent = lambda: (with_sword['raw'],None)
        empty.transactions = current_transactions
        ownership = Rebase.cold((Getsu.W.bundle(parent),before,final),getsu,giant)
    finally:
        empty.parent,empty.transactions = incumbent,transactions
    print('Real title, both confirm inputs, and Giant/Getsu/Mini ownership passed',flush=True)
    leaves = Getsu.leaf(with_sword,final,seeds)
    print('All Getsu/current foreign services and cold vectors',leaves['cases'],cold['vector_cuts'],flush=True)

    side_checks = GiantSide.native_leaf(minus_side,final['raw'],side['labels'])
    canonical = GiantSide.audio(minus_side,final['raw'],side['labels'])
    print('Final adjacent Giant side and Rogue source byte view',side_checks,canonical,flush=True)
    active = Getsu.gameplay(before,final)
    print('Genuine active Getsu FF, IRQ and first sword hit',active,flush=True)
    inputs = (Path(__file__).resolve(),BASE,DELIVERY,GIANT,SIDE,GETSU,Rebase.GIANT,
              Path(Getsu.__file__),Path(GiantSide.__file__),Path(Rebase.__file__))
    return dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=SHA(final['raw']),
                renderer_installed=True,native_HUD=True,cookie=getsu['cookie'],kernel_SHA256=getsu['kernel_SHA256'],
                public_vector_rows=getsu['public_vector_rows'],patches=rows,frontend=menus,frontend_vectors=menu_vectors,
                ownership=ownership,cold=cold,direct=leaves,active=active,Giant_side=side_checks,
                canonical_Rogue=canonical,scope='Exactly the 60 qualified Getsu rows over delivered Mega Giant. '
                'All 12 Giant PRG spans remain byte-exact. Native hardware replay is separate.',
                bindings={p.relative_to(R).as_posix():SHA(p.read_bytes()) for p in inputs})


def stage_packet(output, rom, proof, mode):
    # Reuse the immutable genuine controller and canonical symbol sidecars.
    base, pin = Rebase.BASE, Rebase.PIN
    try:
        Rebase.BASE, Rebase.PIN = BASE,PIN
        Native.stage_packet(output,rom,proof,mode)
    finally:
        Rebase.BASE, Rebase.PIN = base,pin
    ready = output/'ready.json'
    q = Public.read(ready)
    q['bindings'][str(Path(__file__).resolve())] = SHA(Path(__file__).read_bytes())
    ready.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path)
    cli.add_argument('--proof',type=Path)
    cli.add_argument('--mode',choices=('idle','route'))
    args=cli.parse_args()
    output=args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build'
    if args.rom is not None:
        assert args.proof is not None and args.mode is not None
        stage_packet(output,args.rom.resolve(),args.proof.resolve(),args.mode)
        return
    assert args.proof is None and args.mode is None
    output.mkdir(exist_ok=True)
    assert not (output/'proof.json').exists()
    q=verify(output)
    with (output/'proof.json').open('x',encoding='utf-8') as f:
        json.dump(q,f,indent=2)
        f.write('\n')


if __name__=='__main__':
    main()
