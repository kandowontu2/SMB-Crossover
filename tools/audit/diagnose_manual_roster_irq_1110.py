"""Locate a first live-state delta without weakening the genuine ISR assertion."""
import argparse,inspect,json
from pathlib import Path
import check_manual_roster_irq_1110 as Q


def live_delta(a,b,path=()):
 out=[]
 def visit(x,y,p):
  if x==y or len(out)>=24:return
  if isinstance(x,(tuple,list,bytes,bytearray))and isinstance(y,type(x)):
   if len(x)!=len(y):out.append((p,'length',len(x),len(y)))
   for i,(xx,yy)in enumerate(zip(x,y)):
    if xx!=yy:visit(xx,yy,p+(i,))
  else:out.append((p,x,y))
 visit(a,b,path);return out


def main():
 cli=argparse.ArgumentParser();cli.add_argument('--baseline',action='store_true');args=cli.parse_args()
 q=json.loads(Q.PROOF.read_text())
 for name,digest in q['bindings'].items():assert Q.SHA(Q.R/name)==digest,name
 raw=Q.I.BASE.read_bytes()if args.baseline else Q.P.install(Q.I.BASE.read_bytes(),q['patches'])
 assert Q.I.SHA(raw)==(q['parent_SHA256']if args.baseline else q['expected_memory_only_SHA256'])
 inner=inspect.getsource(Q.P.vectors).replace('def vectors(','def qualify(',1)
 needle='assert after == before, (kind, owner, entry)'
 assert inner.count(needle)==1
 inner=inner.replace(needle,'assert after == before, (kind, owner, entry, live_delta(after,before))')
 outer=inspect.getsource(Q.vectors).replace('def vectors(','def diagnostic(',1)
 line="source=inspect.getsource(P.vectors).replace('def vectors(','def qualify(',1)"
 assert outer.count(line)==1
 outer=outer.replace(line,'source=INNER',1).replace('env=dict(P.__dict__)',"env=dict(P.__dict__);env['live_delta']=live_delta",1)
 env=dict(Q.__dict__,INNER=inner,live_delta=live_delta);exec(outer,env)
 try:env['diagnostic'](Q.I.bundle(raw,q['labels']),q['labels'],0x28,((29,0),),('birth',))
 except AssertionError as error:
  result=dict(expected_memory_only_SHA256=Q.I.SHA(raw),baseline=args.baseline,assertion=repr(error),passed=False)
  (Q.I.OUT/('irq-diagnostic-baseline.json'if args.baseline else'irq-diagnostic.json')).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True);return
 raise AssertionError('Original failure not reproduced')


if __name__=='__main__':main()
