# Reviewing a pin file

A pin file records what was approved, by whom, and the exact canonical
descriptor at that moment. When reviewing one:

- Check every tool has an approval record with a name and a note you can
  trace to a decision.
- Compare truncated digests against the previous pin; a changed digest means
  the descriptor moved. Read the stored canonical descriptor to see the
  field, not just the fact.
- Treat additions as decisions: a new tool takes on the trust the pin
  grants, so it deserves the same review as a changed one.

Keep the pin in version control. A pin change with no review discussion is
the review finding, not the tool's.
