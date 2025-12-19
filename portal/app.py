from flask import Flask,render_template,request,jsonify,send_file,session,redirect,url_for
from pathlib import Path
from functools import wraps
import json,datetime,os,secrets,hashlib
app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY',secrets.token_hex(16))
cfg_p=Path('../config/cfg.json')
wh_p=Path('../config/webhooks.json')
st_p=Path('../config/state.json')
auth_p=Path('../config/auth.json')
def ld(p):
 if p.exists():
  with open(p)as f:return json.load(f)
 return{}if'cfg'in str(p)else{"webhooks":[]}
def sv(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 with open(p,'w')as f:json.dump(d,f,indent=2)
def mk_hash(pwd):return hashlib.sha256(pwd.encode()).hexdigest()
def ld_auth():
 auth=ld(auth_p)
 if not auth.get("users"):
  auth["users"]=[{"u":"admin","p":mk_hash("changeme"),"admin":True}]
  sv(auth_p,auth)
 return auth
def chk_auth(fn):
 @wraps(fn)
 def wrapper(*a,**k):
  if"u"not in session:return redirect(url_for('login'))
  return fn(*a,**k)
 return wrapper
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=request.form.get('u')
  p=request.form.get('p')
  auth=ld_auth()
  for usr in auth.get("users",[]):
   if usr["u"]==u and usr["p"]==mk_hash(p):
    session['u']=u
    session['admin']=usr.get("admin",False)
    return redirect(url_for('idx'))
  return render_template('login.html',err='Invalid u/p')
 return render_template('login.html')
@app.route('/logout')
def logout():
 session.clear()
 return redirect(url_for('login'))
@app.route('/')
@chk_auth
def idx():return render_template('index.html')
@app.route('/api/cfg',methods=['GET'])
@chk_auth
def get_cfg():return jsonify(ld(cfg_p))
@app.route('/api/cfg',methods=['POST'])
@chk_auth
def set_cfg():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 sv(cfg_p,request.json)
 return jsonify({"ok":True})
@app.route('/api/wh',methods=['GET'])
@chk_auth
def get_wh():return jsonify(ld(wh_p))
@app.route('/api/wh',methods=['POST'])
@chk_auth
def add_wh():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 wh=ld(wh_p)
 wh["webhooks"].append({**request.json,"id":len(wh["webhooks"])})
 sv(wh_p,wh)
 return jsonify({"ok":True})
@app.route('/api/wh/<int:id>',methods=['DELETE'])
@chk_auth
def del_wh(id):
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 wh=ld(wh_p)
 wh["webhooks"]=[w for w in wh["webhooks"]if w["id"]!=id]
 sv(wh_p,wh)
 return jsonify({"ok":True})
@app.route('/api/st',methods=['GET'])
@chk_auth
def get_st():return jsonify(ld(st_p))
@app.route('/api/exp',methods=['GET'])
@chk_auth
def exp():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 cfg=ld(cfg_p)
 wh=ld(wh_p)
 st=ld(st_p)
 msgs=ld_msgs()
 exp_d={"cfg":cfg,"wh":wh,"st":st,"msgs":msgs,"ts":datetime.datetime.now().isoformat()}
 fn=f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
 with open(fn,'w')as f:json.dump(exp_d,f,indent=2)
 return send_file(fn,as_attachment=True)
@app.route('/api/imp',methods=['POST'])
@chk_auth
def imp():
 try:
  if not session.get('admin'):return jsonify({"err":"No perms"}),403
  d=request.json
  if"cfg"in d:sv(cfg_p,d["cfg"])
  if"wh"in d:sv(wh_p,d["wh"])
  if"st"in d:sv(st_p,d["st"])
  if"msgs"in d:sv(msgs_p,d["msgs"])
  return jsonify({"ok":True})
 except:return jsonify({"err":"Failed"}),400
@app.route('/api/ch',methods=['POST'])
@chk_auth
def ch_chan():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 cfg=ld(cfg_p)
 c=request.json
 if c["act"]=="add":
  if c["cat"]not in cfg["chans"]:cfg["chans"][c["cat"]]=[]
  cfg["chans"][c["cat"]].append(c["name"])
 elif c["act"]=="del":
  if c["cat"]in cfg["chans"]:cfg["chans"][c["cat"]].remove(c["name"])
 elif c["act"]=="ren":
  if c["cat"]in cfg["chans"]:
   idx=cfg["chans"][c["cat"]].index(c["old"])
   cfg["chans"][c["cat"]][idx]=c["new"]
 sv(cfg_p,cfg)
 return jsonify({"ok":True})
@app.route('/api/r',methods=['POST'])
@chk_auth
def ch_role():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 cfg=ld(cfg_p)
 r=request.json
 if r["act"]=="add":cfg["roles"][r["name"]]=r["color"]
 elif r["act"]=="del":del cfg["roles"][r["name"]]
 elif r["act"]=="ren":
  cfg["roles"][r["new"]]=cfg["roles"].pop(r["old"])
 sv(cfg_p,cfg)
 return jsonify({"ok":True})
msgs_p=Path('../config/messages.json')
def ld_msgs():
 m=ld(msgs_p)
 if not m:m={"messages":{}}
 return m
@app.route('/api/msgs',methods=['GET'])
@chk_auth
def get_msgs():return jsonify(ld_msgs())
@app.route('/api/msgs',methods=['POST'])
@chk_auth
def set_msgs():
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 sv(msgs_p,request.json)
 return jsonify({"ok":True})
@app.route('/api/msg/<ch>',methods=['GET'])
@chk_auth
def get_msg(ch):
 m=ld_msgs()
 return jsonify({"msg":m["messages"].get(ch,"")})
@app.route('/api/msg/<ch>',methods=['POST'])
@chk_auth
def set_msg(ch):
 if not session.get('admin'):return jsonify({"err":"No perms"}),403
 m=ld_msgs()
 if"messages"not in m:m["messages"]={}
 m["messages"][ch]=request.json.get("msg","")
 sv(msgs_p,m)
 return jsonify({"ok":True})
if __name__=='__main__':
 ld_auth()
 app.run(debug=False,host='0.0.0.0',port=5000)
