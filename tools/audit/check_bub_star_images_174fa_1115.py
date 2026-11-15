"""Compile and authenticate the passive three-scene Star facade; zero files."""
from hashlib import sha256
import argparse,json
import replay_bub_star_images_174fa_1115 as F

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0);a=ap.parse_args()
    raw,actual=F.Previous.load_current();q=F.metadata(raw,a.identity)
    text=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('RESULT '+text,flush=True);print('RECEIPT '+sha256(text.encode()).hexdigest(),flush=True)
