'use strict';
// The supplied NASA scene is the default. A bundled still scene works offline.
(()=>{const toggle=document.getElementById('scene-toggle');let still=false;try{still=localStorage.getItem('luna-scene')==='still';}catch(_){}function render(){document.body.classList.toggle('still-scene',still);toggle.textContent=still?'Live scene':'Still scene';toggle.setAttribute('aria-pressed',String(still));}toggle.onclick=()=>{still=!still;try{localStorage.setItem('luna-scene',still?'still':'live');}catch(_){}render();};render();})();
