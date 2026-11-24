const API = (localStorage.getItem("seekhtoon_api") || "http://127.0.0.1:8000").replace(/\/$/,"");
const $ = id => document.getElementById(id);
function showPage(name){
 document.querySelectorAll(".page").forEach(p=>p.classList.remove("show"));
 document.querySelectorAll(".nav").forEach(b=>b.classList.toggle("active",b.dataset.page===name));
 $(name).classList.add("show");
 $("heading").textContent=({dashboard:"Dashboard",story:"Story Generator",voice:"Voice Studio",image:"Image Generator",editor:"Photo Editor",characters:"Character Studio",video:"Video Generator"})[name];
 if(name==="characters") loadCharacters();
}
document.querySelectorAll(".nav").forEach(b=>b.addEventListener("click",()=>showPage(b.dataset.page)));
async function api(path, options={}) {
 const res=await fetch(API+path,options);
 const data=await res.json().catch(()=>({detail:"Unexpected server response"}));
 if(!res.ok) throw new Error(data.detail||"Request failed");
 return data;
}
function errorBox(id,e){$(id).textContent="Error: "+e.message}
$("storyBtn").onclick=async()=>{
 $("storyResult").textContent="Generating story...";
 try{const d=await api("/api/story",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({topic:$("topic").value,age_group:$("age").value,moral:$("moral").value})});$("storyResult").textContent=d.story||"No story returned."}
 catch(e){errorBox("storyResult",e)}
};
$("voiceBtn").onclick=async()=>{
 $("voiceResult").textContent="Generating audio...";
 try{const d=await api("/api/voice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:$("voiceText").value})});$("voiceResult").innerHTML=`<audio controls src="${API+d.audio_url}"></audio><p><a href="${API+d.audio_url}" download>Download WAV</a></p>`}
 catch(e){errorBox("voiceResult",e)}
};
$("imageBtn").onclick=async()=>{
 $("imageResult").textContent="Generating image...";
 try{const d=await api("/api/image/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:$("imagePrompt").value})});$("imageResult").innerHTML=`<img src="${API+d.image_url}" alt="Generated cartoon"><p><a href="${API+d.image_url}" download>Download image</a></p>`}
 catch(e){errorBox("imageResult",e)}
};
$("photo").onchange=async e=>{
 const file=e.target.files[0];if(!file)return;
 $("photoResult").textContent="Uploading...";
 try{const fd=new FormData();fd.append("file",file);const d=await api("/api/upload",{method:"POST",body:fd});$("photoResult").innerHTML=`<p>${d.message}</p><img src="${API+d.url}" alt="Uploaded preview">`}
 catch(err){errorBox("photoResult",err)}
};
$("charBtn").onclick=async()=>{
 try{await api("/api/characters",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:$("charName").value,description:$("charDesc").value,style:$("charStyle").value})});$("charName").value="";$("charDesc").value="";loadCharacters()}
 catch(e){errorBox("charList",e)}
};
async function loadCharacters(){
 try{const items=await api("/api/characters");$("charList").innerHTML=items.length?items.map(c=>`<div class="char"><b>${escapeHtml(c.name)}</b><p>${escapeHtml(c.description)}</p><small>${escapeHtml(c.style)}</small> <button data-delete="${c.id}">Delete</button></div>`).join(""):"No characters saved yet.";
 $("charList").querySelectorAll("[data-delete]").forEach(b=>b.onclick=async()=>{try{await api("/api/characters/"+b.dataset.delete,{method:"DELETE"});loadCharacters()}catch(e){errorBox("charList",e)}})}
 catch(e){errorBox("charList",e)}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
$("videoBtn").onclick=async()=>{
 $("videoResult").textContent="Creating video...";
 const images=$("videoImages").value.split(",").map(x=>x.trim()).filter(Boolean);
 try{const d=await api("/api/video",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({image_paths:images,audio_path:$("videoAudio").value.trim()||null,seconds_per_image:Number($("videoSeconds").value)})});$("videoResult").innerHTML=`<video controls width="100%" src="${API+d.video_url}"></video><p><a href="${API+d.video_url}" download>Download MP4</a></p>`}
 catch(e){errorBox("videoResult",e)}
};
