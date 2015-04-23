<p>
    <span id="manual-date">
        <input type="text" name="year" value="${datetime['year']}" />
        ${h.vselect('month', months, datetime)}
        <input type="text" name="day" value="${datetime['day']}" />
    </span>
    <input type="text" id="datepicker" value="${datetime['year']}-${datetime['month']}-${datetime['day']}" />
    <input type="text" class="time" name="hour" value="${datetime['hour']}" />&#58;
    <input type="text" class="time" name="minute" value="${datetime['minute']}" />&#58;
    <input type="text" class="time" name="second" value="${datetime['second']}" />
    <div class="flow-element">
        <div id="pikaday-container"></div>
    </div>
    ${h.form_errors(errors)}
</p>
<script type="text/javascript" src="${url('sys:static', path='js/pikaday.js')}"></script>
<script type="text/javascript">
    document.getElementById('manual-date').style.display = 'none';
    var picker = new Pikaday({
        field: document.getElementById('datepicker'),
        container: document.getElementById('pikaday-container'),
        onSelect: function (date) {
            $('input[name="year"]').val(date.getFullYear());
            $('select[name="month"]').val(date.getMonth() + 1);
            $('input[name="day"]').val(date.getDate());
        }
    });
</script>
