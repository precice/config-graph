# Graph structure
 
## Nodes

- [x] Participant `<participant />`
- [x] Write-Data `<write-data />`
- [x] Read-Data `<read-data />`
- [x] Receive-Mesh-Node
- [x] Data `<data:... />` (To find out if that data is actually ever used)
- [x] Mesh `<mesh />`
- [x] Mapping (with attribute `direction`)
- [x] Coupling Schemes
- [x] Exchanges

## Edges

- [x] Use-Data `<use-data />`: Mesh -> Data
- [x] Write-Data <-> Participant
- [x] Write-Data -> Data
- [x] Write-Data -> Mesh
- [x] Read-Data <-> Participant
- [x] Read-Data <- Data
- [x] Read-Data <- Mesh
- [x] Coupling Scheme Participants:
`<coupling-scheme:...> <participants first="A" second="B" /> </coupling-scheme:..>` Participant-A <-> Coupling-Scheme, Participant-B <-> Coupling-Scheme
- [x] Coupling Scheme <-> Exchange
- [x] Exchange <-> Data
- [x] Exchange <-> Mesh
- [x] Participant (from) -> Exchange -> Participant (to)
- [x] Provide Mesh: Participant -> Mesh
- [x] Receive Mesh: Mesh -> Receive-Mesh
- [x] Receive Mesh: Participant (from) -> Receive-Mesh
- [x] Receive Mesh: Receive-Mesh -> Participant (parent)
- [x] Mapping <- Mesh (from)
- [x] Mapping -> Mesh (to)
- [x] Mapping <-> Participant (which the mapping is a child of)
- [x] Sockets: Participant (acceptor) -> Participant (connector)
- [ ] MPI M2N: TODO
