from probe import *
import time
c=Client();ctx=json.loads((P/'test-context.json').read_text())['context']
for n in range(18):
 p=c.api('poll',{'context':ctx});save('agent-trace.json',p)
 logs=p.get('logs',[]);logs=logs.get('items',[]) if isinstance(logs,dict) else logs
 print(json.dumps(logs[-3:])[:5000],flush=True)
 if not next((x['running'] for x in p['contexts'] if x['id']==ctx),False): break
 time.sleep(10)
print('STATE',ssh('docker exec agent-zero-1 cat /a0/usr/workdir/vision-test/state.json'))
