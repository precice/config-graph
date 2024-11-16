# Graph structure
 
## Nodes

- Participant `<participant />`
- Write-Data `<write-data />`
- Read-Data `<read-data />`
- Data `<data:... />` (To find out if that data is actually ever used)
- Mesh `<mesh />`
- Mapping (with attribute `direction`)
- Coupling `Schemes
- Exchanges

##` Edges

- Use-Data `<use-data />`: Mesh -> Data
- Write-Data <-> Participant
- Write-Data -> Data
- Write-Data -> Mesh
- Read-Data <-> Participant
- Read-Data <- Data
- Read-Data <- Mesh
- Coupling Scheme Participants:
`<coupling-scheme:...> <participants first="A" second="B" /> </coupling-scheme:..>` Participant-A <-> Coupling-Scheme, Participant-B <-> Coupling-Scheme
- Coupling Scheme <-> Exchange
- Exchange <-> Data
- Exchange <-> Mesh
- Participant (from) -> Exchange -> Participant (to)
- Provide Mesh: Participant -> Mesh
- Receive Mesh: Mesh -> Participant
- Mapping <- Mesh (from)
- Mapping -> Mesh (to)
- Mapping <-> Participant (which the mapping is a child of)
- Sockets: Participant (acceptor) -> Participant (connector)