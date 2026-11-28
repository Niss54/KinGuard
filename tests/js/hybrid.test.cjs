const test = require('node:test');
const assert = require('node:assert/strict');
const hybrid = require('../../kinguard/webui/hybrid.js');

function fixture({debug=true, fail=false, cloudFail=false, available='downloadable'}={}) {
  let status=available;
  const events=[];
  const models=[];
  global.LanguageModel={availability:async()=>status};
  const sdk={
    initializeApp:()=>({}),
    initializeAppCheck:(_app,options)=>events.push(['appcheck',options]),
    ReCaptchaEnterpriseProvider:class {}, CustomProvider:class {}, GoogleAIBackend:class {},
    getAI:()=>({}),
    InferenceMode:{PREFER_ON_DEVICE:'prefer',ONLY_ON_DEVICE:'device',ONLY_IN_CLOUD:'cloud'},
    getGenerativeModel:(_ai,options)=>{
      models.push(options);
      return {
        initializeDeviceModel:async(progress)=>{
          events.push(['initialize']); progress(0.5);
          if(fail) throw new Error('download failed');
          if(status==='downloadable') status='available';
        },
        generateContent:async prompt=>{
          const source=options.mode==='cloud'?'in_cloud':'on_device';
          if(cloudFail && source==='in_cloud') throw new Error('App Check rejected');
          events.push(['generate',source,prompt]);
          return {response:{inferenceSource:source,text:()=>source}};
        },
      };
    },
  };
  return {events,models,create:()=>hybrid.create(
    {configured:true,firebase_config:{},app_check_debug:debug},
    (message,status)=>events.push(['status',status,message]),async()=>sdk)};
}

test('fresh downloadable Nano is initialized before English generation; warm calls reuse it',async()=>{
  const f=fixture(); const model=await f.create();
  assert.equal(f.events.filter(e=>e[0]==='initialize').length,0);
  const pending=model.generateContent('mild fever',{inputLanguage:'en'});
  // Initialization is called synchronously inside the user-gesture call path.
  assert.equal(f.events.filter(e=>e[0]==='initialize').length,1);
  assert.equal((await pending).response.inferenceSource,'on_device');
  await model.generateContent('cough',{inputLanguage:'en'});
  assert.equal(f.events.filter(e=>e[0]==='initialize').length,1);
  assert.ok(f.events.find(e=>e[0]==='status'&&e[2].includes('50%')));
  assert.equal(f.models[0].inCloudParams.model,'gemini-3.5-flash-lite');
});

test('Tamil, Hindi, mixed and uncertain input cannot select the English on-device path',async()=>{
  const f=fixture(); const model=await f.create();
  for(const [text,options] of [
    ['வலி',{inputLanguage:'en'}],['दर्द',{inputLanguage:'en'}],
    ['amma nenju valikkuthu',{inputLanguage:'auto'}],['seene mein dard',{}],
    ['English brief',{language:'ta',inputLanguage:'en'}],
    ['English bill',{language:'hi',inputLanguage:'en'}],
  ]) assert.equal((await model.generateContent(text,options)).response.inferenceSource,'in_cloud');
  assert.equal(f.events.filter(e=>e[0]==='initialize').length,0);
  assert.equal(f.models[1].mode,'cloud');
});

test('unavailable or failed device initialization falls back only when cloud is configured',async()=>{
  for(const options of [{available:'unavailable'},{fail:true}]) {
    const f=fixture(options); const model=await f.create();
    assert.equal((await model.generateContent('fever',{inputLanguage:'en'})).response.inferenceSource,'in_cloud');
  }
  const f=fixture({debug:false,available:'unavailable'}); const model=await f.create();
  assert.equal(f.models[0].mode,'device');
  await assert.rejects(model.generateContent('fever',{inputLanguage:'en'}),/unavailable/);
  await assert.rejects(model.generateContent('fever',{inputLanguage:'auto'}),/App Check/);
  assert.equal(f.events.filter(e=>e[0]==='generate').length,0);
});

test('debug App Check works with a blank reCAPTCHA key; cloud rejection stays an error',async()=>{
  const f=fixture(); const model=await f.create();
  assert.equal(global.FIREBASE_APPCHECK_DEBUG_TOKEN,true);
  assert.equal(f.events.filter(e=>e[0]==='appcheck').length,1);
  assert.equal(model.appCheckActive,true);
  const rejected=await fixture({cloudFail:true}).create();
  await assert.rejects(rejected.generateContent('fever'),/App Check rejected/);
  await assert.rejects(hybrid.create({configured:false}),/configuration/);
});
