from probe import *
c=Client();ctx=json.loads((P/'test-context.json').read_text())['context'];p=c.api('poll',{'context':ctx});save('agent-trace.json',p)
truth=json.loads(ssh('docker exec agent-zero-1 cat /a0/usr/workdir/vision-test/groundtruth.json'));state=json.loads(ssh('docker exec agent-zero-1 cat /a0/usr/workdir/vision-test/state.json'));save('challenge-groundtruth.json',truth);save('challenge-state.json',state)
logs=p['logs'];tools=[{'timestamp':datetime.datetime.fromtimestamp(x['timestamp'],datetime.timezone.utc).isoformat(),'tool':x['kvps'].get('_tool_name'),'args':{k:v for k,v in x['kvps'].items() if k not in ['browser_snapshot','Screenshot']},'result':x['content']} for x in logs if x['type']=='tool'];save('tool-trace.json',tools)
shots=list(dict.fromkeys(x['kvps']['browser_snapshot']['path'] for x in logs if x.get('kvps',{}).get('browser_snapshot')))
for i,s in enumerate(shots): (P/f'screenshot-{i:02d}.jpg').write_bytes(subprocess.check_output(['ssh',HOST,'docker exec agent-zero-1 cat '+s]))
save('screenshot-manifest.json',[{'source':s,'local':f'screenshot-{i:02d}.jpg'} for i,s in enumerate(shots)])
(P/'final-screenshot.jpg').write_bytes((P/f'screenshot-{len(shots)-1:02d}.jpg').read_bytes())
allowed=all(t['tool'] in ['browser','vision_load'] and (t['tool']!='browser' or t['args']['action'] in ['open','screenshot','click','mouse']) for t in tools)
responses=[x['content'] for x in logs if x['type']=='response'];direct=json.loads((P/'direct-result.json').read_text())['body']['choices'][0]['message']['content'];direct_truth=json.loads((P/'direct-groundtruth.json').read_text())['quadrants'];matched=all(f'{k}: {v}' in direct for k,v in direct_truth.items())
presets=c.api('plugins/_model_config/model_presets');save('presets-after.json',presets)
preserved=[]
for i in (1,2):
 a=Client(i).api('poll');save(f'after-{i}.json',a);b=json.loads((P/f'before-{i}.json').read_text());preserved.append(all(next(x for x in a['contexts'] if x['id']==old['id'])==old for old in b['contexts']))
result={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'context':ctx,'direct_image_http_status':200,'direct_quadrant_groundtruth_match':matched,'backend_vision_enabled':True,'default_presets_unchanged':presets==json.loads((P/'presets-before.json').read_text()),'existing_contexts_unchanged':preserved,'tools_screenshot_only':allowed,'agent_final_marker_matches':truth['marker'] in responses[-1],'independent_server_stage':state['stage'],'click_count':len(state['clicks']),'correct_clicks':sum(x['correct'] for x in state['clicks']),'first_attempt_pass':False,'second_attempt_pass':state['stage']==2,'retry_guidance':'Supplied verified image dimensions and no-offset fact, NOT target coordinates or marker.','final_marker':truth['marker'],'test_chat_vision_override_only':True}
assert all([matched,allowed,result['agent_final_marker_matches'],state['stage']==2,result['default_presets_unchanged'],all(preserved)])
save('verification.json',result);print(json.dumps(result,indent=2))
# Stop only our exact temporary fixture process; retain evidence and test chat.
print(ssh("docker exec agent-zero-1 sh -c 'kill 2412; ! kill -0 2412 2>/dev/null'"))
