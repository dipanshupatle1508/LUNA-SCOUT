/* Deterministic arcade flight over a spherical Moon. SI units; no renderer required. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.LunarFlight=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';const R=1737400,D=Math.PI/180,clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),wrap=x=>((x+180)%360+360)%360-180;
 const xyz=(lat,lon)=>[Math.cos(lat*D)*Math.cos(lon*D),Math.sin(lat*D),-Math.cos(lat*D)*Math.sin(lon*D)];
 const ll=v=>{const n=Math.hypot(...v);return{lat:Math.asin(clamp(v[1]/n,-1,1))/D,lon:wrap(Math.atan2(-v[2],v[0])/D)};};
 function distance(a,b){const la=a.lat*D,lb=b.lat*D,dl=(b.lon-a.lon)*D,q=Math.sin((lb-la)/2)**2+Math.cos(la)*Math.cos(lb)*Math.sin(dl/2)**2;return 2*R*Math.atan2(Math.sqrt(clamp(q,0,1)),Math.sqrt(clamp(1-q,0,1)));}
 function bearing(a,b){const la=a.lat*D,lb=b.lat*D,dl=(b.lon-a.lon)*D;return(Math.atan2(Math.sin(dl)*Math.cos(lb),Math.cos(la)*Math.sin(lb)-Math.sin(la)*Math.cos(lb)*Math.cos(dl))/D+360)%360;}
 function destination(a,heading,metres){const la=a.lat*D,lo=a.lon*D,h=heading*D,d=metres/R;const lat=Math.asin(clamp(Math.sin(la)*Math.cos(d)+Math.cos(la)*Math.sin(d)*Math.cos(h),-1,1)),lon=lo+Math.atan2(Math.sin(h)*Math.sin(d)*Math.cos(la),Math.cos(d)-Math.sin(la)*Math.sin(lat));return{lat:lat/D,lon:wrap(lon/D)};}
 function interpolate(a,b,f){const u=xyz(a.lat,a.lon),v=xyz(b.lat,b.lon),angle=Math.acos(clamp(u.reduce((s,x,i)=>s+x*v[i],0),-1,1));if(angle<1e-9)return{lat:a.lat,lon:a.lon};if(Math.PI-angle<1e-6)return destination(a,bearing(a,b),distance(a,b)*f);const sa=Math.sin((1-f)*angle)/Math.sin(angle),sb=Math.sin(f*angle)/Math.sin(angle);return ll(u.map((x,i)=>x*sa+v[i]*sb));}
 // Swept contact avoids flying through a beacon during a boosted frame.
 function sweptDistance(a,b,target){const u=xyz(a.lat,a.lon),v=xyz(b.lat,b.lon),p=xyz(target.lat,target.lon),delta=v.map((x,i)=>x-u[i]),den=delta.reduce((s,x)=>s+x*x,0);const f=den?clamp(delta.reduce((s,x,i)=>s+(p[i]-u[i])*x,0)/den,0,1):0;return distance(ll(u.map((x,i)=>x+delta[i]*f)),target);}
 class Flight{
  constructor(start,beacons){this.state={lat:start.lat,lon:wrap(start.lon),heading:0,altitude:60000,speed:0,throttle:0,mode:'flying'};this.beacons=beacons;this.target=null;this.autopilot=false;this.elapsed=0;this.lastLanding=null;this.transition=null;this.departureSite=null;}
  setTarget(id){this.target=this.beacons.find(b=>b.id===id)||null;}
  startAutopilot(){if(!this.target||this.state.mode!=='flying')return false;this.autopilot=true;if(this.departureSite?.id===this.target.id)this.departureSite=null;return true;}
  brake(){this.autopilot=false;this.state.throttle=0;this.state.speed=0;}
  land(site){if(this.state.mode!=='flying')return;this.transition={from:{...this.state},site,elapsed:0};this.state.mode='landing';this.state.speed=this.state.throttle=0;this.autopilot=false;}
  takeoff(){if(this.state.mode!=='landed')return false;this.state.mode='takingoff';this.departureSite=this.lastLanding;this.transition={elapsed:0,site:this.lastLanding};this.autopilot=false;return true;}
  update(dt,input={}){dt=clamp(dt,0,.1);const s=this.state;this.elapsed+=dt;
   if(s.mode==='landing'){const t=this.transition;t.elapsed+=dt;let f=clamp(t.elapsed/3.5,0,1);f=f*f*(3-2*f);Object.assign(s,interpolate(t.from,t.site,f));s.altitude=t.from.altitude*(1-f);if(t.elapsed>=3.5){s.lat=t.site.lat;s.lon=wrap(t.site.lon);s.altitude=0;s.mode='landed';this.lastLanding=t.site;this.transition=null;}return s;}
   if(s.mode==='takingoff'){this.transition.elapsed+=dt;const f=clamp(this.transition.elapsed/3,0,1);s.altitude=30000*f*f*(3-2*f);if(f===1){s.mode='flying';this.transition=null;}return s;}
   if(s.mode==='landed')return s;
   const old={lat:s.lat,lon:s.lon,altitude:s.altitude};
   if(input.brake){this.brake();return s;}
   const manual=(input.turn||input.throttle||input.vertical);if(manual)this.autopilot=false;
   if(this.autopilot&&this.target){const d=distance(s,this.target);if(d>.1)s.heading=bearing(s,this.target);const desired=d>250000?180000:d>60000?30000:d>12000?2400:500;s.speed=Math.min(desired,d/Math.max(dt,.001));s.throttle=desired/180000;const alt=d>200000?60000:Math.max(800,d*.27);s.altitude+=clamp(alt-s.altitude,-18000*dt,18000*dt);}
   else{s.heading=(s.heading+(input.turn||0)*60*dt+360)%360;s.throttle=clamp(s.throttle+(input.throttle||0)*.42*dt,0,1);const max=input.boost?180000:6000,desired=max*s.throttle;s.speed+=(desired-s.speed)*Math.min(1,dt*2.5);s.altitude=clamp(s.altitude+(input.vertical||0)*7000*dt*(input.boost?4:1),800,800000);}
   if(s.speed>.001){const next=destination(s,s.heading,s.speed*dt);s.heading=(bearing(next,s)+180)%360;Object.assign(s,next);}
   if(this.departureSite&&distance(s,this.departureSite)>6000)this.departureSite=null;let hit=null,best=Infinity;if(Math.min(old.altitude,s.altitude)<=12000){for(const b of this.beacons){if(b.id===this.departureSite?.id)continue;const d=sweptDistance(old,s,b);if(d<=3000&&d<best){hit=b;best=d;}}}if(hit)this.land(hit);
   return s;
  }
 }
 return{R,xyz,ll,wrap,distance,bearing,destination,interpolate,sweptDistance,Flight};
});
