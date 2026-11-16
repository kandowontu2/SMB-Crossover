"""Same ordinary Jay controls; read native1UP's actual rewritten popup slot."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json,re
import jay_natural_fsl_controls_v3_1116 as V3

Base,J=V3.Base,V3.J
CHECK_SHA='407f51f1a089a12e31c418af919ae9fb620e790bc2efdb42e6e8b5e5353010f0'
V3_SHA='6746cbe6239e67c08ee6d5cdd9207902bd3b83f86c4d4e1c3fd1be5ef2e58704'


def geometry(raw):
    source=(J.R/'src/level_tiles.s').read_text();data=bytearray()
    for line in source.split('L_GroundArea6:',1)[1].splitlines():
        if '.byte'in line:
            data.extend(int(v,16)for v in re.findall(r'\$([0-9a-fA-F]{2})',line.split(';')[0]))
            if data[-1]==253:break
    data=bytes(data);assert raw.count(data)==1
    rows=[];page=0
    for offset in range(2,len(data)-1,2):
        a,b=data[offset:offset+2];page+=bool(b&128);row=a&15
        if row==13 and not b&64 and not b&128:page=b&31
        if row<12 and not b&112:
            rows.append(dict(offset=offset,bytes=data[offset:offset+2].hex(),kind=b&15,left=page*256+(a>>4)*16,top=32+row*16))
    targets={name:next(r for r in rows if(r['kind'],r['left'],r['top'])==key)for name,key in dict(life=(3,1024,128),star=(6,1616,144)).items()}
    return dict(area='L_GroundArea6',file=raw.index(data),stream_SHA256=J.H(data),targets=targets,units='world pixel left/top')


def run(raw,kind,limit):
    assert kind in('star','life')and J.H(Path(Base.__file__).read_bytes())==CHECK_SHA
    assert J.H(Path(V3.__file__).read_bytes())==V3_SHA
    body=V3.text();source=inspect.getsource(Base.run)
    old="a['kind']==3 and 11 in popups and s['lives']==2"
    new="a['kind']==3 and N.get(m,'FloateyNum_Control',a['slot'])==11 and s['lives']==2"
    assert source.count(old)==1;source=source.replace(old,new)
    old='                        target=node'
    new="                        node.update(actual_popup_control=N.get(m,'FloateyNum_Control',a['slot']),actual_sound_queue=N.get(m,'Square2SoundQueue'))\n"+old
    assert source.count(old)==1;source=source.replace(old,new)
    class Recipe:
        @staticmethod
        def read_text():return body
        @staticmethod
        def read_bytes():return body.encode()
    namespace=dict(Base.__dict__,POLICY=Recipe)
    exec(compile(source,'<strict native popup observer>','exec'),namespace)
    q=namespace['run'](raw,kind,limit)
    q.update(geometry=geometry(raw),same_frozen_V3_controls=True,failed_popup_observer_SHA256=CHECK_SHA,
        control_module_SHA256=V3_SHA,observer_source_SHA256=J.H(Path(__file__).read_bytes()),derived_function_SHA256=J.H(source.encode()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('star','life'),required=True);p.add_argument('--limit',type=int,default=1800);a=p.parse_args()
    assert 100<=a.limit<=2600
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay native-popup source observer attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.kind,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
