"""Recheck genuine audio vectors and owner lifetime on the exact delivered rebase."""

import argparse
import json
from pathlib import Path

import check_native_audio_frame_token_lifecycle_1110_v1 as L
import check_native_audio_frame_token_vectors_1110_v1 as V
from prepare_mini_audio_frame_token_native_1110 import (
    BUILD, EXPECTED, PIN, PROOFS, RUNTIME, build_image, digest, sha,
)
from prepare_mini_lane_audio_native_1110 import without_component


def qualify(final):
    base,expected,proof = build_image()
    assert final==expected and digest(final)==EXPECTED
    before = without_component(final,RUNTIME)
    assert before==base and digest(before)==PIN
    result = dict(parent_SHA256=PIN,candidate_SHA256=EXPECTED,
                  final_minus_audio_spans_SHA256=digest(before),
                  native_vectors=V.qualify(before,final,proof),
                  owner_lifecycle=L.qualify(before,final,proof))
    result.update(passed=True,bindings={str(p.resolve()):sha(p) for p in (Path(__file__),*PROOFS)})
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output!=BUILD
    path = output/'proof.json'
    assert not path.exists(),path
    final = args.rom.read_bytes()
    result = qualify(final)
    result['bindings'][str(args.rom.resolve())] = sha(args.rom)
    output.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(candidate_SHA256=EXPECTED,vector_cases=result['native_vectors']['vector_cases'],
                          owner_round_trips=result['owner_lifecycle']['round_trips'])),flush=True)


if __name__=='__main__':
    main()
