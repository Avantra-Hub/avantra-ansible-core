# Avantra API Reference

> API surface used by the `avantra.core` Ansible collection.
> This document covers **only** the endpoints the collection modules call.

## Authentication

### REST Login

```
POST {base_url}/xn/api/auth/login
Content-Type: application/json

{"username": "...", "password": "..."}

→ 200: {"token": "eyJhbGciOiJ..."}
```

The returned JWT is used as `Authorization: Bearer <token>` for all GraphQL calls.

### SOAP WS-Security

The `workflow_execution` module uses SOAP with WS-Security `UsernameToken` headers — **not** JWT.
Credentials (username/password) are embedded directly in the SOAP envelope header:

```xml
<wsse:Security>
    <wsse:UsernameToken wsu:Id="UsernameToken-{uuid}">
        <wsse:Username>{username}</wsse:Username>
        <wsse:Password Type="...#PasswordText">{password}</wsse:Password>
        <wsse:Nonce EncodingType="...#Base64Binary">{nonce}</wsse:Nonce>
        <wsu:Created>{timestamp}</wsu:Created>
    </wsse:UsernameToken>
    <wsu:Timestamp wsu:Id="TS-{uuid}">
        <wsu:Created>{timestamp}</wsu:Created>
        <wsu:Expires>{timestamp + 5min}</wsu:Expires>
    </wsu:Timestamp>
</wsse:Security>
```

---

## URL Resolution

The collection auto-normalizes URLs. Given a base URL like `https://host:port/xn`:

| Endpoint | URL |
|----------|-----|
| Auth | `{base}/api/auth/login` |
| GraphQL | `{base}/api/graphql` |
| Subscriptions | `{base}/api/subscriptions` |
| SOAP | `{base}/ws` |

Rules: adds `https://` if missing, strips trailing slashes, auto-computes relative paths.
See `plugins/module_utils/avantra/api.py` for exact logic.

---

## GraphQL API

**Endpoint:** `POST {base_url}/xn/api/graphql`
**Auth:** `Authorization: Bearer <token>`

### Queries

#### GetCustomerByName

Used by: `plugins/module_utils/avantra/customer.py`

```graphql
query GetCustomerByName($customer_name: String!) {
    customers(
        where: { filterBy: [{ name: "name", operator: eq, value: $customer_name }] }
    ) {
        id
        name
        sapCustomerNumber
        description
        remarks
        phone
        mobile
        fax
        email
        timezone
        address
        postbox
        postalCode
        city
        country
        timestamp
        customerUrl
        customData
        guid
        parent { id name }
        children { id name }
        childrenCount
    }
}
```

#### ServerGetByName

Used by: `plugins/module_utils/avantra/server.py` → `server.py`, `server_info.py`

```graphql
query ServerGetByName($server_name: String!, $customer_name: String!) {
    systems(
        where: {
            filterBy: [
                { name: "type", operator: eq, value: "SERVER" }
                { name: "name", operator: eq, value: $server_name }
                { name: "customer.name", operator: eq, value: $customer_name }
            ]
        }
    ) {
        ... on Server {
            # Server Fragment — see below
        }
    }
}
```

#### SapSystemGetByUnifiedSapSid

Used by: `plugins/module_utils/avantra/sapsystem.py` → `sapsystem.py`, `sapsystem_info.py`

```graphql
query SapSystemGetByUnifiedSapSid($unified_sap_sid: String!, $customer_name: String!) {
    systems(
        where: {
            filterBy: [
                { name: "type", operator: eq, value: "SAP_SYSTEM" }
                { name: "name", operator: eq, value: $unified_sap_sid }
                { name: "customer.name", operator: eq, value: $customer_name }
            ]
        }
    ) {
        ... on SapSystem {
            # SapSystem Fragment — see below
        }
    }
}
```

### Mutations

#### CreateServer

Used by: `plugins/module_utils/avantra/server.py`

```graphql
mutation CreateServer(
    $input: CreateServerInput!
    $basicCredentials: [SetBasicCredentialsInput!] = []
    $sshCredentials: [SetSshCredentialsInput!] = []
) {
    createServer(input: $input) {
        result { success message code }
        credentials {
            setBasicCredentials(input: $basicCredentials) {
                result { code success message }
            }
            setSshCredentials(input: $sshCredentials) {
                result { code success message }
            }
        }
        server { # Server Fragment }
    }
}
```

**CreateServerInput** (from `systems/server.graphqls`):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `customerId` | `ID!` | yes | |
| `name` | `String!` | yes | |
| `ipAddress` | `String!` | yes | 1–128 chars |
| `description` | `String` | no | |
| `notes` | `String` | no | |
| `systemRole` | `String` | no | |
| `timezone` | `String` | no | |
| `dnsDomain` | `String` | no | |
| `applicationType` | `String` | no | |
| `dnsAliases` | `[String!]` | no | |
| `monitoring` | `Boolean` | no | |
| `customAttributes` | `[CustomAttributeInput!]` | no | |

#### UpdateServer

Used by: `plugins/module_utils/avantra/server.py`

```graphql
mutation UpdateServer(
    $input: UpdateServerInput!
    $basicCredentials: [SetBasicCredentialsInput!] = []
    $sshCredentials: [SetSshCredentialsInput!] = []
) {
    updateServer(input: $input) {
        result { success message code }
        credentials {
            setBasicCredentials(input: $basicCredentials) {
                result { code success message }
            }
            setSshCredentials(input: $sshCredentials) {
                result { code success message }
            }
        }
        server { # Server Fragment }
    }
}
```

#### DeleteServer

Used by: `plugins/module_utils/avantra/server.py`

```graphql
mutation DeleteServer($id: ID!) {
    deleteServer(input: { id: $id }) {
        result { success message code }
    }
}
```

#### CreateSapSystem

Used by: `plugins/module_utils/avantra/sapsystem.py`

```graphql
mutation CreateSapSystem(
    $input: CreateSapSystemInput!
    $basicCredentials: [SetBasicCredentialsInput!] = []
    $sshCredentials: [SetSshCredentialsInput!] = []
    $sapControlCredentials: [SetSapControlCredentialsInput!] = []
    $rfcCredentials: [SetRfcCredentialsInput!] = []
    $oauthCodeCredentials: [SetOAuthCodeCredentialsInput!] = []
    $oauthClientCredentials: [SetOAuthClientCredentialsInput!] = []
) {
    createSapSystem(input: $input) {
        result { success message code }
        credentials {
            setBasicCredentials(input: $basicCredentials) { result { code success message } }
            setSshCredentials(input: $sshCredentials) { result { code success message } }
            setSapControlCredentials(input: $sapControlCredentials) { result { code success message } }
            setRfcCredentials(input: $rfcCredentials) { result { code success message } }
            setOAuthCodeCredentials(input: $oauthCodeCredentials) { result { code success message } }
            setOAuthClientCredentials(input: $oauthClientCredentials) { result { code success message } }
        }
        sapSystem { # SapSystem Fragment }
    }
}
```

**CreateSapSystemInput** (from `systems/sapsystem.graphqls`):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `customerId` | `ID!` | yes | |
| `unifiedSapSid` | `String!` | yes | 1–16 chars |
| `realSapSid` | `String!` | yes | 1–3 chars |
| `description` | `String` | no | |
| `notes` | `String` | no | |
| `systemRole` | `String` | no | |
| `timezone` | `String` | no | |
| `applicationType` | `String` | no | |
| `monitoring` | `Boolean` | no | |
| `database` | `DatabaseConfigInput` | no | `{monitoringServerSystemId, host, port, name}` |
| `remoteOptions` | `RemoteOptionsInput` | no | |
| `customAttributes` | `[CustomAttributeInput!]` | no | |

#### UpdateSapSystem

Same structure as CreateSapSystem but with `UpdateSapSystemInput`.

#### DeleteSapSystem

```graphql
mutation DeleteSapSystem($id: ID!) {
    deleteSapSystem(input: { id: $id }) {
        result { success message code }
    }
}
```

#### Monitoring Mutations

**Server:**
```graphql
mutation TurnMonitoringOffForServer($id: ID!, $cascade: Boolean, $note: String, $until: DateTime) {
    turnMonitoringOffForServer(id: $id, cascade: $cascade, note: $note, until: $until) {
        # Server Fragment
    }
}

mutation TurnMonitoringOnForServer($id: ID!, $cascade: Boolean, $note: String) {
    turnMonitoringOnForServer(id: $id, cascade: $cascade, note: $note) {
        # Server Fragment
    }
}
```

**SAP System:**
```graphql
mutation TurnMonitoringOffForSapSystem($id: ID!, $cascade: Boolean, $note: String, $until: DateTime) {
    turnMonitoringOffForSapSystem(id: $id, cascade: $cascade, note: $note, until: $until) {
        # SapSystem Fragment
    }
}

mutation TurnMonitoringOnForSapSystem($id: ID!, $cascade: Boolean, $note: String) {
    turnMonitoringOnForSapSystem(id: $id, cascade: $cascade, note: $note) {
        # SapSystem Fragment
    }
}
```

#### ExecuteSystemAction

Used by: `plugins/module_utils/avantra/system_actions.py`

```graphql
mutation ExecuteSystemAction(
    $actionId: ID!,
    $executionName: String = null,
    $systemIds: [ID!]!,
    $parameters: [SystemActionParameterInput!]!
) {
    executeSystemAction(
        actionId: $actionId,
        executionName: $executionName,
        parameter: $parameters,
        systemIds: $systemIds
    ) {
        id
        name
        description
        detail
        status
        start
        system { id name }
        log
        timestamp
        user { id principal }
        customer { id name }
    }
}
```

### System Action IDs

| Action | ID | System Type | Parameters |
|--------|----|-------------|------------|
| `SERVER_START` | 20 | Server | `SET_MONI_ON`, `WAIT_SECONDS` |
| `SERVER_STOP` | 21 | Server | `SET_MONI_OFF`, `FORCE_STOP` |
| `SAP_SYSTEM_START` | 1 | SapSystem | `SET_MONI_ON`, `WAIT_SECONDS` |
| `SAP_SYSTEM_STOP` | 2 | SapSystem | `SET_MONI_OFF`, `FORCE_STOP` |
| `SAP_SYSTEM_RESTART` | 201 | SapSystem | `WAIT_SECONDS`, `RESTART_WAIT_SECONDS` |
| `SAP_SYSTEM_WITH_DB_START` | 32 | SapSystem | `CHECK_DB_STATE` |
| `SAP_SYSTEM_WITH_DB_STOP` | 33 | SapSystem | `CHECK_DB_STATE` |
| `SAP_SYSTEM_WITH_DB_RESTART` | 202 | SapSystem | `CHECK_DB_STATE` |
| `SAP_SYSTEM_WITH_DB_AND_HANA_START` | 34 | SapSystem | — |
| `SAP_SYSTEM_WITH_DB_AND_HANA_STOP` | 35 | SapSystem | — |
| `SAP_SYSTEM_WITH_DB_AND_HANA_RESTART` | 203 | SapSystem | — |
| `SAP_SYSTEM_WITH_DB_AND_SERVER_START` | 36 | SapSystem | — |
| `SAP_SYSTEM_WITH_DB_AND_SERVER_STOP` | 37 | SapSystem | — |
| `SAP_SYSTEM_WITH_DB_AND_SERVER_RESTART` | 204 | SapSystem | — |

### GraphQL Filtering

From `filter.graphqls`:

```graphql
input FilterInput {
    filterBy: [FilterByInput!]!     # AND-combined
}

input FilterByInput {
    name: String!                    # field name (dot notation for nested: "customer.name")
    operator: FilterOperator!        # like, eq, isNull, gt, lt, ge, le, isIn
    value: String
}
```

### Server Fragment

Full field set returned by all server queries/mutations. Source: `plugins/module_utils/avantra/server.py`

```graphql
{
    id
    mst
    checks(where: { filterBy: [{ name: "name", operator: eq, value: "AGENTALIVE" }] }) {
        id name status lastRefresh
    }
    customAttributes { id name value }
    customData
    customer { id name }
    description
    maintenance
    monitorOff
    monitorOffUntil
    monitorSwitchReason
    monitorSwitchDate
    name
    operational
    operationalSince
    operationalUntil
    status
    statusId
    systemRole
    type
    timestamp
    uuid
    ipAddress
    dnsAliases
    dnsDomain
    physicalMemory
    filesystemTotalSize
    filesystemTotalUsed
    sapHardwareKey
    osType
    osPlatform
    osName
    osLongName
    osVersion
    osArchitecture
    notes
    virtualClusterServer
    aliveStatus
    aliveLastUpdate
    aliveSince
    javaDetails {
        extern { key value }
        externVersion
        externJavaHome
        intern { key value }
        internVersion
    }
    cpuDetails { name model vendor mhz totalCores }
    cloudDetails { name type }
    gateway
    natTraversal
    publicKey
    applicationType
    rtmStatus
    rtmDate
    timezone
    sapInstanceCount
    sapSystemCount
    cloudServiceCount
    businessObjectCount
    databaseCount
    agentVersion
    administrator { id principal firstname lastname email emailAlternative }
    administratorDeputy { id principal firstname lastname email emailAlternative }
    remote
    assignedSLA { id name }
    monitorLevel
    credentials {
        id
        purpose { key id name }
        ... on BasicAuthenticationCredentials { basicUser: username password }
        ... on RfcAuthenticationCredentials { rfcUser: username password }
        ... on SapControlCredentials { sapControlUser: username password privateKey privateKeyPassphrase }
        ... on SshCredentials { hostname port username password identity identityPassphrase }
    }
}
```

### SapSystem Fragment

Full field set returned by all SAP system queries/mutations. Source: `plugins/module_utils/avantra/sapsystem.py`

```graphql
{
    id
    mst
    checks(where: { filterBy: [{ name: "name", operator: eq, value: "SystemAlive" }] }) {
        id name status lastRefresh
    }
    customAttributes { id name value }
    customData
    customer { id name }
    description
    maintenance
    monitorOff
    monitorOffUntil
    monitorSwitchReason
    monitorSwitchDate
    name
    operational
    operationalSince
    operationalUntil
    status
    statusId
    systemRole
    type
    timestamp
    uuid
    unifiedSapSid
    realSapSid
    applicationType
    timezone
    basisRelease
    componentVersion
    spamPatchLevel
    encoding
    sapInstancesCount
    remoteOptions {
        monitoringServer { id name }
    }
    databaseMonitoringServer { id name }
    administrator { id principal firstname lastname email emailAlternative }
    administratorDeputy { id principal firstname lastname email emailAlternative }
    productVersions { shortDescription product release spStack status }
    database {
        id name databaseType host port version dbmsProduct
        server { id name }
    }
    remote
    assignedSLA { id name }
    solutionManager { id name }
    componentVersion
    avantraTransportVersion
    monitorLevel
    credentials {
        id
        purpose { key id name }
        ... on BasicAuthenticationCredentials { basicUser: username password }
        ... on RfcAuthenticationCredentials { rfcUser: username password }
        ... on SapControlCredentials { sapControlUser: username password privateKey privateKeyPassphrase }
        ... on SshCredentials { hostname port username password identity identityPassphrase }
    }
}
```

### Error Codes

| Code | Name | Context |
|------|------|---------|
| 1010 | `ERROR_NOT_IMPLEMENTED` | Unsupported operation |
| 1011 | `ERROR_ELEMENT_NOT_FOUND` | Entity not found |
| 1100 | `ERROR_DELETE_ELEMENT_SERVER` | Server deletion failure |
| 1102 | `ERROR_DELETE_ELEMENT_SAP_SYSTEM` | SAP system deletion failure |

---

## SOAP API

**WSDL:** `{base_url}/xn/ws/xandria_webservice.wsdl`
**Endpoint:** `POST {base_url}/xn/ws`
**Auth:** WS-Security UsernameToken (NOT JWT)

### StartAutomationWorkflow

Used by: `plugins/modules/workflow_execution.py`

```xml
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:web="http://www.syslink.ch/2013/xandria/webservice">
    <soapenv:Header>
        <!-- WS-Security UsernameToken header -->
    </soapenv:Header>
    <soapenv:Body>
        <web:StartAutomationWorkflowRequest>
            <web:name>{workflow_name}</web:name>
            <web:namespace>{namespace}</web:namespace>
            <web:args>
                <web:key>{key}</web:key>
                <web:value>{value}</web:value>
            </web:args>
            <web:variant>{variant}</web:variant>
            <web:ignoreDefaultVariant>{true|false}</web:ignoreDefaultVariant>
        </web:StartAutomationWorkflowRequest>
    </soapenv:Body>
</soapenv:Envelope>
```

**Response:**
```xml
<StartAutomationWorkflowResponse>
    <executionId>12345</executionId>
    <args>
        <key>...</key>
        <value>...</value>
    </args>
</StartAutomationWorkflowResponse>
```

### Additional SOAP Operations (available in WSDL, not used by modules)

The WSDL exposes 91 operations. Useful for testing/verification:

| Operation | Purpose |
|-----------|---------|
| `GetWebServiceInformation` | Health check (returns version, build info) |
| `GetWorkflows` | List available workflows |
| `GetWorkflow` | Get workflow by name/namespace |
| `GetWorkflowExecution` | Check execution status |
| `GetAllCustomers` | List all customers |
| `GetCustomersByName` | Find customer by name |
| `GetAllServers` / `GetServer` | Server lookup |

### Workflow Types

```
WorkflowInput:
    name, description, type, defaultValue, required, multiple, documentation

    type enum: STRING | INTEGER | BOOLEAN | SCRIPT | PASSWORD | CRED_ID |
               SYSTEM_SELECTOR | SERVER | DATABASE | SAPSYSTEM | SAPINSTANCE |
               SAP_BUSINESS_OBJECT | CLOUDSERVICE | CHECK_TYPE | CUSTOM_CHECK |
               COMPOSITE_CHECK | STATUS | SAP_KERNEL | SYSTEM | FILE_BUNDLE | FILE_TAGS

AutomationExecutionStatus enum:
    CREATED | STARTED | RUNNING | FINISHED_SUCCESS | FINISHED_PARTLY_SUCCESS |
    FINISHED_FAILED | FINISHED_STOPPED
```
