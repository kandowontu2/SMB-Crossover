"""Bound source/NMI proof runner; never emits a cartridge."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_sms_native_prototype_1110 as S
import check_sonic_sms_native_irq_1110 as V


def sha(p):return sha256(p.read_bytes()).hexdigest()


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--name-recipe',type=Path)
    args=cli.parse_args();assert args.output.resolve()==S.OUT
    if args.name_recipe:S.NAME_RECIPE=args.name_recipe.resolve()
    before,after,patches,labels,funding,art,records=S.compose(args.output)
    body=S.body(after)
    print('Actual body',json.dumps(body),flush=True)
    vectors=V.vectors(before,after,funding['required_name_endpoint']['PC'])
    q=dict(passed=True,ROM_written=False,parent_SHA256=S.digest(before),
        expected_memory_only_SHA256=S.digest(after),body=body,vectors=vectors,
        menu_vectors_pending=True,shared_name_CPU_pending=funding['shared_name_CPU_pending'],
        bindings={p.relative_to(S.R).as_posix():sha(p) for p in
                  (Path(__file__),Path(S.__file__),Path(V.__file__),S.SOURCE,
                   S.Render.S.SOURCE,S.NAME_RECIPE,Path(V.Q.__file__))})
    (args.output/'body-vectors.json').write_text(json.dumps(q,indent=2)+'\n')
    print('Body vectors',json.dumps(vectors),flush=True)


if __name__=='__main__':main()
