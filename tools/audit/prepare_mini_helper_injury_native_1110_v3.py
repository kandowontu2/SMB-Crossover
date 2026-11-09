"""Add shared terrain-column palette work to the exact d998 Mini batch."""

import argparse
import json
from pathlib import Path

import check_native_column_palette_1110 as Column
import prepare_mini_helper_injury_native_1110_v2 as Four
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import digest, load
from prepare_mini_lane_audio_native_1110 import verify_parent
from prepare_selected_native_packet_v1 import sha


R,H = Four.R,Four.H
COLUMN = R/'build/native-column-palette-1110/proof.json'
COLUMN_SHA256 = '11108c33e476f181785a8320f99e3cc7b5e2a9d30f8ed7c35675e7734ce5ec46'
COLUMN_ROLE = 'terrain_column_palette'
GROUPS = (*Four.GROUPS,COLUMN_ROLE)


def components():
    published,strict,before_column,before_pair,proofs,groups = Four.components()
    assert sha(COLUMN)==COLUMN_SHA256
    isolated,proof,parts = verify_parent(published,COLUMN)
    assert digest(isolated)==proof['expected_memory_only_SHA256']
    assert len(parts)==1 and parts[0][:2]==(H.offset(3,Column.START),H.offset(3,Column.END))
    lo,hi,_,_ = parts[0]
    assert all(row['file_offset']+len(bytes.fromhex(row['new_hex']))<=lo or row['file_offset']>=hi
               for rows in groups.values() for row in rows)
    for source,h in proof['source_bindings'].items():
        assert sha(R/source)==h,source
    proofs[COLUMN_ROLE],groups[COLUMN_ROLE] = proof,proof['patches']
    final = install(before_column,proof['patches'])
    assert final==install(published,[row for role in GROUPS for row in groups[role]])
    before_pair = install(before_pair,proof['patches'])
    pair = proofs[Four.PAIR_ROLE]
    assert Four.Pair.census(before_pair)==pair['source_ingress']
    assert Four.pair_readers(before_pair)==load(Four.PAIR_READERS)['all_absolute_indexed_and_indirect_literal_matches']
    return published,strict,final,before_pair,before_column,proofs,groups


def qualify(published,final,before_pair,before_column,proofs,groups):
    checked = Four.qualify(published,final,before_pair,proofs,groups)
    foreground = Column.foreground(before_column,final)
    assert json.loads(json.dumps(foreground))==proofs[COLUMN_ROLE]['foreground']
    vectors = Column.vectors(before_column,final)
    checked['final_minus_SHA256'][COLUMN_ROLE] = digest(before_column)
    assert set(checked['final_minus_SHA256'])==set(GROUPS)
    checked[COLUMN_ROLE] = dict(foreground=foreground,vectors=vectors)
    print('Final-minus terrain column foreground and vectors passed.',flush=True)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--census',action='store_true',help='Check the exact preimages and controller without writing.')
    mode.add_argument('--qualify',action='store_true',help='Run all final-minus proofs in memory.')
    mode.add_argument('--emit',action='store_true',help='Run all final-minus proofs and stage one native packet.')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build' and not output.exists()
    published,strict,final,before_pair,before_column,proofs,groups = components()
    packet = Four.Prior.route_controller(strict,final)
    print(json.dumps(dict(parent_SHA256=H.PIN,memory_SHA256=digest(final),groups=GROUPS)),flush=True)
    if args.census:
        return
    checked = qualify(published,final,before_pair,before_column,proofs,groups)
    if args.emit:
        packet[2].update({Path(__file__),Path(Column.__file__),COLUMN})
        # Keep the qualified four-group stager frozen. Its durable groups
        # and final-minus checks come from the exact arguments here.
        Four.stage(output,final,groups,checked,packet)
        receipt = load(output/'proof.json')
        assert set(receipt['groups'])==set(receipt['final_minus_SHA256'])==set(GROUPS)
        print(json.dumps(dict(passed=True,ROM_SHA256=digest(final),qualified_groups=GROUPS)),flush=True)


if __name__=='__main__':
    main()
