"""One bounded empty-FF far-call ancestry aggregate; no artifacts or patches."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import profile_ff_empty_cpu_v2_1110 as P

W,N,L,Fix=P.W,P.N,P.L,P.Fix
PROFILE_PIN='abeb873f46a97dadf2ed652a194d34540c3046a03266ba67e8d406b092915418'


def digest(m):
    h=sha256()
    for a,z in ((0,0x100),(0x200,0x800),(0x5c00,0x8000)):h.update(bytes(m[a:z]))
    for ram in m.ram:h.update(ram)
    h.update(m.vram)
    return h.digest()


def main():
    assert sha256(Path(P.__file__).read_bytes()).hexdigest()==PROFILE_PIN
    original=W.ROM.read_bytes();assert sha256(original).hexdigest()==W.PIN
    image,kernel,cookie,*_=Fix.proposal(original);assert sha256(image).hexdigest()==L.PIN
    with patch.object(L,'sample',lambda *a,**k:None):m,cold,_=L.cold_menu(image,0,cookie,kernel)
    b=m.bundle;labels=defaultdict(lambda:defaultdict(list))
    for name,s in b['syms'].items():
        if s.get('type')!='lab' or 'seg' not in s:continue
        try:at=W.address(b,name);loc=W.location(b,name)
        except (ValueError,KeyError):continue
        if loc<16:continue
        tag=-1 if at<0x8000 else ((loc-16)//8192)|128
        if name.startswith('Ff') and 0xa000<=at<0xc000:tag=3
        labels[tag][at].append(name)
    def label(pt):
        tag,pc=pt;choices=[at for at in labels[tag] if at<=pc]
        if not choices:return f'{tag}:{pc:04X}'
        at=max(choices);names=labels[tag][at]
        return f'{tag}:{pc:04X} '+('/'.join(names[:2]))+f'+{pc-at:X}'
    common=W.address(b,'FarCallCommon');jump=W.address(b,'FarcallJmpTarget_SMC')
    idle=W.address(b,'IdleLoop');groups={};totals=Counter();frame_rows=[]
    for phase,pad,length in (('idle_empty',0,16),('walking_empty',1,16)):
        for epoch in range(length):
            before=P.state(m);assert not any(before['enemy_flags'])
            m.controller_pad=pad;W.clear_logs(m);P.normal_nmi(m)
            c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
            frames=[];events=[];last=None;entered=Counter()
            for _ in range(300000):
                for i in range(len(events)-1,-1,-1):
                    e=events[i]
                    if (c.pc,c.sp)==e['goal']:
                        key=e['key'];row=groups[key];row['calls']+=1
                        row['cycles']+=c.processorCycles-e['begin']
                        row['unchanged_application']+=int(digest(m)==e['memory'])
                        row['unchanged_AXYP']+=int((c.a,c.x,c.y,c.p)==e['regs'])
                        row.setdefault('first_outputs',dict(A=c.a,X=c.x,Y=c.y,P=c.p))
                        row['ancestry'][e['ancestry']]+=1
                        del events[i]
                while frames and c.sp>=frames[-1]['goal'][1]:frames.pop()
                if (c.pc,c.sp)==(idle+12,252):
                    assert not events and not frames,[(e['key'],e['goal']) for e in events]
                    break
                pt=P.point(m,c.pc)
                if c.pc in (common,jump):
                    kind='FarCallCommon' if c.pc==common else 'SMC_target'
                    destination=m[jump+1]+256*m[jump+2]
                    raw=c.a if c.pc==common else (m.rawtags[(destination-0x8000)//8192] if destination>=0x8000 else -1)
                    target=(raw,destination);key=(kind,last,target)
                    if key not in groups:groups[key]=dict(calls=0,cycles=0,unchanged_application=0,
                        unchanged_AXYP=0,ancestry=Counter(),first_inputs=dict(A=c.a,X=c.x,Y=c.y,P=c.p))
                    ret=m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1
                    goal=(ret,(c.sp+2)&255) if kind=='FarCallCommon' else (jump+3,c.sp)
                    events.append(dict(key=key,goal=goal,begin=c.processorCycles,memory=digest(m),
                        regs=(c.a,c.x,c.y,c.p),ancestry=tuple((f['callsite'],f['callee']) for f in frames[-6:])))
                    entered[kind]+=1
                opcode=m[c.pc];assert opcode
                if opcode==0x20:
                    target=m[c.pc+1]+256*m[c.pc+2]
                    frames.append(dict(goal=(c.pc+3,c.sp),callsite=pt,callee=P.point(m,target)))
                c.step();last=pt
            else:raise AssertionError(('Main bound',hex(c.pc)))
            after=P.state(m);assert not any(after['enemy_flags']) and after['lives']==2 and after['engine']==8
            frame_rows.append(dict(phase=phase,epoch=epoch,cycles=c.processorCycles,entries=dict(entered),before=before,after=after))
            totals.update(entered)
    output=[]
    for (kind,site,target),r in sorted(groups.items(),key=lambda z:z[1]['cycles'],reverse=True):
        if r['calls']<8:continue
        output.append(dict(kind=kind,callsite=label(site),target=label(target),calls=r['calls'],
            calls_per_Main=r['calls']/len(frame_rows),inclusive_cycles_per_Main=r['cycles']/len(frame_rows),
            mean_inclusive_cycles=r['cycles']/r['calls'],unchanged_application=r['unchanged_application'],
            unchanged_AXYP=r['unchanged_AXYP'],first_inputs=r['first_inputs'],first_outputs=r['first_outputs'],
            top_ancestry=[dict(calls=count,JSR_edges=[label(site)+' => '+label(target) for site,target in path]) for path,count in r['ancestry'].most_common(1)]))
    sites=Counter();site_cycles=Counter()
    for (kind,site,target),r in groups.items():
        if kind=='FarCallCommon':sites[site]+=r['calls'];site_cycles[site]+=r['cycles']
    common_sites=[dict(site=label(site),calls=count,calls_per_Main=count/len(frame_rows),
        inclusive_cycles_per_Main=site_cycles[site]/len(frame_rows)) for site,count in sites.most_common(25)]
    untouched=[row for row in output if row['kind']=='SMC_target' and row['unchanged_application']==row['calls']]
    objects={}
    for name,length in (('ObjectMetasprite',24),('Enemy_Flag',6),('Misc_State',9),('Block_State',2),
                        ('FloateyNum_Control',7),('RgShotType',10),('SmShotType',3),('SmBombAge',3)):
        if name in b['syms']:objects[name]=[N.get(m,name,i) for i in range(length)]
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,output_files=0,
        candidate_SHA256=L.PIN,cold=cold,Main_updates=len(frame_rows),totals=dict(totals),
        first=frame_rows[0],last=frame_rows[-1],terminal_object_fields=objects,
        common_callsite_totals=common_sites,dominant_common_spans=[r for r in output if r['kind']=='FarCallCommon'][:16],
        untouched_application_targets=untouched[:20],
        scope='Actual far-call entry/SMC-target ancestry and return spans in32 controller-only empty FF updates. Inclusive spans overlap by nesting. Memory digest excludes dead stack/SMC/mapper transport; equality is a measured scene property, not a general skip authorization. No candidate modification.')),flush=True)


if __name__=='__main__':main()
