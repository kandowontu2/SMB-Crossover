"""Controller-only Alex/Ryan routes using the frozen sparse native observer."""
from pathlib import Path
import argparse
import json
import current_ice_route_1030_v1 as I


def prepare(args):
    I.D.C.BASE.update(alex=(20,21,'RcVariant',0), ryan=(20,21,'RcVariant',1))
    I.prepare(args)
    p = args.output.resolve()/'native-ice-packet.json'
    h = json.loads(p.read_text())
    h['bindings'][str(Path(__file__).resolve())] = I.D.sha(__file__)
    h['observer_scope'] = 'Same generic eight review markers and all native assertions; genuine menu20/raw21/RcVariant. No Ice-specific motion or state assertions.'
    q = p.with_name('native-city-packet.json')
    assert not q.exists()
    q.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(packet=str(q),packet_sha256=I.D.sha(q),native=False)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='action',required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--identity',choices=['alex','ryan'],required=True)
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--frames',type=int,default=6000)
    p.add_argument('--policy',type=Path,required=True)
    p = sub.add_parser('run')
    p.add_argument('--packet',type=Path,required=True)
    args = ap.parse_args()
    if args.action=='prepare':
        assert 1 <= args.frames <= 6000
        prepare(args)
    else:
        return I.run(args)


if __name__=='__main__':
    raise SystemExit(main())
