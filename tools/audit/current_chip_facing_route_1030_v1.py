"""Sparse controller-only Chip/Dale facing review plus the existing 1-1 route."""
from pathlib import Path
import argparse
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import current_character_route_1030_v4 as D
import current_ice_route_1030_v1 as I


def prepare(args):
    source=I.SCRIPT.read_text()
    needle="""  want('corner-332',c.x>=332 and c.x<345)
  want('corner-345',c.x>=345 and c.x<360)
  want('corner-360',c.x>=360 and c.x<380)"""
    replacement="""  want('facing-right',r('PlayerFacingDir')==1 and c.vx>0 and c.vx<128 and c.x<280)
  want('facing-left',r('PlayerFacingDir')==2 and c.vx>=128 and c.x<280)
  want('throw',r('CdThrowAge')>=16)"""
    assert source.count(needle)==1
    script=args.output.resolve().parent/'current-chip-facing-sparse-1030-v1.lua'
    generated=source.replace(needle,replacement)
    if script.exists():assert script.read_text()==generated
    else:script.write_text(generated)
    original=D.C.prepare
    def facing_prepare(a):
        D.C.SCRIPT=script
        D.C.MARKERS=['first-active','facing-right','facing-left','throw','power-change','flagpole','endpoint','failure']
        return original(a)
    D.C.prepare=facing_prepare
    D.prepare(args)
    p=args.output.resolve()/'native-packet.json'
    h=json.loads(p.read_text())
    h.update(emulator_timeout_seconds=145,process_timeout_seconds=160,
        prepared_predecessor_sha256=D.sha(p),
        timeout_basis='Same sparse observer as measured 4490-frame RCR79.847s;6000frame ceiling unchanged. Only three capture-trigger names/conditions change.')
    h['bindings'][str(Path(__file__).resolve())]=D.sha(__file__)
    q=p.with_name('native-chip-packet.json')
    assert not q.exists()
    q.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(packet=str(q),packet_sha256=D.sha(q),native=False)))


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare')
    p.add_argument('--identity',choices=['chip','dale'],required=True)
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--frames',type=int,default=6000)
    p.add_argument('--policy',type=Path,default=R/'tools/playthroughs/current_chip_facing_1030_v1.lua')
    p=sub.add_parser('run')
    p.add_argument('--packet',type=Path,required=True)
    args=ap.parse_args()
    if args.action=='prepare':
        assert 1<=args.frames<=6000
        args.output.resolve().parent.mkdir(parents=True,exist_ok=True)
        prepare(args)
    else:return I.run(args)


if __name__=='__main__':raise SystemExit(main())
