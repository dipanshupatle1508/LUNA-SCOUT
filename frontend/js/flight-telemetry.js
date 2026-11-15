'use strict';
window.FlightTelemetry=class{
 constructor(){this.busy=false;this.lastRequest=-Infinity;this.last=null;this.failed=false;this.$=id=>document.getElementById(id);}
 update(now,state,time){
  if(this.last){const moved=LunarFlight.distance(state,this.last),dated=Math.abs(time-Date.parse(this.last.t))/1000,stale=moved>3000||dated>120||Math.abs(state.altitude-this.last.altitude_m)>1000;this.$('telemetry-live').textContent=stale?'UPDATING':'LIVE';this.$('telemetry-live').classList.toggle('pending',stale);}
  if(this.busy||now-this.lastRequest<(this.failed?5000:1500))return;
  this.busy=true;this.lastRequest=now;const query=new URLSearchParams({lat:state.lat.toFixed(6),lon:state.lon.toFixed(6),altitude:Math.max(0,state.altitude).toFixed(1),at:new Date(time).toISOString()});
  fetch('/api/flight-status?'+query).then(async r=>{const d=await r.json();if(!r.ok)throw Error(d.detail||'Visibility unavailable');return d;}).then(d=>{
    this.last=d;this.failed=false;const angle=v=>(v>=0?'+':'')+v.toFixed(1)+'°';
    this.$('sun-angle').textContent=angle(d.sun.el)+' el · '+d.sun.az.toFixed(0)+'° az';
    this.$('illumination').textContent=d.sun.status;this.$('illumination').dataset.state=d.sun.status==='SHADOWED'?'bad':'good';
    this.$('sun-fraction').textContent=(100*d.sun.fraction).toFixed(0)+'% of Sun visible';
    this.$('earth-angle').textContent=angle(d.earth.el)+' el · '+d.earth.az.toFixed(0)+'° az';
    this.$('direct-earth').textContent=d.earth.status;this.$('direct-earth').dataset.state=d.earth.status==='CLEAR'?'good':'bad';
    this.$('earth-phase').textContent=(100*d.earth.phase).toFixed(0)+'% lit';
    this.$('telemetry-note').textContent='LOLA '+Math.round(d.resolution_m)+' m · '+(d.altitude_m<1?'2 m landed reference':'spacecraft altitude')+' · full Earth disk criterion';
    this.$('telemetry-sample').textContent=d.t.slice(11,19)+' UTC · '+d.lat.toFixed(3)+'°, '+d.lon.toFixed(3)+'°';
    this.$('telemetry-error').textContent='';
  }).catch(e=>{this.failed=true;this.$('telemetry-live').textContent='UNAVAILABLE';this.$('telemetry-error').textContent=e.message;for(const id of ['illumination','direct-earth']){this.$(id).textContent='—';this.$(id).dataset.state='unknown';}}).finally(()=>this.busy=false);
 }
};
