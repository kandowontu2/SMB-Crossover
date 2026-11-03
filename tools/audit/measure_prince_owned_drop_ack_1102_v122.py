"""Acknowledge the native no-drop policy only after actor revalidation."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_owned_drop_ack_1102_v120 as OLD
O=OLD.O


def main():
 text=inspect.getsource(OLD.main).replace('v120','v122')
 old="out=out.replace(' stx PpProxyBestSlot',' stx InvDropEnemy')"
 new=r"""out=out.replace(' stx PpProxyBestSlot\\n','')
 out=out.replace(' ldy #1\\n jsr PpNativeCall',' stx InvDropEnemy\\n ldy #1\\n jsr PpNativeCall')"""
 assert old in text;text=text.replace(old,new)
 env=dict(OLD.__dict__,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 path=O/'deferred-strike-measurement-v122.json';q=json.loads(path.read_text());q['native_no_drop_acknowledgement']['invalid_actor_effects']='STX InvDropEnemy occurs only after exact existing flag1/ID0..6/notdefeated revalidation. All rejected stale/absent events retain zero native effect.'
 q['bindings'].update({Path(OLD.__file__).relative_to(R).as_posix():OLD.V.C.M.sha(Path(OLD.__file__).read_bytes())});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
