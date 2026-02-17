"""
Scoring rubric with anchor examples for each dimension at each quality level.

Following Step 1.3 of the research plan: GQM operationalization with
2-3 worked anchor examples per quality level per dimension.

These examples serve as the codebook for human annotation (Phase 2)
and as few-shot examples for LLM scoring (Phase 3).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnchorExample:
    """A worked example at a specific quality level for a dimension."""

    score: int
    excerpt: str  # ADR excerpt demonstrating this quality level
    annotation_notes: str  # Explanation of why this score was assigned


@dataclass(frozen=True)
class DimensionRubric:
    """Complete rubric for a single dimension, including anchor examples."""

    dimension_id: str
    scoring_instructions: str
    anchor_examples: list[AnchorExample]


# ---------------------------------------------------------------------------
# Anchor examples for each dimension
# ---------------------------------------------------------------------------

SCORING_RUBRIC: dict[str, DimensionRubric] = {
    "A1": DimensionRubric(
        dimension_id="A1",
        scoring_instructions=(
            "Evaluate whether all relevant sections are present and contain substantive "
            "content. Mandatory sections: Context/Problem Statement, Decision (or Considered "
            "Options + Decision Outcome), Rationale. Expected sections: Consequences (Pros/Cons). "
            "Optional: Decision Drivers, Confirmation, More Information/Links. "
            "A section with only a placeholder or single generic sentence counts as absent."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt=(
                    "# Use React\n\n"
                    "We decided to use React for the frontend."
                ),
                annotation_notes=(
                    "Score 1: Only a title and a one-line decision. No context, no rationale, "
                    "no consequences. Missing all mandatory sections except a bare decision statement."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "# Use PostgreSQL for the Database\n\n"
                    "## Context\n"
                    "We need a database.\n\n"
                    "## Decision\n"
                    "We will use PostgreSQL.\n\n"
                    "## Consequences\n"
                    "TBD"
                ),
                annotation_notes=(
                    "Score 2: All mandatory sections present but context is trivially short "
                    "(one sentence), consequences is a placeholder. No rationale depth, "
                    "no alternatives discussed."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "# Use Docker for Containerization\n\n"
                    "## Context\n"
                    "Our application currently runs directly on VMs, making deployment "
                    "inconsistent across environments. We need a containerization strategy "
                    "to ensure reproducible builds.\n\n"
                    "## Decision\n"
                    "We will containerize all services using Docker.\n\n"
                    "## Rationale\n"
                    "Docker provides consistent environments across dev, staging, and production. "
                    "Our team already has Docker experience.\n\n"
                    "## Consequences\n"
                    "### Pros\n"
                    "- Consistent deployment across environments\n"
                    "- Faster onboarding for new developers\n\n"
                    "### Cons\n"
                    "- Additional complexity in orchestration\n"
                    "- Image size management overhead"
                ),
                annotation_notes=(
                    "Score 3: All mandatory sections present with substantive content. "
                    "Context explains the problem, decision is clear, rationale given, "
                    "consequences include both pros and cons. Missing: decision drivers, "
                    "alternatives considered, confirmation, links."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "# ADR-005: Use gRPC for Inter-Service Communication\n\n"
                    "## Status\nAccepted\n\n"
                    "## Context and Problem Statement\n"
                    "Our microservices currently communicate via REST/JSON over HTTP/1.1. "
                    "As we scale to 15+ services, latency and payload overhead become "
                    "significant. We need a more efficient inter-service protocol.\n\n"
                    "## Decision Drivers\n"
                    "- Latency requirements: <50ms p99 for internal calls\n"
                    "- Strong typing across 3 language stacks (Go, Python, Java)\n"
                    "- Backward compatibility for evolving APIs\n\n"
                    "## Considered Options\n"
                    "1. REST/JSON (status quo)\n"
                    "2. gRPC with Protocol Buffers\n"
                    "3. Apache Thrift\n\n"
                    "## Decision Outcome\n"
                    "Chosen option: gRPC with Protocol Buffers, because it meets our latency "
                    "requirements, provides strong typing across all three language stacks, "
                    "and has the strongest ecosystem support.\n\n"
                    "## Consequences\n"
                    "### Pros\n"
                    "- 3-10x reduction in serialization overhead vs JSON\n"
                    "- Generated client/server stubs reduce boilerplate\n"
                    "- Native streaming support for real-time features\n\n"
                    "### Cons\n"
                    "- Not human-readable on the wire (harder debugging)\n"
                    "- Team needs Protocol Buffers training (~2 weeks)\n"
                    "- Browser clients need grpc-web proxy\n\n"
                    "## Links\n"
                    "- Related to ADR-003 (Microservice Architecture)\n"
                    "- gRPC benchmarks: https://grpc.io/docs/guides/benchmarking/"
                ),
                annotation_notes=(
                    "Score 4: Fully complete. Has metadata (status), clear context with "
                    "architectural significance, explicit decision drivers with measurable "
                    "criteria, three considered options, decision outcome with because-clause, "
                    "specific consequences (both pros and cons with concrete details), and "
                    "links to related ADRs and external references."
                ),
            ),
        ],
    ),
    "A2": DimensionRubric(
        dimension_id="A2",
        scoring_instructions=(
            "Evaluate structural adherence to a recognized ADR template. Check heading "
            "hierarchy (H1 for title, H2 for sections), section ordering, metadata presence "
            "(status, date, deciders), and markdown formatting quality."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt=(
                    "Database Decision\n\n"
                    "We need a database for our project. After some research, we decided to "
                    "use MongoDB because it is flexible and easy to use. There might be some "
                    "performance issues but we think it will work fine."
                ),
                annotation_notes=(
                    "Score 1: No headings, no sections, no markdown formatting. "
                    "Plain text paragraph that cannot be mapped to any ADR template."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "# MongoDB for Data Storage\n\n"
                    "Context: We need a flexible database.\n\n"
                    "Decision: Use MongoDB.\n\n"
                    "Why: It's schema-less and good for our use case.\n\n"
                    "- Pro: Flexible schema\n"
                    "- Con: No joins"
                ),
                annotation_notes=(
                    "Score 2: Has a title heading but sections use inconsistent labeling "
                    "(inline labels instead of H2 headings). 'Why' is non-standard. "
                    "No metadata. Lists not in proper section."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "# Use MongoDB for Data Storage\n\n"
                    "## Context\n"
                    "We need a flexible database for our product catalog.\n\n"
                    "## Decision\n"
                    "We will use MongoDB.\n\n"
                    "## Rationale\n"
                    "Schema flexibility suits our evolving data model.\n\n"
                    "## Consequences\n"
                    "### Pros\n- Flexible schema\n### Cons\n- No native joins"
                ),
                annotation_notes=(
                    "Score 3: Proper H1 title, H2 sections, H3 sub-sections. "
                    "Follows recognizable template order. Minor issue: no metadata "
                    "(status, date). Markdown formatting is correct."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "# ADR-012: Use MongoDB for Product Catalog Storage\n\n"
                    "## Status\nAccepted\n\n"
                    "## Date\n2024-03-15\n\n"
                    "## Deciders\nBackend team, Tech Lead\n\n"
                    "## Context and Problem Statement\n[...]\n\n"
                    "## Decision Drivers\n[...]\n\n"
                    "## Considered Options\n[...]\n\n"
                    "## Decision Outcome\n[...]\n\n"
                    "## Consequences\n### Pros\n[...]\n### Cons\n[...]\n\n"
                    "## More Information\n[...]"
                ),
                annotation_notes=(
                    "Score 4: Full MADR compliance. Numbered ADR title, all metadata fields "
                    "(status, date, deciders), complete section set in standard order, "
                    "correct heading hierarchy, proper markdown formatting throughout."
                ),
            ),
        ],
    ),
    "B1": DimensionRubric(
        dimension_id="B1",
        scoring_instructions=(
            "Evaluate the quality of the context/problem statement. Look for: clear "
            "articulation of the problem, architectural significance, project-specific "
            "details (not generic), and identification of forces/constraints/drivers."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt="## Context\nWe need a framework.",
                annotation_notes=(
                    "Score 1: Single vague sentence. No problem articulation, no "
                    "architectural significance, no drivers or constraints."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Context\n"
                    "As a web developer, I need to choose a CSS framework for styling "
                    "the website. There are many options available and I need to pick one."
                ),
                annotation_notes=(
                    "Score 2: States a generic need but provides no project-specific details. "
                    "No drivers, no constraints, no architectural significance explained."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Context\n"
                    "Our e-commerce platform currently handles 10,000 orders/day with a "
                    "monolithic architecture. We are experiencing database bottlenecks during "
                    "peak hours. We need to decide on a caching strategy to reduce database "
                    "load while maintaining data consistency for inventory management."
                ),
                annotation_notes=(
                    "Score 3: Project-specific with concrete details (order volume, current "
                    "architecture). Two implicit drivers (performance, consistency). "
                    "A reader understands the situation. Could improve by explicitly "
                    "listing drivers and stating architectural significance."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Context and Problem Statement\n"
                    "Our SaaS platform serves 500+ enterprise clients across 12 regions. "
                    "Current authentication uses session-based auth stored in a single Redis "
                    "instance, creating a SPOF and limiting horizontal scaling. With SOC2 "
                    "compliance requirements and the planned migration to microservices "
                    "(see ADR-003), we need a stateless, distributed authentication mechanism.\n\n"
                    "## Decision Drivers\n"
                    "- Must support horizontal scaling across 3+ regions\n"
                    "- SOC2 compliance: token expiration, audit logging\n"
                    "- Developer experience: minimal changes to existing 40+ API endpoints\n"
                    "- Performance: <10ms auth overhead per request"
                ),
                annotation_notes=(
                    "Score 4: Rich, project-specific context with quantified details. "
                    "Architectural significance clear (SPOF, scaling limitation). "
                    "Four explicit, measurable decision drivers. References related ADR. "
                    "A new team member would fully understand the situation."
                ),
            ),
        ],
    ),
    "B2": DimensionRubric(
        dimension_id="B2",
        scoring_instructions=(
            "Evaluate the coverage and quality of alternatives considered. "
            "Check for: ≥2 genuinely distinct alternatives, sufficient description "
            "of each, and whether alternatives are seriously evaluated or are strawmen."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt=(
                    "## Decision\n"
                    "We will use React for the frontend."
                ),
                annotation_notes=(
                    "Score 1: Only one option presented (the chosen one). No alternatives "
                    "discussed whatsoever. Violates the minimum requirement."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Considered Options\n"
                    "1. React\n"
                    "2. Angular\n"
                    "3. Vue.js\n\n"
                    "We chose React."
                ),
                annotation_notes=(
                    "Score 2: Three alternatives listed but described in zero detail. "
                    "No evaluation criteria applied. Reader cannot understand the "
                    "differences or why React was chosen."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Considered Options\n"
                    "### Option 1: REST API\n"
                    "Traditional HTTP-based API using JSON. Well-understood by the team.\n\n"
                    "### Option 2: GraphQL\n"
                    "Query language for APIs that allows clients to request exactly the "
                    "data they need. Reduces over-fetching.\n\n"
                    "We chose REST because our API surface is simple and well-defined."
                ),
                annotation_notes=(
                    "Score 3: Two distinct alternatives with adequate descriptions. "
                    "Reader understands each approach. Brief rationale for choice. "
                    "Could improve with more options and systematic evaluation."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Considered Options\n"
                    "### Option 1: REST/JSON (Status Quo)\n"
                    "Continue with current REST API design. Familiar to all developers, "
                    "extensive tooling (Swagger/OpenAPI). Limited real-time capabilities.\n\n"
                    "### Option 2: gRPC\n"
                    "Binary protocol with Protocol Buffers. 3-10x faster serialization. "
                    "Strong typing but requires proxy for browser clients.\n\n"
                    "### Option 3: GraphQL\n"
                    "Flexible querying, reduces over/under-fetching. Higher server-side "
                    "complexity and N+1 query risks.\n\n"
                    "| Criterion | REST | gRPC | GraphQL |\n"
                    "|-----------|------|------|---------|\n"
                    "| Latency | Medium | Low | Medium |\n"
                    "| Team familiarity | High | Low | Medium |\n"
                    "| Browser support | Native | Proxy needed | Native |"
                ),
                annotation_notes=(
                    "Score 4: Three well-described, genuinely distinct alternatives. "
                    "Each option has specific pros/cons. Systematic comparison using "
                    "evaluation criteria in a table. Rejected options would have clear "
                    "reasoning based on the comparison."
                ),
            ),
        ],
    ),
    "B3": DimensionRubric(
        dimension_id="B3",
        scoring_instructions=(
            "Evaluate the depth and quality of the rationale/justification. Look for: "
            "explicit because-clauses, references to decision drivers, tradeoff "
            "acknowledgment, evidence (benchmarks, experience, references), and "
            "explanation of why alternatives were rejected."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt="## Decision\nWe chose MongoDB because it is the best option.",
                annotation_notes=(
                    "Score 1: Assertion without reasoning. 'Best option' provides "
                    "no actual rationale. Decision appears arbitrary."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Rationale\n"
                    "We chose React because it is popular, has a large community, "
                    "and is well-supported by Facebook. It is also easy to learn."
                ),
                annotation_notes=(
                    "Score 2: Generic reasons not tied to project context. 'Popular' "
                    "and 'large community' are not project-specific drivers. "
                    "No tradeoff discussion or comparison to alternatives."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Rationale\n"
                    "We chose PostgreSQL over MongoDB because our data model is highly "
                    "relational (orders → line items → products) and we need ACID "
                    "transactions for payment processing. While MongoDB offers schema "
                    "flexibility, our schema is stable and relational integrity is "
                    "more important for our use case."
                ),
                annotation_notes=(
                    "Score 3: References project-specific drivers (relational model, "
                    "ACID for payments). Acknowledges tradeoff (flexibility vs. integrity). "
                    "Explains why alternative was less suitable. Could improve with "
                    "quantitative evidence."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Rationale\n"
                    "We chose gRPC over REST because:\n"
                    "1. **Latency**: Our benchmarks show gRPC achieves 8ms p99 vs 35ms "
                    "for REST/JSON on our typical payload (2KB order objects), meeting "
                    "our <50ms target with headroom.\n"
                    "2. **Type safety**: Proto definitions generate clients for all three "
                    "of our language stacks, reducing integration bugs that cost us ~40 "
                    "engineering hours last quarter.\n"
                    "3. **Backward compatibility**: Proto3 field numbering provides "
                    "forward/backward compatibility without API versioning.\n\n"
                    "We accepted the tradeoff of reduced debuggability (binary protocol) "
                    "by investing in gRPC reflection and grpcurl tooling. The 2-week "
                    "team training cost is justified by the long-term velocity gains."
                ),
                annotation_notes=(
                    "Score 4: Exemplary. Each driver from the context is explicitly "
                    "addressed with evidence (benchmarks, cost data). Tradeoffs "
                    "acknowledged with mitigation. Training cost honestly assessed. "
                    "Clear why alternatives were rejected against each criterion."
                ),
            ),
        ],
    ),
    "B4": DimensionRubric(
        dimension_id="B4",
        scoring_instructions=(
            "Evaluate the specificity and balance of stated consequences. Check for: "
            "both positive and negative consequences, project-specific detail "
            "(not generic), actionability, and coverage of different impact areas "
            "(technical, process, team)."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt="(No consequences section present)",
                annotation_notes="Score 1: Consequences completely absent.",
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Consequences\n"
                    "### Pros\n"
                    "- Better performance\n"
                    "- More scalable\n"
                    "- Modern technology\n\n"
                    "### Cons\n"
                    "- Learning curve"
                ),
                annotation_notes=(
                    "Score 2: Consequences listed but entirely generic. 'Better performance' "
                    "and 'more scalable' could apply to any technology. No project-specific "
                    "detail. Cons severely underrepresented (single item)."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Consequences\n"
                    "### Pros\n"
                    "- Consistent deployment across our 3 environments (dev, staging, prod)\n"
                    "- Faster onboarding: new devs can run the full stack in <30 minutes\n\n"
                    "### Cons\n"
                    "- Adds ~200MB to each service image; need to optimize base images\n"
                    "- Team needs Docker training (3 of 8 developers have no experience)"
                ),
                annotation_notes=(
                    "Score 3: Project-specific consequences with concrete details "
                    "(number of environments, onboarding time, image size, team skill gap). "
                    "Both pros and cons covered. Could improve with process/organizational "
                    "impact and mitigation strategies."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Consequences\n"
                    "### Positive\n"
                    "- **Performance**: 3-10x serialization speedup reduces inter-service "
                    "latency, directly addressing our <50ms p99 target\n"
                    "- **Developer productivity**: Generated stubs eliminate ~2000 lines "
                    "of boilerplate API client code across 3 codebases\n"
                    "- **API evolution**: Proto field numbering allows non-breaking changes "
                    "without API versioning overhead\n\n"
                    "### Negative\n"
                    "- **Debugging**: Binary protocol requires grpcurl/reflection setup; "
                    "mitigation: add grpc-web proxy for dev environment inspection\n"
                    "- **Team ramp-up**: ~2 weeks of Protocol Buffers training for 5 devs; "
                    "planned for Sprint 14\n"
                    "- **Browser clients**: Need grpc-web proxy layer; adds 1 component "
                    "to frontend deployment pipeline"
                ),
                annotation_notes=(
                    "Score 4: Comprehensive, project-specific consequences covering "
                    "performance, productivity, and process. Concrete metrics and "
                    "quantified impacts. Negative consequences include mitigation "
                    "strategies with timeline. Covers technical, team, and process impacts."
                ),
            ),
        ],
    ),
    "B5": DimensionRubric(
        dimension_id="B5",
        scoring_instructions=(
            "Evaluate how clearly and specifically the decision is stated. Check for: "
            "explicit identification of the chosen option, scope of the decision, "
            "actionability (can a developer implement based on this?), and decision status."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt="We will use a modern framework for the frontend.",
                annotation_notes=(
                    "Score 1: No specific technology identified. 'Modern framework' is "
                    "completely ambiguous. A developer cannot act on this."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Decision\n"
                    "We will use React for the frontend because it is widely adopted."
                ),
                annotation_notes=(
                    "Score 2: Specific technology named but no version, no scope "
                    "(which part of the frontend?), no status. Minimal actionability."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Decision Outcome\n"
                    "Chosen option: PostgreSQL for the main application database. "
                    "We will migrate from SQLite during the next sprint."
                ),
                annotation_notes=(
                    "Score 3: Clear decision with specific technology and scope "
                    "(main application database). Migration timeline mentioned. "
                    "Missing: version, status field, detailed scope."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Decision Outcome\n"
                    "**Status**: Accepted\n\n"
                    "Chosen option: gRPC with Protocol Buffers (proto3) for all internal "
                    "service-to-service communication. External-facing APIs will continue "
                    "using REST/JSON (see ADR-008). Migration will proceed service-by-service "
                    "starting with the Order Service in Sprint 15."
                ),
                annotation_notes=(
                    "Score 4: Precise decision with technology + version (proto3), "
                    "clear scope (internal only, external excluded), status indicated, "
                    "migration plan with timeline. References related ADR for scope boundary. "
                    "Any developer could act on this immediately."
                ),
            ),
        ],
    ),
    "C1": DimensionRubric(
        dimension_id="C1",
        scoring_instructions=(
            "Evaluate linguistic quality, logical flow, and editorial polish. Consider "
            "grammar, clarity of expression, logical progression between sections, "
            "appropriate use of technical language, and document length (neither "
            "excessively verbose nor too terse)."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt=(
                    "The using of this technology will be make our system more better "
                    "and efficiency. When we deploying the application it can make "
                    "the performance increase very much and the developer team will "
                    "easy to understanding the code."
                ),
                annotation_notes=(
                    "Score 1: Numerous grammatical errors throughout. Unclear what "
                    "technology is referenced. Incoherent sentence structure makes "
                    "content difficult to understand."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Context\n"
                    "We are looking for a solution. Our current system has some problems. "
                    "The system is slow sometimes. We need something better.\n\n"
                    "## Decision\n"
                    "After research, we use Redis. It provides caching mechanism that "
                    "store data in memory and retrieve fast."
                ),
                annotation_notes=(
                    "Score 2: Understandable but vague and simplistic. Short, choppy "
                    "sentences lack detail. Grammatically mostly correct but reads "
                    "as rough draft quality."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Context\n"
                    "Our application currently queries the database directly for every "
                    "API request, resulting in response times that exceed our 200ms target "
                    "during peak traffic. We need a caching layer to reduce database load.\n\n"
                    "## Decision\n"
                    "We will use Redis as an in-memory cache between the API layer and "
                    "the database, with a TTL-based invalidation strategy."
                ),
                annotation_notes=(
                    "Score 3: Clear, professional language. Logical flow from problem "
                    "to solution. Technical terms used appropriately. Minor: could "
                    "benefit from smoother transitions between sections."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Context and Problem Statement\n"
                    "Our e-commerce API serves product catalog data to 50,000 concurrent "
                    "users during flash sales. Direct database queries result in 800ms "
                    "p95 latency—4x our 200ms SLA. Analysis shows 85% of catalog reads "
                    "hit identical product records within a 5-minute window, making this "
                    "an ideal caching candidate."
                ),
                annotation_notes=(
                    "Score 4: Polished, concise, and data-driven writing. Each sentence "
                    "adds information. Logical progression from scale → problem → analysis → "
                    "opportunity. Technical language precise and consistent. Could serve "
                    "as a writing exemplar."
                ),
            ),
        ],
    ),
    "C2": DimensionRubric(
        dimension_id="C2",
        scoring_instructions=(
            "Evaluate internal consistency of the document. Check for: contradictions "
            "between sections, consistent terminology, alignment between stated drivers "
            "and evaluation criteria, and whether the decision logically follows "
            "from the analysis."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt=(
                    "## Context\n"
                    "Performance is our top priority. Response time must be under 100ms.\n\n"
                    "## Decision\n"
                    "We chose Django because it has excellent documentation and a large "
                    "community.\n\n"
                    "## Consequences\n"
                    "### Pros\n- Easy to learn\n### Cons\n- Known to be slower than "
                    "alternatives for high-performance applications"
                ),
                annotation_notes=(
                    "Score 1: Direct contradiction: context says performance is top priority, "
                    "but the decision ignores performance entirely. Consequences even admit "
                    "the choice is slower. Decision does not follow from the stated drivers."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## Context\n"
                    "We need a scalable message broker for our event-driven architecture.\n\n"
                    "## Decision\n"
                    "We will use RabbitMQ for our messaging needs.\n\n"
                    "## Rationale\n"
                    "Kafka provides excellent throughput for our event streaming requirements."
                ),
                annotation_notes=(
                    "Score 2: Inconsistency between decision (RabbitMQ) and rationale "
                    "(discusses Kafka). Likely a copy-paste error but creates confusion "
                    "about what was actually decided."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Context\n"
                    "We need a container orchestration platform for our microservices.\n\n"
                    "## Decision Drivers\n"
                    "- Ease of deployment\n- Cost efficiency\n- Team expertise\n\n"
                    "## Decision\n"
                    "We will use Kubernetes.\n\n"
                    "## Rationale\n"
                    "Kubernetes offers robust deployment capabilities and our DevOps team "
                    "has prior experience with it."
                ),
                annotation_notes=(
                    "Score 3: Mostly consistent. Decision references two of three drivers "
                    "(deployment, expertise) but doesn't address cost efficiency. "
                    "No contradictions. Terminology is consistent."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Decision Drivers\n"
                    "1. Latency <50ms p99\n"
                    "2. Multi-language support (Go, Python, Java)\n"
                    "3. Backward compatibility\n\n"
                    "## Rationale\n"
                    "gRPC addresses each driver:\n"
                    "1. Benchmarked at 8ms p99 (Driver 1: ✓)\n"
                    "2. Proto generates stubs for all three stacks (Driver 2: ✓)\n"
                    "3. Proto3 field numbering ensures compatibility (Driver 3: ✓)"
                ),
                annotation_notes=(
                    "Score 4: Perfect alignment between drivers and evaluation. "
                    "Each driver explicitly addressed in rationale with the same "
                    "numbering. Consistent terminology throughout. Decision is the "
                    "logical conclusion of the analysis."
                ),
            ),
        ],
    ),
    "C3": DimensionRubric(
        dimension_id="C3",
        scoring_instructions=(
            "Evaluate the presence and quality of traceable links to other artifacts. "
            "Check for: links to related ADRs, requirements/user stories, external "
            "documentation, benchmarks, and identification of affected components. "
            "Note: student ADRs may have limited traceability opportunities, so "
            "evaluate relative to what would be reasonable for the context."
        ),
        anchor_examples=[
            AnchorExample(
                score=1,
                excerpt="(No references, links, or mentions of any related artifacts)",
                annotation_notes=(
                    "Score 1: Complete isolation. No links to documentation, "
                    "no references to related decisions, no mention of affected components."
                ),
            ),
            AnchorExample(
                score=2,
                excerpt=(
                    "## More Information\n"
                    "For more details, see the official React documentation."
                ),
                annotation_notes=(
                    "Score 2: One generic reference without a URL. No links to "
                    "related ADRs, requirements, or specific documentation pages."
                ),
            ),
            AnchorExample(
                score=3,
                excerpt=(
                    "## Links\n"
                    "- [PostgreSQL documentation](https://www.postgresql.org/docs/)\n"
                    "- Related to ADR-003: Choice of ORM\n"
                    "- Affects: User Service, Order Service database schemas"
                ),
                annotation_notes=(
                    "Score 3: External documentation link, related ADR reference, "
                    "and identification of affected components. Provides reasonable "
                    "traceability for locating related information."
                ),
            ),
            AnchorExample(
                score=4,
                excerpt=(
                    "## Links\n"
                    "- Supersedes: ADR-002 (REST for inter-service communication)\n"
                    "- Related: ADR-003 (Microservice Architecture), ADR-008 (External API)\n"
                    "- Requirement: NFR-12 (Internal latency <50ms p99)\n"
                    "- gRPC benchmarks: https://grpc.io/docs/guides/benchmarking/\n"
                    "- Affected components: Order Service, Inventory Service, User Service\n"
                    "- Migration tracking: JIRA epic INFRA-456"
                ),
                annotation_notes=(
                    "Score 4: Rich traceability web. Supersedes relationship, multiple "
                    "related ADRs, requirement link, external evidence, affected components, "
                    "and project management tracking. Supports full decision archaeology."
                ),
            ),
        ],
    ),
}
