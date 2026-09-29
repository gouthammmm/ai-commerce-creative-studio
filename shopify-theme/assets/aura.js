document.querySelectorAll('[data-product-form]').forEach(section=>{
  const select=section.querySelector('[data-variant-select]');
  if(!select)return;
  const price=section.querySelector('[data-product-price]');
  const image=section.querySelector('[data-product-image]');
  const button=section.querySelector('[data-add-button]');
  const status=section.querySelector('[data-variant-status]');
  const money=(minor)=>{
    const currency=document.documentElement.dataset.currency||'AED';
    return new Intl.NumberFormat(document.documentElement.lang||'en',{style:'currency',currency}).format(Number(minor)/100);
  };
  const sync=()=>{
    const option=select.selectedOptions[0];
    if(!option)return;
    const amount=Number(option.dataset.price||0),compare=Number(option.dataset.compare||0),available=option.dataset.available==='true';
    if(price)price.innerHTML=`${money(amount)}${compare>amount?` <s>${money(compare)}</s>`:''}`;
    if(button){button.disabled=!available;button.textContent=available?'Add to bag':'Sold out'}
    if(image&&option.dataset.image){image.src=option.dataset.image;image.srcset='';image.alt=option.textContent.trim()}
    if(status)status.textContent=available?'Selected option is available.':'This option is sold out.';
  };
  select.addEventListener('change',sync);sync();
});
document.querySelectorAll('[data-end]').forEach(section=>{const end=new Date(section.dataset.end);const out=section.querySelector('.countdown-readout');if(!out||Number.isNaN(end.getTime()))return;const update=()=>{const ms=end-Date.now();if(ms<=0){out.textContent='Campaign has ended';return}const days=Math.floor(ms/86400000),hours=Math.floor(ms%86400000/3600000),mins=Math.floor(ms%3600000/60000);out.textContent=`${days} days · ${hours} hours · ${mins} minutes`};update();setInterval(update,60000)});
