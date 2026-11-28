/* Shared Firebase lifecycle and language routing for dashboard and handoff. */
(function(root) {
  const SDK_VERSION = "13.4.0";
  const DEFAULT_MODEL = "gemini-3.5-flash-lite";
  const englishOptions = {
    expectedInputs: [{type:"text", languages:["en"]}],
    expectedOutputs: [{type:"text", languages:["en"]}],
  };
  async function loadSDK() {
    const base = `https://www.gstatic.com/firebasejs/${SDK_VERSION}`;
    const modules = await Promise.all([
      import(`${base}/firebase-app.js`), import(`${base}/firebase-app-check.js`),
      import(`${base}/firebase-ai.js`),
    ]);
    return Object.assign({}, ...modules);
  }
  function useCloud(language, inputLanguage, text) {
    // Romanised Tamil/Hindi cannot reliably be detected with a character regex.
    // Unspecified/mixed input therefore defaults to cloud; English is explicit.
    return language !== "en" || inputLanguage !== "en" || /[\u0900-\u0DFF]/u.test(text);
  }
  async function create(config, onStatus = () => {}, loader = loadSDK) {
    if(!config?.configured) throw new Error("Firebase AI configuration is missing.");
    const sdk = await loader();
    const app = sdk.initializeApp(config.firebase_config);
    const appCheck = !!(config.recaptcha_site_key || config.app_check_debug);
    if(config.app_check_debug) root.FIREBASE_APPCHECK_DEBUG_TOKEN = true;
    if(appCheck) {
      const provider = config.recaptcha_site_key
        ? new sdk.ReCaptchaEnterpriseProvider(config.recaptcha_site_key)
        : new sdk.CustomProvider({getToken: () => Promise.reject(new Error("App Check debug mode active"))});
      sdk.initializeAppCheck(app, {provider, isTokenAutoRefreshEnabled:true});
    }
    const ai = sdk.getAI(app, {backend:new sdk.GoogleAIBackend()});
    const inCloudParams = {model:config.cloud_fallback_model || DEFAULT_MODEL};
    const local = sdk.getGenerativeModel(ai, {
      mode: appCheck ? sdk.InferenceMode.PREFER_ON_DEVICE : sdk.InferenceMode.ONLY_ON_DEVICE,
      inCloudParams, onDeviceParams:{createOptions:englishOptions},
    });
    const cloud = appCheck ? sdk.getGenerativeModel(ai, {
      mode:sdk.InferenceMode.ONLY_IN_CLOUD, inCloudParams,
    }) : null;
    let initialization = null;
    let initialized = false;
    let deviceAvailable = false;
    function initializeDevice() {
      if(initialized) return Promise.resolve(deviceAvailable);
      if(initialization) return initialization;
      onStatus("Preparing on-device model; the first download may take several minutes.", "downloading");
      // Invoked directly from the click path, before the first await in generate.
      // Do not move this to page-load initialization: Chrome requires activation.
      let pending;
      try {
        pending = local.initializeDeviceModel(progress => {
          onStatus(`Downloading on-device model: ${Math.round(progress * 100)}%`, "downloading");
        });
      } catch(error) { pending = Promise.reject(error); }
      initialization = Promise.resolve(pending).then(async () => {
        const status = await root.LanguageModel?.availability(englishOptions) || "unavailable";
        deviceAvailable = status === "available";
        initialized = deviceAvailable;
        onStatus(deviceAvailable ? "On-device model available; actual source is shown after each response."
          : "On-device model unavailable; cloud fallback requires configured App Check.", status);
        return deviceAvailable;
      }).catch(error => {
        onStatus(`On-device initialization failed: ${String(error)}. Cloud fallback requires App Check.`, "unavailable");
        if(!cloud) throw error;
        return false;
      }).finally(() => { initialization = null; });
      return initialization;
    }
    return {
      appCheckActive:appCheck,
      async generateContent(prompt, {language="en", inputLanguage="auto"} = {}) {
        if(useCloud(language, inputLanguage, prompt)) {
          if(!cloud) throw new Error("This language needs cloud inference. Configure Firebase App Check first.");
          onStatus("Using cloud inference for the selected or mixed language.", null);
          return cloud.generateContent(prompt);
        }
        const available = await initializeDevice();
        if(!available && !cloud) throw new Error("On-device model unavailable and cloud App Check is not configured.");
        return (available ? local : cloud).generateContent(prompt);
      },
    };
  }
  const api = {create, useCloud, SDK_VERSION, DEFAULT_MODEL};
  root.KinGuardHybrid = api;
  if(typeof module !== "undefined") module.exports = api;
})(globalThis);
