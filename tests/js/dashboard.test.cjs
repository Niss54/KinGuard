const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('kinguard/webui/index.html','utf8');
const extract=(start,end)=>html.slice(html.indexOf(start),html.indexOf(end));
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject};};
const tick=()=>new Promise(resolve=>setImmediate(resolve));

function fixture(){
  const pending=[];
  const S={caseId:'A',parentId:'parent-A',token:'family-A',linkToken:null,hybrid:{},hospitals:[]};
  const context=vm.createContext({S,render:()=>{},api:(path,options)=>{
    if(path==='/api/whoami')return Promise.resolve({signed_in:true});
    const response=deferred(); pending.push({path,options,...response});return response.promise;
  }});
  vm.runInContext(extract('function requestContext(','async function api(')+
    extract('function resetCaseScopedState(','function useCase(')+
    extract('async function load(','function render('),context);
  const resolveCase=(id)=>pending.filter(p=>p.path.startsWith(`/api/cases/${id}/`)).forEach(p=>
    p.resolve(p.path.endsWith('/brief')?{brief:{parent_id:`parent-${id}`,note:id}}:{owner:id}));
  const resolveParent=(id)=>pending.filter(p=>p.path.startsWith(`/api/parents/parent-${id}`)).forEach(p=>p.resolve({owner:id}));
  return {S,context,pending,resolveCase,resolveParent};
}

test('late case A cannot replace case B brief, bills or parent record',async()=>{
  const f=fixture(); const a=f.context.load(); await tick();
  f.S.caseId='B';const b=f.context.load();await tick();
  f.resolveCase('B');await tick();f.resolveParent('B');await b;
  f.resolveCase('A');await a;
  assert.equal(f.S.caseId,'B');assert.equal(f.S.brief.brief.note,'B');
  assert.equal(f.S.bills.owner,'B');assert.equal(f.S.record.owner,'B');
  assert.equal(f.S.parentId,'parent-B');
  assert.equal(f.pending.filter(p=>p.path.includes('/parents/parent-A')).length,0);
  assert.ok(f.pending.filter(p=>p.path.includes('/cases/A')).every(p=>p.options.context.caseId==='A'));
});

test('case switch while parent reads are pending discards all old data',async()=>{
  const f=fixture(); const a=f.context.load();await tick();f.resolveCase('A');await tick();
  f.S.caseId='B';const b=f.context.load();await tick();
  assert.equal(f.S.brief,null);assert.equal(f.S.record,null);
  f.resolveCase('B');await tick();f.resolveParent('B');await b;
  f.resolveParent('A');await a;
  assert.equal(f.S.record.owner,'B');assert.equal(f.S.brief.brief.note,'B');
});

test('sign-out during load cannot restore protected data; stale errors cannot wipe new case',async()=>{
  const f=fixture();const a=f.context.load();await tick();
  f.S.token=null;f.context.resetCaseScopedState(false);f.resolveCase('A');await a;
  assert.equal(f.S.brief,null);assert.equal(f.S.record,null);
  f.S.token='family-B';f.S.caseId='B';const b=f.context.load();await tick();
  f.resolveCase('B');await tick();f.resolveParent('B');await b;
  assert.equal(f.S.brief.brief.note,'B');
});

test('newer refresh of the same case wins over an earlier response',async()=>{
  const f=fixture();const first=f.context.load();await tick();
  const old=f.pending.slice();const second=f.context.load();await tick();
  f.pending.filter(p=>!old.includes(p)).forEach(p=>p.resolve(
    p.path.endsWith('/brief')?{brief:{parent_id:'parent-A',note:'new'}}:{owner:'new'}));
  await tick();f.resolveParent('A');await second;
  old.forEach(p=>p.reject(new Error('old request failed')));await first;
  assert.equal(f.S.brief.brief.note,'new');assert.equal(f.S.bills.owner,'new');
});

test('signed links can load parent data without a full session',async()=>{
  const f=fixture();f.S.token=null;f.S.linkToken='signed-link';
  const load=f.context.load();await tick();f.resolveCase('A');await tick();
  f.resolveParent('A');await load;
  assert.equal(f.S.record.owner,'A');
  assert.ok(f.pending.every(p=>p.options.context.linkToken==='signed-link'));
});

test('actual signOut clears protected state and invalidates pending case requests',async()=>{
  const f=fixture();const old=f.context.load();await tick();
  f.S.record={private:'old record'};f.S.brief={brief:{note:'old brief'}};
  const start=html.indexOf('function signOut(){');
  const end=html.indexOf('\n}',start)+2;
  vm.runInContext(html.slice(start,end),f.context);
  const realLoad=f.context.load;f.context.load=()=>{};
  f.context.signOut();
  assert.equal(f.S.token,null);assert.equal(f.S.record,null);assert.equal(f.S.brief,null);
  f.resolveCase('A');await old;
  assert.equal(f.S.record,null);assert.equal(f.S.brief,null);
  f.context.load=realLoad;
});

test('case switch clears payment destination and discards late QR and handoff links',async()=>{
  const f=fixture();const requests=[];
  Object.assign(f.context,{API:'',fetch:()=>{const p=deferred();requests.push(p);return p.promise;}});
  vm.runInContext(extract('async function showUpi(','function hideUpi(')+
    extract('async function mintHandoff(','async function revokeHandoff('),f.context);
  f.S.upi={private:'old destination'};
  const upi=f.context.showUpi('payment-A');const handoff=f.context.mintHandoff();
  f.context.resetCaseScopedState();f.S.caseId='B';
  assert.equal(f.S.upi,null);assert.equal(f.S.handoff,null);
  requests[0].resolve({ok:true,json:async()=>({vpa:'case-A'})});
  requests[1].resolve({ok:true,json:async()=>({url:'case-A-private-link'})});
  await Promise.all([upi,handoff]);
  assert.equal(f.S.upi,null);assert.equal(f.S.handoff,null);
});
