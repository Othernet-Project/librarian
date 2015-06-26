<%namespace name='widgets' file='_widgets.tpl'/>

<%widgets:accordion id="${name}">
    <h2>${heading}</h2>
    <div class="dash-section-content">
        ${self.body(**context.kwargs)}
    </div>
</%widgets:accordion>
