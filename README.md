# When the Agent Decides

Five design failures observed in autonomous AI agents for offensive security, and the engineering principles that fix each one — documented as a short research paper, with minimal illustrative code for each pattern.

This is not a product release and not a tool. It's a field report: what actually broke while operating an autonomous pentesting agent against real infrastructure, why it broke, and what changed as a result. No target, client, or product name from the original system is included anywhere in this repo — the value here is the pattern, not the implementation it came from.

## The paper

- 📄 [English (PDF)](paper/en/When_the_Agent_Decides.pdf) · [LaTeX source](paper/en/paper_en.tex)
- 📄 [Español (PDF)](paper/es/Cuando_el_Agente_Decide.pdf) · [fuente LaTeX](paper/es/paper_es.tex)

**Abstract.** Autonomous AI agents for penetration testing promise to scale offensive work without scaling the human team. In practice, the reliability of these systems depends less on the capability of the model orchestrating them and more on concrete engineering decisions: what the LLM is allowed to decide and what it isn't, how a finding gets verified before it's believed, and how silently the system can degrade when a tool fails.

## The five findings

1. **The mirage of total autonomy.** Letting an LLM decide which capability to call, turn by turn, produces coverage that looks complete on paper and isn't. Capabilities that must always run belong in a deterministic core, not in the agent's discretion.
2. **Adversarial verification, not optional.** An agent has a structural conflict of interest reporting its own findings. A field case: 7 CRITICAL/HIGH findings reported in one pass, 6 discarded by an independent verifier for lack of fresh evidence.
3. **An evidence hierarchy.** Not every "confirmed" finding carries the same weight. Text heuristics, timing signals, tool re-runs, and out-of-band network callbacks sit on a very different confidence spectrum — and a report should say so.
4. **The model isn't the bottleneck.** A controlled comparison found an "uncensored" fine-tune took 2.8× longer than the base model for identical recall, and a specialized offensive-security model couldn't reliably honor a tool-calling contract at all.
5. **Environment fragility as a silent failure.** A correctly-built tool silently failing to run because of a `PATH` mismatch dropped real coverage below reported coverage for an entire session, with no loud error anywhere.

## Patterns

Each finding has a corresponding minimal, runnable illustration in [`patterns/`](patterns/) — written from scratch for this repo, not extracted from any production system:

| File | Principle |
|---|---|
| [`01_deterministic_core.py`](patterns/01_deterministic_core.py) | Split capabilities into an always-run core and an agent-discretionary periphery. |
| [`02_adversarial_verification.py`](patterns/02_adversarial_verification.py) | Verify findings in a pass with no access to the original reasoning trace. |
| [`03_evidence_hierarchy.py`](patterns/03_evidence_hierarchy.py) | Rank confirmation techniques by false-positive risk; label accordingly. |
| [`04_historical_context_as_hint.py`](patterns/04_historical_context_as_hint.py) | The exact prompt bug that caused 6/7 false positives, and its fix. |
| [`05_environment_defensive_execution.py`](patterns/05_environment_defensive_execution.py) | Make the process guarantee its own environment instead of trusting the launcher. |

```bash
python3 patterns/02_adversarial_verification.py
```

Each file runs standalone with no dependencies beyond the Python standard library.

## Methodological note

The observations in the paper come from operating a single system in production across several work sessions — not a controlled study across multiple systems. The figures cited are real measurements from those runs.

---

# Cuando el agente decide *(ES)*

Cinco fallos de diseño observados en agentes autónomos de IA para seguridad ofensiva, y los principios de ingeniería que corrigen cada uno — documentados como un research paper corto, con código ilustrativo mínimo por cada patrón.

Esto no es el lanzamiento de un producto ni una herramienta. Es un reporte de campo: qué falló de verdad operando un agente autónomo de pentesting contra infraestructura real, por qué falló, y qué cambió como resultado. Ningún nombre de objetivo, cliente o producto del sistema original aparece en este repo — lo que vale aquí es el patrón, no la implementación de la que salió.

El paper completo está en `paper/es/` (PDF + fuente LaTeX). Los cinco patrones de código en `patterns/` son los mismos que arriba, aplicables sin importar el idioma.

## Licencia

MIT — ver [LICENSE](LICENSE).
