# **Architectural Analysis of Lazy-Loaded Tooling and Discovery Engines in the OpenCode AI Agent Ecosystem**

AI coding assistants designed for local terminal execution face a critical structural constraint: the systemic "Token Tax" associated with tool schema and instruction injection.1 In standard agent loops, Model Context Protocol (MCP) tool schemas and local skill configurations are loaded into the primary conversation context prior to processing the first user message.1 As an engineer's toolkit expands to accommodate complex, multi-project workflows requiring dozens of specialized skills and MCP servers, this eager loading model scales context consumption linearly.1 The resulting prompt bloat limits reasoning space, increases API costs, and triggers context-exhaustion failures on models with restrictive input thresholds.1  
Resolving this token tax requires decoupling asset registration from execution context.2 Transitioning to an on-demand, lazy-loaded paradigm ensures that extensive tool catalogs are exposed to the agent as lightweight metadata.2 Full schemas and operational parameters are resolved dynamically only when the language model determines that a specific asset is required for the task at hand.2 This report evaluates the current ecosystem of lazy-loading plugins, proxy tools, and experimental core features to establish a scalable runtime architecture for large-scale tool management.

## **Exhaustive Evaluation of Ecosystem Solutions**

A comparative analysis of community plugins, proxy engines, and native configurations highlights the trade-offs between specialized utility and architectural stability.

### **opencode-dynamic-skills**

* **Name and GitHub/npm Link:** npm: https://www.npmjs.com/package/opencode-dynamic-skills (derived from opencode-skillful and oh-my-openagent).6  
* **One-Sentence Description:** A high-performance, open-source OpenCode plugin designed to catalog local skills dynamically and load their operational scripts on demand without upfront context injection.6  
* **Maintenance Status:** Active, with the current v1.3.0 release delivering a complete architectural rewrite to resolve Node.js and Electron runtime bugs.6  
* **Skill Management Handling:** Lazy. The plugin scans configured directories at startup but only injects the core SKILL.md body and root-relative file manifests into the conversation history when explicitly triggered by natural language queries or direct slash commands.6  
* **MCP Server Handling:** Eager/Not Handled. This plugin is built exclusively for orchestrating local skill workspaces and does not manage, proxy, or route Model Context Protocol servers.6  
* **Pros and Cons:**  
  * *Pros:* Complete compatibility with current OpenCode plugin architectures; eliminates Bun-specific runtime compile issues; implements robust, root-relative file safety boundaries that prevent directory traversal attacks.6  
  * *Cons:* Lacks native MCP capabilities, requiring coordination with an external gateway to optimize remote tool servers.  
* **Verdict:** Recommended. It is the premier, community-maintained successor to the archived opencode-skillful package.

### **harshal-mcp-proxy**

* **Name and GitHub/npm Link:** GitHub: https://github.com/HarshalRathore/harshal-mcp-proxy (npm: https://www.npmjs.com/package/harshal-mcp-proxy).7  
* **One-Sentence Description:** A specialized, open-source Model Context Protocol proxy that consolidates multiple upstream MCP servers into a single background daemon, exposing them to agents via six compact meta-tools.8  
* **Maintenance Status:** Active, with stable releases published directly to the global npm registry.7  
* **Skill Management Handling:** Eager/Not Handled. It functions purely as an MCP proxy and does not inspect or manage local skill folders.  
* **How it Handles MCP Servers:** Lazy. Instead of exposing raw schemas for dozens of connected servers, the proxy registers six lightweight gateway tools (representing a baseline cost of \~375 tokens).8 Tool schemas are requested dynamically (gateway.describe) and executed (gateway.invoke) only when matching keyword queries are resolved via an in-memory search engine.8  
* **Pros and Cons:**  
  * *Pros:* Decreases MCP startup token footprints by up to 99%; runs as a centralized background service (systemd) to prevent process duplication and reduce RAM consumption when running multiple IDEs and terminal agents simultaneously 8; incorporates automatic output truncation and pagination.8  
  * *Cons:* Requires manual coordination of upstream JSON-RPC endpoints inside an external configuration file.7  
* **Verdict:** Recommended. It provides the most efficient pathway for managing over 50 MCP servers on local hardware.

### **OpenCode Native Lazy Loading (experimental.mcp\_lazy)**

* **Name and GitHub/npm Link:** GitHub: https://github.com/anomalyco/opencode (Specifically Pull Request \#12520 and Issue \#8625).5  
* **One-Sentence Description:** An experimental, core-level configuration option that prevents connected MCP server schemas from being automatically inlined, exposing an on-demand mcp\_search tool instead.5  
* **Maintenance Status:** Active on development branches; the original pull request was recently rebased and bug-fixed to align with modern upstream releases.9  
* **Skill Management Handling:** Eager. Native core skills are still statically parsed and injected into the default system prompt, maintaining a baseline overhead for local skill libraries.4  
* **How it Handles MCP Servers:** Lazy. When enabled via the experimental.mcp\_lazy config key, raw tool schemas are excluded from the initial payload.5 Available servers are listed as plain text in the system prompt, allowing the agent to discover, search, and call tools on-demand.5  
* **Pros and Cons:**  
  * *Pros:* Built directly into the OpenCode core, eliminating the need to deploy and manage external proxy engines; closely mirrors the deferred meta-tool pattern used by Claude Code and GPT-5.5  
  * *Cons:* Because it is experimental, it requires manual compilation from source forks to access rebased fixes 9; current iterations suffer from minor output fidelity degradation, converting rich multi-part responses (such as images or binary artifacts) into flat text representations.5  
* **Verdict:** Worth Testing. It represents the native future of OpenCode’s tool management but requires compilation.

### **oh-my-opencode-slim**

* **Name and GitHub/npm Link:** GitHub: https://github.com/alvinunreal/oh-my-opencode-slim.11  
* **One-Sentence Description:** A comprehensive multi-agent orchestration framework for OpenCode that distributes developer tasks among specialized, sandboxed subagents.11  
* **Maintenance Status:** Highly active, with consistent, structured releases (e.g., v1.0.7) and regular community contributions.13  
* **Skill Management Handling:** Eager but Partitioned. Skills are statically assigned to specific subagent prompts (e.g., assigning a code simplification skill exclusively to an advisor subagent).11  
* **How it Handles MCP Servers:** Eager but Partitioned. Connected MCP servers are hard-coded to specific specialized agents (e.g., restricting the web search MCP to the research agent).11  
* **Pros and Cons:**  
  * *Pros:* Decreases primary context bloat by dividing tool availability across distinct agent boundaries; provides robust background task scheduling, terminal-multiplexer integration, and built-in repository mapping skills.11  
  * *Cons:* Does not perform runtime-driven lazy-loading; tools are statically mapped at startup, meaning users must manually coordinate workflows across subagents.  
* **Verdict:** Worth Testing. It is highly effective for structuring large development projects, but it does not solve the need for dynamic, single-session tool discovery.

### **NadirClaw**

* **Name and GitHub/npm Link:** GitHub: https://github.com/NadirRouter/NadirClaw.15  
* **One-Sentence Description:** An open-source, self-hosted LLM routing gateway that intercepts API traffic to optimize prompt formatting and compact bloated context schemas before execution.15  
* **Maintenance Status:** Active, with frequent patches and high community engagement.15  
* **Skill Management Handling:** Eager/Not Handled.  
* **How it Handles MCP Servers:** Compacted. It does not defer schema loading at the client layer; instead, it intercepts outbound requests, compressing whitespaces, JSON blocks, and duplicated tool descriptions to achieve a 30% to 70% reduction in transmitted input tokens.15  
* **Pros and Cons:**  
  * *Pros:* Sits transparently at the networking boundary as an OpenAI-compatible proxy 15; implements intelligent, latency-optimized routing between cheap local models and premium reasoning engines.15  
  * *Cons:* Cannot prevent client-side context exhaustion or memory-related crashes, as the client still compiles and attempts to parse the massive raw schemas locally before transmission.4  
* **Verdict:** Worth Testing. It is an exceptional tool for API cost control, but it must be paired with local lazy-loading managers to resolve local client bloat.

### **@zenobius/opencode-skillful**

* **Name and GitHub/npm Link:** GitHub: https://github.com/zenobi-us/opencode-skillful.17  
* **One-Sentence Description:** The legacy on-demand skill discovery and injection plugin designed to resolve local skill scripts through semantic lookup tools.17  
* **Maintenance Status:** Archived and unmaintained, with no developmental activity in the last six months.  
* **Skill Management Handling:** Lazy. Discovers skill directories during initialization but defers full instruction injection until the user runs a dynamic loading command.17  
* **How it Handles MCP Servers:** Eager/Not Handled.  
* **Pros and Cons:**  
  * *Pros:* Pioneered the core on-demand skill pattern used within the ecosystem.17  
  * *Cons:* Contains a critical compile-time bug where Bun-specific modules are bundled into the final build, causing immediate runtime failures when loaded inside standard Node.js, Electron, or Windows environments.18  
* **Verdict:** Not Suitable.

## **Comparative Performance Metrics**

The table below contrasts the evaluated platforms across core performance vectors, operational costs, and scalability thresholds.

| System Identifier | Maintenance Status | Open Source License | Financial Cost | Skill Loading Efficiency | MCP Loading Efficiency | OpenCode Native Compatibility | Scalability (100+ Skills, 50+ MCPs) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **opencode-dynamic-skills** 6 | Highly Active (v1.3.0) 6 | MIT License 6 | Fully Free 6 | Excellent (On-Demand Fetching) 6 | None (Exclusively Manages Skills) 6 | Native Plugin Setup 6 | Scalable to 100+ skills 6 |
| **harshal-mcp-proxy** 7 | Active Community 7 | MIT License | Fully Free 7 | None (Exclusively Manages MCPs) | Excellent (99% Token Reduction) 7 | High (Requires Standard Config Mapping) 8 | Highly Scalable to 50+ servers 7 |
| **Native mcp\_lazy** 5 | Rebased Fork Active 9 | MIT License 19 | Fully Free | Poor (Eager Core Injection) 4 | Excellent (Centralized Search Tool) 5 | Experimental Core Option 5 | Scalable to 50+ servers 9 |
| **oh-my-opencode-slim** 11 | Highly Active (v1.0.7) 13 | MIT License 19 | Fully Free | Moderate (Static Partitioning) 11 | Moderate (Static Partitioning) 11 | High (Native Presets) 11 | Limited by hard-coded subagent presets 11 |
| **NadirClaw** 15 | Active (v1.0+) 15 | MIT License 15 | Fully Free 15 | None | Moderate (Lossless Text Compaction) 15 | Sits at API Gateway Boundary 15 | Limited (Schemas still loaded, only compressed) 15 |

To illustrate the direct impact of these choices on API usage and conversational overhead, the following table details the context window consumption at session initialization:

| Configuration Strategy | Approximate Overhead at Session Initialization | Resulting Context Window Availability (262K Limit) | Causal Impact on Large-Scale Environments |
| :---- | :---- | :---- | :---- |
| **Unoptimized Default** (1,300+ skills, 50+ MCPs) | \~198,000 tokens 1 | \~24.4% remaining | Immediate context exhaustion; frequent BadRequestErrors 4 |
| **Static Partitioning** (oh-my-opencode-slim) | \~45,000 tokens 11 | \~82.8% remaining | Stable execution; requires manual agent-switching overhead 11 |
| **API Compaction Gateway** (NadirClaw) | \~115,000 tokens 15 | \~56.1% remaining | Slower context growth; fails to prevent client-side parsing spikes 4 |
| **Dynamic Lazy Stack** (dynamic-skills \+ mcp-proxy) | \~2,500 tokens 2 | \~99.0% remaining | Highly stable; context scales dynamically on-demand 6 |

## **OpenCode Roadmaps, Structural Token Tax, and Core Regressions**

An analysis of OpenCode’s developmental trajectory reveals deep-seated architectural patterns and technical regressions that impact power users.

### **The Mechanism of Core Skill Duplication**

In the standard OpenCode core, skill information is compiled twice for every LLM request.10 First, the full XML instruction block of every active skill is compiled within the system prompt via the SystemPrompt.skills() class.10 Second, the identical instruction block is appended directly into the primary skill tool’s description field.10 This duplicate mapping is designed to ensure that models read skill payloads regardless of whether they prioritize system guidelines or tool registries.10  
However, in large-scale configurations, this duplication acts as an immediate prompt tax, consuming 5,000 to 7,000 tokens per request for a simple library of only 30 skills.10 When a comprehensive suite like opencode-skills-antigravity is added, this dual-injection mechanism consumes over 148,000 tokens before processing the user's first query, rendering advanced reasoning models inoperable.4 Despite multiple community requests (Issue \#13188, Issue \#22236) urging the core team to restrict injection to a single entry point or transition to a summary-only model preview (Issue \#27439), as of mid-2026, the core skill framework remains statically eager.2

### **Native MCP Auto-Discovery Limitations**

OpenCode's native tool architecture relies on a static internal tool registry that governs core operations like bash, read, and write.21 The platform does *not* natively auto-discover local or remote MCP servers without explicit definitions inside the opencode.jsonc file.21 A common integration failure occurs when users configure external MCP routing targets using the mcpServers key (the standard convention for VS Code, Cline, and Cursor).21 OpenCode silently ignores this parameter, requiring the explicit mcp root key to register external tooling 21:

JSON  
{  
  "mcp": {  
    "target-server": {  
      "type": "remote",  
      "url": "http://127.0.0.1:8765/mcp/target",  
      "enabled": true  
    }  
  }  
}

Furthermore, in non-interactive execution modes, any external file or directory tool calls routed via MCP will fail silently or be auto-rejected unless explicitly whitelisted in the platform's singular permissions block (using the correct singular permission key rather than the plural permissions schema).21

### **Core Compiler and Immutability Regressions**

Recent platform upgrades (v1.14.34+) introduced a severe runtime regression that directly collides with community orchestrator plugins like oh-my-openagent.22 This regression stems from two parallel bugs:

1. **Immer State Freezing in EventV2:** When experimental features are enabled (OPENCODE\_EXPERIMENTAL=true), OpenCode processes tool calls through a new event framework.22 This framework passes raw tool arguments directly by reference into Immer's produce() state-updater.23 Immer subsequently calls Object.freeze() on the produced state tree to enforce structural immutability, freezing the original arguments object.23 Any plugin hook that attempts to modify tool arguments before execution—such as an agent rewriting shell variables in tool.execute.before—immediately crashes the process, throwing a fatal TypeError: Attempted to assign to readonly property.22  
2. **Bun Minifier Stream Mutation Crash:** In parallel, recent Effect-TS dependency updates (specifically transitioning to 4.0.0-beta.59) refactored the binary utility mkUint8Array to use a mutable fold accumulator for faster data parsing.24 When OpenCode compiles its release binaries using Bun's minification flags (bun build \--compile \--minify), JavaScript engine optimizations cause the mutable accumulator to freeze between iterations.24 Any subsequent binary file stream collection—such as the git cat-file operations that occur during multi-turn agent sessions—fails instantly.24

These regressions require power users to run their environments with minification disabled, pin dependencies to safe historical ranges (e.g., 4.0.0-beta.57), or bypass experimental flags entirely (OPENCODE\_EXPERIMENTAL=false) to ensure stable runtime executions.23

## **Ranked Recommendations and Migration Roadmap**

To manage 100+ skills and 50+ MCP servers without encountering token bloat, runtime crashes, or memory exhaustion, a decoupled architectural strategy is required.

                  ┌────────────────────────────────────────┐  
                  │          OpenCode CLI Session          │  
                  │       \~/.config/opencode/opencode.json  │  
                  └───────────────────┬────────────────────┘  
                                      │  
             ┌────────────────────────┴────────────────────────┐  
             ▼                                                 ▼  
┌─────────────────────────────┐                 ┌─────────────────────────────┐  
│  opencode-dynamic-skills    │                 │      harshal-mcp-proxy      │  
│  (Skill Loading Layer)      │                 │     (Local MCP Gateway)     │  
└────────────┬────────────────┘                 └──────────────┬──────────────┘  
             │                                                 │  
             ▼                                                 ▼  
                     
 \~/.config/opencode/dynamic-skills/               50+ Local/Remote MCPs  
  (Metadata-only Index Loading)                    (Resolved to 6 Meta-Tools)

By separating skill orchestration from the Model Context Protocol network layer, this hybrid architecture scales tool capabilities while keeping startup context minimal.

### **Ranked Core Solutions**

1. **opencode-dynamic-skills:** The premier choice for local skill isolation. It fixes the legacy Bun compiler bugs of opencode-skillful while implementing safe, root-relative file traversal.6  
2. **harshal-mcp-proxy:** The most robust solution for massive MCP environments, consolidating multiple background processes into a single daemon and replacing large tool schemas with an on-demand meta-tool interface.8  
3. **OpenCode Native experimental.mcp\_lazy:** A strong native option for users who want to avoid third-party proxy daemons, though it currently requires manually building OpenCode from community-rebased forks.5

### **Suggested Step-by-Step Migration Roadmap**

Follow this migration path to transition from a legacy, unmaintained opencode-skillful setup to the recommended lazy-loaded architecture.

#### **Step 1: Clean and Isolate the Workspace**

The default OpenCode startup scanner eagerly indexes any folders within the default paths (\~/.config/opencode/skills/ or \~/.claude/skills/), causing automatic prompt injection.2 To prevent this, isolate your custom skills:

* Create a dedicated, non-standard directory:  
  Bash  
  mkdir \-p \~/.config/opencode/dynamic-skills-workspace

* Relocate all your SKILL.md folders from standard paths into this new directory.2  
* This immediately stops the core parser from inlining descriptions, reducing your initialization overhead from over 140,000 tokens to roughly 9,000 tokens.2

#### **Step 2: Uninstall the Legacy Skillful Plugin**

Remove the archived package and clear its cached artifacts to prevent Bun-specific compilation conflicts:

Bash  
npm uninstall \-g @zenobius/opencode-skillful

#### **Step 3: Install and Configure opencode-dynamic-skills**

Install the updated rewrite globally to make its tools accessible to the agent runtime:

Bash  
npm install \-g opencode-dynamic-skills@latest

On startup, the plugin automatically creates a configuration file at \~/.config/opencode/opencode-dynamic-skills.config.jsonc.6 Open this file and configure it to point to your isolated workspace:

Code snippet  
{  
  "basePaths": \[  
    "\~/.config/opencode/dynamic-skills-workspace"  
  \],  
  "enableSkillAliases": true,  
  "slashCommandName": "skill"  
}

#### **Step 4: Configure the Primary OpenCode Manifest**

Open your main OpenCode configuration file (\~/.config/opencode/opencode.json) and update the plugin registry 25:

JSON  
{  
  "plugin": \[  
    "opencode-dynamic-skills"  
  \]  
}

Restart OpenCode. The agent will now initialize with a clean context, utilizing the skill\_find and skill\_use tools to locate and inject skills on-demand.6

#### **Step 5: Consolidate the MCP Layer**

Install the proxy gateway globally to aggregate your 50+ MCP servers:

Bash  
npm install \-g harshal-mcp-proxy

Copy the default template configuration file:

Bash  
cp $(npm root \-g)/harshal-mcp-proxy/config.example.json \~/.config/harshal-mcp-proxy/config.json

Edit \~/.config/harshal-mcp-proxy/config.json to define your 50+ upstream MCP servers (such as filesystem access, database tools, and browser automation engines).7 Start the daemon as a background service:

Bash  
harshal-mcp-proxy \--daemon

#### **Step 6: Route the Client to the Local Gateway**

Update your primary opencode.json configuration file, clearing all individual MCP servers and replacing them with a single reference to the local gateway 21:

JSON  
{  
  "mcp": {  
    "harshal-gateway": {  
      "type": "remote",  
      "url": "http://127.0.0.1:8765/mcp",  
      "enabled": true,  
      "timeout": 30000  
    }  
  }  
}

This configuration replaces the individual tool definitions of your 50+ servers with six lightweight metadata tools.8 The agent will now dynamically query the local index and load full schemas on demand, ensuring complete token efficiency across large development workspaces.8

#### **Works cited**

1. \[FEATURE\]: Implement Dynamic/Lazy Loading for MCP Tool Schemas to Prevent Context Bloat · Issue \#17482 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/17482](https://github.com/anomalyco/opencode/issues/17482)  
2. \[FEATURE\]: Lazy-load agent/skill lists instead of inlining into tool descriptions · Issue \#13188 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/13188](https://github.com/anomalyco/opencode/issues/13188)  
3. Implement Dynamic/Lazy Loading for MCP Tool Schemas to Prevent Context Bloat · Issue \#17480 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/17480](https://github.com/anomalyco/opencode/issues/17480)  
4. Skills descriptions bloat system prompt (\~600KB / \~150K tokens), breaking Bedrock and small-context models · Issue \#20647 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/20647](https://github.com/anomalyco/opencode/issues/20647)  
5. feat: mcp-search tool for lazy loading mcp by TheOutdoorProgrammer · Pull Request \#12520 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/pull/12520](https://github.com/anomalyco/opencode/pull/12520)  
6. opencode-dynamic-skills 1.3.0 on npm \- Libraries.io \- security & maintenance data for open source software, accessed May 26, 2026, [https://libraries.io/npm/opencode-dynamic-skills](https://libraries.io/npm/opencode-dynamic-skills)  
7. \[Update\] harshal-mcp-proxy is now on npm — no more clone \+ build, just \`npm install \-g\`, accessed May 26, 2026, [https://www.reddit.com/r/ClaudeAI/comments/1t5jgjr/update\_harshalmcpproxy\_is\_now\_on\_npm\_no\_more/](https://www.reddit.com/r/ClaudeAI/comments/1t5jgjr/update_harshalmcpproxy_is_now_on_npm_no_more/)  
8. Built an MCP proxy that killed my context bloat AND my RAM usage — here's how \- Reddit, accessed May 26, 2026, [https://www.reddit.com/r/opencodeCLI/comments/1sxe0q3/built\_an\_mcp\_proxy\_that\_killed\_my\_context\_bloat/](https://www.reddit.com/r/opencodeCLI/comments/1sxe0q3/built_an_mcp_proxy_that_killed_my_context_bloat/)  
9. \[FEATURE\]:Add mcp search tool, reduce mcp tool occupying a lot of context · Issue \#8625 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/8625](https://github.com/anomalyco/opencode/issues/8625)  
10. Skill list injected twice per request wastes \~5K–7K tokens of context budget \#22236 \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/22236](https://github.com/anomalyco/opencode/issues/22236)  
11. alvinunreal/oh-my-opencode-slim: Slimmed, cleaned and ... \- GitHub, accessed May 26, 2026, [https://github.com/alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim)  
12. Best OpenCode Plugins to improve flow state coding in 2026 \- Composio, accessed May 26, 2026, [https://composio.dev/content/best-opencode-plugins](https://composio.dev/content/best-opencode-plugins)  
13. Oh My OpenCode Slim \- Browse /v1.0.7 at SourceForge.net, accessed May 26, 2026, [https://sourceforge.net/projects/oh-my-opencode-slim.mirror/files/v1.0.7/](https://sourceforge.net/projects/oh-my-opencode-slim.mirror/files/v1.0.7/)  
14. Oh My Opencode Slim | Agenting Development, accessed May 26, 2026, [https://ohmyopencodeslim.com/](https://ohmyopencodeslim.com/)  
15. NadirRouter/NadirClaw: Open-source LLM router & AI cost ... \- GitHub, accessed May 26, 2026, [https://github.com/NadirRouter/NadirClaw](https://github.com/NadirRouter/NadirClaw)  
16. Show HN: NadirClaw, LLM router that cuts costs by routing prompts right | Hacker News, accessed May 26, 2026, [https://news.ycombinator.com/item?id=47054977](https://news.ycombinator.com/item?id=47054977)  
17. zenobi-us/opencode-skillful: OpenCode Skills Plugin ... \- GitHub, accessed May 26, 2026, [https://github.com/zenobi-us/opencode-skillful](https://github.com/zenobi-us/opencode-skillful)  
18. AGENTS.md \- zenobi-us/opencode-skillful \- GitHub, accessed May 26, 2026, [https://github.com/zenobi-us/opencode-skillful/blob/main/AGENTS.md](https://github.com/zenobi-us/opencode-skillful/blob/main/AGENTS.md)  
19. anomalyco/opencode: The open source coding agent. \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode](https://github.com/anomalyco/opencode)  
20. \[FEATURE\]: inject skill list via system-reminder so models reliably discover skills · Issue \#15653 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/15653](https://github.com/anomalyco/opencode/issues/15653)  
21. OpenCode integration guide: MCP, permissions, and API routing gotchas \#27450 \- GitHub, accessed May 26, 2026, [https://github.com/github/gh-aw/issues/27450](https://github.com/github/gh-aw/issues/27450)  
22. Subagent asking for permission even though it has already · Issue \#25835 · anomalyco/opencode \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/25835](https://github.com/anomalyco/opencode/issues/25835)  
23. Bash tool fails with 'Attempted to assign to readonly property' in v1.14.34 \#25873 \- GitHub, accessed May 26, 2026, [https://github.com/anomalyco/opencode/issues/25873](https://github.com/anomalyco/opencode/issues/25873)  
24. Stream.mkUint8Array crashes in Bun compiled+minified binaries: mutable Channel.runFold accumulator · Issue \#2126 · Effect-TS/effect-smol \- GitHub, accessed May 26, 2026, [https://github.com/Effect-TS/effect-smol/issues/2126](https://github.com/Effect-TS/effect-smol/issues/2126)  
25. antongulin/opencode-skill-creator \- GitHub, accessed May 26, 2026, [https://github.com/antongulin/opencode-skill-creator](https://github.com/antongulin/opencode-skill-creator)  
26. How to Add MCP to OpenCode in 2026: Setup, Config & Examples | Composio, accessed May 26, 2026, [https://composio.dev/content/mcp-with-opencode](https://composio.dev/content/mcp-with-opencode)  
27. modelcontextprotocol/servers: Model Context Protocol Servers \- GitHub, accessed May 26, 2026, [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)