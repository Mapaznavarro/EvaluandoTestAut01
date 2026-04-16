// Pega esto en la consola cuando el modal esté visible en pantalla
const modal = document.querySelector('app-modal');
console.log('app-modal existe:', !!modal);
console.log('app-modal outerHTML:', modal?.outerHTML?.substring(0, 3000));

// También verificar si está oculto con display:none o visibility
if (modal) {
  const style = window.getComputedStyle(modal);
  console.log('display:', style.display);
  console.log('visibility:', style.visibility);
  console.log('opacity:', style.opacity);
}

// Buscar cualquier backdrop
document.querySelectorAll('[class*="backdrop"], [class*="modal"], app-modal').forEach(el => {
  console.log(el.tagName, el.className, el.offsetParent !== null ? 'VISIBLE' : 'OCULTO');
});
