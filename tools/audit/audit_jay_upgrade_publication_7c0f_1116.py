"""Passive current Jay upgrade publication witness, ordinary V3 prefix only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import jay_natural_fsl_controls_v3_1116 as V3

J,Base=V3.J,V3.Base
N,W=J.N,J.W
V3_SHA='6746cbe6239e67c08ee6d5cdd9207902bd3b83f86c4d4e1c3fd1be5ef2e58704'
CHECK_SHA='407f51f1a089a12e31c418af919ae9fb620e790bc2efdb42e6e8b5e5353010f0'


def run(raw):
    assert J.H(Path(V3.__file__).read_bytes())==V3_SHA
    assert J.H(Path(Base.__file__).read_bytes())==CHECK_SHA
    q=J.bindings(raw);m=J.cold(raw);fields=q['fields'];counts=Counter();writes=[];reads=[];points={};preimages={}
    for name in('JnMovement','UnionPwrUpCore','JnCollectPickup'):
        at=W.location(m.bundle,name);pc=W.address(m.bundle,name);tag=((at-16)//8192)|128
        points[tag,pc]=name;preimages[name]=dict(file=at,PC=pc,tag=tag,first48=raw[at:at+48].hex())
    union=preimages['UnionPwrUpCore'];data=bytes.fromhex(union['first48']);needle=bytes((0xad,fields['PlayerStatus']&255,fields['PlayerStatus']>>8))
    assert data.count(needle)==1
    readpc=union['PC']+data.index(needle)
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
    def row():
        return dict(Main=counts['GameLoop'],frame=N.get(m,'FrameCounter'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),stars=N.get(m,'JnStars'),status=N.get(m,'PlayerStatus'),tier=N.get(m,'JnOwnedTier'),hp=N.get(m,'JnHealth'))
    old=N.NesMPU
    class Observe(old):
        def step(self):
            pc=self.pc;t=tag(pc)
            if(t,pc)==(q['hooks']['GameLoop']['tag'],q['hooks']['GameLoop']['PC']):counts['GameLoop']+=1
            name=points.get((t,pc))
            if name:counts[name]+=1
            isread=(t,pc)==(union['tag'],readpc)
            before=row()if isread else None
            stars=N.get(m,'JnStars');status=N.get(m,'PlayerStatus')
            result=super().step()
            if isread:
                assert len(reads)<4;reads.append(dict(before=before,PC=pc,tag=t,A_after_actual_LDA=self.a,SP=self.sp))
            if(stars,status)!=(N.get(m,'JnStars'),N.get(m,'PlayerStatus')):
                assert len(writes)<8;writes.append(dict(PC=pc,tag=t,opcode=m[pc],before=dict(stars=stars,status=status),after=row()))
            return result
    with patch.object(J,'cold',lambda image:m if image is raw else (_ for _ in()).throw(AssertionError('Unknown image'))),patch.object(N,'NesMPU',Observe):
        route=V3.run(raw,'flower',1170)
    assert route['fault']is None and route['Main']==route['motor']==1170
    assert len(route['collected'])==1 and len(route['births'])==2
    assert all(b['label']=='mushroom'for b in route['births'])
    assert counts['JnMovement']==0 and counts['JnCollectPickup']==1 and counts['UnionPwrUpCore']==2
    assert len(reads)==2 and all(r['A_after_actual_LDA']==0 for r in reads)
    assert len(writes)==1 and writes[0]['before']==dict(stars=0,status=0)and writes[0]['after']['stars']==128 and writes[0]['after']['status']==0
    out=dict(passed=True,kind='passive genuine upgrade-publication failure witness',owning_SHA256=J.PIN,
        route_receipt=route['receipt_SHA256'],Main=route['Main'],motor=route['motor'],counts=dict(counts),preimages=preimages,
        actual_PlayerStatus_LDA=reads,actual_stars_or_status_changes=writes,collected=route['collected'],births=route['births'],
        terminal=route['terminal'],no_gameplay_writes_or_repair=True,generated_files=0,native=False,
        V3_SHA256=V3_SHA,source_checker_SHA256=CHECK_SHA,source_SHA256=J.H(Path(__file__).read_bytes()))
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Upgrade publication witness attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
