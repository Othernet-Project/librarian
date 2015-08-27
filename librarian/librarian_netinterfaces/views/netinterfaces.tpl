<%inherit file="_dashboard_section.tpl"/>

## Translators, used as note in Application network interfaces section
<p>${_('List of available network interfaces')}</p>
<table class="network-interfaces">
    <tr>
        ## Translators, used as label for network interface name
        <th>${_('Interface name')}</th>
        <th>${'IPv4'}</th>
        <th>${'IPv6'}</th>
    </tr>
    % for iface in interfaces:
    <tr>
        <%
        if iface.is_wireless:
            interface_type = 'wireless'
        else:
            interface_type = 'ethernet'
        %>
        <td><span class="icon ${interface_type}"></span> ${iface.name}</td>
        <td>${iface.ipv4}</td>
        <td>${iface.ipv6}</td>
    </tr>
    % endfor
</table>
