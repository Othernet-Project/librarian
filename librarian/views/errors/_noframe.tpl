<%inherit file="/narrow_base.tpl"/>

## When this template is loaded into an iframe, the code in the extra_head 
## script tag causes it to escape the frame.
<%block name="extra_head">
<script>
if (this != top) {
    top.location.replace(this.location.href);
}
</script>
</%block>
