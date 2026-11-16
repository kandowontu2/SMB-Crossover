"""Compile frozen life calibration controllers and reject nonowning inputs."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import json
import replay_bowser_natural_stock_bc5_1115 as Base
import replay_bowser_oneup_lifecycle_bc5_1115 as Observer

def run(raw):
    rows=[]
    for identity in(0,1):
        for name,module,args in(('baseL',Base,dict(identity=identity,kind='oneup')),('firstWriter',Observer,dict(identity=identity))):
            text=module.controller(raw,**args)
            rows.append(dict(scope=name,identity=identity,source=Path(module.__file__).name,
                source_SHA256=sha256(Path(module.__file__).read_bytes()).hexdigest(),LF_Lua_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text)))
    wrong=bytearray(raw);wrong[16+8192]^=1;rejected=[]
    for label,image in(('truncated',raw[:-1]),('unowned_byte',bytes(wrong)),('reference67',Base.Current.reference(raw))):
        for module in(Base,Observer):
            try:module.controller(image)
            except AssertionError:rejected.append(dict(image=label,factory=Path(module.__file__).name))
            else:raise AssertionError('Frozen current controller accepted a wrong image')
    q=dict(passed=True,ROM_SHA256=Base.PIN,controllers=rows,strict_rejections=rejected,
        scope='Readonly compile/binding only; firstWriter identity1 has no separate source gameplay claim',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest();return q

if __name__=='__main__':
    raw=Base.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Readonly life metadata attempted output/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
