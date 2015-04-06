<%inherit file="_dashboard_section.tpl"/>

## Translators, used as note in Application network interfaces section
<p>${_('List of available network interfaces')}</p>
<table>
    <tr>
        <th>${_('Interface name')}</th>
        <th>${_('IPv4')}</th>
        <th>${_('IPv6')}</th>
    </tr>
    % for iface in interfaces:
    <tr>
        <td>${iface.name}</td>
        <td>${iface.ipv4}</td>
        <td>${iface.ipv6}</td>
    </tr>
    % endfor
</table>
