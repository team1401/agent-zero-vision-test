from probe import *
import copy
c=Client(1)
before=c.api('poll');assert not any(x['running'] for x in before['contexts'])
# Back up, but do not modify, default presets. Only new test context is overridden.
presets=c.api('plugins/_model_config/model_presets');save('presets-before.json',presets)
ctx=c.api('chat_create',{'project_name':''})['ctxid'];save('test-context.json',{'context':ctx})
chat=copy.deepcopy(presets['presets'][0]['chat']);chat['vision']=True
chat['kwargs']['temperature']=0
chat['kwargs']['extra_body']={'enable_thinking':False}
c.api('plugins/_model_config/model_override',{'context_id':ctx,'action':'set','override':{'chat':chat}})
save('override-readback.json',c.api('plugins/_model_config/model_override',{'context_id':ctx,'action':'get'}))
subprocess.run(['scp',str(P/'challenge_server.py'),HOST+':/tmp/a0-vision-test-server.py'],check=True,capture_output=True)
ssh('docker exec agent-zero-1 mkdir -p /a0/usr/workdir/vision-test; docker cp /tmp/a0-vision-test-server.py agent-zero-1:/a0/usr/workdir/vision-test/server.py; rm /tmp/a0-vision-test-server.py')
ssh("docker exec -d agent-zero-1 /opt/venv-a0/bin/python /a0/usr/workdir/vision-test/server.py")
print(ssh("docker exec agent-zero-1 curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18764"))
text='''This is an authorized harmless screenshot-only browser navigation test. In this NEW chat browser context open http://127.0.0.1:18764 using your browser tool. The page contains a randomized visual challenge. Take a screenshot, then call vision_load with the returned screenshot path to SEE it. Read the instruction in the image, identify its target circle, and click its center using browser click x/y coordinates. Then take and load a fresh screenshot, follow its next visual instruction, click, and take/load a final screenshot. Report the exact final visible success marker. Strict rules: use only browser open, screenshot, coordinate click/mouse and vision_load, then response. NO browser content/detail/evaluate, DOM, accessibility, OCR, code execution, HTTP requests, file reads, source inspection, or other tools. Do not guess. Screenshots and vision_load are the evidence. Limit to four clicks total; if images fail report the exact failure and stop. Do not touch other contexts or tabs. Your model supports image input and vision is enabled for this test chat.'''
save('task-request.json',{'context':ctx,'text':text})
print(c.api('message_async',{'context':ctx,'text':text}));print('CONTEXT',ctx)
