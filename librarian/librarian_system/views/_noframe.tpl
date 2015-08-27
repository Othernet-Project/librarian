<%inherit file="base.tpl"/>

<%block name="extra_head">
<script>
if (this != top) { 
    top.location.replace(this.location.href); 
}
</script>
</%block>
