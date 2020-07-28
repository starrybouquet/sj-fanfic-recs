/*! scripts/tumblr/utils/exceptions.js */
!function(t,n){"use strict";function e(t,n,e,r){t.addEventListener?t.addEventListener(n,e,!!r):t.attachEvent&&t.attachEvent("on"+n,e,!!r)}function r(t){var n=decodeURIComponent(h.cookie).match(new RegExp(t+"=([^;]+)"));return n&&n.length>1?n[1]:null}function o(t,n){return"string"==typeof t&&t.length>n?[t.slice(0,n/2),"...",t.length-n,"...",t.slice(-n/2)].join(""):t}function i(){return((h.head||{}).innerHTML||"").indexOf("#missinge_button")!==-1}function a(t,n,e,i,a){try{if(n=o(n,300)||"",k.test(n)&&!A.test(n))return;if(a=I(o(a&&a.stack,1e3)||""),k.test(a)&&!A.test(a))return;j.push({path:(h.location||{}).pathname||"NO_LOCATION_OR_PATHNAME",msg:o(t,200)||"",url:n,ln:y(e,10)||-1,col:y(i,10)||-1,err:a,group:R("js_errors_web_a")("A",R("js_errors_web_b")("B","*")),logged_in:!!r("logged_in")}),E.___err=!0}catch(a){}}function c(t,n){"number"==typeof n&&O.random()>n||(t instanceof b?(t.url||(t.url="//www.tumblr.com/"),a(t.message,t.url,t.ln,t.col,t)):T.push(I(t)))}function u(t){for(var n,e,r=t.length;r>0;)e=O.floor(O.random()*r),r--,n=t[r],t[r]=t[e],t[e]=n;return t}function s(t){if(!S||!S.getEntriesByType)return t;var n=S.getEntriesByType("resource"),e={};x(n,function(t){var n=(t.name.match(/\/\/([^\/]+)/)||"")[1];if(n.indexOf(".tumblr.")!==-1){e[t.initiatorType]||(e[t.initiatorType]=[]);var r=n.split(".")[0];e[t.initiatorType].push({name:t.name.split(n)[1],duration:(t.duration||"").toString(),bucket:r,protocol:(t.nextHopProtocol||"").toString(),timing:{redirectStart:(t.redirectStart||"").toString(),redirectEnd:(t.redirectEnd||"").toString(),fetchStart:(t.fetchStart||"").toString(),domainLookupStart:(t.domainLookupStart||"").toString(),domainLookupEnd:(t.domainLookupEnd||"").toString(),connectStart:(t.connectStart||"").toString(),connectEnd:(t.connectEnd||"").toString(),secureConnectionStart:(t.secureConnectionStart||"").toString(),requestStart:(t.requestStart||"").toString(),responseStart:(t.responseStart||"").toString(),responseEnd:(t.responseEnd||"").toString(),transferSize:(t.transferSize||"").toString()}})}}),w.entries||(w.entries=[]);for(var r=[{type:"img",num:10},{type:"link",num:2},{type:"script",num:2},{type:"css",num:2}],o=0;o<r.length;++o){var i=r[o],a=e[i.type];if(a)for(i.num<a.length&&u(a);i.num&&a.length;)w.entries.push(a.pop()),--i.num}return D(w)&&((t||(t={})).perf=w,w.timing=S.timing,w.memory=S.memory,w.navigation=S.navigation),t}function l(){try{L||(j.length=0,c(new b("PAGE_DID_NOT_LOAD")));var n;if(!i()&&R("enable_js_errors_log")(function(){j.length&&((n||(n={})).errors=j)}),R("js_performance_logging")(function(){try{n=s(n)}catch(t){}}),R("enable_js_ephemeral_log")(function(){T.length&&((n||(n={})).ephemeral=T)}),!n)return;n.cdn=d||"CDN_LOOKUP_FAILED";var e=JSON.stringify({form_key:(h.getElementById("tumblr_form_key")||h.body).getAttribute("content"),gpop:(h.getElementById("tumblr_gpop")||h.body).getAttribute("content"),log:n}),r=new N;r.open("POST","/svc/log/capture/exceptions?mode=xhr"),r.setRequestHeader("Content-type","application/json"),r.onreadystatechange=function(){4===r.readyState&&(j.length=T.length=0)},r.send(e)}catch(o){if(!t.jQuery)return;(n||(n={})).errors||(n.errors=j),t.jQuery.ajax({dataType:"json",contentType:"application/json",type:"POST",data:{form_key:t.jQuery("#tumblr_form_key").attr("content"),log:n},url:"/svc/log/capture/exceptions?mode=jquery",withFormKey:!0}),c(o)}}function g(){w.page_info={},w.page_info.path=h.location.pathname||"n/a"}function p(){var t=(new v).getTime(),n=t-S.timing.navigationStart;w.page_load_time=n}function f(){if(S&&S.timing)try{g(),p()}catch(t){}}function m(){L=!0,f()}var d,h=t.document,_=t.navigator,y=t.parseInt,S=t.performance,E=t.window,v=t.Date,b=t.Error,O=t.Math,N=t.XMLHttpRequest,T=[],j=[],w={},L=!1,k=/https?:\/\//,A=/https?:\/\/[^\/]*tumblr[^\/]*/,I=function(t){return t&&t.stringify&&function(n){try{return t.stringify(n)}catch(e){return c(e),'"FAILED_JSON_STRINGIFY"'}}||function(){return'"NO_JSON_STRINGIFY"'}}(t.JSON),R=function(t){return t&&t.Flags||function(){function t(t,n){return"function"==typeof t?t.call(this,n):t}c(new b("Missing Tumblr.Flags in exceptions.js"));var n={enable_js_errors_log:!0,enable_js_ephemeral_log:!0};return function(e){var r=!!n[e];return function o(n,e){var i=t.call(this,r?n:e,r);return void 0!==i?i:o}}}()}(t.Tumblr),D=function(t){return t&&t.keys||function(n){var e=[],r=t.prototype.hasOwnProperty;for(var o in n)r.call(n,o)&&e.push(o);return e}}(t.Object),x=function(t,n,e){if("function"==typeof n)for(var r=(t&&t.length)>>>0,o=0;o<r;o++)n.call(e,t[o],o,t)};!function(){try{var t=new N;t.open("GET","https://assets.tumblr.com/delivery/cdn.json"),t.onreadystatechange=function(){if(t.readyState===N.DONE)try{d=JSON.parse(t.response).cdn}catch(n){d="CDN_BAD_RESPONSE"}},t.send()}catch(n){}}();c.debugDump=function(){var n=[];return x(h.getElementsByTagName("script"),function(t){n.push(t.src)}),{timestamp:+new v,path:(h.location||{}).href||"NO_HREF",lang:(_||{}).userLanguage||(_||{}).language||"NO_LANG",referrer:h.referrer||"NO_REFERRER",ua:(_||{}).userAgent||"NO_UA",timing:(S||{}).timing||"NO_TIMING",scripts:n,globals:D(t),cookie:h.cookie,ephemeral:T,errors:j,document:(h.documentElement||{}).innerHTML||"NO_DOCUMENT"}};!function(){e(E,"beforeunload",l),E.onerror=a}(),(n.Utils||(n.Utils={})).exceptions=c,e(E,"load",m)}(this,this.Tumblr||(this.Tumblr={}));