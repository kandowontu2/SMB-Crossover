"""Root-only exact590 named sprite probes; bounded RAM-only PNGs."""
from hashlib import sha256
import argparse,json
from pathlib import Path

import replay_named_world_images_590_1115 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=F.R/'build/smb2-flag-native-1113'
SOURCE='9f6236e3b54fbd837ba72dd5a7f6d5f625024839a3b8d95315a4b67b5e6b07bf'
LUA={
    'donkey_kong':'196a8402e6a036fb2a76363f68b255518b30577d8ecb6b15162eaf7d1e5f3bc8',
    'hogan':'136ec5809a05b1d38651419aa3e093a8e94e1696ebee8741cbae0f838c7d6aa4',
    'dibiase':'3007638ffaeb70a1e0a87dfffa2ad410a92cee2ff12efd6b92ae68875c2ab9e2',
    'bigelow':'c517479155f651f443e8a42d5605e5bda7778c9493619c1be248d31ea3a2f8f5',
    'honky':'0017d5ee8e1940ccaba131880e642709c7b25949bb4768d93d4032743d03dfa2',
    'savage':'4278e1ae8a3789fc31e965bc1bcc6cca6d2158012ac19f23855642b36409976b',
    'andre':'b3afacc5d3d92b79245ffb9831e4d8fd2f4c2aa3b98cefad0ec323ab6051f237',
}


def execute(key):
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==SOURCE
    before=check(F.ROM);raw=F.ROM.read_bytes();assert sha256(raw).hexdigest()==F.PIN
    text=F.controller(raw,key);assert sha256(text.encode()).hexdigest()==LUA[key]
    assert{p.name for p in OUT.iterdir()if p.is_file()}=={'candidate.nes','controller.lua'}
    Storage.preflight(private_root=OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    candidate=(OUT/'candidate.nes').read_bytes()
    script=OUT/'controller.lua';script.write_bytes(text.encode())
    q=run(script,F.ROM,OUT/'capture',F.PIN,180)
    assert q['script_SHA256']==LUA[key]and q['outputs_written']==0
    if q['passed']:assert len(q['images'])==(3 if key=='donkey_kong'else 2)
    assert all(im['bytes']<=65536 for im in q['images'])
    assert F.ROM.read_bytes()==raw and check(F.ROM)==before
    assert(OUT/'candidate.nes').read_bytes()==candidate
    return dict(identity=key,**q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',nargs='+',choices=LUA,required=True);a=p.parse_args()
    failures=[]
    for key in a.identity:
        q=execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        if not q['passed']:failures.append(key)
    assert not failures,('Opening graphics observations remain unqualified',failures)
