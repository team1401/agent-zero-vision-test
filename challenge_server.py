from http.server import HTTPServer,BaseHTTPRequestHandler
from PIL import Image,ImageDraw,ImageFont
import random,json,pathlib,io,datetime
P=pathlib.Path('/a0/usr/workdir/vision-test');P.mkdir(exist_ok=True)
r=random.SystemRandom(); stages=[];state={'stage':0,'clicks':[]}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
for step in range(2):
 colors=['red','blue','green','purple'];r.shuffle(colors);coords=[(150,180),(440,180),(150,420),(440,420)];target=r.choice(colors)
 stages.append({'colors':colors,'coords':coords,'target':target,'center':coords[colors.index(target)]})
marker='VISION-PASS-'+str(r.randrange(100000,999999))
(P/'groundtruth.json').write_text(json.dumps({'stages':stages,'marker':marker}))
def image():
 im=Image.new('RGB',(640,560),'white');d=ImageDraw.Draw(im)
 if state['stage']>=2:d.text((50,150),marker,fill='black',font=font)
 else:
  s=stages[state['stage']];d.text((25,25),'Click the '+s['target']+' circle',fill='black',font=font)
  for color,(x,y) in zip(s['colors'],s['coords']):d.ellipse((x-60,y-60,x+60,y+60),fill=color)
 b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def persist(): (P/'state.json').write_text(json.dumps(state,indent=2))
class H(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path.startswith('/image'):data=image();mime='image/png'
  else:data=b'''<!doctype html><title>Visual challenge</title><style>body{margin:0}</style><img src="/image" draggable="false"><script>document.querySelector('img').onclick=async e=>{await fetch('/click',{method:'POST',body:JSON.stringify({x:e.offsetX,y:e.offsetY})});e.target.src='/image?t='+Date.now()}</script>''';mime='text/html'
  self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def do_POST(self):
  v=json.loads(self.rfile.read(int(self.headers['Content-Length'])));s=stages[min(state['stage'],1)];cx,cy=s['center'];ok=(v['x']-cx)**2+(v['y']-cy)**2<=3600
  state['clicks'].append({'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':state['stage'],**v,'correct':ok})
  if ok and state['stage']<2:state['stage']+=1
  persist();self.send_response(204);self.end_headers()
persist();HTTPServer(('127.0.0.1',18764),H).serve_forever()
