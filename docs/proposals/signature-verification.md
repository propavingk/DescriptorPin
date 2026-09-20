# Proposal: signature verification

Status: closed, not planned for this tool.

The idea is to verify a publisher signature over each descriptor, so trust
does not depend on a locally recorded pin.

Out of scope for the same reason the tool never opens a socket: a signature
scheme turns DescriptorPin into a verifier with key distribution problems of
its own, and the pin already answers the question this tool exists to ask,
which is whether anything changed after the human approval. Teams that want
publisher signatures can pair the pin with their existing signing pipeline
and keep the field-level diff from this tool.
