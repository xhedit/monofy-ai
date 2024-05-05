var monofy;(()=>{"use strict";var t={};(t=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})})(t);var e=null;function n(){if(!e){var t=window.AudioContext||window.webkitAudioContext;e=new t,console.log("Audio context created");var n=e.createBuffer(1,1,e.sampleRate),o=e.createBufferSource();o.buffer=n,o.connect(e.destination),o.start(0)}return e}var o,i=["white","black","white","white","black","white","black","white","white","black","white","black"],r=["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"],a=function(){this.events=[],this.title="Untitled",this.description="No description",this.tempo=120},s=function(){function t(){var t=this;this.buffer=null,this.domElement=document.createElement("div"),this.domElement.classList.add("audio-canvas"),this.canvas=document.createElement("canvas"),this.canvas.width=800,this.canvas.height=200,this.domElement.appendChild(this.canvas),this.canvas.addEventListener("click",(function(){t.buffer&&t.playBuffer(t.buffer)})),this.ctx=this.canvas.getContext("2d")}return t.prototype.generateAudio=function(t){return e=this,o=arguments,r=function(t,e){var o,i=this;return void 0===e&&(e=!1),function(t,e){var n,o,i,r,a={label:0,sent:function(){if(1&i[0])throw i[1];return i[1]},trys:[],ops:[]};return r={next:s(0),throw:s(1),return:s(2)},"function"==typeof Symbol&&(r[Symbol.iterator]=function(){return this}),r;function s(s){return function(l){return function(s){if(n)throw new TypeError("Generator is already executing.");for(;r&&(r=0,s[0]&&(a=0)),a;)try{if(n=1,o&&(i=2&s[0]?o.return:s[0]?o.throw||((i=o.return)&&i.call(o),0):o.next)&&!(i=i.call(o,s[1])).done)return i;switch(o=0,i&&(s=[2&s[0],i.value]),s[0]){case 0:case 1:i=s;break;case 4:return a.label++,{value:s[1],done:!1};case 5:a.label++,o=s[1],s=[0];continue;case 7:s=a.ops.pop(),a.trys.pop();continue;default:if(!((i=(i=a.trys).length>0&&i[i.length-1])||6!==s[0]&&2!==s[0])){a=0;continue}if(3===s[0]&&(!i||s[1]>i[0]&&s[1]<i[3])){a.label=s[1];break}if(6===s[0]&&a.label<i[1]){a.label=i[1],i=s;break}if(i&&a.label<i[2]){a.label=i[2],a.ops.push(s);break}i[2]&&a.ops.pop(),a.trys.pop();continue}s=e.call(t,a)}catch(t){s=[6,t],o=0}finally{n=i=0}if(5&s[0])throw s[1];return{value:s[0]?s[1]:void 0,done:!0}}([s,l])}}}(this,(function(r){switch(r.label){case 0:return[4,new Promise((function(o,r){var a={text:t.label};fetch("/api/tts/edge",{method:"POST",body:JSON.stringify(a),headers:{"Content-Type":"application/json"}}).then((function(t){return t.arrayBuffer()})).then((function(t){console.log("Audio buffer downloaded",t),n().decodeAudioData(t,(function(t){i.buffer=t,e&&i.playBuffer(t),o(t)}))})).catch((function(t){console.error("Error downloading audio buffer",t),r(t)}))}))];case 1:return o=r.sent(),this.loadBuffer(o),[2,o]}}))},new((i=void 0)||(i=Promise))((function(t,n){function a(t){try{l(r.next(t))}catch(t){n(t)}}function s(t){try{l(r.throw(t))}catch(t){n(t)}}function l(e){var n;e.done?t(e.value):(n=e.value,n instanceof i?n:new i((function(t){t(n)}))).then(a,s)}l((r=r.apply(e,o||[])).next())}));var e,o,i,r},t.prototype.playBuffer=function(t){var e=n(),o=e.createBufferSource();o.buffer=t,o.connect(e.destination),o.start()},t.prototype.loadBuffer=function(t){this.buffer=t;var e=t.getChannelData(0),n=e.length,o=this.canvas.width/n;this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height),this.ctx.beginPath(),this.ctx.moveTo(0,this.canvas.height/2);for(var i=0;i<n;i++){var r=i*o,a=(e[i]+1)*this.canvas.height/2;this.ctx.lineTo(r,a)}this.ctx.lineTo(this.canvas.width,this.canvas.height/2),this.ctx.stroke()},t}(),l=(o=function(t,e){return o=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&(t[n]=e[n])},o(t,e)},function(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Class extends value "+String(e)+" is not a constructor or null");function n(){this.constructor=t}o(t,e),t.prototype=null===e?Object.create(e):(n.prototype=e.prototype,new n)}),c=function(t){function e(e){var n=t.call(this,e)||this;return n.domElement.classList.add("piano-roll-note-editor"),n.domElement.style.display="none",n.textInput=document.createElement("input"),n.textInput.setAttribute("placeholder","Note lyric"),n.textInput.classList.add("lyric-editor-text"),n.textInput.type="text",n.domElement.appendChild(n.textInput),n.pitchSlider=document.createElement("input"),n.pitchSlider.classList.add("lyric-editor-pitch"),n.pitchSlider.type="range",n.pitchSlider.min="-0.5",n.pitchSlider.max="0.5",n.pitchSlider.step="0.01",n.pitchSlider.addEventListener("input",(function(){n.note.pitch=parseFloat(n.pitchSlider.value)})),n.domElement.appendChild(n.pitchSlider),n.audioCanvas=new s,n.domElement.appendChild(n.audioCanvas.domElement),n.saveButton.addEventListener("click",(function(){n.audioCanvas.domElement.style.display="block",n.audioCanvas.generateAudio(n.note,!0).then((function(t){n.note.audio=t})),n.onsave(n.note)})),n}return l(e,t),e.prototype.show=function(e,n,o){var i,r;t.prototype.show.call(this,e,n,o),this.textInput.value=(null===(i=this.note)||void 0===i?void 0:i.label)||"",(null===(r=this.note)||void 0===r?void 0:r.audio)?(this.audioCanvas.loadBuffer(this.note.audio),this.audioCanvas.domElement.style.display="block"):this.audioCanvas.domElement.style.display="none"},e}(function(){function t(t){var e=this;this.onsave=t,this.note=null,this.domElement=document.createElement("div"),this.domElement.classList.add("piano-roll-dialog"),this.closeButton=document.createElement("button"),this.closeButton.textContent="X",this.domElement.appendChild(this.closeButton),this.closeButton.addEventListener("click",(function(){e.domElement.style.display="none"})),this.saveButton=document.createElement("button"),this.saveButton.textContent="Save",this.domElement.appendChild(this.saveButton),this.saveButton.addEventListener("click",(function(){e.onsave(e.note)}))}return t.prototype.show=function(t,e,n){var o;console.log(t),this.note=t,this.domElement.style.display="block",this.domElement.style.left="".concat(e,"px"),this.domElement.style.top="".concat(n,"px"),null===(o=this.domElement.parentElement)||void 0===o||o.appendChild(this.domElement)},t}());function d(t){return"".concat(r[t%r.length]).concat(Math.floor(t/r.length))}var u=function(){function t(t,e){this.grid=t,this.label="",this.audio=null,this.pitch=e.pitch,this.start=e.start,this.end=e.end,this.domElement=document.createElement("div"),this.domElement.classList.add("piano-roll-note"),this.domElement.style.height="".concat(t.noteHeight,"px"),this.noteLabel=document.createElement("div"),this.noteLabel.classList.add("piano-roll-note-label"),this.noteLabel.textContent=d(this.pitch),this.domElement.appendChild(this.noteLabel),this.lyricLabel=document.createElement("div"),this.lyricLabel.classList.add("piano-roll-note-lyric"),this.domElement.appendChild(this.lyricLabel),e.label&&(this.lyricLabel.textContent=e.label),this.update(),t.domElement.appendChild(this.domElement)}return t.prototype.update=function(){this.noteLabel.textContent=d(this.pitch),this.lyricLabel.textContent=this.label,this.domElement.style.top="".concat((87-this.pitch)*this.grid.noteHeight,"px"),this.domElement.style.left="".concat(this.start*this.grid.beatWidth,"px"),this.domElement.style.width="".concat(100*(this.end-this.start),"px")},t}(),h=function(){function t(){var t=this;this.notes=[],this.currentNote=null,this.noteHeight=20,this.beatWidth=100,this.dragMode=null,this.domElement=document.createElement("div"),this.domElement.classList.add("piano-roll-grid-container"),this.gridElement=document.createElement("div"),this.gridElement.classList.add("piano-roll-grid");var e=document.createElement("canvas");e.width=4*this.beatWidth,e.height=this.noteHeight,console.log("debug",e.width,e.height);var n=e.getContext("2d");if(n){n.strokeStyle="#ddd",n.lineWidth=1;for(var o=1;o<4;o++)n.beginPath(),n.moveTo(o*this.beatWidth,0),n.lineTo(o*this.beatWidth,this.noteHeight),n.stroke();n.lineWidth=3,n.strokeStyle="#aaa",n.beginPath(),n.moveTo(0,0),n.lineTo(0,this.noteHeight),n.stroke()}for(var i=0;i<88;i++){var r=document.createElement("div");r.classList.add("piano-roll-grid-row"),r.style.height="".concat(this.noteHeight,"px"),this.gridElement.appendChild(r),r.style.backgroundImage="url(".concat(e.toDataURL(),")"),r.style.backgroundRepeat="repeat"}this.domElement.appendChild(this.gridElement),this.noteEditor=new c((function(e){var n=t.noteEditor.domElement.querySelector(".lyric-editor-text");e.label=(null==n?void 0:n.value)||"",e.update()})),document.body.appendChild(this.noteEditor.domElement),this.gridElement.addEventListener("pointerdown",(function(e){var n;console.log(e);var o=e.layerX;if(e.preventDefault(),"block"!==t.noteEditor.domElement.style.display)if(e.target instanceof HTMLDivElement&&e.target.classList.contains("piano-roll-note")){t.gridElement.classList.add("dragging");var i=t.notes.find((function(t){return t.domElement===e.target}));(e.ctrlKey||1===e.button)&&(i?t.noteEditor.show(i,e.clientX+20,e.clientY-5):t.noteEditor.domElement.style.display="none"),i&&(t.currentNote=i,2===e.button?(t.remove(i),t.currentNote=null):(null===(n=t.currentNote.domElement.parentElement)||void 0===n||n.appendChild(t.currentNote.domElement),o<6?t.dragMode="start":t.currentNote.domElement.offsetWidth-o<6?t.dragMode="end":t.dragMode="move",console.log("drag mode",t.dragMode,o,t.currentNote.domElement.offsetWidth)))}else{if(0!==e.button)return;if(e.target===t.gridElement){t.gridElement.classList.add("dragging");var r=87-Math.floor(e.layerY/t.noteHeight);t.currentNote=new u(t,{pitch:r,start:e.layerX/t.beatWidth,end:(e.layerX+.125)/t.beatWidth,label:""}),t.add(t.currentNote),t.dragMode="end"}}else t.noteEditor.domElement.style.display="none"})),this.gridElement.addEventListener("pointerup",(function(){t.gridElement.classList.remove("dragging"),t.currentNote=null})),this.gridElement.addEventListener("pointerleave",(function(){t.gridElement.classList.remove("dragging"),t.currentNote&&(t.remove(t.currentNote),t.currentNote=null)})),this.gridElement.addEventListener("contextmenu",(function(t){t.preventDefault()})),this.gridElement.addEventListener("pointermove",(function(e){if(t.currentNote&&1===e.buttons)if("start"===t.dragMode)t.currentNote.start=e.layerX/t.beatWidth,t.currentNote.domElement.style.left="".concat(t.currentNote.start*t.beatWidth,"px"),t.currentNote.domElement.style.width="".concat((t.currentNote.end-t.currentNote.start)*t.beatWidth,"px");else if("end"===t.dragMode)t.currentNote.end=e.layerX/t.beatWidth,t.currentNote.domElement.style.width="".concat((t.currentNote.end-t.currentNote.start)*t.beatWidth,"px");else if("move"===t.dragMode){var n=e.movementX/t.beatWidth;t.currentNote.start+=n,t.currentNote.end+=n,t.currentNote.domElement.style.left="".concat(t.currentNote.start*t.beatWidth,"px")}})),this.gridElement.addEventListener("pointerup",(function(){t.gridElement.classList.remove("dragging"),t.currentNote&&(t.currentNote.domElement.style.pointerEvents="auto"),t.currentNote=null})),this.gridElement.addEventListener("pointerleave",(function(){t.gridElement.classList.remove("dragging"),t.currentNote&&(t.currentNote.domElement.style.pointerEvents="auto"),t.currentNote=null})),this.update()}return t.prototype.update=function(){this.notes.forEach((function(t){return t.update()}))},t.prototype.add=function(t){this.notes.push(t),this.gridElement.appendChild(t.domElement)},t.prototype.remove=function(t){this.notes=this.notes.filter((function(e){return e!==t})),this.gridElement.removeChild(t.domElement)},t.prototype.load=function(t){var e=this,n=new a;"title"in t&&(n.title=t.title),"description"in t&&(n.description=t.description),"tempo"in t&&(n.tempo=t.tempo),"events"in t&&(n.events=t.events.map((function(t){return new u(e,t)})))},t.prototype.download=function(){var t=new a;t.events=this.notes;var e=JSON.stringify(t),n=new Blob([e],{type:"application/json"}),o=URL.createObjectURL(n),i=document.createElement("a");return i.href=o,i.download="composition.json",i.click(),URL.revokeObjectURL(o),t},t}(),p=function(){function t(){this.keys=[],this.noteHeight=20,this.domElement=document.createElement("div"),this.domElement.classList.add("piano-roll-keyboard"),this.redraw()}return t.prototype.redraw=function(){this.domElement.innerHTML="";for(var t=87;t>=0;t--){var e=document.createElement("div");e.classList.add("piano-roll-keyboard-key"),e.style.height="".concat(this.noteHeight,"px"),e.style.backgroundColor="white"===i[t%12]?"#fff":"#000",e.style.color="white"===i[t%12]?"#000":"#fff",e.textContent=r[t%12]+(t/12|0).toString(),this.domElement.appendChild(e)}},t}(),m=function(){function t(t){var e=this;this.clock=t,this.cursorUpdateInterval=null,this.scheduledSources=[],this.domElement=document.createElement("div"),this.domElement.classList.add("piano-roll"),this.sideKeyboard=new p,this.domElement.appendChild(this.sideKeyboard.domElement),this.grid=new h,this.domElement.appendChild(this.grid.domElement),this.cursor=document.createElement("div"),this.cursor.classList.add("piano-roll-cursor"),this.grid.domElement.appendChild(this.cursor),t.on("start",(function(){var t;e.cursorUpdateInterval&&clearInterval(e.cursorUpdateInterval),e.cursor.style.transform="translateX(0)",e.cursor.style.display="block",null===(t=e.cursor.parentElement)||void 0===t||t.appendChild(e.cursor),e.scheduleAudioEvents()})),t.on("render",(function(){e.updateCursor()})),t.on("stop",(function(){e.cursor.style.display="none",e.scheduledSources.forEach((function(t){return t.stop()})),e.scheduledSources=[]}))}return t.prototype.updateCursor=function(){this.clock.isPlaying&&(this.cursor.style.transform="translateX(".concat(this.clock.currentBeat*this.grid.beatWidth,"px)"))},t.prototype.scheduleAudioEvents=function(){var t=this,e=n();this.grid.notes.forEach((function(n){var o=e.createBufferSource();o.buffer=n.audio,o.connect(e.destination),o.start(e.currentTime+60*n.start/t.clock.bpm),t.scheduledSources.push(o)}))},t}();const f=function(){function t(){this._events={},this._onceEvents={}}return t.prototype.on=function(t,e){return this._events[t]||(this._events[t]=[]),this._events[t].push(e),this},t.prototype.once=function(t,e){return this._onceEvents[t]||(this._onceEvents[t]=[]),this._onceEvents[t].push(e),this},t.prototype.fireEvent=function(t,e){var n=this._onceEvents[t];if(n){for(var o=0,i=n;o<i.length;o++){var r=i[o];try{r(e)}catch(e){console.error("Error executing .once callback for event: ".concat(t),e)}}this._onceEvents[t]=void 0}var a=this._events[t];if(a)for(var s=0,l=a;s<l.length;s++){r=l[s];try{r(e)}catch(e){console.error("Error executing .on callback for event: ".concat(t),e)}}},t}();var v=function(){var t=function(e,n){return t=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&(t[n]=e[n])},t(e,n)};return function(e,n){if("function"!=typeof n&&null!==n)throw new TypeError("Class extends value "+String(n)+" is not a constructor or null");function o(){this.constructor=e}t(e,n),e.prototype=null===n?Object.create(n):(o.prototype=n.prototype,new o)}}(),y=new(function(t){function e(){var e=t.call(this)||this;return e._isPlaying=!1,e._bpm=100,e.intervalId=null,e.startTime=null,e.domElement=document.createElement("div"),e.domElement.classList.add("audio-clock"),e.bpmInput=document.createElement("input"),e.bpmInput.classList.add("audio-clock-bpm"),e.bpmInput.type="number",e.bpmInput.value="120",e.bpmInput.addEventListener("input",(function(){e._bpm=parseFloat(e.bpmInput.value)})),e.domElement.appendChild(e.bpmInput),e.playPauseButton=document.createElement("button"),e.playPauseButton.classList.add("audio-clock-play-pause"),e.playPauseButton.textContent="Play",e.playPauseButton.addEventListener("click",(function(){e._isPlaying?e.stop():(n(),e.play())})),e.domElement.appendChild(e.playPauseButton),e.stopButton=document.createElement("button"),e.stopButton.classList.add("audio-clock-stop"),e.stopButton.textContent="Stop",e.stopButton.addEventListener("click",(function(){e.stop()})),e.domElement.appendChild(e.stopButton),e.currentTimeDisplay=document.createElement("span"),e.currentTimeDisplay.classList.add("audio-clock-time"),e.currentTimeDisplay.textContent="01:01",e.domElement.appendChild(e.currentTimeDisplay),e}return v(e,t),Object.defineProperty(e.prototype,"currentBeat",{get:function(){return(null!==this.startTime?n().currentTime-this.startTime:0)*(this._bpm/60)},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"isPlaying",{get:function(){return this._isPlaying},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"bpm",{get:function(){return this._bpm},enumerable:!1,configurable:!0}),e.prototype.start=function(){var t=this;this.fireEvent("start"),this.startTime=n().currentTime,console.log("Started at",this.startTime),this.intervalId=setInterval((function(){t.updateCurrentTimeDisplay(t.currentBeat)}),250),requestAnimationFrame(this.render.bind(this))},e.prototype.render=function(){this.fireEvent("render"),this._isPlaying&&requestAnimationFrame(this.render.bind(this))},e.prototype.stop=function(){this.fireEvent("stop"),this.intervalId&&clearInterval(this.intervalId),this._isPlaying=!1,this.intervalId=null,this.startTime=null,this.updateCurrentTimeDisplay(this.currentBeat),this.playPauseButton.textContent="Play"},e.prototype.play=function(){this._isPlaying?this.stop():this.start(),this._isPlaying=!this._isPlaying,this.playPauseButton.textContent=this._isPlaying?"Pause":"Play"},e.prototype.updateCurrentTimeDisplay=function(t){var e=Math.floor(t/4)+1,n=Math.floor(t%4)+1,o="".concat(e.toString().padStart(2,"0"),":").concat(n.toString().padStart(2,"0"));this.currentTimeDisplay.textContent=o},e}(f)),E=new m(y),g=document.createElement("div");g.style.width="100%",g.style.height="100%",document.body.appendChild(g),g.appendChild(y.domElement),g.appendChild(E.domElement),monofy=t})();
//# sourceMappingURL=monofy-studio.js.map