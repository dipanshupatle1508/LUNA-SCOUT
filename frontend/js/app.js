'use strict';
const chips=document.getElementById('chips');
fetch('/api/sites').then(r=>{if(!r.ok)throw new Error('Sites unavailable');return r.json();}).then(sites=>{
 for(const site of sites){const a=document.createElement('a');a.className='chip glass '+site.status;a.href='mission.html#'+new URLSearchParams({site:site.id});a.textContent=site.name;a.title=site.note;chips.append(a);}
}).catch(()=>{const a=document.createElement('a');a.className='chip glass';a.href='mission.html';a.textContent='Open mission planner';chips.append(a);});
