"""descriptorpin: a defensive integrity monitor for MCP tool descriptors.

descriptorpin pins a canonical hash of every tool descriptor (name,
description, input schema) from a Model Context Protocol server inventory,
then on a later scan reports silent mutation (rug pull shape), cross-server
name collisions (shadowing shape), instruction-shaped text in descriptions
(poisoning shape), and stdio transport risk.

