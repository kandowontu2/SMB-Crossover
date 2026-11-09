"""Check native vector continuations on the exact composed Mini box image."""

import argparse
import json
from pathlib import Path

import check_mini_native_body_box_dispatch_irq_1110 as Body
import check_native_platform_box_vectors_1110_v1 as Platform
from prepare_mini_body_platform_native_1110 import (
    GIRDER, PIN, PLATFORM, build_image, digest, load, sha, without_component,
)


def qualify(final, with_girder=False):
    _,expected,components = build_image(with_girder)
    assert final==expected,'Composed ROM differs from the verified patches'
    result = dict(parent_SHA256=PIN,candidate_SHA256=digest(final),girder_included=with_girder)
    result['body_box'] = Body.qualify(final)
    result['platform_box'] = Platform.qualify(without_component(final,PLATFORM),final)
    if with_girder:
        from check_native_girder_irq_1110_v1 import P, vectors
        baseline = without_component(final,GIRDER)
        result['girder'] = vectors(P.bundle(baseline),P.bundle(final),load(GIRDER))
    result['passed'] = True
    result['bindings'] = {str(path.resolve()):sha(path) for pair in components for path in pair}
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--with-girder',action='store_true')
    args = cli.parse_args()
    result = qualify(args.rom.read_bytes(),args.with_girder)
    args.output.mkdir(exist_ok=True)
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}),flush=True)


if __name__=='__main__':
    main()
