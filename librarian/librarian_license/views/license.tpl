<%inherit file="_dashboard_section.tpl"/>

<p>
## Translators, this is a note about GPL license in the 'About' section on dashboard
${_('''
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
''')}
</p>
## Translators, used as label for Librarian version in dashboard's 'About' section
<p><strong>${_('version:')}</strong> ${app_version}</p>

## Translators, appears in copyright line in dashboard's 'About' section
<p>&copy;2014-2015 Outernet Inc<br>${_('Some rights reserved.')}</p>
