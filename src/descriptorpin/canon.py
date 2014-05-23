"""Canonical serialisation of a tool descriptor.

A descriptor is a tool's name, description, and input schema. Two servers,
or two versions of one server, may serialise the same descriptor with
different key order or whitespace. Hashing the raw bytes would then report
a change where none exists, or miss a real change hidden behind reordering.

