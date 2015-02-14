"""Transport risk: stdio and other declared transports.

descriptorpin flags servers whose declared transport is stdio. Published
research on Model Context Protocol security found that a stdio server is
launched as a local subprocess from client configuration, so a crafted
configuration entry can turn a descriptor exchange into command execution
on the host. The specification treats launching that subprocess as expected
