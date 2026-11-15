const assert=require('node:assert/strict');
const F=require('../../frontend/js/flight-core.js');
const near=(a,b,e=1e-7)=>assert.ok(Math.abs(a-b)<=e,`${a} != ${b}`);
// Real spherical motion crosses the date line, poles, and circles the whole Moon.
near(F.distance({lat:0,lon:0},{lat:0,lon:90}),Math.PI*F.R/2,.001);
let p=F.destination({lat:0,lon:179},90,Math.PI*F.R/90);near(p.lat,0);near(p.lon,-179);
p=F.destination({lat:89,lon:0},0,Math.PI*F.R/90);near(p.lat,89);near(Math.abs(p.lon),180);
p=F.destination({lat:0,lon:0},90,2*Math.PI*F.R);near(p.lat,0);near(p.lon,0);
// A fast frame crossing a beacon must not tunnel through it.
assert.ok(F.sweptDistance({lat:0,lon:-1},{lat:0,lon:1},{lat:0,lon:0})<.001);
const target={id:'beacon',name:'Beacon',lat:0,lon:0};
let g=new F.Flight({lat:0,lon:-.2},[target]);g.state.heading=90;g.state.altitude=5000;g.state.speed=180000;g.state.throttle=1;g.update(.1,{boost:true});assert.equal(g.state.mode,'landing');
for(let i=0;i<40;i++)g.update(.1,{});assert.equal(g.state.mode,'landed');near(g.state.lat,0);near(g.state.lon,0);near(g.state.altitude,0);
assert.equal(g.takeoff(),true);for(let i=0;i<31;i++)g.update(.1,{});assert.equal(g.state.mode,'flying');assert.ok(g.state.altitude>12000);
// Passing above the capture volume must keep flying.
g=new F.Flight({lat:0,lon:-.2},[target]);Object.assign(g.state,{heading:90,altitude:50000,speed:180000,throttle:1});g.update(.1,{boost:true});assert.equal(g.state.mode,'flying');
// Autopilot genuinely traverses to a different site, then automatically lands.
g=new F.Flight({lat:0,lon:23},[{id:'destination',name:'Destination',lat:-69.373,lon:32.319}]);g.setTarget('destination');assert.equal(g.startAutopilot(),true);let moved=false;for(let i=0;i<4000&&g.state.mode!=='landed';i++){g.update(.1,{});moved=moved||Math.abs(g.state.lat)>.1;}assert.ok(moved);assert.equal(g.state.mode,'landed');near(g.state.lat,-69.373);near(g.state.lon,32.319);
// Manual controls cancel autopilot and the brake produces a stable hover.
g.takeoff();for(let i=0;i<31;i++)g.update(.1,{});g.startAutopilot();g.update(.1,{turn:1});assert.equal(g.autopilot,false);g.state.speed=1000;g.update(.1,{brake:true});assert.equal(g.state.speed,0);
console.log('Flight math, swept beacon contact, assisted landing, lift-off, autopilot and braking passed.');

// Leaving a recently landed beacon for a nearby site must not recapture the origin.
{const start={id:'origin',lat:-89.67,lon:129.78},target={id:'ridge',lat:-89.489,lon:-137.8675},g=new F.Flight(start,[start,target]);g.land(start);for(let i=0;i<40;i++)g.update(.1);assert.equal(g.state.mode,'landed');g.takeoff();for(let i=0;i<40;i++)g.update(.1);g.setTarget('ridge');g.startAutopilot();for(let i=0;i<3000&&g.state.mode!=='landed';i++)g.update(.1);assert.equal(g.state.mode,'landed');assert.equal(g.lastLanding.id,'ridge');}
