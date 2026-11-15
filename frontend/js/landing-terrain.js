'use strict';
// Surveyed LOLA relief + explicitly decorative, reproducible close-range detail.
window.createLandingTerrain=function(THREE,data,seed=71,cpu=false){
 const group=new THREE.Group(),R=LunarFlight.R;let value=seed>>>0,disposed=false;
 const random=()=>{value=(1664525*value+1013904223)>>>0;return value/4294967296;};
 const height=(grid,x,z)=>{const n=grid.size,c=Math.max(0,Math.min(n-1,(x/grid.extent_m+1)*.5*(n-1))),r=Math.max(0,Math.min(n-1,(z/grid.extent_m+1)*.5*(n-1))),i=Math.floor(c),j=Math.floor(r),u=c-i,v=r-j,a=grid.height_m,i1=Math.min(n-1,i+1),j1=Math.min(n-1,j+1);return(1-v)*((1-u)*a[j*n+i]+u*a[j*n+i1])+v*((1-u)*a[j1*n+i]+u*a[j1*n+i1]);};
 const base=(x,z)=>height(data.near,x,z)-data.ground_m-(x*x+z*z)/(2*R);
 const craters=Array.from({length:22},()=>{const a=random()*Math.PI*2,d=14+random()*95;return{x:Math.cos(a)*d,z:Math.sin(a)*d,r:1+random()*3.4};});
 function detail(x,z){const d=Math.hypot(x,z),clear=Math.min(1,Math.max(0,(d-7)/7)),edge=Math.min(1,Math.max(0,(128-d)/22));let h=.065*Math.sin(x*1.7+Math.sin(z*2.3))*.65+.035*Math.sin(x*4.3-z*3.7);for(const c of craters){const r=Math.hypot(x-c.x,z-c.z)/c.r;if(r<1.5)h+=c.r*(-.14*Math.exp(-r*r*3.4)+.055*Math.exp(-(((r-.95)/.18)**2)));}return h*clear*edge;}
 function terrain(grid,segments,extent,withDetail){const g=new THREE.PlaneGeometry(extent*2,extent*2,segments,segments);g.rotateX(-Math.PI/2);const p=g.attributes.position,color=new Float32Array(p.count*3),uv=g.attributes.uv;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i),h=height(grid,x,z)-data.ground_m-(x*x+z*z)/(2*R);p.setY(i,h+(withDetail?detail(x,z)+.035:0));const q=.42+.035*Math.sin(x*.031)*Math.cos(z*.037);color.set([q,q*.985,q*.965],i*3);uv.setXY(i,x/8,z/8);}g.setAttribute('color',new THREE.BufferAttribute(color,3));g.computeVertexNormals();const mat=new THREE.MeshStandardMaterial({color:0xb6b5b2,vertexColors:true,roughness:1,polygonOffset:withDetail,polygonOffsetFactor:withDetail?-1:0});const mesh=new THREE.Mesh(g,mat);mesh.receiveShadow=true;group.add(mesh);return mesh;}
 const far=terrain(data.far,cpu?40:128,data.far.extent_m,false),near=terrain(data.near,cpu?32:256,data.near.extent_m,false),patch=terrain(data.near,cpu?40:192,128,true);
 // Real elevation surfaces overlap. Hide far centre to prevent coarser triangles covering near terrain.
 for(const mesh of [far,near]){const cut=mesh===far?data.near.extent_m*.94:116,g=mesh.geometry,idx=g.index,p=g.attributes.position,keep=[];for(let i=0;i<idx.count;i+=3){const ids=[idx.getX(i),idx.getX(i+1),idx.getX(i+2)];if(!ids.every(j=>Math.abs(p.getX(j))<cut&&Math.abs(p.getZ(j))<cut))keep.push(...ids);}g.setIndex(keep);mesh.userData.cpuRespectIndex=true;}
 patch.userData.cpuRespectIndex=true;patch.userData.photoSurface=near.userData.photoSurface=true;
 const textureReady=new Promise(resolve=>new THREE.TextureLoader().load('assets/apollo11-undisturbed-soil.png',source=>{
   if(disposed){source.dispose();resolve(false);return;}
   // Mirror a centre crop to hide repeat seams; monochrome tones reduce baked photographic light.
   const tile=document.createElement('canvas');tile.width=tile.height=512;const ctx=tile.getContext('2d'),im=source.image;
   for(let y=0;y<2;y++)for(let x=0;x<2;x++){ctx.save();ctx.translate(x?512:0,y?512:0);ctx.scale(x?-1:1,y?-1:1);ctx.drawImage(im,im.width*.19,im.height*.19,im.width*.6,im.height*.6,0,0,256,256);ctx.restore();}
   const pixels=ctx.getImageData(0,0,512,512);for(let i=0;i<pixels.data.length;i+=4){const v=.2126*pixels.data[i]+.7152*pixels.data[i+1]+.0722*pixels.data[i+2],q=Math.max(38,Math.min(200,120+(v-115)*.55));pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=q;}ctx.putImageData(pixels,0,0);
   const map=new THREE.CanvasTexture(tile);map.wrapS=map.wrapT=THREE.RepeatWrapping;map.encoding=THREE.sRGBEncoding;map.anisotropy=4;const bump=map.clone();bump.encoding=THREE.LinearEncoding;bump.needsUpdate=true;
   for(const mesh of [patch,near]){mesh.material.map=map;mesh.material.bumpMap=bump;mesh.material.bumpScale=mesh===patch?.055:.025;mesh.material.color.setHex(0xbdbbb7);mesh.material.vertexColors=false;mesh.material.needsUpdate=true;}
   source.dispose();resolve(true);
 },undefined,()=>resolve(false)));
 const rockMaterial=new THREE.MeshStandardMaterial({color:0x696865,roughness:.98,flatShading:true});
 for(let i=0;i<180;i++){const a=random()*Math.PI*2,d=9+Math.pow(random(),.65)*110,x=Math.cos(a)*d,z=Math.sin(a)*d,size=.035+Math.pow(random(),3)*.62,g=new THREE.IcosahedronGeometry(1,i<30?1:0),p=g.attributes.position;for(let j=0;j<p.count;j++){const scale=.82+random()*.3;p.setXYZ(j,p.getX(j)*scale,p.getY(j)*scale,p.getZ(j)*scale);}g.computeVertexNormals();const rock=new THREE.Mesh(g,rockMaterial);rock.scale.set(size*(.8+random()*.6),size*(.45+random()*.5),size*(.8+random()*.6));rock.position.set(x,base(x,z)+detail(x,z)+size*.24,z);rock.rotation.set(random(),random()*Math.PI*2,random()*.4);rock.castShadow=rock.receiveShadow=true;rock.userData.decorative=true;group.add(rock);}
 group.userData.textureReady=textureReady;group.userData.height=base;
 group.userData.dispose=()=>{disposed=true;const geometries=new Set(),materials=new Set(),textures=new Set();group.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)materials.add(o.material);});materials.forEach(m=>{if(m.map)textures.add(m.map);if(m.bumpMap)textures.add(m.bumpMap);m.dispose();});geometries.forEach(g=>g.dispose());textures.forEach(t=>t.dispose());};
 return group;
};
