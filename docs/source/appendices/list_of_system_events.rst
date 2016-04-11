Appendix E: List of system events in Librarian
==============================================

This section provides a list of core events that are triggered in supervisor
(unprefixed) or the exports subsystem (prefixed with 'exp').

=====================  ========================================================
pre_start              Server is about to start
post_start             Server has started
background             New background loop cycle
shutdown               Server is about to go down
immediate_shutdown     Server is about to go down in an emergency
exp.collected          Component exports of some type were collected
exp.installed          Component exports of some type were installed
exp.finished           All components have been processed
=====================  ========================================================
