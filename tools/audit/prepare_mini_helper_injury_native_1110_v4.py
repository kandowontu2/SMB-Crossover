"""Compose the six verified Mini and shared engine groups from d998."""

import argparse
import json
from pathlib import Path

import check_native_parser_triple_shadow_1110 as Parser
import check_native_parser_triple_shadow_irq_1110 as ParserIRQ
import prepare_mini_helper_injury_native_1110_v3 as Five
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import verify_interrupts, verify_parent
from prepare_selected_native_packet_v1 import sha


R,H = Five.R,Five.H
PARSER = R/'build/native-parser-triple-shadow-1110/proof.json'
PARSER_IRQ = PARSER.with_name('irq-v2.json')
PARSER_SHA256 = '7ad0ec35df6f204bd0254145a580f6c9af7aebdfce2fa3212d99378793eb00a3'
PARSER_IRQ_SHA256 = '55fbf9ed73d4c979cdfbd5880cc5680aaf3b0604f63440682b28ef5b935dafbf'
PARSER_ROLE = 'parser_triple_shadow'
GROUPS = (*Five.GROUPS,PARSER_ROLE)


def components():
    assert sha(PARSER)==PARSER_SHA256 and sha(PARSER_IRQ)==PARSER_IRQ_SHA256
    published,strict,before_parser,before_pair,before_column,proofs,groups = Five.components()
    isolated,proof,parts = verify_parent(published,PARSER)
    verify_interrupts(PARSER,PARSER_IRQ,proof)
    assert digest(isolated)==proof['expected_memory_only_SHA256']
    assert [row[:2] for row in parts]==[(H.offset(bank,pc),H.offset(bank,pc)+n) for bank,pc,n,_ in Parser.SPANS]
    receipt = load(PARSER_IRQ)
    assert receipt['cuts']['normal']==74 and len(receipt['paired_parser_resumes'])==78
    assert receipt['backup_written_before_next_actual_read']
    for lo,hi,_,_ in parts:
        assert all(row['file_offset']+len(bytes.fromhex(row['new_hex']))<=lo or row['file_offset']>=hi
                   for rows in groups.values() for row in rows)
    proofs[PARSER_ROLE],groups[PARSER_ROLE] = proof,proof['patches']
    final = install(before_parser,proof['patches'])
    assert final==install(published,[row for role in GROUPS for row in groups[role]])
    before_pair = install(before_pair,proof['patches'])
    before_column = install(before_column,proof['patches'])
    pair = proofs[Five.Four.PAIR_ROLE]
    assert Five.Four.Pair.census(before_pair)==pair['source_ingress']
    assert Five.Four.pair_readers(before_pair)==load(Five.Four.PAIR_READERS)['all_absolute_indexed_and_indirect_literal_matches']
    assert Parser.ingress(before_parser)==proof['source_ingress']
    return published,strict,final,before_pair,before_column,before_parser,proofs,groups


def qualify(published,final,before_pair,before_column,before_parser,proofs,groups):
    checks = Five.qualify(published,final,before_pair,before_column,proofs,groups)
    proof = proofs[PARSER_ROLE]
    columns = Parser.H.check_tails(*[Parser.P.bundle(image) for image in (before_parser,final)])
    assert json.loads(json.dumps(columns))==proof['column_tails']
    whole = Parser.whole(before_parser,final)
    with Five.Four.Prior.strict_dispatch_kernel():
        vectors = ParserIRQ.vectors(before_parser,final,proof['labels'])
    checks['final_minus_SHA256'][PARSER_ROLE] = digest(before_parser)
    assert set(checks['final_minus_SHA256'])==set(GROUPS)
    checks[PARSER_ROLE] = dict(column_tails=columns,whole=whole,vectors=vectors)
    print('Final-minus triple-shadow parser foreground and vectors passed.',flush=True)
    return checks


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Check the exact preimages and controller without writing.')
    mode.add_argument('--qualify',action='store_true',help='Run all final-minus proofs in memory.')
    mode.add_argument('--emit',action='store_true',help='Run all final-minus proofs and stage one native packet.')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build' and not output.exists()
    published,strict,final,before_pair,before_column,before_parser,proofs,groups = components()
    packet = Five.Four.Prior.route_controller(strict,final)
    print(json.dumps(dict(parent_SHA256=H.PIN,memory_SHA256=digest(final),groups=GROUPS)),flush=True)
    if args.census:
        return
    checks = qualify(published,final,before_pair,before_column,before_parser,proofs,groups)
    if args.emit:
        packet[2].update({Path(__file__),Path(Five.__file__),Path(Five.Column.__file__),Five.COLUMN,
                          Path(Parser.__file__),Path(ParserIRQ.__file__),PARSER,PARSER_IRQ})
        Five.Four.stage(output,final,groups,checks,packet)
        receipt = load(output/'proof.json')
        assert set(receipt['groups'])==set(receipt['final_minus_SHA256'])==set(GROUPS)
        print(json.dumps(dict(passed=True,ROM_SHA256=digest(final),qualified_groups=GROUPS)),flush=True)


if __name__=='__main__':
    main()
