import requests,subprocess,json,pathlib,datetime,base64,random,io
from PIL import Image,ImageDraw
P=pathlib.Path(__file__).parent
HOST='root@<agent-zero-host>'
def ssh(cmd): return subprocess.check_output(['ssh','-o','BatchMode=yes',HOST,cmd],timeout=30).decode()
def save(n,d): (P/n).write_text(json.dumps(d,indent=2))
class Client:
 def __init__(self,i=1):
  self.url=f'http://<agent-zero-host>:{50079+i}';self.s=requests.Session()
  raw=ssh(f'docker exec agent-zero-{i} cat /a0/usr/.env')
  env=dict(line.split('=',1) for line in raw.splitlines() if '=' in line and not line.startswith('#'))
  self.s.post(self.url+'/login',data={'username':env['AUTH_LOGIN'].strip('"\''),'password':env['AUTH_PASSWORD'].strip('"\'')},timeout=20).raise_for_status()
  t=self.s.get(self.url+'/api/csrf_token',timeout=20).json();assert t['ok'];self.s.headers.update({'X-CSRF-Token':t['token'],'Origin':self.url})
 def api(self,path,data=None):
  r=self.s.post(self.url+'/api/'+path,json=data or {},timeout=60);r.raise_for_status();return r.json()
if __name__=='__main__':
 save('health.json',requests.get('http://<agent-zero-host>:8731/health',timeout=20).json())
 for i in (1,2):
  c=Client(i);p=c.api('poll');save(f'before-{i}.json',p);print(i,json.dumps({k:v for k,v in p.items() if k not in ['logs','notifications']})[:10000])
 colors=['red','blue','green','purple'];random.SystemRandom().shuffle(colors)
 im=Image.new('RGB',(640,480),'white');d=ImageDraw.Draw(im)
 for color,(x,y) in zip(colors,[(160,120),(480,120),(160,360),(480,360)]): d.ellipse((x-60,y-60,x+60,y+60),fill=color)
 im.save(P/'direct-challenge.png');save('direct-groundtruth.json',{'quadrants':dict(zip(['top-left','top-right','bottom-left','bottom-right'],colors))})
 payload={'model':'halogen-qwen3.8-flash-next','messages':[{'role':'user','content':[{'type':'text','text':'Identify the color of the circle in each quadrant: top-left, top-right, bottom-left, bottom-right. Answer only those four labels and colors.'},{'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode((P/'direct-challenge.png').read_bytes()).decode()}}]}],'max_tokens':300,'temperature':0,'enable_thinking':False}
 r=requests.post('http://<agent-zero-host>:8731/v1/chat/completions',json=payload,timeout=120);save('direct-result.json',{'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':r.status_code,'body':r.json()});print('DIRECT',r.status_code,r.text)
