<%inherit file="_dashboard_section.tpl"/>

## Translators, used as note in Application network interfaces section
<p>${_('List of available network interfaces')}</p>
<table>
    <tr>
        ## Translators, used as label for network interface name
        <th>${_('Interface name')}</th>
        <th>${'IPv4'}</th>
        <th>${'IPv6'}</th>
        ## Translators, used as label for network interface type
        <th>${_('Type')}</th>
    </tr>
    % for iface in interfaces:
    <tr>
        <td>${iface.name}</td>
        <td>${iface.ipv4}</td>
        <td>${iface.ipv6}</td>
        <td class="${iface.interface_type}"></td>
    </tr>
    % endfor
</table>
