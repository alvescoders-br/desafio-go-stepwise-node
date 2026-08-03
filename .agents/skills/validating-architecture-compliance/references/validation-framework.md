# Validation Framework — Detailed Criteria

This reference contains the full checklist and criteria for each of the four validation areas:

## Table of Contents
1. [Area 1: Architecture Compliance Validation](#area-1-architecture-compliance-validation)
2. [Area 2: Component Architecture Mapping](#area-2-component-architecture-mapping)
3. [Area 3: Quality Attributes & NFR Validation](#area-3-quality-attributes--nfr-validation)
4. [Area 4: Gap Analysis & Severity Classification](#area-4-gap-analysis--severity-classification)

## Area 1: Architecture Compliance Validation

**Goal:** Confirm that requirements align with the ASD's technical framework.

### 1.1 Pattern Compliance
**ASD reference:** Software Architecture → Architecture Patterns

Check that the requirement:
- Can be implemented using one or more of the architecture patterns already documented in the ASD
- Does not implicitly introduce a new pattern (e.g., adding event sourcing when the ASD only documents REST-based patterns)
- Does not contradict an existing architectural decision recorded in the ADR log

**Questions to ask:**
- Which ASD pattern covers this requirement?
- Does the requirement fit naturally into that pattern, or does it require stretching/bending it?

### 1.2 Technology Stack Compatibility
**ASD reference:** Software Architecture → Technology Stack

Check that the requirement:
- Can be implemented with the approved technology stack
- Does not require adding new technologies not present in the ASD
- Does not require upgrading or replacing existing stack components

**Questions to ask:**
- Does the implementation require any library, framework, or runtime not in the ASD tech stack?
- If a new technology is needed, does the ASD explicitly permit extension, or is there a constraint?

### 1.3 Integration Point Validation
**ASD reference:** Integration Strategy → Key Integrations

Check that the requirement:
- Uses only integration points defined in the ASD
- Does not require new external integrations not described in the ASD
- Complies with the integration protocols, contracts, and versions documented

**Questions to ask:**
- Does this requirement call an external system? Is that integration in the ASD?
- Does it respect the integration owner, type, and spec version as documented?

### 1.4 Implementation Capacity
**ASD reference:** Software Architecture → Architecture Patterns (and team context)

Assess whether:
- The team has the skills to implement the requirement within ASD-defined patterns
- The requirement's complexity is within the team's architectural understanding

**Note:** This is an advisory check, not a blocker by itself. Flag concerns here but do not let skill gaps alone mark a requirement as non-compliant.

### 1.5 Infrastructure Compliance
**ASD reference:** Infrastructure Architecture

Check that the requirement:
- Can be hosted on the infrastructure described in the ASD
- Does not require new infrastructure components (new cloud services, new regions, new network zones) not in the ASD
- Respects defined environment boundaries (dev, staging, prod)

### 1.6 Architectural Integrity Impact
**ASD reference:** Constraints → Specification

Assess whether the requirement:
- Introduces technical debt not sanctioned by the ASD
- Violates ASD-documented constraints (technology bans, compliance mandates, cost boundaries)
- Degrades maintainability of the existing architecture

## Area 2: Component Architecture Mapping

**Goal:** Map each requirement to concrete ASD architectural components to confirm they exist and can fulfill the requirement.

### 2.1 PBC Mapping

**ASD reference:** Software Architecture → Packaged Business Capabilities (PBC Diagram)

For each requirement, identify:
- Which PBC(s) in the ASD will own or execute this capability
- Whether the PBC's defined role and scope covers this requirement
- Whether the PBC already exists or whether the requirement is implicitly creating a new one (which would be a critical gap)

**Checklist:**
- [ ] Requirement maps to ≥1 named PBC in the ASD
- [ ] The PBC's documented scope includes this capability
- [ ] No new PBC is being implicitly created

### 2.2 Data Sources Compliance
**ASD reference:** Data Strategy → Key Data Sources

Verify:
- The data the requirement reads/writes is stored in an ASD-documented data source
- The requirement does not introduce a new data store not described in the ASD
- Data flows between PBCs comply with the ASD's data strategy

**Checklist:**
- [ ] All data entities touched by the requirement have a home in the ASD's data strategy
- [ ] No new database, cache, or storage technology is being added
- [ ] Data ownership between PBCs is respected

### 2.3 Service Dependencies
**ASD reference:** Integration Strategy → Key Integrations

Map:
- All service-to-service calls the requirement introduces or relies on
- That each dependency is a documented integration in the ASD
- That the dependency direction aligns with the ASD's integration topology

**Checklist:**
- [ ] All service calls reference documented ASD integrations
- [ ] Dependency direction does not create circular dependencies not present in ASD
- [ ] Spec versions and contracts are respected

---

## Area 3: Quality Attributes & NFR Validation

**Goal:** Confirm that the requirement can be implemented while meeting the ASD's non-functional targets.

### 3.1 Performance Target Alignment
**ASD reference:** Non-Functional Requirements → Performance and Scalability

Assess whether the requirement:
- Can meet ASD-defined SLOs (e.g., response time, throughput)
- Doesn't degrade existing performance SLOs of the components it touches
- Has been scoped in a way that allows the ASD's performance patterns to apply

**Red flags:**
- Requirement calls for synchronous processing of large data volumes where ASD mandates async
- Requirement adds N+1 query risks in a performance-sensitive path

### 3.2 Security Pattern Compliance
**ASD reference:** Non-Functional Requirements → Security and Privacy

Verify:
- Authentication and authorization approach follows ASD-defined security patterns
- Data handling complies with ASD privacy requirements (encryption at rest/in transit, PII handling)
- No new security surfaces are introduced without ASD coverage

**Checklist:**
- [ ] Auth/authz mechanism matches ASD security patterns
- [ ] PII and sensitive data handled per ASD privacy specification
- [ ] No new ports, endpoints, or access paths bypassing ASD security controls

### 3.3 Scalability & Usability Fit
**ASD reference:** Performance and Scalability (for Scalability) + Operational Requirements (for Usability)

For scalability:
- Does the requirement's load profile fit within ASD-defined scaling strategies?
- Does it require new auto-scaling rules or infrastructure capacity not in the ASD?

For usability:
- Are operational requirements (observability, logging, alerting) met per ASD operational standards?
- Can the requirement be monitored and operated within existing tooling defined in the ASD?

---

## Area 4: Gap Analysis & Severity Classification

**Goal:** Consolidate all validation gaps and assess their severity.

### Gap Severity Levels

| Severity | Definition | Characteristics |
|----------|------------|-----------------|
| **Critical** | Requirement fundamentally violates ASD constraints or requires a new ASD component | New architecture pattern needed; new technology not in stack; new external integration; new PBC required; new data store needed; ASD constraint must be relaxed |
| **Major** | Requirement deviates from ASD patterns in significant ways | Uses documented components but in non-standard ways; stretches existing patterns; partial compliance with multiple minor issues |
| **Minor** | Small deviation or ambiguity that can be resolved at implementation level within ASD | Unclear specification in requirement; minor implementation detail not explicitly covered; edge case not documented |
| **None** | Full compliance with ASD | All checks pass; requirement maps cleanly to existing architecture |

### Gap Identification Examples

**Critical gaps typically involve:**
- A new architecture pattern is required (Area 1.1)
- A new technology not in the approved stack is needed (Area 1.2)
- A new integration with an external system is required (Area 1.3)
- A new PBC must be created to own the capability (Area 2.1)
- A new data store or storage strategy is needed (Area 2.2)
- NFR targets cannot be met within existing ASD patterns (Area 3)
- An ASD constraint must be relaxed (Area 1.6)

**Major gaps typically involve:**
- Using existing components in ways not explicitly documented
- Performance impacts that approach but don't violate SLO limits
- Security patterns that need clarification or extension
- Data flows that cross PBC boundaries in new ways

**Minor gaps typically involve:**
- Ambiguity in requirement wording vs. ASD terminology
- Edge cases not explicitly documented in ASD
- Implementation details left to development team discretion

### Consolidation Checklist

Before finalizing the compliance report, confirm:
- [ ] All four validation areas have been assessed for every requirement
- [ ] Every gap has a severity and affected ASD section cited
- [ ] Compliance status is clear: Compliant or Non-Compliant (with gap details)
- [ ] All findings cite specific ASD sections, not general principles
