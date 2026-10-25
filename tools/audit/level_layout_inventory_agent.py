"""Read-only inventory of pinned Crossover level XML; never edits ROM/source maps."""
from pathlib import Path
import collections, hashlib, json, re, sys, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[2]
O=R/'build/verification/level-layout-audit-agent'
def record(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(R)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(path):
    root=ET.fromstring(path.read_bytes());out={}
    for lev in root:
        if 'ID'not in lev.attrib:continue
        for area in lev:
            if 'ID'not in area.attrib:continue
            d=dict(level=lev.attrib,area=area.attrib)
            for kind in ('MAP','PICKUPS'):
                s=area.findtext(kind)
                if s is not None:d[kind]=[row.split(',')for row in s.strip().split('],')]
            out[lev.attrib['ID']+area.attrib['ID']]=d
    return out
def tiles(a,kind):
    return {(x,y):v for y,row in enumerate(a.get(kind,[]))for x,v in enumerate(row)if v not in ('0','')}
def brief(v):return v.split('&&')[0]
def main():
    O.mkdir(parents=True,exist_ok=True)
    paths=[R/'reference/crossover/assets/45_com.smbc.level.LevelData_LevelDataXML.bin',R/'reference/crossover2/extracted/binaryData/322_com.smbc.level.LevelData_LevelDataXML.bin']
    maps=[load(p)for p in paths]
    result=dict(sources=[record(p)for p in paths],counts=[dict(levels=len({x[:3]for x in m}),areas=len(m))for m in maps],areas=[],helpers=[],version_differences=[])
    for key in sorted(set(maps[0])|set(maps[1])):
        a,b=(m.get(key,{})for m in maps)
        result['areas'].append(dict(id=key,early_attributes={k:v for k,v in a.items()if k not in('MAP','PICKUPS')},later_attributes={k:v for k,v in b.items()if k not in('MAP','PICKUPS')},early_dimensions=[len(a.get('MAP',[[]])[0]),len(a.get('MAP',[]))],later_dimensions=[len(b.get('MAP',[[]])[0]),len(b.get('MAP',[]))]))
        for vi,m in enumerate(maps):
            ar=m.get(key,{})
            for kind in ('MAP','PICKUPS'):
                for(x,y),v in tiles(ar,kind).items():
                    if 'charHorz'in v or 'charVert'in v:
                        result['helpers'].append(dict(version=('early','2.02')[vi],area=key,layer=kind,x_tile=x,y_tile=y,x=x*16,y=y*16,value=v))
        for kind in ('MAP','PICKUPS'):
            ta,tb=tiles(a,kind),tiles(b,kind)
            for x,y in sorted(set(ta)|set(tb),key=lambda p:(p[1],p[0])):
                va,vb=ta.get((x,y),'0'),tb.get((x,y),'0')
                if va!=vb:result['version_differences'].append(dict(area=key,layer=kind,x_tile=x,y_tile=y,x=x*16,y=y*16,early=va,later=vb))
    (O/'xml-inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(counts=result['counts'],helpers=collections.Counter(z['version']for z in result['helpers']),version_differences=len(result['version_differences']),by_area=collections.Counter(z['area']for z in result['version_differences'])),indent=2))
    for h in result['helpers']:print(h)
if __name__=='__main__':main()
