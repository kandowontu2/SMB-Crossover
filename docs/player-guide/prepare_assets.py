"""Validate included authentic images; regenerate native portraits only on request."""
from pathlib import Path
import json,hashlib,argparse
H=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--recapture-portraits',action='store_true');a=p.parse_args()
 if a.recapture_portraits:
  from capture_portrait_pixels import main as capture
  import sys
  sys.argv=[sys.argv[0]];capture()
 manifest=json.loads((H/'assets/edition-provenance.json').read_text())
 for pic in manifest:
  if 'asset'in pic:assert hashlib.sha256((H/'assets/edition'/pic['asset']).read_bytes()).hexdigest()==pic['sha256'],pic['asset']
 print('Authentic cached assets verified. ROM/source-backed recapture requires the original workspace.')
if __name__=='__main__':main()
