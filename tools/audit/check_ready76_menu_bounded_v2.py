"""Run the complete admission matrix against an explicitly selected joint."""
from pathlib import Path
import argparse,hashlib,json
import check_ready76_menu_bounded_v1 as V


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();V.J=args.joint.resolve();V.O=args.output.resolve();V.main()
    path=V.O/'controls.json';data=json.loads(path.read_text())
    data['bindings'][str(Path(__file__).resolve())]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
