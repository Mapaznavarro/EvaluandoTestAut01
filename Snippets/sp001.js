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

// Respuesta
Script snippet #1:3 app-modal existe: true
Script snippet #1:4 app-modal outerHTML: <app-modal _ngcontent-ng-c3295250274="" _nghost-ng-c2773784004=""><div _ngcontent-ng-c2773784004="" class="modal-background"><div _ngcontent-ng-c2773784004="" class="backdrop"></div><div tabindex="0" class="cdk-visually-hidden cdk-focus-trap-anchor" aria-hidden="true"></div><div _ngcontent-ng-c2773784004="" cdktrapfocus="" class="modal" style="width: 498px;"><div _ngcontent-ng-c2773784004="" class="header"><div _ngcontent-ng-c2773784004="" class="title"> Notificaciones </div><div _ngcontent-ng-c2773784004="" class="options"><!----><div _ngcontent-ng-c2773784004="" class="option close"><svg _ngcontent-ng-c2773784004="" class="svg-inline--fa fa-xmark fa-fw" aria-hidden="true" focusable="false" data-prefix="fal" data-icon="xmark" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg=""><path fill="currentColor" d="M324.5 411.1c6.2 6.2 16.4 6.2 22.6 0s6.2-16.4 0-22.6L214.6 256 347.1 123.5c6.2-6.2 6.2-16.4 0-22.6s-16.4-6.2-22.6 0L192 233.4 59.6 100.9c-6.2-6.2-16.4-6.2-22.6 0s-6.2 16.4 0 22.6L169.4 256 36.9 388.5c-6.2 6.2-6.2 16.4 0 22.6s16.4 6.2 22.6 0L192 278.6 324.5 411.1z"></path></svg><!-- <i _ngcontent-ng-c2773784004="" class="fal fa-times fa-fw"></i> --></div><!----></div></div><!----><overlay-scrollbars _ngcontent-ng-c2773784004="" data-overlayscrollbars-initialize="" class="content" data-overlayscrollbars="host"><div overlayscrollbars="" data-overlayscrollbars-contents="" data-overlayscrollbars-viewport="scrollbarHidden overflowXHidden overflowYHidden" tabindex="-1" style="margin-right: 0px; margin-bottom: 0px; margin-left: 0px; top: 0px; right: auto; left: 0px; width: calc(100% + 0px); padding: 0px;"><!----><app-dynamic-loader _ngcontent-ng-c2773784004=""><app-notification-modal><div class="notification-modal"><app-notification-modal-item _nghost-ng-c2080019026=""><div _ngcontent-ng-c2080019026="" class="notification-modal-item"><div _ngcontent-ng-c2080019026="" class="header"><div _ngcontent-ng-c2080019026="" class="header-title"><div _ngcontent-ng-c2080019026="" class="state"><i _ngcontent-ng-c2080019026="" class="fa-fw error"></i></div><!----> Errores </div><div _ngcontent-ng-c2080019026="" class="options"><div _ngcontent-ng-c2080019026="" class="option hidden"><svg _ngcontent-ng-c2080019026="" class="svg-inline--fa fa-plus fa-fw fa-sm" aria-hidden="true" focusable="false" data-prefix="fal" data-icon="plus" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" data-fa-i2svg=""><path fill="currentColor" d="M240 64c0-8.8-7.2-16-16-16s-16 7.2-16 16l0 176L32 240c-8.8 0-16 7.2-16 16s7.2 16 16 16l176 0 0 176c0 8.8 7.2 16 16 16s16-7.2 16-16l0-176 176 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-176 0 0-176z"></path></svg><!-- <i _ngcontent-ng-c2080019026="" class="fal fa-plus fa-sm fa-fw"></i> --></div><div _ngcontent-ng-c2080019026="" class="option"><svg _ngcontent-ng-c2080019026="" class="svg-inline--fa fa-minus fa-fw fa-sm" aria-hidden="true" focusable="false" data-prefix="fal" data-icon="minus" role="img" xmln
Script snippet #1:9 display: inline
Script snippet #1:10 visibility: visible
Script snippet #1:11 opacity: 1
Script snippet #1:16 DIV modal-container VISIBLE
Script snippet #1:16 APP-MODAL  VISIBLE
Script snippet #1:16 DIV modal-background VISIBLE
Script snippet #1:16 DIV backdrop VISIBLE
Script snippet #1:16 DIV modal VISIBLE
Script snippet #1:16 DIV notification-modal VISIBLE
Script snippet #1:16 DIV notification-modal-item VISIBLE
VM4088 Script snippet #1:1 undefined

