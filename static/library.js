// Saved canvas layouts are kept in SQLite. Uploaded source imagery is stored as a
// downscaled data URL where browser canvas permissions allow it.
async function refreshDesignLibrary(){
  try{
    const data=await api('/api/designs');
    const root=$('#designLibrary');
    if(!root)return;
    root.innerHTML=data.designs.length?data.designs.map(d=>`<article class="saved-design"><img src="${esc(d.payload.preview||'')}" alt="${esc(d.name)} preview"><h3>${esc(d.name)}</h3><p>${esc(d.format)} · ${new Date(d.created_at).toLocaleDateString()}</p><div class="saved-design-actions"><button data-design-open="${d.id}">Open settings</button><button data-design-delete="${d.id}">Delete</button></div></article>`).join(''):'<div class="empty-list">Saved campaign layouts will appear here.</div>';
    $$('[data-design-open]').forEach(b=>b.onclick=()=>restoreSavedDesign(data.designs.find(d=>d.id==b.dataset.designOpen)));
    $$('[data-design-delete]').forEach(b=>b.onclick=async()=>{if(!confirm('Delete this saved design?'))return;try{await api(`/api/designs/${b.dataset.designDelete}`,{method:'DELETE'});await refreshDesignLibrary();toast('Design removed from the local library.')}catch(e){toast(e.message)}});
  }catch(e){/* API status is already shown by the main app shell. */}
}
function restoreSavedDesign(row){
  if(!row)return;const p=row.payload;
  Object.assign(poster,{format:p.format||'post',headline:p.headline||'',support:p.support||'',cta:p.cta||'',font:p.font||'Manrope',color:p.color||'#f6f2ea',bg:p.bg||'#5a594d',overlay:p.overlay??38,align:p.align||'left',gradient:p.gradient||'none',shape:p.shape??true,shapeType:p.shapeType||'rule',size:p.size||78,zoom:p.zoom||100,cropX:p.cropX||0,cropY:p.cropY||0,pos:p.positions||poster.pos,uploadName:p.uploaded_image||'',image:null,imageUrl:''});
  for(const [id,key] of [['posterFormat','format'],['posterHeadline','headline'],['posterSupport','support'],['posterCta','cta'],['posterFont','font'],['posterColor','color'],['posterBg','bg'],['posterOverlay','overlay']])$('#'+id).value=poster[key];
  $('#opacityVal').textContent=poster.overlay+'%';$('#posterSize').value=poster.size;$('#shapeType').value=poster.shapeType;$('#cropX').value=poster.cropX;$('#cropY').value=poster.cropY;$('#cropZoom').value=poster.zoom;$$('#gradientOptions button').forEach(b=>b.classList.toggle('selected',b.dataset.gradient===poster.gradient));
  if(p.source_image){const im=new Image();im.onload=()=>{poster.image=im;drawPoster()};im.src=p.source_image}else poster._starterRequested=false;
  navigate('poster');initCanvas();toast('Saved layout settings loaded. Save again to create a new version.');
}
async function saveCanvasDesign(){
  const name=prompt('Name this design',`${poster.format} campaign creative`);if(!name)return;
  try{
    const thumb=document.createElement('canvas');thumb.width=360;thumb.height=Math.round(360*canvas.height/canvas.width);thumb.getContext('2d').drawImage(canvas,0,0,thumb.width,thumb.height);
    let preview=null,sourceImage=null;try{preview=thumb.toDataURL('image/jpeg',.62)}catch{}
    if(poster.image?.complete)try{const base=document.createElement('canvas');base.width=Math.min(1000,canvas.width);base.height=Math.round(base.width*canvas.height/canvas.width);const c=base.getContext('2d');const scale=Math.max(base.width/poster.image.width,base.height/poster.image.height),w=poster.image.width*scale,h=poster.image.height*scale;c.drawImage(poster.image,(base.width-w)/2,(base.height-h)/2,w,h);sourceImage=base.toDataURL('image/jpeg',.76)}catch{}
    await api('/api/designs',{method:'POST',body:JSON.stringify({name,format:$('#posterFormat').selectedOptions[0].text,payload:{headline:poster.headline,support:poster.support,cta:poster.cta,font:poster.font,color:poster.color,bg:poster.bg,overlay:poster.overlay,align:poster.align,format:poster.format,gradient:poster.gradient||'none',shape:poster.shape,shapeType:poster.shapeType,size:poster.size,zoom:poster.zoom,cropX:poster.cropX,cropY:poster.cropY,positions:poster.pos,uploaded_image:poster.uploadName||null,source_image:sourceImage,preview}})});
    await refreshDesignLibrary();toast('Design and editable layout saved locally.');
  }catch(e){toast(e.message)}
}
$('#saveDesign').onclick=saveCanvasDesign;
$$('#gradientOptions button').forEach(b=>b.onclick=()=>{poster.gradient=b.dataset.gradient;$$('#gradientOptions button').forEach(x=>x.classList.toggle('selected',x===b));drawPoster()});
// Attach saved layouts to a campaign; a campaign may contain several creative IDs.
const campaignListNode=$('#campaignList');
if(campaignListNode){
  const addAttachButtons=()=>{$$('.campaign-row').forEach(row=>{const edit=row.querySelector('[data-edit]');if(!edit||row.querySelector('[data-attach]'))return;const id=edit.dataset.edit;const btn=document.createElement('button');btn.dataset.attach=id;btn.textContent='Add creative';row.querySelector('.campaign-menu').prepend(btn);const campaign=campaigns.find(c=>String(c.id)===String(id));const p=row.querySelector('p');if(campaign&&p&&!p.dataset.counted){p.textContent+=` · ${(campaign.creative_ids||[]).length} saved creatives`;p.dataset.counted='1'}})};
  new MutationObserver(addAttachButtons).observe(campaignListNode,{childList:true,subtree:true});
  campaignListNode.addEventListener('click',async e=>{const b=e.target.closest('[data-attach]');if(!b)return;try{const data=await api('/api/designs');if(!data.designs.length){toast('Save a poster design before attaching a campaign creative.');return}openModal(`<button class="modal-close" data-close>×</button><div class="eyebrow">CAMPAIGN ASSETS</div><h2>Add a saved creative</h2><label class="field"><span>CHOOSE A DESIGN</span><select id="creativeToAttach">${data.designs.map(d=>`<option value="${d.id}">${esc(d.name)} · ${esc(d.format)}</option>`).join('')}</select></label><button class="button button-dark button-full" id="attachNow">Attach to campaign ↗</button>`);$('[data-close]').onclick=closeModal;$('#attachNow').onclick=async()=>{try{await api(`/api/campaigns/${b.dataset.attach}/creatives`,{method:'POST',body:JSON.stringify({design_id:Number($('#creativeToAttach').value)})});closeModal();await loadCampaigns();toast('Creative attached to campaign.')}catch(err){toast(err.message)}}}catch(err){toast(err.message)}});
}
refreshDesignLibrary();
const caseStudy=$('.case-study');if(caseStudy&&!$('#caseCreativeAssets')){const gallery=document.createElement('div');gallery.id='caseCreativeAssets';gallery.className='case-assets';gallery.innerHTML='<div class="eyebrow">CAMPAIGN ASSETS / EDITABLE SVG</div><div><a href="/static/creative-assets/aura-autumn-poster.svg" target="_blank" rel="noopener">Campaign poster ↗</a><a href="/static/creative-assets/aura-instagram-post.svg" target="_blank" rel="noopener">Instagram post ↗</a><a href="/static/creative-assets/aura-instagram-story.svg" target="_blank" rel="noopener">Instagram story ↗</a><a href="/static/creative-assets/aura-product-ad.svg" target="_blank" rel="noopener">Product ad ↗</a><a href="/static/creative-assets/aura-storefront-hero.svg" target="_blank" rel="noopener">Storefront hero ↗</a><a href="/static/creative-assets/aura-email-banner.svg" target="_blank" rel="noopener">Email banner ↗</a><a href="/static/creative-assets/aura-wordmark.svg" target="_blank" rel="noopener">Wordmark ↗</a></div>';caseStudy.append(gallery)}
