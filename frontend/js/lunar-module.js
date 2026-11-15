// Detailed Apollo-style lunar module adapted from the user-supplied Lunar Module 3D.html.
// Illustrative exploration hardware; not a reconstruction of each mission's lander.
window.createLunarModule=function(THREE){
var seed=7;function rnd(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
var V=(x,y,z)=>new THREE.Vector3(x,y,z);
/* textures for the lander */
function tex(w,h,fn){var c=document.createElement('canvas');c.width=w;c.height=h;fn(c.getContext('2d'));return new THREE.CanvasTexture(c)}
var foil=tex(256,256,function(x){x.fillStyle='#808080';x.fillRect(0,0,256,256);for(var i=0;i<260;i++){x.strokeStyle='hsl(0,0%,'+(30+rnd()*60)+'%)';x.lineWidth=1+rnd()*2;x.beginPath();var a=rnd()*256,b=rnd()*256;x.moveTo(a,b);x.lineTo(a+(rnd()-.5)*60,b+(rnd()-.5)*60);x.stroke()}});
foil.wrapS=foil.wrapT=THREE.RepeatWrapping;foil.repeat.set(2,1);
var flagT=tex(128,80,function(x){for(var i=0;i<13;i++){x.fillStyle=i%2?'#f4f4f4':'#b22234';x.fillRect(0,i*80/13,128,80/13+1)}x.fillStyle='#3c3b6e';x.fillRect(0,0,56,43)});
var usaT=tex(256,128,function(x){x.fillStyle='#f2f2ee';x.fillRect(0,0,256,128);x.fillStyle='#222';x.font='bold 84px Arial,sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText('USA',128,68)});
var gold=new THREE.MeshStandardMaterial({color:0xc8a02a,metalness:.85,roughness:.38,bumpMap:foil,bumpScale:.028});
var silver=new THREE.MeshStandardMaterial({color:0xaeb2b6,metalness:.7,roughness:.45,bumpMap:foil,bumpScale:.015});
var dark=new THREE.MeshStandardMaterial({color:0x1b1b1d,metalness:.3,roughness:.7});
var steel=new THREE.MeshStandardMaterial({color:0x8d9094,metalness:.8,roughness:.4});
var glass=new THREE.MeshStandardMaterial({color:0x5a6bd0,emissive:0x2a3a9a,emissiveIntensity:.8,roughness:.2});

var lm=new THREE.Group();
function add(mesh,parent){mesh.castShadow=true;mesh.receiveShadow=true;(parent||lm).add(mesh);return mesh}
function strut(a,b,r,m){var d=b.clone().sub(a),s=new THREE.Mesh(new THREE.CylinderGeometry(r,r,d.length(),6),m||steel);
s.position.copy(a).addScaledVector(d,.5);s.quaternion.setFromUnitVectors(V(0,1,0),d.normalize());return add(s)}

/* descent stage */
var ds=add(new THREE.Mesh(new THREE.CylinderGeometry(1.9,1.9,1.3,8),gold));ds.position.y=2.2;ds.rotation.y=Math.PI/8;
var top=add(new THREE.Mesh(new THREE.CylinderGeometry(1.95,1.95,.12,8),silver));top.position.y=2.9;top.rotation.y=Math.PI/8;
for(var k=0;k<4;k++){var a=Math.PI/4+k*Math.PI/2;
var pn=add(new THREE.Mesh(new THREE.BoxGeometry(1.25,.95,.06),dark));pn.position.set(Math.sin(a)*1.78,2.2,Math.cos(a)*1.78);pn.rotation.y=a}
var bay=add(new THREE.Mesh(new THREE.BoxGeometry(.3,1.05,.95),silver));bay.position.set(1.9,2.15,0);
var bd=add(new THREE.Mesh(new THREE.BoxGeometry(.05,.5,.5),dark));bd.position.set(2.07,2.15,.05);
var tank=add(new THREE.Mesh(new THREE.CylinderGeometry(.16,.16,.5,12),steel));tank.position.set(2.0,2.05,-.6);
var eng=add(new THREE.Mesh(new THREE.CylinderGeometry(.3,.75,.8,16,1,true),dark));eng.position.y=1.15;eng.material=new THREE.MeshStandardMaterial({color:0x222224,side:THREE.DoubleSide,roughness:.6});
var fl=new THREE.Mesh(new THREE.PlaneGeometry(.62,.4),new THREE.MeshStandardMaterial({map:flagT,roughness:.8}));fl.position.set(-.85,2.35,1.78);lm.add(fl);
var us=new THREE.Mesh(new THREE.PlaneGeometry(.78,.39),new THREE.MeshStandardMaterial({map:usaT,roughness:.8}));us.position.set(-.15,2.3,1.79);lm.add(us);

/* ascent stage */
var as=new THREE.Group();as.position.y=3.5;lm.add(as);
var ab=add(new THREE.Mesh(new THREE.CylinderGeometry(1.4,1.65,1.5,8),silver),as);ab.rotation.y=Math.PI/8;
var band=add(new THREE.Mesh(new THREE.CylinderGeometry(1.42,1.42,.3,8),dark),as);band.rotation.y=Math.PI/8;band.position.y=.2;
var fb=add(new THREE.Mesh(new THREE.BoxGeometry(1.4,1.25,.9),silver),as);fb.position.set(0,.05,1.35);
var hatch=add(new THREE.Mesh(new THREE.BoxGeometry(.72,.85,.06),dark),as);hatch.position.set(0,-.12,1.82);
var porch=add(new THREE.Mesh(new THREE.BoxGeometry(.9,.06,.4),steel),as);porch.position.set(0,-.62,2.05);
var wg=new THREE.Shape();wg.moveTo(-.3,.28);wg.lineTo(.3,.28);wg.lineTo(0,-.3);wg.closePath();
[-.72,.72].forEach(function(wx){var w=new THREE.Mesh(new THREE.ShapeGeometry(wg),glass);w.position.set(wx,.42,1.81);as.add(w)});
var roof=add(new THREE.Mesh(new THREE.BoxGeometry(1.9,.14,1.9),silver),as);roof.position.y=.82;roof.rotation.y=Math.PI/8;
var stick=add(new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,.7,6),steel),as);stick.position.y=1.2;
var dish=add(new THREE.Mesh(new THREE.SphereGeometry(.55,24,8,0,6.283,0,Math.PI/2),steel),as);dish.material=new THREE.MeshStandardMaterial({color:0xd6d8da,metalness:.6,roughness:.35,side:THREE.DoubleSide});
dish.scale.y=.45;dish.position.y=1.62;dish.rotation.x=-.35;
var arm=add(new THREE.Mesh(new THREE.CylinderGeometry(.03,.03,1.3,6),steel),as);arm.position.set(-1.45,1.15,.8);arm.rotation.z=.15;
var d2=add(new THREE.Mesh(new THREE.SphereGeometry(.28,16,6,0,6.283,0,Math.PI/2),dish.material),as);d2.scale.y=.5;d2.position.set(-1.55,1.8,.8);d2.rotation.set(.9,.6,0);
for(var q=0;q<4;q++){var a=Math.PI/4+q*Math.PI/2+Math.PI/4,qx=Math.sin(a)*1.75,qz=Math.cos(a)*1.75;
var qb=add(new THREE.Mesh(new THREE.BoxGeometry(.3,.3,.3),dark),as);qb.position.set(qx,-.1,qz);qb.rotation.y=a;
for(var s=-1;s<=1;s+=2){var th=add(new THREE.Mesh(new THREE.CylinderGeometry(.04,.09,.28,8),steel),as);th.position.set(qx+Math.sin(a+s*1.57)*.2,-.1,qz+Math.cos(a+s*1.57)*.2);th.rotation.set(Math.cos(a+s*1.57)*1.57,0,-Math.sin(a+s*1.57)*1.57)}}

/* legs */
var Ps=[],Bs=[];
for(var l=0;l<4;l++){var a=l*Math.PI/2,dx=Math.sin(a),dz=Math.cos(a);
var T=V(1.7*dx,2.85,1.7*dz),F=V(4.4*dx,.16,4.4*dz),P=T.clone().lerp(F,.55),B=V(1.65*dx,1.75,1.65*dz);
Ps.push(P);Bs.push(B);
strut(T,F,.09,silver);strut(B,P,.06,steel);
var pad=add(new THREE.Mesh(new THREE.CylinderGeometry(.55,.68,.1,24),gold));pad.position.set(F.x,.07,F.z);
var cap=add(new THREE.Mesh(new THREE.SphereGeometry(.14,10,8),steel));cap.position.copy(F).y+=.1;
if(l===0){ /* ladder on the front leg */
[-.2,.2].forEach(function(o){strut(V(o,2.75,1.9),V(o,.4,4.2),.035,steel)});
for(var r=0;r<9;r++){var u=.04+r*.115,pt=V(0,2.75,1.9).lerp(V(0,.4,4.2),u);var rung=add(new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,.44,6),steel));rung.position.copy(pt);rung.rotation.z=Math.PI/2}}}
for(var l=0;l<4;l++){var n=(l+1)%4,a1=l*Math.PI/2+Math.PI/4;
var cx=V(1.8*Math.sin(a1),1.7,1.8*Math.cos(a1));strut(Ps[l],cx,.045,steel);strut(Ps[n],cx,.045,steel)}

lm.position.y=0;
return lm;
};
