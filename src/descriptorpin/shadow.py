"""Cross-server name collision detection and precedence risk.

The shadowing shape is two or more servers exposing a tool with the same
name. A client that resolves a tool by bare name must pick one, and the
losing definition is shadowed. An attacker who registers a second server
