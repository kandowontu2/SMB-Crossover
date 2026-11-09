"""Layer the authenticated Mini powered-injury repair over six engine groups."""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import shutil

import check_mini_native_injury_status_1110 as Status
import prepare_mini_helper_injury_native_1110_v4 as Six
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import digest, load
from deliver_mini_nightly_root_1103_v30 import proof as native_proof
from prepare_mini_lane_audio_native_1110 import verify_parent, verify_payload
from prepare_selected_native_packet_v1 import prepare, sha


R,H = Six.R,Six.H
L = H.L
Five,Four,Prior = Six.Five,Six.Five.Four,Six.Five.Four.Prior
STATUS = R/'build/mini-native-injury-status-fix-1110/proof.json'
STATUS_SHA256 = '640f25d54e13bae12bf7cdaab3e53fb8ecac2491ad6a5f202d48144c2efb9161'
KERNEL = STATUS.with_name('kernel.bin')
SIX_CANDIDATE = R/'build/mini-helper-injury-parser-native-1110'
STATUS_ROLE = 'mini_powered_injury_status'
GROUPS = (*Six.GROUPS,STATUS_ROLE)
STATUS_RANGES = [(pc-0xa000,pc-0xa000+n) for pc,n in ((Status.ENTRY,3),(Status.LEAF,4))]
COOKIE = slice(L.COOKIE+3,L.COOKIE+16)


def authentic_payload(image):
    assert image[L.COOKIE:L.COOKIE+3]==bytes((167,41,1))
    assert image[COOKIE]==H.A.digest(image[L.CODE:L.CODE+7168])


def status_on(image,status_rows):
    """Apply the same source bytes and authenticate the resulting variant."""
    authentic_payload(image)
    revised = bytearray(install(image,status_rows[:2]))
    revised[COOKIE] = H.A.digest(revised[L.CODE:L.CODE+7168])
    result = bytes(revised)
    authentic_payload(result)
    return result


def components():
    published,strict,six,_,_,bca,proofs,groups = Six.components()
    assert sha(STATUS)==STATUS_SHA256 and digest(bca)==Status.PIN and bca==Status.ROM.read_bytes()
    isolated,status,parts = verify_parent(bca,STATUS)
    assert digest(isolated)==status['expected_memory_only_SHA256']
    assert [row[:2] for row in parts]==[(L.CODE+lo,L.CODE+hi) for lo,hi in STATUS_RANGES]+[
        (COOKIE.start,COOKIE.stop)]
    for source,h in status['source_bindings'].items():
        assert sha(R/source)==h,source
    assert status['vectors']['full_force_resumes']>0
    assert all(row['old']['first_source_tier']==41 and row['new']['first_source_tier']==0
               for row in status['lifecycle'])
    parent_rows = [row for role in Six.GROUPS for row in groups[role]]
    overlaps = []
    for role,rows in groups.items():
        for row in rows:
            start = row['file_offset']
            end = start+len(bytes.fromhex(row['new_hex']))
            overlaps.extend((role,lo,hi) for lo,hi,_,_ in parts if start<hi and lo<end)
    assert overlaps==[('strict_offscreen',COOKIE.start,COOKIE.stop)]
    assert status_on(bca,status['patches'])==isolated
    final = install(six,status['patches'])
    assert six==install(published,parent_rows) and final==status_on(six,status['patches'])
    verify_payload(final,KERNEL)
    old_labels = Prior.Strict.KERNEL.with_suffix('.lbl').read_text().splitlines()
    assert [line for line in KERNEL.with_suffix('.lbl').read_text().splitlines()
            if not line.endswith(' .MiniHostInjury')]==old_labels
    proofs[STATUS_ROLE],groups[STATUS_ROLE] = status,status['patches']
    return published,strict,six,final,proofs,groups


def final_minus(published,six,groups):
    images = {STATUS_ROLE:six}
    for removed in Six.GROUPS:
        rows = [row for role in Six.GROUPS if role!=removed for row in groups[role]]
        images[removed] = status_on(install(published,rows),groups[STATUS_ROLE])
    strict_out = images['strict_offscreen']
    assert strict_out[COOKIE]!=six[COOKIE]
    assert strict_out[COOKIE]!=images['injury_admission'][COOKIE]
    return images


@contextmanager
def status_dispatch_kernel():
    edge = Prior.Dispatch.Edge
    previous = edge.KERNEL,edge.KERNEL_PIN
    edge.KERNEL,edge.KERNEL_PIN = KERNEL,sha(KERNEL)
    try:
        yield
    finally:
        edge.KERNEL,edge.KERNEL_PIN = previous


def json_value(data):
    return json.loads(json.dumps(data))


def qualify(published,six,final,proofs,groups):
    images = final_minus(published,six,groups)
    checked = dict(final_minus_SHA256={role:digest(image) for role,image in images.items()})
    checked['strict_offscreen'] = Prior.NormalIRQ.qualify(images['strict_offscreen'],final,proofs['strict_offscreen'])
    before = images['injury_admission']
    foreground = Prior.Injury.foreground(before,final)
    assert json_value(foreground)==proofs['injury_admission']['foreground']
    lifecycle = Prior.InjuryIRQ.lifecycle(before,final)
    expected = load(Prior.INJURY_IRQ)['native_injury_sequence']
    for phase in expected.values():
        assert phase['native_status_after_force_injury']==41
        phase['native_status_after_force_injury'] = 0
    assert lifecycle==expected
    checked['injury_admission'] = dict(foreground=foreground,native_injury_sequence=lifecycle,
                                      vectors=Prior.InjuryIRQ.vectors(before,final))
    print('Status-authenticated offscreen and post-injury final-minus checks passed.',flush=True)

    with status_dispatch_kernel():
        before,receipt = images['ordinary_enemy_dispatch'],proofs['ordinary_enemy_dispatch']
        finite = Prior.Dispatch.finite(before,final)
        assert finite==receipt['all_8bit_dispatch']
        checked['ordinary_enemy_dispatch'] = dict(finite=finite,whole_GameLoop=Prior.Dispatch.whole(before,final),
                                                    vectors=Prior.Dispatch.vectors(before,final))
        before,receipt = images[Four.PAIR_ROLE],proofs[Four.PAIR_ROLE]
        assert Four.Pair.census(before)==receipt['source_ingress']
        assert Four.pair_readers(before)==load(Four.PAIR_READERS)['all_absolute_indexed_and_indirect_literal_matches']
        direct = Four.Pair.direct(before,final)
        assert direct==receipt['actual_caller_cases']
        checked[Four.PAIR_ROLE] = dict(actual_caller_cases=direct,whole_GameLoop=Four.Pair.whole(before,final),
                                      vectors=Four.PairIRQ.vectors(before,final,receipt['labels']))
        before,receipt = images[Six.PARSER_ROLE],proofs[Six.PARSER_ROLE]
        assert Six.Parser.ingress(before)==receipt['source_ingress']
        tails = Six.Parser.H.check_tails(*[Six.Parser.P.bundle(image) for image in (before,final)])
        assert json_value(tails)==receipt['column_tails']
        checked[Six.PARSER_ROLE] = dict(column_tails=tails,whole=Six.Parser.whole(before,final),
                                       vectors=Six.ParserIRQ.vectors(before,final,receipt['labels']))
    before,receipt = images[Five.COLUMN_ROLE],proofs[Five.COLUMN_ROLE]
    foreground = Five.Column.foreground(before,final)
    assert json_value(foreground)==receipt['foreground']
    checked[Five.COLUMN_ROLE] = dict(foreground=foreground,vectors=Five.Column.vectors(before,final))
    print('Status-authenticated ordinary actors, pairs, terrain and parser final-minus checks passed.',flush=True)

    before = images[STATUS_ROLE]
    cold,masks = H.A.exact_cold(before,final,STATUS_RANGES)
    foreground = Status.foreground(before,final,masks)
    assert json_value(foreground)==proofs[STATUS_ROLE]['foreground']
    lifecycles = []
    for tier in (1,2):
        old,new = (Status.lifecycle(raw,tier,status) for raw,status in ((before,41),(final,0)))
        assert old['injury_frames']==new['injury_frames'] and old['lives']==new['lives']
        assert new['injury_frames'][-1][2]==7 and new['first_source_tier']==0
        lifecycles.append(dict(previous_tier=tier,old=old,new=new))
    assert json_value(lifecycles)==proofs[STATUS_ROLE]['lifecycle']
    checked[STATUS_ROLE] = dict(cold=cold,foreground=foreground,lifecycle=lifecycles,
                                vectors=Status.vectors(final))
    combined_ranges = proofs['strict_offscreen']['exact_changed_code']+STATUS_RANGES
    checked['cold_Mini'],_ = H.A.exact_cold(published,final,combined_ranges)
    assert set(checked['final_minus_SHA256'])==set(GROUPS)
    print('Exact powered injury native status and source resumption checks passed.',flush=True)
    return checked


def route_controller(strict,final):
    text,ready,refs = Prior.route_controller(strict,final)
    old,new = sha(Prior.Strict.KERNEL),sha(KERNEL)
    assert text.count(old)==1
    hooks = re.findall(r'\["pc"\]=(\d+),\["physical"\]=(\d+),\["memory"\]="nesWorkRam",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert len(hooks)==5
    for pc,physical,data in hooks:
        at = L.CODE+int(pc)-0xa000
        expected = bytes(map(int,data.split(',')))
        assert int(physical)==int(pc)-0x4000
        assert final[at:at+len(expected)]==expected,pc
    return text.replace(old,new),ready,refs


def stage(output,six,final,groups,checks,packet):
    text,ready,refs = packet
    pin,base = digest(final),digest(six)
    meta_path = SIX_CANDIDATE/'candidate.json'
    meta = load(meta_path)
    six_proof = SIX_CANDIDATE/'proof.json'
    assert meta['candidate_SHA256']==base and meta['composed_proof_SHA256']==sha(six_proof)
    refs.update((Path(__file__),Path(Six.__file__),Path(Five.__file__),Path(Four.__file__),Path(Prior.__file__),
                 Path(Status.__file__),STATUS,KERNEL,KERNEL.with_suffix('.lbl'),KERNEL.with_suffix('.s'),
                 meta_path,six_proof,SIX_CANDIDATE/'candidate.nes',
                 SIX_CANDIDATE/'mini/ready.json',SIX_CANDIDATE/'mini/capture/binding.json',
                 SIX_CANDIDATE/'mini/capture/result.json'))
    output.mkdir()
    rom = output/'candidate.nes'
    rom.write_bytes(final)
    assert sha(rom)==pin
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(H.BASE.with_suffix(suffix),rom.with_suffix(suffix))
        assert sha(rom.with_suffix(suffix))==sha(H.BASE.with_suffix(suffix))
    receipt = output/'proof.json'
    report = dict(passed=True,ROM_written=True,native_pending=True,parent_SHA256=H.PIN,
                  immediate_six_group_SHA256=base,candidate_SHA256=pin,kernel_SHA256=sha(KERNEL),
                  groups=groups,apply_order=GROUPS,shared_cookie_slice=[COOKIE.start,COOKIE.stop],
                  birth_relative_left=[256,263],
                  helpers=[dict(stage='1-1',left=left,center=left+16,initial_top=192,width=32) for left in H.LEFTS],
                  status_fix_scope='Authentic Mini service5 returns native small status, with native injury and lift motion preserved.',
                  bindings={str(path.resolve()):sha(path) for path in sorted(refs)},**checks)
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    manifest = rom.with_suffix('.json')
    meta.update(parent_SHA256=base,candidate_SHA256=pin,kernel_SHA256=sha(KERNEL),
                actual_MiniScene=checks['cold_Mini'],composed_proof_SHA256=sha(receipt),
                verification='Private seven-group Mini powered injury replay pending')
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    prepare(output/'mini',rom,text,refs|{receipt,manifest},expected=pin,timeout=ready['timeout'],
            scope=ready['scope'],allow_interactive=ready['allow_interactive'])
    print(json.dumps(dict(passed=True,ROM_SHA256=pin,qualified_groups=GROUPS)),flush=True)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Check layered preimages and exact native hooks without writing.')
    mode.add_argument('--qualify',action='store_true',help='Run all final-minus proofs in memory.')
    mode.add_argument('--emit',action='store_true',help='After native six passes, stage one seven-group replay.')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build' and not output.exists()
    published,strict,six,final,proofs,groups = components()
    packet = route_controller(strict,final)
    baselines = final_minus(published,six,groups)
    print(json.dumps(dict(parent_SHA256=H.PIN,immediate_six_group_SHA256=digest(six),
                          memory_SHA256=digest(final),groups=GROUPS,
                          without_strict_authenticated_cookie=baselines['strict_offscreen'][COOKIE].hex())),flush=True)
    if args.census:
        return
    if args.emit:
        assert (SIX_CANDIDATE/'candidate.nes').read_bytes()==six
        result = native_proof(SIX_CANDIDATE/'mini',digest(six))
        assert result['full_stage'] and result['last']['lives']==2
    checks = qualify(published,six,final,proofs,groups)
    if args.emit:
        stage(output,six,final,groups,checks,packet)


if __name__=='__main__':
    main()
