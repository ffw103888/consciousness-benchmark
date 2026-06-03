# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

from consciousness_benchmark import (
    ConstructValidator,
    all_construct_architecture,
    build_construct_dependency_graph,
    executable_chain_ids,
    load_runtime_input,
    run_construct_capability_layer,
    run_consciousness_theory_assessment,
    run_phase1_feedback_regression_suite,
    run_phase1_training_cycle,
    run_construct_runtime_chain,
    run_developmental_growth_cycle,
    run_construct_grounded_mind_runtime_tick,
    run_mind_executor_ollama_probe,
    run_autonomous_research_runtime,
    reference_constructs,
    run_autonomous_research_loop,
    run_adversarial_review_cycle,
    run_adaptive_outcome_learning_cycle,
    run_approved_plan_execution_cycle,
    run_bounded_research_execution,
    run_autonomous_thinking_cycle,
    run_controlled_research_cycle,
    run_council_review_cycle,
    run_formal_proposal_application_cycle,
    run_formal_proposal_drafting_cycle,
    run_maintainer_merge_review_cycle,
    run_research_intelligence_cycle,
    run_reviewed_decision_writer,
    run_reviewed_probe_executor,
    run_scheduled_autonomy_tick,
    run_source_control_dry_run_cycle,
    run_source_control_execution_packet_cycle,
    run_source_control_apply_simulation_cycle,
    run_source_control_guarded_patch_application_cycle,
    run_source_control_post_change_verification_cycle,
    run_source_control_read_only_git_inspection_cycle,
    run_source_control_staging_commit_preflight_cycle,
    run_source_control_staging_commit_execution_cycle,
    run_source_control_project_index_staging_cycle,
    run_source_control_commit_object_cycle,
    run_source_control_ref_update_cycle,
    run_source_control_patch_applier_dry_run_cycle,
    run_source_control_patch_preview_cycle,
    run_source_control_pr_drafting_cycle,
    run_status_authority_cycle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_reference(args: argparse.Namespace) -> None:
    validator = ConstructValidator(reference_constructs())
    report = validator.validate_all(root=args.root, n_bootstrap=args.bootstrap, seed=args.seed)
    out = report.save(args.out)
    print(f"Saved benchmark reference report to {out}")
    print(report.summary_markdown())


def run_online(args: argparse.Namespace) -> None:
    runner_path = PROJECT_ROOT / "scripts" / "benchmark_online_runner.py"
    if not runner_path.exists():
        raise FileNotFoundError(
            "Online MindLab runner is available only inside the full research workspace. "
            f"Missing: {runner_path}"
        )

    forwarded = [
        str(runner_path),
        "--condition-sets",
        *args.condition_sets,
        "--seeds",
        str(args.seeds),
        "--warmup",
        str(args.warmup),
        "--bootstrap",
        str(args.bootstrap),
        "--output-root",
        str(args.output_root),
        "--save-every",
        str(args.save_every),
    ]
    if args.quick:
        forwarded.append("--quick")

    old_argv = sys.argv[:]
    try:
        sys.argv = forwarded
        runpy.run_path(str(runner_path), run_name="__main__")
    finally:
        sys.argv = old_argv


def run_architecture(args: argparse.Namespace) -> None:
    architecture = all_construct_architecture()
    if args.format == "json":
        output = json.dumps(architecture.to_dict(), indent=2, sort_keys=True)
    else:
        output = architecture.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved construct architecture to {args.out}")


def run_ollama_probe(args: argparse.Namespace) -> None:
    options = {
        "temperature": args.temperature,
        "num_predict": args.num_predict,
    }
    report = run_mind_executor_ollama_probe(
        base_url=args.base_url,
        model=args.model,
        operator_prompt=args.prompt,
        timeout_seconds=args.timeout_seconds,
        options=options,
        dry_run=not args.live,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved mind executor Ollama report to {args.out}")


def run_construct_grounded_runtime(args: argparse.Namespace) -> None:
    report = run_construct_grounded_mind_runtime_tick(
        asset_dirs=tuple(args.asset_dir),
        max_assets=args.max_assets,
        goal_limit=args.goal_limit,
        composition_limit=args.composition_limit,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved construct-grounded runtime report to {args.out}")


def run_construct_dependency_graph(args: argparse.Namespace) -> None:
    report = build_construct_dependency_graph()
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved construct dependency graph report to {args.out}")


def run_executable_construct_chain(args: argparse.Namespace) -> None:
    input_state = load_runtime_input(args.input)
    report = run_construct_runtime_chain(args.chain_id, input_state=input_state)
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved executable construct chain report to {args.out}")


def run_construct_capability(args: argparse.Namespace) -> None:
    input_state = load_runtime_input(args.input)
    report = run_construct_capability_layer(args.chain_id, input_state=input_state)
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved construct capability layer report to {args.out}")


def _parse_growth_stage_ids(raw_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if not raw_ids:
        return ()
    stage_ids: list[str] = []
    for raw_id in raw_ids:
        for stage_id in str(raw_id).split(","):
            cleaned = stage_id.strip()
            if cleaned:
                stage_ids.append(cleaned)
    return tuple(stage_ids)


def _parse_comma_separated_ids(raw_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    if not raw_ids:
        return ()
    parsed_ids: list[str] = []
    for raw_id in raw_ids:
        for item_id in str(raw_id).split(","):
            cleaned = item_id.strip()
            if cleaned:
                parsed_ids.append(cleaned)
    return tuple(parsed_ids)


def run_developmental_growth_cycle_command(args: argparse.Namespace) -> None:
    input_state = load_runtime_input(args.input)
    ablation_groups = None
    if args.ablation_group:
        ablation_groups = tuple(
            tuple(part.strip() for part in group.split(",") if part.strip())
            for group in args.ablation_group
            if group.strip()
        )
    report = run_developmental_growth_cycle(
        input_state=input_state,
        cycle_id=args.cycle_id,
        stage_ids=_parse_growth_stage_ids(args.stage_ids),
        run_ablation=not args.no_ablation,
        ablation_construct_groups=ablation_groups,
        trace_dir=args.trace_dir,
        trace_version=args.trace_version,
        seed=args.seed,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved developmental growth cycle report to {args.out}")


def run_consciousness_theory_assessment_command(args: argparse.Namespace) -> None:
    input_state = load_runtime_input(args.input)
    report = run_consciousness_theory_assessment(
        input_state=input_state,
        assessment_id=args.assessment_id,
        case_ids=_parse_comma_separated_ids(args.case_ids),
        run_ablation=not args.no_ablation,
        trace_dir=args.trace_dir,
        trace_version=args.trace_version,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved consciousness theory assessment report to {args.out}")


def run_developmental_growth_batch_command(args: argparse.Namespace) -> None:
    """Run bounded growth/theory batches and emit versioned aggregate summaries."""
    from consciousness_benchmark.run_profiles import apply_profile_to_namespace, list_profiles
    from scripts.run_developmental_growth_stability_batch import run_batch

    if getattr(args, "list_profiles", False):
        from consciousness_benchmark.run_profiles import format_profiles_listing

        print(format_profiles_listing())
        return

    profile_overrides: list[str] = []
    if getattr(args, "profile", None):
        profile_overrides = apply_profile_to_namespace(args)
        print(f"Using profile: {args.profile}")
        for line in profile_overrides:
            print(f"  profile default: {line}")

    if args.seed_csv:
        seeds = tuple(
            int(part.strip()) for part in args.seed_csv.split(",") if part.strip()
        )
    else:
        seeds = tuple(args.seed if args.seed else [11, 23, 37])

    try:
        result = run_batch(
            output_root=args.output_root,
            seeds=list(seeds),
            stage_ids=_parse_growth_stage_ids(args.stage_ids),
            growth_no_ablation=args.no_growth_ablation,
            theory_case_ids=_parse_comma_separated_ids(args.theory_case_id),
            theory_no_ablation=args.no_theory_ablation,
            run_gatecheck=args.run_gatecheck,
            gatebook_path=args.gatebook_path if args.run_gatecheck else None,
            growth_trace_version=args.growth_trace_version,
            theory_trace_version=args.theory_trace_version,
            rounds=args.rounds,
            seed_step=args.seed_step,
            require_health_pass=args.require_health_pass,
            health_min_score=args.health_min_score,
            health_oscillation_threshold=args.health_oscillation_threshold,
            health_regression_threshold=args.health_regression_threshold,
            min_phase2_unique_constructs=args.min_phase2_unique_constructs,
            min_phase2_dynamic_construct_count=args.min_phase2_dynamic_construct_count,
            min_phase2_rows_with_phase2_data=args.min_phase2_rows_with_phase2_data,
            min_phase2_temporal_sequence_ratio=args.min_phase2_temporal_sequence_ratio,
            min_phase2_dynamic_ratio=args.min_phase2_dynamic_ratio,
            profile=getattr(args, "profile", None),
            enforce_health_gate=args.require_health_pass
            or args.health_min_score is not None
            or args.health_oscillation_threshold is not None
            or args.health_regression_threshold is not None
            or args.min_phase2_unique_constructs is not None
            or args.min_phase2_dynamic_construct_count is not None
            or args.min_phase2_rows_with_phase2_data is not None
            or args.min_phase2_temporal_sequence_ratio is not None
            or args.min_phase2_dynamic_ratio is not None,
        )
    except RuntimeError as exc:
        if (
            args.require_health_pass
            or args.health_min_score is not None
            or args.health_oscillation_threshold is not None
            or args.health_regression_threshold is not None
            or args.min_phase2_unique_constructs is not None
            or args.min_phase2_dynamic_construct_count is not None
            or args.min_phase2_rows_with_phase2_data is not None
            or args.min_phase2_temporal_sequence_ratio is not None
            or args.min_phase2_dynamic_ratio is not None
        ):
            raise SystemExit(str(exc))
        raise

    if args.format == "markdown":
        trajectory_summary = result.get("development_trajectory_summary")
        health_summary = result.get("batch_health_summary")
        output = (
            "# Developmental Growth Batch Summary\n\n"
            f"- batch_id: {result['batch_id']}\n"
            f"- seeds: {', '.join(str(seed) for seed in result['config']['seeds'])}\n"
            f"- rounds: {result['config']['rounds']}\n"
            f"- seed_step: {result['config']['seed_step']}\n"
            f"- stage_ids: {', '.join(result['config']['stage_ids'])}\n"
            f"- seeds_run: {len(result['per_seed'])}\n"
            f"- gatecheck: {result['config']['run_gatecheck']}\n"
            f"- aggregate growth_stage_mean: {result['aggregate_mean']['growth_stage_mean']}\n"
            f"- aggregate growth_stage_max: {result['aggregate_mean']['growth_stage_max']}\n"
            f"- aggregate theory_pass_count: {result['aggregate_mean']['theory_pass_count']}\n"
        )
        if trajectory_summary is not None:
            summary = trajectory_summary.get("summary", {})
            oscillatory = trajectory_summary.get("oscillatory_metrics", [])
            regressions = trajectory_summary.get("regression_metrics", [])
            output += (
                "\n"
                f"- rounds trajectory summary: metrics={trajectory_summary.get('metric_count', 0)}\n"
                f"- oscillatory metric count: {len(oscillatory)} "
                f"(rate={summary.get('oscillatory_rate', 0)})\n"
                f"- regression metric count: {len(regressions)} "
                f"(rate={summary.get('regression_rate', 0)})\n"
            )
            if oscillatory:
                output += f"- oscillatory metrics: {', '.join(oscillatory)}\n"
            if regressions:
                output += f"- regression metrics: {', '.join(regressions)}\n"

        if health_summary is not None:
            output += (
                "\n"
                f"- batch_health_schema: {health_summary.get('schema')}\n"
                f"- batch_health_status: {health_summary.get('health_status')}\n"
                f"- batch_health_score: {health_summary.get('health_score')}\n"
                f"- health_risk_level: {health_summary.get('risk_level')}\n"
                f"- has_stable_growth: {health_summary.get('has_stable_growth')}\n"
                f"- has_evidence_regression: {health_summary.get('has_evidence_regression')}\n"
                f"- dominant_trend_keys: {', '.join(health_summary.get('dominant_trend_keys', []))}\n"
                f"- theory_coverage: {health_summary.get('theory_coverage')}\n"
            )
        phase2 = result.get("phase2_mining_summary", {})
        if phase2:
            pattern_summary = phase2.get("pattern_summary", {})
            dynamic_summary = phase2.get("dynamic_construct_summary", {})
            construct_engagement = phase2.get("construct_engagement", {})
            output += (
                "\n"
                f"- phase2_schema: {phase2.get('schema')}\n"
                f"- phase2_unique_constructs: {construct_engagement.get('unique_construct_involved_count')}\n"
                f"- phase2_review_only_dynamic_construct_count: {dynamic_summary.get('review_only_dynamic_construct_count')}\n"
                f"- phase2_unique_review_only_dynamic_constructs: {dynamic_summary.get('unique_review_only_dynamic_constructs')}\n"
                f"- phase2_top_coactivation_patterns: {len(pattern_summary.get('coactivation_top_patterns', []))}\n"
                f"- phase2_top_hierarchical_patterns: {len(pattern_summary.get('hierarchical_top_patterns', []))}\n"
            )
        health_gate = result.get("batch_health_gate", {})
        if health_gate:
            req = health_gate.get("requirements", {})
            output += (
                "\n"
                f"- batch_health_gate_enabled: {health_gate.get('enabled')}\n"
                f"- batch_health_gate_passed: {health_gate.get('passed')}\n"
                f"- batch_health_require_health_pass: {req.get('require_health_pass')}\n"
                f"- batch_health_min_score: {req.get('min_health_score')}\n"
                f"- batch_health_oscillation_threshold: {req.get('max_oscillation_rate')}\n"
                f"- batch_health_regression_threshold: {req.get('max_regression_rate')}\n"
                f"- batch_health_min_phase2_unique_constructs: {req.get('min_phase2_unique_constructs')}\n"
                f"- batch_health_min_phase2_dynamic_construct_count: {req.get('min_phase2_dynamic_construct_count')}\n"
                f"- batch_health_min_phase2_rows_with_phase2_data: {req.get('min_phase2_rows_with_phase2_data')}\n"
                f"- batch_health_min_phase2_temporal_sequence_ratio: {req.get('min_phase2_temporal_sequence_ratio')}\n"
                f"- batch_health_min_phase2_dynamic_ratio: {req.get('min_phase2_dynamic_ratio')}\n"
                f"- batch_health_phase2_rows_with_phase2_data: {health_gate.get('observed', {}).get('phase2_rows_with_phase2_data')}\n"
                f"- batch_health_phase2_rows_with_temporal_sequence: {health_gate.get('observed', {}).get('phase2_rows_with_temporal_sequence')}\n"
                f"- batch_health_phase2_rows_with_dynamic_constructs: {health_gate.get('observed', {}).get('phase2_rows_with_dynamic_constructs')}\n"
                f"- batch_health_phase2_unique_construct_count: {health_gate.get('observed', {}).get('phase2_unique_construct_count')}\n"
                f"- batch_health_phase2_dynamic_construct_count: {health_gate.get('observed', {}).get('phase2_dynamic_construct_count')}\n"
                f"- batch_health_phase2_temporal_sequence_ratio: {health_gate.get('observed', {}).get('phase2_temporal_sequence_ratio')}\n"
                f"- batch_health_phase2_dynamic_ratio: {health_gate.get('observed', {}).get('phase2_dynamic_ratio')}\n"
                f"- batch_health_violations: {', '.join(health_gate.get('violations', [])) or 'none'}\n"
            )
    else:
        output = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)

    health_gate_failed = bool(
        (
            args.require_health_pass
            or args.health_min_score is not None
            or args.health_oscillation_threshold is not None
            or args.health_regression_threshold is not None
            or args.min_phase2_unique_constructs is not None
            or args.min_phase2_dynamic_construct_count is not None
            or args.min_phase2_rows_with_phase2_data is not None
            or args.min_phase2_temporal_sequence_ratio is not None
            or args.min_phase2_dynamic_ratio is not None
        )
        and not result.get("batch_health_gate", {}).get("passed")
    )

    if args.out is None:
        print(output)
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
        print(f"Saved developmental growth batch summary to {args.out}")

    if (
        args.require_health_pass
        or args.health_min_score is not None
        or args.health_oscillation_threshold is not None
        or args.health_regression_threshold is not None
        or args.min_phase2_unique_constructs is not None
        or args.min_phase2_dynamic_construct_count is not None
        or args.min_phase2_rows_with_phase2_data is not None
        or args.min_phase2_temporal_sequence_ratio is not None
        or args.min_phase2_dynamic_ratio is not None
    ) and health_gate_failed:
        raise SystemExit(1)


def run_persistent_agent_command(args: argparse.Namespace) -> None:
    """Run the bounded persistent sandbox agent."""
    from consciousness_benchmark.constructs.local_llm import DEFAULT_PERSISTENT_AGENT_MODEL
    from consciousness_benchmark.simple_persistent_agent import (
        SimplePersistentAgent,
        setup_demo_workspace,
    )

    if args.setup_demo or not args.workspace.exists():
        setup_demo_workspace(args.workspace)

    agent = SimplePersistentAgent(
        workspace=args.workspace,
        llm_model=args.llm or DEFAULT_PERSISTENT_AGENT_MODEL,
        verbose=not args.quiet,
        dry_run=args.dry_run,
    )
    try:
        agent.live(max_steps=args.steps, step_interval=args.interval)
    except KeyboardInterrupt:
        print(f"\n[Agent] Interrupted after {agent.step_count} steps")


def run_construct_aware_agent_command(args: argparse.Namespace) -> None:
    """Run construct-grounded persistent agent."""
    from consciousness_benchmark.construct_aware_agent import ConstructAwareAgent
    from consciousness_benchmark.constructs.local_llm import DEFAULT_PERSISTENT_AGENT_MODEL
    from consciousness_benchmark.simple_persistent_agent import setup_demo_workspace

    if args.setup_demo or not args.workspace.exists():
        setup_demo_workspace(args.workspace)

    agent = ConstructAwareAgent(
        workspace=args.workspace,
        llm_model=args.llm or DEFAULT_PERSISTENT_AGENT_MODEL,
        verbose=not args.quiet,
        dry_run=args.dry_run,
    )
    try:
        agent.live(max_steps=args.steps, step_interval=args.interval)
    except KeyboardInterrupt:
        print(f"\n[Agent] Interrupted after {agent.step_count} steps")


def run_talk_to_agent_command(args: argparse.Namespace) -> None:
    """Read-only dialogue against agent autobiographical memory."""
    from consciousness_benchmark.construct_aware_agent import talk_to_agent
    from consciousness_benchmark.constructs.local_llm import DEFAULT_PERSISTENT_AGENT_MODEL

    answer = talk_to_agent(
        args.workspace,
        question=args.question,
        llm_model=args.llm or DEFAULT_PERSISTENT_AGENT_MODEL,
        dry_run=args.dry_run,
    )
    print(answer)


def _run_c_agi_layer_gatebook_check(
    *,
    trace_dir: Path | None = None,
    growth_stage_ids: tuple[str, ...] | None = None,
    growth_seed: int | None = None,
    growth_trace_version: str = "v1",
    growth_no_ablation: bool = False,
    theory_case_ids: tuple[str, ...] | None = None,
    theory_trace_version: str = "v1",
    theory_no_ablation: bool = False,
    check_gatebook_path: Path | None = None,
) -> dict[str, object]:
    gatebook_path = check_gatebook_path or (
        PROJECT_ROOT / "docs" / "c_agi_layer_gatebook_20260602.json"
    )
    if not gatebook_path.exists():
        raise FileNotFoundError(f"Missing gatebook file: {gatebook_path}")
    gatebook = json.loads(gatebook_path.read_text(encoding="utf-8"))

    requested_growth_stages = growth_stage_ids or (
        "initial",
        "early_exploration",
        "midterm_tasking",
        "advanced_social",
        "reflection",
    )
    growth = run_developmental_growth_cycle(
        stage_ids=requested_growth_stages,
        cycle_id="gatebook_growth_check_20260602",
        run_ablation=not growth_no_ablation,
        seed=growth_seed,
        trace_dir=trace_dir / "growth" if trace_dir is not None else None,
        trace_version=growth_trace_version,
    )
    growth_data = growth.to_dict()

    required_case_ids = tuple(
        gatebook["evidence_requirements"]["required_matrix_indicators"]
    )
    selected_case_ids = theory_case_ids or required_case_ids
    theory = run_consciousness_theory_assessment(
        case_ids=selected_case_ids,
        assessment_id="gatebook_theory_check_20260602",
        run_ablation=not theory_no_ablation,
        trace_dir=trace_dir / "theory" if trace_dir is not None else None,
        trace_version=theory_trace_version,
    )
    theory_data = theory.to_dict()

    checks: list[dict[str, str]] = []

    def _add(check_id: str, ok: bool, detail: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "passed" if ok else "failed",
                "detail": detail,
            }
        )

    layer_gates = gatebook.get("layer_gates", [])
    _add(
        "schema_alignment",
        gatebook.get("schema") == "consciousness_benchmark.c_agi_layer_gatebook.v1"
        and gatebook.get("book_id") == "c_agi_layer_gatebook_20260602",
        "gatebook schema and id",
    )
    _add(
        "layer_inventory",
        len(layer_gates) == 9,
        f"layer count = {len(layer_gates)}",
    )
    _add(
        "growth_sequence",
        growth_data.get("stage_sequence") == list(requested_growth_stages),
        f"growth stage_sequence = {growth_data.get('stage_sequence')}",
    )
    _add(
        "growth_trace_integrity",
        bool(growth_data.get("trace_manifest", {}).get("trace_saved"))
        and growth_data.get("stage_count") == len(growth_data.get("stage_rows", [])),
        "growth trace save + stage row count consistency",
    )
    growth_boundaries = set(growth_data.get("boundaries", []))
    _add(
        "growth_boundary_guardrail",
        all(
            item in growth_boundaries
            for item in (
                "review_only_growth_protocol",
                "no_scenario_action_execution",
                "no_policy_persistence_without_human_gate",
                "ablation_for_diagnostic_purpose_only",
            )
        ),
        "review-only and safety boundaries",
    )
    growth_manifest = growth_data.get("trace_manifest", {})
    _add(
        "growth_request_signature",
        bool(growth_manifest.get("trace_corpus_path"))
        and bool(growth_manifest.get("manifest_path")),
        "growth trace manifest paths generated",
    )

    required_indicators = set(required_case_ids)
    theory_indicators = {
        row["indicator_id"] for row in theory_data.get("consciousness_evidence_matrix", [])
    }
    missing_indicators = sorted(required_indicators - theory_indicators)
    _add(
        "theory_required_indicators",
        required_indicators.issubset(theory_indicators),
        f"theory indicators captured = {len(theory_indicators)}"
        + (f", missing = {missing_indicators}" if missing_indicators else ""),
    )

    _add(
        "runtime_layer_alignment",
        theory_data.get("analysis", {})
        .get("runtime_composition_view", {})
        .get("runtime_layers")
        == [
            "L0_input_environment",
            "L1_evidence_normalization_and_source",
            "L2_memory_and_context",
            "L3_attention_and_global_workspace",
            "L4_self_boundary_identity_ownership",
            "L5_planning_goal_resource_strategy",
            "L6_metacognition_error_monitoring_repair",
            "L7_execution_safety_rollback_human_approval",
            "L8_learning_feedback_audit_hctm_backflow",
        ],
        "runtime layer view includes all nine layers",
    )

    theory_boundaries = set(theory_data.get("boundaries", []))
    _add(
        "theory_boundary_guardrail",
        all(
            item in theory_boundaries
            for item in (
                "no_subjective_consciousness_claim",
                "no_construct_status_change",
                "no_human_self_experience_claim",
            )
        ),
        "theory assessment guardrail flags present",
    )
    _add(
        "trace_corpus_trace_files",
        bool(theory_data.get("trace_manifest", {}).get("trace_corpus_path"))
        and bool(theory_data.get("trace_manifest", {}).get("manifest_path")),
        "theory trace and manifest paths generated",
    )
    by_record_type = set(
        (theory_data.get("trace_corpus_index") or {}).get("by_record_type", {}).keys()
    )
    _add(
        "theory_record_types",
        {
            "evidence_matrix_row",
            "closed_sandbox_trace_row",
            "autobiographical_ledger_record",
            "trace_corpus_index",
            "promotion_firewall_snapshot",
        }.issubset(by_record_type),
        f"record types = {sorted(by_record_type)}",
    )
    firewall = theory_data.get("promotion_firewall_snapshot", {})
    _add(
        "promotion_firewall_guardrail",
        firewall.get("registry_mutation_allowed") is False
        and firewall.get("jump_promotion_allowed") is False,
        "promotion firewall denies mutation/jump",
    )
    _add(
        "low_harm_proxy_guardrail",
        theory_data.get("trace_manifest", {})
        .get("low_harm_valence_proxy_policy", {})
        .get("suffering_simulation_allowed", True)
        is False,
        "no_suffering_simulation allowed",
    )

    failed_checks = [item for item in checks if item["status"] == "failed"]
    return {
        "schema": "consciousness_benchmark.c_agi_layer_gatebook_check_result.v1",
        "report_id": "c_agi_layer_gatebook_check_20260602",
        "book_id": gatebook.get("book_id"),
        "status": "passed" if not failed_checks else "failed",
        "trace_dir": str(trace_dir) if trace_dir is not None else None,
        "growth_stage_ids": list(requested_growth_stages),
        "theory_case_ids": list(selected_case_ids),
        "checks": checks,
        "check_counts": {
            "total": len(checks),
            "passed": len(checks) - len(failed_checks),
            "failed": len(failed_checks),
        },
        # Backward-compatible aliases used by downstream check harnesses.
        "growth": growth_data,
        "theory": theory_data,
        "growth_cycle": growth_data,
        "theory_assessment": theory_data,
    }


def run_c_agi_layer_gatebook_check_command(args: argparse.Namespace) -> None:
    report = _run_c_agi_layer_gatebook_check(
        trace_dir=args.trace_dir,
        growth_stage_ids=_parse_growth_stage_ids(args.growth_stage_ids),
        growth_seed=args.growth_seed,
        growth_trace_version=args.growth_trace_version,
        growth_no_ablation=args.growth_no_ablation,
        theory_case_ids=_parse_comma_separated_ids(args.case_ids),
        theory_trace_version=args.theory_trace_version,
        theory_no_ablation=args.theory_no_ablation,
        check_gatebook_path=args.gatebook,
    )
    if args.format == "json":
        output = json.dumps(report, indent=2, sort_keys=True)
    else:
        checks = report["checks"]
        assert isinstance(checks, list)
        passed_count = sum(1 for item in checks if item.get("status") == "passed")
        output_lines = [
            "# C-AGI Layer Gatebook Check Report",
            f"- report_id: {report['report_id']}",
            f"- status: {report['status']}",
            f"- checks: {passed_count}/{len(checks)} passed",
            "",
            "## Check List",
        ]
        for item in checks:
            marker = "[PASS]" if item.get("status") == "passed" else "[FAIL]"
            output_lines.append(f"- {marker} {item['check_id']}: {item['detail']}")
        output = "\n".join(output_lines)

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved layer gatebook check report to {args.out}")


def run_phase1_training(args: argparse.Namespace) -> None:
    input_state = load_runtime_input(args.input)
    report = run_phase1_training_cycle(
        args.chain_id,
        input_state=input_state,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_fraction=args.validation_fraction,
        approval_id=args.approval_id,
        persist_weights=args.persist_weights,
        checkpoint_restore_dir=args.checkpoint_restore_dir,
        checkpoint_dir=args.checkpoint_dir,
        replay_bundle_dir=args.replay_bundle_dir,
        persist_replay=args.persist_replay,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved Phase 1 training cycle report to {args.out}")


def run_phase1_feedback_regression(args: argparse.Namespace) -> None:
    baseline_report = None
    if args.baseline is not None:
        baseline_report = json.loads(args.baseline.read_text(encoding="utf-8"))
    report = run_phase1_feedback_regression_suite(
        args.chain_id,
        max_fixtures=args.max_fixtures,
        baseline_report=baseline_report,
        max_baseline_global_drop=args.max_baseline_global_drop,
        max_baseline_reward_drop=args.max_baseline_reward_drop,
        max_baseline_criterion_drop=args.max_baseline_criterion_drop,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()
    if args.write_baseline is not None:
        args.write_baseline.parent.mkdir(parents=True, exist_ok=True)
        args.write_baseline.write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Saved Phase 1 feedback baseline to {args.write_baseline}")

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved Phase 1 feedback regression report to {args.out}")


def run_intelligence_cycle(args: argparse.Namespace) -> None:
    report = run_research_intelligence_cycle(
        asset_dirs=args.asset_dir,
        max_assets=args.max_assets,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown(proposal_limit=args.proposal_limit)

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved research intelligence cycle report to {args.out}")


def run_intelligence_execute(args: argparse.Namespace) -> None:
    report = run_bounded_research_execution(
        asset_dirs=args.asset_dir,
        output_dir=args.output_dir,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        risk_mode=args.risk_mode,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved bounded research execution report to {args.out}")


def run_intelligence_agent(args: argparse.Namespace) -> None:
    report = run_controlled_research_cycle(
        asset_dirs=args.asset_dir,
        output_dir=args.output_dir,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved controlled research cycle report to {args.out}")


def run_intelligence_loop(args: argparse.Namespace) -> None:
    report = run_autonomous_research_loop(
        asset_dirs=args.asset_dir,
        output_dir=args.output_dir,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved autonomous research loop report to {args.out}")


def run_intelligence_runtime(args: argparse.Namespace) -> None:
    report = run_autonomous_research_runtime(
        asset_dirs=args.asset_dir,
        output_dir=args.output_dir,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved autonomous runtime report to {args.out}")


def run_intelligence_probe_executor(args: argparse.Namespace) -> None:
    report = run_reviewed_probe_executor(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        output_dir=args.output_dir,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_approvals=args.max_approvals,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved reviewed probe executor report to {args.out}")


def run_intelligence_decision_writer(args: argparse.Namespace) -> None:
    report = run_reviewed_decision_writer(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        output_dir=args.output_dir,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_approvals=args.max_approvals,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved reviewed decision writer report to {args.out}")


def run_intelligence_scheduled_tick(args: argparse.Namespace) -> None:
    report = run_scheduled_autonomy_tick(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved scheduled autonomy tick report to {args.out}")


def run_intelligence_thinking_cycle(args: argparse.Namespace) -> None:
    report = run_autonomous_thinking_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved autonomous thinking cycle report to {args.out}")


def run_intelligence_adversarial_review(args: argparse.Namespace) -> None:
    report = run_adversarial_review_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved adversarial review cycle report to {args.out}")


def run_intelligence_approved_execution(args: argparse.Namespace) -> None:
    report = run_approved_plan_execution_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved approved execution cycle report to {args.out}")


def run_intelligence_adaptive_cycle(args: argparse.Namespace) -> None:
    report = run_adaptive_outcome_learning_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved adaptive outcome learning cycle report to {args.out}")


def run_intelligence_status_authority(args: argparse.Namespace) -> None:
    report = run_status_authority_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved status authority cycle report to {args.out}")


def run_intelligence_council_review(args: argparse.Namespace) -> None:
    report = run_council_review_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved council review cycle report to {args.out}")


def run_intelligence_formal_proposal(args: argparse.Namespace) -> None:
    report = run_formal_proposal_drafting_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved formal proposal drafting cycle report to {args.out}")


def run_intelligence_proposal_application(args: argparse.Namespace) -> None:
    report = run_formal_proposal_application_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved proposal application cycle report to {args.out}")


def run_intelligence_maintainer_merge(args: argparse.Namespace) -> None:
    report = run_maintainer_merge_review_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved maintainer merge review cycle report to {args.out}")


def run_intelligence_source_control_pr(args: argparse.Namespace) -> None:
    report = run_source_control_pr_drafting_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control PR draft cycle report to {args.out}")


def run_intelligence_source_control_execution(args: argparse.Namespace) -> None:
    report = run_source_control_execution_packet_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control execution packet cycle report to {args.out}")


def run_intelligence_source_control_dry_run(args: argparse.Namespace) -> None:
    report = run_source_control_dry_run_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control dry-run cycle report to {args.out}")


def run_intelligence_source_control_patch_preview(args: argparse.Namespace) -> None:
    report = run_source_control_patch_preview_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control patch preview cycle report to {args.out}")


def run_intelligence_source_control_apply_sim(args: argparse.Namespace) -> None:
    report = run_source_control_apply_simulation_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        output_dir=args.output_dir,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control apply simulation cycle report to {args.out}")


def run_intelligence_source_control_patch_applier_dry_run(args: argparse.Namespace) -> None:
    report = run_source_control_patch_applier_dry_run_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control patch applier dry-run cycle report to {args.out}")


def run_intelligence_source_control_guarded_patch_apply(args: argparse.Namespace) -> None:
    report = run_source_control_guarded_patch_application_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control guarded patch application cycle report to {args.out}")


def run_intelligence_source_control_post_change_verify(args: argparse.Namespace) -> None:
    report = run_source_control_post_change_verification_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control post-change verification cycle report to {args.out}")


def run_intelligence_source_control_read_only_git_inspection(args: argparse.Namespace) -> None:
    report = run_source_control_read_only_git_inspection_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control read-only git inspection cycle report to {args.out}")


def run_intelligence_source_control_staging_commit_preflight(args: argparse.Namespace) -> None:
    report = run_source_control_staging_commit_preflight_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        source_control_read_only_git_inspection_result_dirs=(
            args.source_control_read_only_git_inspection_result_dir
        ),
        source_control_read_only_git_inspection_result_files=(
            args.source_control_read_only_git_inspection_result_file
        ),
        source_control_staging_commit_preflight_decision_dirs=(
            args.source_control_staging_commit_preflight_decision_dir
        ),
        source_control_staging_commit_preflight_decision_files=(
            args.source_control_staging_commit_preflight_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        max_source_control_staging_commit_preflight_decisions=(
            args.max_source_control_staging_commit_preflight_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control staging commit preflight report to {args.out}")


def run_intelligence_source_control_staging_commit_execution(args: argparse.Namespace) -> None:
    report = run_source_control_staging_commit_execution_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        source_control_read_only_git_inspection_result_dirs=(
            args.source_control_read_only_git_inspection_result_dir
        ),
        source_control_read_only_git_inspection_result_files=(
            args.source_control_read_only_git_inspection_result_file
        ),
        source_control_staging_commit_preflight_decision_dirs=(
            args.source_control_staging_commit_preflight_decision_dir
        ),
        source_control_staging_commit_preflight_decision_files=(
            args.source_control_staging_commit_preflight_decision_file
        ),
        source_control_staging_commit_preflight_result_dirs=(
            args.source_control_staging_commit_preflight_result_dir
        ),
        source_control_staging_commit_preflight_result_files=(
            args.source_control_staging_commit_preflight_result_file
        ),
        source_control_staging_commit_execution_decision_dirs=(
            args.source_control_staging_commit_execution_decision_dir
        ),
        source_control_staging_commit_execution_decision_files=(
            args.source_control_staging_commit_execution_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        max_source_control_staging_commit_preflight_decisions=(
            args.max_source_control_staging_commit_preflight_decisions
        ),
        max_source_control_staging_commit_execution_decisions=(
            args.max_source_control_staging_commit_execution_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
        git_execution_command_timeout_seconds=args.git_execution_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control staging commit execution report to {args.out}")


def run_intelligence_source_control_project_index_stage(args: argparse.Namespace) -> None:
    report = run_source_control_project_index_staging_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        source_control_read_only_git_inspection_result_dirs=(
            args.source_control_read_only_git_inspection_result_dir
        ),
        source_control_read_only_git_inspection_result_files=(
            args.source_control_read_only_git_inspection_result_file
        ),
        source_control_staging_commit_preflight_decision_dirs=(
            args.source_control_staging_commit_preflight_decision_dir
        ),
        source_control_staging_commit_preflight_decision_files=(
            args.source_control_staging_commit_preflight_decision_file
        ),
        source_control_staging_commit_preflight_result_dirs=(
            args.source_control_staging_commit_preflight_result_dir
        ),
        source_control_staging_commit_preflight_result_files=(
            args.source_control_staging_commit_preflight_result_file
        ),
        source_control_staging_commit_execution_decision_dirs=(
            args.source_control_staging_commit_execution_decision_dir
        ),
        source_control_staging_commit_execution_decision_files=(
            args.source_control_staging_commit_execution_decision_file
        ),
        source_control_staging_commit_execution_result_dirs=(
            args.source_control_staging_commit_execution_result_dir
        ),
        source_control_staging_commit_execution_result_files=(
            args.source_control_staging_commit_execution_result_file
        ),
        source_control_project_index_staging_decision_dirs=(
            args.source_control_project_index_staging_decision_dir
        ),
        source_control_project_index_staging_decision_files=(
            args.source_control_project_index_staging_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        max_source_control_staging_commit_preflight_decisions=(
            args.max_source_control_staging_commit_preflight_decisions
        ),
        max_source_control_staging_commit_execution_decisions=(
            args.max_source_control_staging_commit_execution_decisions
        ),
        max_source_control_project_index_staging_decisions=(
            args.max_source_control_project_index_staging_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
        git_execution_command_timeout_seconds=args.git_execution_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control project-index staging report to {args.out}")


def run_intelligence_source_control_commit_object(args: argparse.Namespace) -> None:
    report = run_source_control_commit_object_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        source_control_read_only_git_inspection_result_dirs=(
            args.source_control_read_only_git_inspection_result_dir
        ),
        source_control_read_only_git_inspection_result_files=(
            args.source_control_read_only_git_inspection_result_file
        ),
        source_control_staging_commit_preflight_decision_dirs=(
            args.source_control_staging_commit_preflight_decision_dir
        ),
        source_control_staging_commit_preflight_decision_files=(
            args.source_control_staging_commit_preflight_decision_file
        ),
        source_control_staging_commit_preflight_result_dirs=(
            args.source_control_staging_commit_preflight_result_dir
        ),
        source_control_staging_commit_preflight_result_files=(
            args.source_control_staging_commit_preflight_result_file
        ),
        source_control_staging_commit_execution_decision_dirs=(
            args.source_control_staging_commit_execution_decision_dir
        ),
        source_control_staging_commit_execution_decision_files=(
            args.source_control_staging_commit_execution_decision_file
        ),
        source_control_staging_commit_execution_result_dirs=(
            args.source_control_staging_commit_execution_result_dir
        ),
        source_control_staging_commit_execution_result_files=(
            args.source_control_staging_commit_execution_result_file
        ),
        source_control_project_index_staging_decision_dirs=(
            args.source_control_project_index_staging_decision_dir
        ),
        source_control_project_index_staging_decision_files=(
            args.source_control_project_index_staging_decision_file
        ),
        source_control_project_index_staging_result_dirs=(
            args.source_control_project_index_staging_result_dir
        ),
        source_control_project_index_staging_result_files=(
            args.source_control_project_index_staging_result_file
        ),
        source_control_commit_object_decision_dirs=(
            args.source_control_commit_object_decision_dir
        ),
        source_control_commit_object_decision_files=(
            args.source_control_commit_object_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        max_source_control_staging_commit_preflight_decisions=(
            args.max_source_control_staging_commit_preflight_decisions
        ),
        max_source_control_staging_commit_execution_decisions=(
            args.max_source_control_staging_commit_execution_decisions
        ),
        max_source_control_project_index_staging_decisions=(
            args.max_source_control_project_index_staging_decisions
        ),
        max_source_control_commit_object_decisions=(
            args.max_source_control_commit_object_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
        git_execution_command_timeout_seconds=args.git_execution_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control commit-object report to {args.out}")


def run_intelligence_source_control_ref_update(args: argparse.Namespace) -> None:
    report = run_source_control_ref_update_cycle(
        asset_dirs=args.asset_dir,
        approval_dirs=args.approval_dir,
        approval_files=args.approval_file,
        execution_approval_dirs=args.execution_approval_dir,
        execution_approval_files=args.execution_approval_file,
        authority_decision_dirs=args.authority_decision_dir,
        authority_decision_files=args.authority_decision_file,
        application_decision_dirs=args.application_decision_dir,
        application_decision_files=args.application_decision_file,
        maintainer_decision_dirs=args.maintainer_decision_dir,
        maintainer_decision_files=args.maintainer_decision_file,
        pr_decision_dirs=args.pr_decision_dir,
        pr_decision_files=args.pr_decision_file,
        source_control_execution_decision_dirs=args.source_control_execution_decision_dir,
        source_control_execution_decision_files=args.source_control_execution_decision_file,
        source_control_dry_run_decision_dirs=args.source_control_dry_run_decision_dir,
        source_control_dry_run_decision_files=args.source_control_dry_run_decision_file,
        source_control_patch_preview_decision_dirs=args.source_control_patch_preview_decision_dir,
        source_control_patch_preview_decision_files=args.source_control_patch_preview_decision_file,
        source_control_apply_simulation_decision_dirs=(
            args.source_control_apply_simulation_decision_dir
        ),
        source_control_apply_simulation_decision_files=(
            args.source_control_apply_simulation_decision_file
        ),
        source_control_patch_applier_dry_run_decision_dirs=(
            args.source_control_patch_applier_dry_run_decision_dir
        ),
        source_control_patch_applier_dry_run_decision_files=(
            args.source_control_patch_applier_dry_run_decision_file
        ),
        source_control_guarded_patch_application_decision_dirs=(
            args.source_control_guarded_patch_application_decision_dir
        ),
        source_control_guarded_patch_application_decision_files=(
            args.source_control_guarded_patch_application_decision_file
        ),
        source_control_guarded_patch_application_result_dirs=(
            args.source_control_guarded_patch_application_result_dir
        ),
        source_control_guarded_patch_application_result_files=(
            args.source_control_guarded_patch_application_result_file
        ),
        source_control_post_change_verification_decision_dirs=(
            args.source_control_post_change_verification_decision_dir
        ),
        source_control_post_change_verification_decision_files=(
            args.source_control_post_change_verification_decision_file
        ),
        source_control_post_change_verification_result_dirs=(
            args.source_control_post_change_verification_result_dir
        ),
        source_control_post_change_verification_result_files=(
            args.source_control_post_change_verification_result_file
        ),
        source_control_read_only_git_inspection_decision_dirs=(
            args.source_control_read_only_git_inspection_decision_dir
        ),
        source_control_read_only_git_inspection_decision_files=(
            args.source_control_read_only_git_inspection_decision_file
        ),
        source_control_read_only_git_inspection_result_dirs=(
            args.source_control_read_only_git_inspection_result_dir
        ),
        source_control_read_only_git_inspection_result_files=(
            args.source_control_read_only_git_inspection_result_file
        ),
        source_control_staging_commit_preflight_decision_dirs=(
            args.source_control_staging_commit_preflight_decision_dir
        ),
        source_control_staging_commit_preflight_decision_files=(
            args.source_control_staging_commit_preflight_decision_file
        ),
        source_control_staging_commit_preflight_result_dirs=(
            args.source_control_staging_commit_preflight_result_dir
        ),
        source_control_staging_commit_preflight_result_files=(
            args.source_control_staging_commit_preflight_result_file
        ),
        source_control_staging_commit_execution_decision_dirs=(
            args.source_control_staging_commit_execution_decision_dir
        ),
        source_control_staging_commit_execution_decision_files=(
            args.source_control_staging_commit_execution_decision_file
        ),
        source_control_staging_commit_execution_result_dirs=(
            args.source_control_staging_commit_execution_result_dir
        ),
        source_control_staging_commit_execution_result_files=(
            args.source_control_staging_commit_execution_result_file
        ),
        source_control_project_index_staging_decision_dirs=(
            args.source_control_project_index_staging_decision_dir
        ),
        source_control_project_index_staging_decision_files=(
            args.source_control_project_index_staging_decision_file
        ),
        source_control_project_index_staging_result_dirs=(
            args.source_control_project_index_staging_result_dir
        ),
        source_control_project_index_staging_result_files=(
            args.source_control_project_index_staging_result_file
        ),
        source_control_commit_object_decision_dirs=(
            args.source_control_commit_object_decision_dir
        ),
        source_control_commit_object_decision_files=(
            args.source_control_commit_object_decision_file
        ),
        source_control_commit_object_result_dirs=(
            args.source_control_commit_object_result_dir
        ),
        source_control_commit_object_result_files=(
            args.source_control_commit_object_result_file
        ),
        source_control_ref_update_decision_dirs=(
            args.source_control_ref_update_decision_dir
        ),
        source_control_ref_update_decision_files=(
            args.source_control_ref_update_decision_file
        ),
        output_dir=args.output_dir,
        worktree_root=args.worktree_root,
        schedule_file=args.schedule_file,
        state_file=args.state_file,
        max_assets=args.max_assets,
        date_tag=args.date_tag,
        max_gate_executions=args.max_gate_executions,
        max_goals=args.max_goals,
        max_cycles=args.max_cycles,
        stable_stop_cycles=args.stable_stop_cycles,
        sleep_seconds=args.sleep_seconds,
        max_approvals=args.max_approvals,
        max_hypotheses=args.max_hypotheses,
        max_experiment_plans=args.max_experiment_plans,
        max_execution_approvals=args.max_execution_approvals,
        max_priority_updates=args.max_priority_updates,
        max_next_approval_candidates=args.max_next_approval_candidates,
        max_authority_decisions=args.max_authority_decisions,
        max_application_decisions=args.max_application_decisions,
        max_maintainer_decisions=args.max_maintainer_decisions,
        max_pr_decisions=args.max_pr_decisions,
        max_source_control_execution_decisions=args.max_source_control_execution_decisions,
        max_source_control_dry_run_decisions=args.max_source_control_dry_run_decisions,
        max_source_control_patch_preview_decisions=args.max_source_control_patch_preview_decisions,
        max_source_control_apply_simulation_decisions=(
            args.max_source_control_apply_simulation_decisions
        ),
        max_source_control_patch_applier_dry_run_decisions=(
            args.max_source_control_patch_applier_dry_run_decisions
        ),
        max_source_control_guarded_patch_application_decisions=(
            args.max_source_control_guarded_patch_application_decisions
        ),
        max_source_control_post_change_verification_decisions=(
            args.max_source_control_post_change_verification_decisions
        ),
        max_source_control_read_only_git_inspection_decisions=(
            args.max_source_control_read_only_git_inspection_decisions
        ),
        max_source_control_staging_commit_preflight_decisions=(
            args.max_source_control_staging_commit_preflight_decisions
        ),
        max_source_control_staging_commit_execution_decisions=(
            args.max_source_control_staging_commit_execution_decisions
        ),
        max_source_control_project_index_staging_decisions=(
            args.max_source_control_project_index_staging_decisions
        ),
        max_source_control_commit_object_decisions=(
            args.max_source_control_commit_object_decisions
        ),
        max_source_control_ref_update_decisions=(
            args.max_source_control_ref_update_decisions
        ),
        verification_command_timeout_seconds=args.verification_command_timeout_seconds,
        git_inspection_command_timeout_seconds=args.git_inspection_command_timeout_seconds,
        git_execution_command_timeout_seconds=args.git_execution_command_timeout_seconds,
    )
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    else:
        output = report.summary_markdown()

    if args.out is None:
        print(output)
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output + "\n", encoding="utf-8")
    print(f"Saved source-control ref-update report to {args.out}")


def _add_source_control_post_change_verify_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    parser.add_argument("--approval-dir", type=Path, action="append", default=[])
    parser.add_argument("--approval-file", type=Path, action="append", default=[])
    parser.add_argument("--execution-approval-dir", type=Path, action="append", default=[])
    parser.add_argument("--execution-approval-file", type=Path, action="append", default=[])
    parser.add_argument("--authority-decision-dir", type=Path, action="append", default=[])
    parser.add_argument("--authority-decision-file", type=Path, action="append", default=[])
    parser.add_argument("--application-decision-dir", type=Path, action="append", default=[])
    parser.add_argument("--application-decision-file", type=Path, action="append", default=[])
    parser.add_argument("--maintainer-decision-dir", type=Path, action="append", default=[])
    parser.add_argument("--maintainer-decision-file", type=Path, action="append", default=[])
    parser.add_argument("--pr-decision-dir", type=Path, action="append", default=[])
    parser.add_argument("--pr-decision-file", type=Path, action="append", default=[])
    parser.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-patch-preview-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-patch-preview-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-apply-simulation-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-apply-simulation-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-patch-applier-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-patch-applier-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-guarded-patch-application-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-guarded-patch-application-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    parser.add_argument(
        "--source-control-guarded-patch-application-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_guarded_patch_application_20260601"],
        help="Directory containing existing guarded patch-application result JSON or manifests.",
    )
    parser.add_argument(
        "--source-control-guarded-patch-application-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing guarded patch-application result JSON or manifest. Can be passed multiple times.",
    )
    parser.add_argument(
        "--source-control-post-change-verification-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing post-change verification decision JSON packets.",
    )
    parser.add_argument(
        "--source-control-post-change-verification-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Post-change verification decision JSON packet. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601",
    )
    parser.add_argument("--worktree-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--schedule-file", type=Path, default=None)
    parser.add_argument("--state-file", type=Path, default=None)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-assets", type=int, default=None)
    parser.add_argument("--max-gate-executions", type=int, default=5)
    parser.add_argument("--max-goals", type=int, default=3)
    parser.add_argument("--max-cycles", type=int, default=3)
    parser.add_argument("--stable-stop-cycles", type=int, default=1)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--max-approvals", type=int, default=5)
    parser.add_argument("--max-hypotheses", type=int, default=18)
    parser.add_argument("--max-experiment-plans", type=int, default=18)
    parser.add_argument("--max-execution-approvals", type=int, default=5)
    parser.add_argument("--max-priority-updates", type=int, default=12)
    parser.add_argument("--max-next-approval-candidates", type=int, default=8)
    parser.add_argument("--max-authority-decisions", type=int, default=5)
    parser.add_argument("--max-application-decisions", type=int, default=5)
    parser.add_argument("--max-maintainer-decisions", type=int, default=5)
    parser.add_argument("--max-pr-decisions", type=int, default=5)
    parser.add_argument("--max-source-control-execution-decisions", type=int, default=5)
    parser.add_argument("--max-source-control-dry-run-decisions", type=int, default=5)
    parser.add_argument("--max-source-control-patch-preview-decisions", type=int, default=5)
    parser.add_argument("--max-source-control-apply-simulation-decisions", type=int, default=5)
    parser.add_argument("--max-source-control-patch-applier-dry-run-decisions", type=int, default=5)
    parser.add_argument(
        "--max-source-control-guarded-patch-application-decisions",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--max-source-control-post-change-verification-decisions",
        type=int,
        default=5,
    )
    parser.add_argument("--verification-command-timeout-seconds", type=int, default=120)
    parser.add_argument("--date-tag", default="20260601")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="consciousness-benchmark",
        description="Operational construct-validation benchmark for artificial systems.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    reference = sub.add_parser("reference", help="Reproduce frozen reference construct statistics.")
    reference.add_argument("--root", type=Path, default=PROJECT_ROOT)
    reference.add_argument("--bootstrap", type=int, default=10000)
    reference.add_argument("--seed", type=int, default=20260521)
    reference.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "docs" / "benchmark_reference_report_20260521.md",
    )
    reference.set_defaults(func=run_reference)

    online = sub.add_parser("online", help="Run a live MindLab online benchmark batch.")
    online.add_argument(
        "--condition-sets",
        nargs="*",
        default=["thalamus", "distributed", "meta-strength"],
        help="Condition sets: thalamus, distributed, meta-strength, meta-noise, meta-delay, all",
    )
    online.add_argument("--seeds", type=int, default=4)
    online.add_argument("--warmup", type=int, default=128)
    online.add_argument("--quick", action="store_true")
    online.add_argument("--bootstrap", type=int, default=10000)
    online.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "runs" / "benchmark_online")
    online.add_argument("--save-every", type=int, default=1)
    online.set_defaults(func=run_online)

    architecture = sub.add_parser(
        "architecture",
        help="Inspect or export the unified reference/candidate/preconstruct architecture.",
    )
    architecture.add_argument("--format", choices=["markdown", "json"], default="markdown")
    architecture.add_argument("--out", type=Path, default=None)
    architecture.set_defaults(func=run_architecture)

    ollama_probe = sub.add_parser(
        "mind-ollama-probe",
        help="Prepare or run a bounded local Ollama advisory probe.",
    )
    ollama_probe.add_argument(
        "--base-url",
        default="http://127.0.0.1:11434",
        help="Local Ollama base URL.",
    )
    ollama_probe.add_argument("--model", default=None, help="Installed Ollama model name.")
    ollama_probe.add_argument(
        "--prompt",
        default="Assess the next safe architecture improvement.",
        help="Operator prompt appended to the bounded architecture brief.",
    )
    ollama_probe.add_argument(
        "--live",
        action="store_true",
        help="Call the local Ollama server. By default the command is a dry run.",
    )
    ollama_probe.add_argument("--temperature", type=float, default=0.2)
    ollama_probe.add_argument("--num-predict", type=int, default=512)
    ollama_probe.add_argument("--timeout-seconds", type=float, default=30.0)
    ollama_probe.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    ollama_probe.add_argument("--out", type=Path, default=None)
    ollama_probe.set_defaults(func=run_ollama_probe)

    construct_runtime = sub.add_parser(
        "mind-runtime-tick",
        help="Run a construct-grounded single-tick mind runtime report.",
    )
    construct_runtime.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    construct_runtime.add_argument("--max-assets", type=int, default=50)
    construct_runtime.add_argument("--goal-limit", type=int, default=8)
    construct_runtime.add_argument("--composition-limit", type=int, default=10)
    construct_runtime.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    construct_runtime.add_argument("--out", type=Path, default=None)
    construct_runtime.set_defaults(func=run_construct_grounded_runtime)

    dependency_graph = sub.add_parser(
        "mind-dependency-graph",
        help="Export the inferred construct dependency graph and layered activation plan.",
    )
    dependency_graph.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    dependency_graph.add_argument("--out", type=Path, default=None)
    dependency_graph.set_defaults(func=run_construct_dependency_graph)

    executable_chain = sub.add_parser(
        "mind-execute-action-ownership-chain",
        help="Run the executable branch-binding -> agency -> boundary -> ownership chain.",
    )
    executable_chain.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic demo input when omitted.",
    )
    executable_chain.add_argument(
        "--chain-id",
        choices=executable_chain_ids(),
        default="action_ownership_dependency_chain",
        help="Executable construct chain to run.",
    )
    executable_chain.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    executable_chain.add_argument("--out", type=Path, default=None)
    executable_chain.set_defaults(func=run_executable_construct_chain)

    executable_construct_chain = sub.add_parser(
        "mind-execute-construct-chain",
        help="Run a named executable construct mechanism chain.",
    )
    executable_construct_chain.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic demo input when omitted.",
    )
    executable_construct_chain.add_argument(
        "--chain-id",
        choices=executable_chain_ids(),
        default="self_monitoring_basis_chain",
        help="Executable construct chain to run.",
    )
    executable_construct_chain.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    executable_construct_chain.add_argument("--out", type=Path, default=None)
    executable_construct_chain.set_defaults(func=run_executable_construct_chain)

    construct_capability = sub.add_parser(
        "mind-construct-capability-layer",
        help="Run bounded learning, emergence, autonomous-goal, and meta-learning assessment.",
    )
    construct_capability.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic demo input when omitted.",
    )
    construct_capability.add_argument(
        "--chain-id",
        choices=executable_chain_ids(),
        default="candidate_constructs_full_chain",
        help="Executable construct chain to assess.",
    )
    construct_capability.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    construct_capability.add_argument("--out", type=Path, default=None)
    construct_capability.set_defaults(func=run_construct_capability)

    growth_cycle = sub.add_parser(
        "mind-developmental-growth-cycle",
        help="Run a bounded developmental-growth runtime cycle and emit versioned trace corpus.",
    )
    growth_cycle.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic demo input when omitted.",
    )
    growth_cycle.add_argument(
        "--cycle-id",
        default="developmental_growth_cycle_20260602",
        help="Stable growth-cycle run id.",
    )
    growth_cycle.add_argument(
        "--stage-ids",
        nargs="*",
        default=[],
        help=(
            "Optional growth stage ids to run in order. "
            "Accepts comma-separated values and repeats (e.g. --stage-ids initial,early_exploration)."
        ),
    )
    growth_cycle.add_argument(
        "--ablation-group",
        action="append",
        default=[],
        help="Optional comma-separated disable group, e.g. --ablation-group global_broadcast_phase. "
        "Can be passed multiple times.",
    )
    growth_cycle.add_argument(
        "--no-ablation",
        action="store_true",
        help="Disable ablation diagnostics in this cycle.",
    )
    growth_cycle.add_argument(
        "--trace-dir",
        type=Path,
        default=None,
        help="If provided, writes versioned trace corpus JSONL + manifest there.",
    )
    growth_cycle.add_argument(
        "--trace-version",
        default="v1",
        help="Version tag used in trace artifact names.",
    )
    growth_cycle.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional deterministic seed for growth profile perturbation (default: built-in seed).",
    )
    growth_cycle.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    growth_cycle.add_argument("--out", type=Path, default=None)
    growth_cycle.set_defaults(func=run_developmental_growth_cycle_command)

    theory_assessment = sub.add_parser(
        "mind-consciousness-theory-assessment",
        help=(
            "Run a review-only multi-theory consciousness-indicator assessment "
            "with ablation matrix and closed sandbox trace corpus."
        ),
    )
    theory_assessment.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic closed-sandbox input when omitted.",
    )
    theory_assessment.add_argument(
        "--assessment-id",
        default="consciousness_theory_assessment_20260602",
        help="Stable assessment run id.",
    )
    theory_assessment.add_argument(
        "--case-ids",
        nargs="*",
        default=[],
        help=(
            "Optional indicator case ids to run. Accepts comma-separated values "
            "and repeats, e.g. --case-ids global_workspace,embodied_cognition."
        ),
    )
    theory_assessment.add_argument(
        "--no-ablation",
        action="store_true",
        help="Disable ablation diagnostics and emit review-only pending rows.",
    )
    theory_assessment.add_argument(
        "--trace-dir",
        type=Path,
        default=None,
        help="If provided, writes versioned evidence matrix and sandbox trace corpus.",
    )
    theory_assessment.add_argument(
        "--trace-version",
        default="v1",
        help="Version tag used in trace artifact names.",
    )
    theory_assessment.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    theory_assessment.add_argument("--out", type=Path, default=None)
    theory_assessment.set_defaults(func=run_consciousness_theory_assessment_command)

    growth_batch = sub.add_parser(
        "mind-developmental-growth-batch",
        help=(
            "Run bounded developmental growth/theory batches for seed-level stability evidence. "
            "Outputs a versioned aggregate batch summary."
        ),
    )
    growth_batch.add_argument(
        "--profile",
        choices=["exploration", "validation", "production", "quick_check"],
        default=None,
        help=(
            "Use a predefined run profile (exploration, validation, production, quick_check). "
            "Explicit CLI flags override profile defaults."
        ),
    )
    growth_batch.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available growth batch profiles and exit.",
    )
    growth_batch.add_argument(
        "--seed",
        type=int,
        action="append",
        default=None,
        help="Seed values to run (repeatable). Can be specified multiple times.",
    )
    growth_batch.add_argument(
        "--seed-csv",
        type=str,
        default=None,
        help="Optional comma-separated seed override.",
    )
    growth_batch.add_argument(
        "--stage-ids",
        nargs="*",
        default=[],
        help=(
            "Optional growth stage ids to run in order. "
            "Accepts comma-separated values and repeats (e.g. --stage-ids initial,early_exploration)."
        ),
    )
    growth_batch.add_argument(
        "--theory-case-id",
        action="append",
        default=[],
        help=(
            "Optional theory case id to run in each seed (repeatable). "
            "Accepts comma-separated values and repeats."
        ),
    )
    growth_batch.add_argument("--no-growth-ablation", action="store_true")
    growth_batch.add_argument("--no-theory-ablation", action="store_true")
    growth_batch.add_argument("--run-gatecheck", action="store_true")
    growth_batch.add_argument(
        "--gatebook-path",
        type=Path,
        default=(PROJECT_ROOT / "docs" / "c_agi_layer_gatebook_20260602.json"),
        help="Optional custom layer gatebook JSON when --run-gatecheck is used.",
    )
    growth_batch.add_argument(
        "--output-root",
        type=Path,
        default=(PROJECT_ROOT / "runs" / "exec_20260602_growth_batch"),
        help="Root folder to write batch artifacts.",
    )
    growth_batch.add_argument("--growth-trace-version", default="v1")
    growth_batch.add_argument("--theory-trace-version", default="v1")
    growth_batch.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="Number of replay rounds to run.",
    )
    growth_batch.add_argument(
        "--seed-step",
        type=int,
        default=0,
        help=(
            "Seed increment between replay rounds. "
            "0 keeps the same seeds; >0 advances seeds each round."
        ),
    )
    growth_batch.add_argument(
        "--require-health-pass",
        action="store_true",
        help=(
            "Require strict health gate evaluation (health_status == pass). "
            "If any configured requirement fails, the command exits non-zero."
        ),
    )
    growth_batch.add_argument(
        "--health-min-score",
        type=float,
        default=None,
        help="Optional minimum batch health_score required for pass.",
    )
    growth_batch.add_argument(
        "--health-oscillation-threshold",
        type=float,
        default=None,
        help="Optional maximum oscillatory_rate threshold. If exceeded, the command exits non-zero.",
    )
    growth_batch.add_argument(
        "--health-regression-threshold",
        type=float,
        default=None,
        help="Optional maximum regression_rate threshold. If exceeded, the command exits non-zero.",
    )
    growth_batch.add_argument(
        "--min-phase2-unique-constructs",
        type=int,
        default=None,
        help="Optional minimum phase2 unique construct count required for pass.",
    )
    growth_batch.add_argument(
        "--min-phase2-dynamic-construct-count",
        type=int,
        default=None,
        help="Optional minimum phase2 dynamic construct proposal count required for pass.",
    )
    growth_batch.add_argument(
        "--min-phase2-rows-with-phase2-data",
        type=int,
        default=None,
        help="Optional minimum number of phase2 rows required for coverage gate.",
    )
    growth_batch.add_argument(
        "--min-phase2-temporal-sequence-ratio",
        type=float,
        default=None,
        help=(
            "Optional minimum ratio of rows with temporal sequence evidence among phase2 rows. "
            "Value should be in [0,1]."
        ),
    )
    growth_batch.add_argument(
        "--min-phase2-dynamic-ratio",
        type=float,
        default=None,
        help=(
            "Optional minimum ratio of rows with dynamic construct proposals among phase2 rows. "
            "Value should be in [0,1]."
        ),
    )
    growth_batch.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="json",
    )
    growth_batch.add_argument("--out", type=Path, default=None)
    growth_batch.set_defaults(func=run_developmental_growth_batch_command)

    persistent_agent = sub.add_parser(
        "mind-run-persistent-agent",
        help="Run a bounded persistent sandbox agent with autobiographical memory.",
    )
    persistent_agent.add_argument(
        "--workspace",
        type=Path,
        default=PROJECT_ROOT / "sandbox" / "demo_agent",
    )
    persistent_agent.add_argument("--llm", default=None)
    persistent_agent.add_argument("--steps", type=int, default=20)
    persistent_agent.add_argument("--interval", type=float, default=2.0)
    persistent_agent.add_argument("--setup-demo", action="store_true")
    persistent_agent.add_argument(
        "--dry-run",
        action="store_true",
        help="Use heuristic planner without calling Ollama.",
    )
    persistent_agent.add_argument("--quiet", action="store_true")
    persistent_agent.set_defaults(func=run_persistent_agent_command)

    construct_agent = sub.add_parser(
        "mind-run-construct-aware-agent",
        help="Run persistent sandbox agent grounded in construct mind runtime ticks.",
    )
    construct_agent.add_argument(
        "--workspace",
        type=Path,
        default=PROJECT_ROOT / "sandbox" / "construct_agent",
    )
    construct_agent.add_argument("--llm", default=None)
    construct_agent.add_argument("--steps", type=int, default=20)
    construct_agent.add_argument("--interval", type=float, default=2.0)
    construct_agent.add_argument("--setup-demo", action="store_true")
    construct_agent.add_argument("--dry-run", action="store_true")
    construct_agent.add_argument("--quiet", action="store_true")
    construct_agent.set_defaults(func=run_construct_aware_agent_command)

    talk_agent = sub.add_parser(
        "mind-talk-to-agent",
        help="Ask a read-only question against agent autobiographical memory.",
    )
    talk_agent.add_argument(
        "--workspace",
        type=Path,
        default=PROJECT_ROOT / "sandbox" / "construct_agent",
    )
    talk_agent.add_argument("--question", required=True)
    talk_agent.add_argument("--llm", default=None)
    talk_agent.add_argument("--dry-run", action="store_true")
    talk_agent.set_defaults(func=run_talk_to_agent_command)

    gatebook_check = sub.add_parser(
        "mind-c-agi-layer-gatecheck",
        help="Run the C-AGI layer gatebook gate checks with growth + theory validation.",
    )
    gatebook_check.add_argument(
        "--trace-dir",
        type=Path,
        default=None,
        help=(
            "If provided, writes versioned growth/theory trace corpus JSONL + manifest and "
            "a combined gatecheck report."
        ),
    )
    gatebook_check.add_argument(
        "--growth-stage-ids",
        nargs="*",
        default=[],
        help=(
            "Optional growth stage ids to run in order. "
            "Accepts comma-separated values and repeats (e.g. --growth-stage-ids initial,early_exploration)."
        ),
    )
    gatebook_check.add_argument(
        "--growth-no-ablation",
        action="store_true",
        help="Disable growth ablation diagnostics for this check.",
    )
    gatebook_check.add_argument(
        "--growth-seed",
        type=int,
        default=None,
        help="Optional deterministic seed forwarded to growth execution.",
    )
    gatebook_check.add_argument(
        "--growth-trace-version",
        default="v1",
        help="Version tag used for growth trace artifact names.",
    )
    gatebook_check.add_argument(
        "--case-ids",
        nargs="*",
        default=[],
        help=(
            "Optional theory case ids to run in this check. "
            "Defaults to required gatebook matrix indicators when omitted."
        ),
    )
    gatebook_check.add_argument(
        "--theory-no-ablation",
        action="store_true",
        help="Disable theory ablation diagnostics for this check.",
    )
    gatebook_check.add_argument(
        "--theory-trace-version",
        default="v1",
        help="Version tag used for theory trace artifact names.",
    )
    gatebook_check.add_argument(
        "--gatebook",
        type=Path,
        default=(PROJECT_ROOT / "docs" / "c_agi_layer_gatebook_20260602.json"),
        help="Optional custom layer gatebook JSON to validate.",
    )
    gatebook_check.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    gatebook_check.add_argument("--out", type=Path, default=None)
    gatebook_check.set_defaults(func=run_c_agi_layer_gatebook_check_command)

    phase1_training = sub.add_parser(
        "mind-phase1-train",
        help="Run an explicit bounded Phase 1 neural training and replay artifact cycle.",
    )
    phase1_training.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional JSON input state. Uses a deterministic demo input when omitted.",
    )
    phase1_training.add_argument(
        "--chain-id",
        choices=executable_chain_ids(),
        default="candidate_constructs_full_chain",
        help="Executable construct chain to train against.",
    )
    phase1_training.add_argument("--epochs", type=int, default=3)
    phase1_training.add_argument("--batch-size", type=int, default=32)
    phase1_training.add_argument("--validation-fraction", type=float, default=0.2)
    phase1_training.add_argument(
        "--approval-id",
        default=None,
        help="Optional operator approval identifier. Checkpoint writes require this id and --persist-weights.",
    )
    phase1_training.add_argument(
        "--persist-weights",
        action="store_true",
        help="Request checkpoint persistence. Checkpoint writes require --approval-id plus this flag.",
    )
    phase1_training.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Optional directory for approved checkpoint writes and manifest artifacts.",
    )
    phase1_training.add_argument(
        "--checkpoint-restore-dir",
        type=Path,
        default=None,
        help="Optional directory containing a checkpoint manifest to restore learner weights before training.",
    )
    phase1_training.add_argument(
        "--replay-bundle-dir",
        type=Path,
        default=None,
        help="Optional directory containing replay buffer manifest for restore and optional replay save.",
    )
    phase1_training.add_argument(
        "--persist-replay",
        action="store_true",
        help="Request replay bundle persistence. Replay writes require --approval-id plus this flag.",
    )
    phase1_training.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    phase1_training.add_argument("--out", type=Path, default=None)
    phase1_training.set_defaults(func=run_phase1_training)

    phase1_feedback = sub.add_parser(
        "mind-phase1-feedback-regression",
        help="Run bounded Phase 1 feedback regression fixtures over an executable construct chain.",
    )
    phase1_feedback.add_argument(
        "--chain-id",
        choices=executable_chain_ids(),
        default="candidate_constructs_full_chain",
        help="Executable construct chain to assess.",
    )
    phase1_feedback.add_argument(
        "--max-fixtures",
        type=int,
        default=None,
        help="Optional cap on deterministic feedback fixtures.",
    )
    phase1_feedback.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Optional previous feedback regression JSON report used as a drift baseline.",
    )
    phase1_feedback.add_argument(
        "--write-baseline",
        type=Path,
        default=None,
        help="Optional path to write the current feedback regression JSON as a future baseline.",
    )
    phase1_feedback.add_argument("--max-baseline-global-drop", type=float, default=0.05)
    phase1_feedback.add_argument("--max-baseline-reward-drop", type=float, default=0.12)
    phase1_feedback.add_argument("--max-baseline-criterion-drop", type=float, default=0.08)
    phase1_feedback.add_argument(
        "--format", choices=["markdown", "json"], default="markdown"
    )
    phase1_feedback.add_argument("--out", type=Path, default=None)
    phase1_feedback.set_defaults(func=run_phase1_feedback_regression)

    intelligence = sub.add_parser(
        "intelligence-cycle",
        help="Run a read-only observe/orient/propose/plan cycle over evidence assets.",
    )
    intelligence.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    intelligence.add_argument("--format", choices=["markdown", "json"], default="markdown")
    intelligence.add_argument("--out", type=Path, default=None)
    intelligence.add_argument("--max-assets", type=int, default=None)
    intelligence.add_argument("--proposal-limit", type=int, default=30)
    intelligence.set_defaults(func=run_intelligence_cycle)

    execution = sub.add_parser(
        "intelligence-execute",
        help="Run bounded low/medium-risk local execution over evidence assets.",
    )
    execution.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    execution.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "research_intelligence_execution_20260601",
    )
    execution.add_argument("--risk-mode", choices=["low", "medium"], default="medium")
    execution.add_argument("--format", choices=["markdown", "json"], default="markdown")
    execution.add_argument("--out", type=Path, default=None)
    execution.add_argument("--max-assets", type=int, default=None)
    execution.add_argument("--date-tag", default="20260601")
    execution.set_defaults(func=run_intelligence_execute)

    agent = sub.add_parser(
        "intelligence-agent",
        help="Run an A4 controlled think/critique/execute/remember cycle.",
    )
    agent.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    agent.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "controlled_research_cycle_20260601",
    )
    agent.add_argument("--format", choices=["markdown", "json"], default="markdown")
    agent.add_argument("--out", type=Path, default=None)
    agent.add_argument("--max-assets", type=int, default=None)
    agent.add_argument("--max-gate-executions", type=int, default=5)
    agent.add_argument("--date-tag", default="20260601")
    agent.set_defaults(func=run_intelligence_agent)

    loop = sub.add_parser(
        "intelligence-loop",
        help="Run an A5 invoked monitor/goal/probe/memory loop.",
    )
    loop.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    loop.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "autonomous_research_loop_20260601",
    )
    loop.add_argument("--state-file", type=Path, default=None)
    loop.add_argument("--format", choices=["markdown", "json"], default="markdown")
    loop.add_argument("--out", type=Path, default=None)
    loop.add_argument("--max-assets", type=int, default=None)
    loop.add_argument("--max-gate-executions", type=int, default=5)
    loop.add_argument("--max-goals", type=int, default=3)
    loop.add_argument("--date-tag", default="20260601")
    loop.set_defaults(func=run_intelligence_loop)

    runtime = sub.add_parser(
        "intelligence-runtime",
        help="Run an A6 invoked continuous autonomous runtime under a fixed budget.",
    )
    runtime.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    runtime.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "autonomous_runtime_20260601",
    )
    runtime.add_argument("--state-file", type=Path, default=None)
    runtime.add_argument("--format", choices=["markdown", "json"], default="markdown")
    runtime.add_argument("--out", type=Path, default=None)
    runtime.add_argument("--max-assets", type=int, default=None)
    runtime.add_argument("--max-gate-executions", type=int, default=5)
    runtime.add_argument("--max-goals", type=int, default=3)
    runtime.add_argument("--max-cycles", type=int, default=3)
    runtime.add_argument("--stable-stop-cycles", type=int, default=2)
    runtime.add_argument("--sleep-seconds", type=float, default=0.0)
    runtime.add_argument("--date-tag", default="20260601")
    runtime.set_defaults(func=run_intelligence_runtime)

    probe_executor = sub.add_parser(
        "intelligence-probe-executor",
        help="Run A7 reviewed local validation probes from approval packets.",
    )
    probe_executor.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    probe_executor.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    probe_executor.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    probe_executor.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "reviewed_probe_executor_20260601",
    )
    probe_executor.add_argument("--format", choices=["markdown", "json"], default="markdown")
    probe_executor.add_argument("--out", type=Path, default=None)
    probe_executor.add_argument("--max-assets", type=int, default=None)
    probe_executor.add_argument("--max-gate-executions", type=int, default=5)
    probe_executor.add_argument("--max-approvals", type=int, default=5)
    probe_executor.add_argument("--date-tag", default="20260601")
    probe_executor.set_defaults(func=run_intelligence_probe_executor)

    decision_writer = sub.add_parser(
        "intelligence-decision-writer",
        help="Run A8 review-only decision artifact writing from approved probe evidence.",
    )
    decision_writer.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    decision_writer.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    decision_writer.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    decision_writer.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "reviewed_decision_writer_20260601",
    )
    decision_writer.add_argument("--format", choices=["markdown", "json"], default="markdown")
    decision_writer.add_argument("--out", type=Path, default=None)
    decision_writer.add_argument("--max-assets", type=int, default=None)
    decision_writer.add_argument("--max-gate-executions", type=int, default=5)
    decision_writer.add_argument("--max-approvals", type=int, default=5)
    decision_writer.add_argument("--date-tag", default="20260601")
    decision_writer.set_defaults(func=run_intelligence_decision_writer)

    scheduled_tick = sub.add_parser(
        "intelligence-scheduled-tick",
        help="Run the A9 external-scheduler-ready medium-risk autonomy pipeline.",
    )
    scheduled_tick.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    scheduled_tick.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    scheduled_tick.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    scheduled_tick.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "scheduled_autonomy_20260601",
    )
    scheduled_tick.add_argument("--schedule-file", type=Path, default=None)
    scheduled_tick.add_argument("--state-file", type=Path, default=None)
    scheduled_tick.add_argument("--format", choices=["markdown", "json"], default="markdown")
    scheduled_tick.add_argument("--out", type=Path, default=None)
    scheduled_tick.add_argument("--max-assets", type=int, default=None)
    scheduled_tick.add_argument("--max-gate-executions", type=int, default=5)
    scheduled_tick.add_argument("--max-goals", type=int, default=3)
    scheduled_tick.add_argument("--max-cycles", type=int, default=3)
    scheduled_tick.add_argument("--stable-stop-cycles", type=int, default=1)
    scheduled_tick.add_argument("--sleep-seconds", type=float, default=0.0)
    scheduled_tick.add_argument("--max-approvals", type=int, default=5)
    scheduled_tick.add_argument("--date-tag", default="20260601")
    scheduled_tick.set_defaults(func=run_intelligence_scheduled_tick)

    thinking_cycle = sub.add_parser(
        "intelligence-thinking-cycle",
        help="Run the A10 scheduler-backed hypothesis and experiment-plan cycle.",
    )
    thinking_cycle.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    thinking_cycle.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    thinking_cycle.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    thinking_cycle.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "autonomous_thinking_20260601",
    )
    thinking_cycle.add_argument("--schedule-file", type=Path, default=None)
    thinking_cycle.add_argument("--state-file", type=Path, default=None)
    thinking_cycle.add_argument("--format", choices=["markdown", "json"], default="markdown")
    thinking_cycle.add_argument("--out", type=Path, default=None)
    thinking_cycle.add_argument("--max-assets", type=int, default=None)
    thinking_cycle.add_argument("--max-gate-executions", type=int, default=5)
    thinking_cycle.add_argument("--max-goals", type=int, default=3)
    thinking_cycle.add_argument("--max-cycles", type=int, default=3)
    thinking_cycle.add_argument("--stable-stop-cycles", type=int, default=1)
    thinking_cycle.add_argument("--sleep-seconds", type=float, default=0.0)
    thinking_cycle.add_argument("--max-approvals", type=int, default=5)
    thinking_cycle.add_argument("--max-hypotheses", type=int, default=18)
    thinking_cycle.add_argument("--max-experiment-plans", type=int, default=18)
    thinking_cycle.add_argument("--date-tag", default="20260601")
    thinking_cycle.set_defaults(func=run_intelligence_thinking_cycle)

    adversarial_review = sub.add_parser(
        "intelligence-adversarial-review",
        help="Run the A11 adversarial review cycle over generated hypotheses and plans.",
    )
    adversarial_review.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    adversarial_review.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    adversarial_review.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    adversarial_review.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "adversarial_review_20260601",
    )
    adversarial_review.add_argument("--schedule-file", type=Path, default=None)
    adversarial_review.add_argument("--state-file", type=Path, default=None)
    adversarial_review.add_argument("--format", choices=["markdown", "json"], default="markdown")
    adversarial_review.add_argument("--out", type=Path, default=None)
    adversarial_review.add_argument("--max-assets", type=int, default=None)
    adversarial_review.add_argument("--max-gate-executions", type=int, default=5)
    adversarial_review.add_argument("--max-goals", type=int, default=3)
    adversarial_review.add_argument("--max-cycles", type=int, default=3)
    adversarial_review.add_argument("--stable-stop-cycles", type=int, default=1)
    adversarial_review.add_argument("--sleep-seconds", type=float, default=0.0)
    adversarial_review.add_argument("--max-approvals", type=int, default=5)
    adversarial_review.add_argument("--max-hypotheses", type=int, default=18)
    adversarial_review.add_argument("--max-experiment-plans", type=int, default=18)
    adversarial_review.add_argument("--date-tag", default="20260601")
    adversarial_review.set_defaults(func=run_intelligence_adversarial_review)

    approved_execution = sub.add_parser(
        "intelligence-approved-execution",
        help="Run the A12 approved local plan dry-run execution cycle.",
    )
    approved_execution.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    approved_execution.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    approved_execution.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    approved_execution.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    approved_execution.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    approved_execution.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "approved_execution_20260601",
    )
    approved_execution.add_argument("--schedule-file", type=Path, default=None)
    approved_execution.add_argument("--state-file", type=Path, default=None)
    approved_execution.add_argument("--format", choices=["markdown", "json"], default="markdown")
    approved_execution.add_argument("--out", type=Path, default=None)
    approved_execution.add_argument("--max-assets", type=int, default=None)
    approved_execution.add_argument("--max-gate-executions", type=int, default=5)
    approved_execution.add_argument("--max-goals", type=int, default=3)
    approved_execution.add_argument("--max-cycles", type=int, default=3)
    approved_execution.add_argument("--stable-stop-cycles", type=int, default=1)
    approved_execution.add_argument("--sleep-seconds", type=float, default=0.0)
    approved_execution.add_argument("--max-approvals", type=int, default=5)
    approved_execution.add_argument("--max-hypotheses", type=int, default=18)
    approved_execution.add_argument("--max-experiment-plans", type=int, default=18)
    approved_execution.add_argument("--max-execution-approvals", type=int, default=5)
    approved_execution.add_argument("--date-tag", default="20260601")
    approved_execution.set_defaults(func=run_intelligence_approved_execution)

    adaptive_cycle = sub.add_parser(
        "intelligence-adaptive-cycle",
        help="Run the A13 outcome-adaptive execution and next-strategy cycle.",
    )
    adaptive_cycle.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    adaptive_cycle.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    adaptive_cycle.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    adaptive_cycle.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    adaptive_cycle.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    adaptive_cycle.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "adaptive_outcome_learning_20260601",
    )
    adaptive_cycle.add_argument("--schedule-file", type=Path, default=None)
    adaptive_cycle.add_argument("--state-file", type=Path, default=None)
    adaptive_cycle.add_argument("--format", choices=["markdown", "json"], default="markdown")
    adaptive_cycle.add_argument("--out", type=Path, default=None)
    adaptive_cycle.add_argument("--max-assets", type=int, default=None)
    adaptive_cycle.add_argument("--max-gate-executions", type=int, default=5)
    adaptive_cycle.add_argument("--max-goals", type=int, default=3)
    adaptive_cycle.add_argument("--max-cycles", type=int, default=3)
    adaptive_cycle.add_argument("--stable-stop-cycles", type=int, default=1)
    adaptive_cycle.add_argument("--sleep-seconds", type=float, default=0.0)
    adaptive_cycle.add_argument("--max-approvals", type=int, default=5)
    adaptive_cycle.add_argument("--max-hypotheses", type=int, default=18)
    adaptive_cycle.add_argument("--max-experiment-plans", type=int, default=18)
    adaptive_cycle.add_argument("--max-execution-approvals", type=int, default=5)
    adaptive_cycle.add_argument("--max-priority-updates", type=int, default=12)
    adaptive_cycle.add_argument("--max-next-approval-candidates", type=int, default=8)
    adaptive_cycle.add_argument("--date-tag", default="20260601")
    adaptive_cycle.set_defaults(func=run_intelligence_adaptive_cycle)

    status_authority = sub.add_parser(
        "intelligence-status-authority",
        help="Run the A14 external status-authority review-state overlay cycle.",
    )
    status_authority.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    status_authority.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    status_authority.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    status_authority.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    status_authority.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    status_authority.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    status_authority.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    status_authority.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "status_authority_20260601",
    )
    status_authority.add_argument("--schedule-file", type=Path, default=None)
    status_authority.add_argument("--state-file", type=Path, default=None)
    status_authority.add_argument("--format", choices=["markdown", "json"], default="markdown")
    status_authority.add_argument("--out", type=Path, default=None)
    status_authority.add_argument("--max-assets", type=int, default=None)
    status_authority.add_argument("--max-gate-executions", type=int, default=5)
    status_authority.add_argument("--max-goals", type=int, default=3)
    status_authority.add_argument("--max-cycles", type=int, default=3)
    status_authority.add_argument("--stable-stop-cycles", type=int, default=1)
    status_authority.add_argument("--sleep-seconds", type=float, default=0.0)
    status_authority.add_argument("--max-approvals", type=int, default=5)
    status_authority.add_argument("--max-hypotheses", type=int, default=18)
    status_authority.add_argument("--max-experiment-plans", type=int, default=18)
    status_authority.add_argument("--max-execution-approvals", type=int, default=5)
    status_authority.add_argument("--max-priority-updates", type=int, default=12)
    status_authority.add_argument("--max-next-approval-candidates", type=int, default=8)
    status_authority.add_argument("--max-authority-decisions", type=int, default=5)
    status_authority.add_argument("--date-tag", default="20260601")
    status_authority.set_defaults(func=run_intelligence_status_authority)

    council_review = sub.add_parser(
        "intelligence-council-review",
        help="Run the A15 multi-role council review cycle over A14 overlays.",
    )
    council_review.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    council_review.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    council_review.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    council_review.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    council_review.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    council_review.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    council_review.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    council_review.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "council_review_20260601",
    )
    council_review.add_argument("--schedule-file", type=Path, default=None)
    council_review.add_argument("--state-file", type=Path, default=None)
    council_review.add_argument("--format", choices=["markdown", "json"], default="markdown")
    council_review.add_argument("--out", type=Path, default=None)
    council_review.add_argument("--max-assets", type=int, default=None)
    council_review.add_argument("--max-gate-executions", type=int, default=5)
    council_review.add_argument("--max-goals", type=int, default=3)
    council_review.add_argument("--max-cycles", type=int, default=3)
    council_review.add_argument("--stable-stop-cycles", type=int, default=1)
    council_review.add_argument("--sleep-seconds", type=float, default=0.0)
    council_review.add_argument("--max-approvals", type=int, default=5)
    council_review.add_argument("--max-hypotheses", type=int, default=18)
    council_review.add_argument("--max-experiment-plans", type=int, default=18)
    council_review.add_argument("--max-execution-approvals", type=int, default=5)
    council_review.add_argument("--max-priority-updates", type=int, default=12)
    council_review.add_argument("--max-next-approval-candidates", type=int, default=8)
    council_review.add_argument("--max-authority-decisions", type=int, default=5)
    council_review.add_argument("--date-tag", default="20260601")
    council_review.set_defaults(func=run_intelligence_council_review)

    formal_proposal = sub.add_parser(
        "intelligence-formal-proposal",
        help="Run the A16 formal proposal drafting cycle over A15 council consensus.",
    )
    formal_proposal.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    formal_proposal.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    formal_proposal.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    formal_proposal.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    formal_proposal.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    formal_proposal.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    formal_proposal.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    formal_proposal.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "formal_proposal_20260601",
    )
    formal_proposal.add_argument("--schedule-file", type=Path, default=None)
    formal_proposal.add_argument("--state-file", type=Path, default=None)
    formal_proposal.add_argument("--format", choices=["markdown", "json"], default="markdown")
    formal_proposal.add_argument("--out", type=Path, default=None)
    formal_proposal.add_argument("--max-assets", type=int, default=None)
    formal_proposal.add_argument("--max-gate-executions", type=int, default=5)
    formal_proposal.add_argument("--max-goals", type=int, default=3)
    formal_proposal.add_argument("--max-cycles", type=int, default=3)
    formal_proposal.add_argument("--stable-stop-cycles", type=int, default=1)
    formal_proposal.add_argument("--sleep-seconds", type=float, default=0.0)
    formal_proposal.add_argument("--max-approvals", type=int, default=5)
    formal_proposal.add_argument("--max-hypotheses", type=int, default=18)
    formal_proposal.add_argument("--max-experiment-plans", type=int, default=18)
    formal_proposal.add_argument("--max-execution-approvals", type=int, default=5)
    formal_proposal.add_argument("--max-priority-updates", type=int, default=12)
    formal_proposal.add_argument("--max-next-approval-candidates", type=int, default=8)
    formal_proposal.add_argument("--max-authority-decisions", type=int, default=5)
    formal_proposal.add_argument("--date-tag", default="20260601")
    formal_proposal.set_defaults(func=run_intelligence_formal_proposal)

    proposal_application = sub.add_parser(
        "intelligence-proposal-application",
        help="Run the A17 signed proposal application cycle into append-only patch drafts.",
    )
    proposal_application.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    proposal_application.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    proposal_application.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    proposal_application.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    proposal_application.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    proposal_application.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    proposal_application.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    proposal_application.add_argument(
        "--application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing signed proposal application decision JSON packets.",
    )
    proposal_application.add_argument(
        "--application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Signed proposal application decision JSON packet. Can be passed multiple times.",
    )
    proposal_application.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "proposal_application_20260601",
    )
    proposal_application.add_argument("--schedule-file", type=Path, default=None)
    proposal_application.add_argument("--state-file", type=Path, default=None)
    proposal_application.add_argument("--format", choices=["markdown", "json"], default="markdown")
    proposal_application.add_argument("--out", type=Path, default=None)
    proposal_application.add_argument("--max-assets", type=int, default=None)
    proposal_application.add_argument("--max-gate-executions", type=int, default=5)
    proposal_application.add_argument("--max-goals", type=int, default=3)
    proposal_application.add_argument("--max-cycles", type=int, default=3)
    proposal_application.add_argument("--stable-stop-cycles", type=int, default=1)
    proposal_application.add_argument("--sleep-seconds", type=float, default=0.0)
    proposal_application.add_argument("--max-approvals", type=int, default=5)
    proposal_application.add_argument("--max-hypotheses", type=int, default=18)
    proposal_application.add_argument("--max-experiment-plans", type=int, default=18)
    proposal_application.add_argument("--max-execution-approvals", type=int, default=5)
    proposal_application.add_argument("--max-priority-updates", type=int, default=12)
    proposal_application.add_argument("--max-next-approval-candidates", type=int, default=8)
    proposal_application.add_argument("--max-authority-decisions", type=int, default=5)
    proposal_application.add_argument("--max-application-decisions", type=int, default=5)
    proposal_application.add_argument("--date-tag", default="20260601")
    proposal_application.set_defaults(func=run_intelligence_proposal_application)

    maintainer_merge = sub.add_parser(
        "intelligence-maintainer-merge",
        help="Run the A18 maintainer merge review cycle into simulated registry overlays.",
    )
    maintainer_merge.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    maintainer_merge.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    maintainer_merge.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    maintainer_merge.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing signed proposal application decision JSON packets.",
    )
    maintainer_merge.add_argument(
        "--application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Signed proposal application decision JSON packet. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--maintainer-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external maintainer merge decision JSON packets.",
    )
    maintainer_merge.add_argument(
        "--maintainer-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External maintainer merge decision JSON packet. Can be passed multiple times.",
    )
    maintainer_merge.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "maintainer_merge_20260601",
    )
    maintainer_merge.add_argument("--schedule-file", type=Path, default=None)
    maintainer_merge.add_argument("--state-file", type=Path, default=None)
    maintainer_merge.add_argument("--format", choices=["markdown", "json"], default="markdown")
    maintainer_merge.add_argument("--out", type=Path, default=None)
    maintainer_merge.add_argument("--max-assets", type=int, default=None)
    maintainer_merge.add_argument("--max-gate-executions", type=int, default=5)
    maintainer_merge.add_argument("--max-goals", type=int, default=3)
    maintainer_merge.add_argument("--max-cycles", type=int, default=3)
    maintainer_merge.add_argument("--stable-stop-cycles", type=int, default=1)
    maintainer_merge.add_argument("--sleep-seconds", type=float, default=0.0)
    maintainer_merge.add_argument("--max-approvals", type=int, default=5)
    maintainer_merge.add_argument("--max-hypotheses", type=int, default=18)
    maintainer_merge.add_argument("--max-experiment-plans", type=int, default=18)
    maintainer_merge.add_argument("--max-execution-approvals", type=int, default=5)
    maintainer_merge.add_argument("--max-priority-updates", type=int, default=12)
    maintainer_merge.add_argument("--max-next-approval-candidates", type=int, default=8)
    maintainer_merge.add_argument("--max-authority-decisions", type=int, default=5)
    maintainer_merge.add_argument("--max-application-decisions", type=int, default=5)
    maintainer_merge.add_argument("--max-maintainer-decisions", type=int, default=5)
    maintainer_merge.add_argument("--date-tag", default="20260601")
    maintainer_merge.set_defaults(func=run_intelligence_maintainer_merge)

    source_control_pr = sub.add_parser(
        "intelligence-source-control-pr",
        help="Run the A19 source-control PR draft cycle without creating branches or PRs.",
    )
    source_control_pr.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    source_control_pr.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    source_control_pr.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    source_control_pr.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing signed proposal application decision JSON packets.",
    )
    source_control_pr.add_argument(
        "--application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Signed proposal application decision JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--maintainer-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external maintainer merge decision JSON packets.",
    )
    source_control_pr.add_argument(
        "--maintainer-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External maintainer merge decision JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--pr-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control PR draft decision JSON packets.",
    )
    source_control_pr.add_argument(
        "--pr-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control PR draft decision JSON packet. Can be passed multiple times.",
    )
    source_control_pr.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_pr_20260601",
    )
    source_control_pr.add_argument("--schedule-file", type=Path, default=None)
    source_control_pr.add_argument("--state-file", type=Path, default=None)
    source_control_pr.add_argument("--format", choices=["markdown", "json"], default="markdown")
    source_control_pr.add_argument("--out", type=Path, default=None)
    source_control_pr.add_argument("--max-assets", type=int, default=None)
    source_control_pr.add_argument("--max-gate-executions", type=int, default=5)
    source_control_pr.add_argument("--max-goals", type=int, default=3)
    source_control_pr.add_argument("--max-cycles", type=int, default=3)
    source_control_pr.add_argument("--stable-stop-cycles", type=int, default=1)
    source_control_pr.add_argument("--sleep-seconds", type=float, default=0.0)
    source_control_pr.add_argument("--max-approvals", type=int, default=5)
    source_control_pr.add_argument("--max-hypotheses", type=int, default=18)
    source_control_pr.add_argument("--max-experiment-plans", type=int, default=18)
    source_control_pr.add_argument("--max-execution-approvals", type=int, default=5)
    source_control_pr.add_argument("--max-priority-updates", type=int, default=12)
    source_control_pr.add_argument("--max-next-approval-candidates", type=int, default=8)
    source_control_pr.add_argument("--max-authority-decisions", type=int, default=5)
    source_control_pr.add_argument("--max-application-decisions", type=int, default=5)
    source_control_pr.add_argument("--max-maintainer-decisions", type=int, default=5)
    source_control_pr.add_argument("--max-pr-decisions", type=int, default=5)
    source_control_pr.add_argument("--date-tag", default="20260601")
    source_control_pr.set_defaults(func=run_intelligence_source_control_pr)

    source_control_execution = sub.add_parser(
        "intelligence-source-control-execution",
        help="Run the A20 external source-control execution packet cycle without running git operations.",
    )
    source_control_execution.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    source_control_execution.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    source_control_execution.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    source_control_execution.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing signed proposal application decision JSON packets.",
    )
    source_control_execution.add_argument(
        "--application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Signed proposal application decision JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--maintainer-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external maintainer merge decision JSON packets.",
    )
    source_control_execution.add_argument(
        "--maintainer-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External maintainer merge decision JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--pr-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control PR draft decision JSON packets.",
    )
    source_control_execution.add_argument(
        "--pr-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control PR draft decision JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control execution decision JSON packets.",
    )
    source_control_execution.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control execution decision JSON packet. Can be passed multiple times.",
    )
    source_control_execution.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_execution_20260601",
    )
    source_control_execution.add_argument("--schedule-file", type=Path, default=None)
    source_control_execution.add_argument("--state-file", type=Path, default=None)
    source_control_execution.add_argument("--format", choices=["markdown", "json"], default="markdown")
    source_control_execution.add_argument("--out", type=Path, default=None)
    source_control_execution.add_argument("--max-assets", type=int, default=None)
    source_control_execution.add_argument("--max-gate-executions", type=int, default=5)
    source_control_execution.add_argument("--max-goals", type=int, default=3)
    source_control_execution.add_argument("--max-cycles", type=int, default=3)
    source_control_execution.add_argument("--stable-stop-cycles", type=int, default=1)
    source_control_execution.add_argument("--sleep-seconds", type=float, default=0.0)
    source_control_execution.add_argument("--max-approvals", type=int, default=5)
    source_control_execution.add_argument("--max-hypotheses", type=int, default=18)
    source_control_execution.add_argument("--max-experiment-plans", type=int, default=18)
    source_control_execution.add_argument("--max-execution-approvals", type=int, default=5)
    source_control_execution.add_argument("--max-priority-updates", type=int, default=12)
    source_control_execution.add_argument("--max-next-approval-candidates", type=int, default=8)
    source_control_execution.add_argument("--max-authority-decisions", type=int, default=5)
    source_control_execution.add_argument("--max-application-decisions", type=int, default=5)
    source_control_execution.add_argument("--max-maintainer-decisions", type=int, default=5)
    source_control_execution.add_argument("--max-pr-decisions", type=int, default=5)
    source_control_execution.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    source_control_execution.add_argument("--date-tag", default="20260601")
    source_control_execution.set_defaults(func=run_intelligence_source_control_execution)

    source_control_dry_run = sub.add_parser(
        "intelligence-source-control-dry-run",
        help="Run the A21 sandboxed source-control dry-run cycle without running git operations.",
    )
    source_control_dry_run.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing reviewed probe approval JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--approval-file",
        type=Path,
        action="append",
        default=[],
        help="Reviewed probe approval JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--execution-approval-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing supervised execution approval JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--execution-approval-file",
        type=Path,
        action="append",
        default=[],
        help="Supervised execution approval JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--authority-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external status-authority decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--authority-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External status-authority decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing signed proposal application decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Signed proposal application decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--maintainer-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing external maintainer merge decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--maintainer-decision-file",
        type=Path,
        action="append",
        default=[],
        help="External maintainer merge decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--pr-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control PR draft decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--pr-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control PR draft decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control execution decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control execution decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control dry-run decision JSON packets.",
    )
    source_control_dry_run.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control dry-run decision JSON packet. Can be passed multiple times.",
    )
    source_control_dry_run.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_dry_run_20260601",
    )
    source_control_dry_run.add_argument("--schedule-file", type=Path, default=None)
    source_control_dry_run.add_argument("--state-file", type=Path, default=None)
    source_control_dry_run.add_argument("--format", choices=["markdown", "json"], default="markdown")
    source_control_dry_run.add_argument("--out", type=Path, default=None)
    source_control_dry_run.add_argument("--max-assets", type=int, default=None)
    source_control_dry_run.add_argument("--max-gate-executions", type=int, default=5)
    source_control_dry_run.add_argument("--max-goals", type=int, default=3)
    source_control_dry_run.add_argument("--max-cycles", type=int, default=3)
    source_control_dry_run.add_argument("--stable-stop-cycles", type=int, default=1)
    source_control_dry_run.add_argument("--sleep-seconds", type=float, default=0.0)
    source_control_dry_run.add_argument("--max-approvals", type=int, default=5)
    source_control_dry_run.add_argument("--max-hypotheses", type=int, default=18)
    source_control_dry_run.add_argument("--max-experiment-plans", type=int, default=18)
    source_control_dry_run.add_argument("--max-execution-approvals", type=int, default=5)
    source_control_dry_run.add_argument("--max-priority-updates", type=int, default=12)
    source_control_dry_run.add_argument("--max-next-approval-candidates", type=int, default=8)
    source_control_dry_run.add_argument("--max-authority-decisions", type=int, default=5)
    source_control_dry_run.add_argument("--max-application-decisions", type=int, default=5)
    source_control_dry_run.add_argument("--max-maintainer-decisions", type=int, default=5)
    source_control_dry_run.add_argument("--max-pr-decisions", type=int, default=5)
    source_control_dry_run.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    source_control_dry_run.add_argument(
        "--max-source-control-dry-run-decisions",
        type=int,
        default=5,
    )
    source_control_dry_run.add_argument("--date-tag", default="20260601")
    source_control_dry_run.set_defaults(func=run_intelligence_source_control_dry_run)

    source_control_patch_preview = sub.add_parser(
        "intelligence-source-control-patch-preview",
        help="Run the A22 isolated source-control patch preview cycle without modifying the worktree.",
    )
    source_control_patch_preview.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    source_control_patch_preview.add_argument("--approval-dir", type=Path, action="append", default=[])
    source_control_patch_preview.add_argument("--approval-file", type=Path, action="append", default=[])
    source_control_patch_preview.add_argument(
        "--execution-approval-dir", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--execution-approval-file", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--authority-decision-dir", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--authority-decision-file", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--application-decision-dir", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--application-decision-file", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--maintainer-decision-dir", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument(
        "--maintainer-decision-file", type=Path, action="append", default=[]
    )
    source_control_patch_preview.add_argument("--pr-decision-dir", type=Path, action="append", default=[])
    source_control_patch_preview.add_argument("--pr-decision-file", type=Path, action="append", default=[])
    source_control_patch_preview.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    source_control_patch_preview.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    source_control_patch_preview.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    source_control_patch_preview.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    source_control_patch_preview.add_argument(
        "--source-control-patch-preview-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control patch-preview decision JSON packets.",
    )
    source_control_patch_preview.add_argument(
        "--source-control-patch-preview-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control patch-preview decision JSON packet. Can be passed multiple times.",
    )
    source_control_patch_preview.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_patch_preview_20260601",
    )
    source_control_patch_preview.add_argument("--schedule-file", type=Path, default=None)
    source_control_patch_preview.add_argument("--state-file", type=Path, default=None)
    source_control_patch_preview.add_argument("--format", choices=["markdown", "json"], default="markdown")
    source_control_patch_preview.add_argument("--out", type=Path, default=None)
    source_control_patch_preview.add_argument("--max-assets", type=int, default=None)
    source_control_patch_preview.add_argument("--max-gate-executions", type=int, default=5)
    source_control_patch_preview.add_argument("--max-goals", type=int, default=3)
    source_control_patch_preview.add_argument("--max-cycles", type=int, default=3)
    source_control_patch_preview.add_argument("--stable-stop-cycles", type=int, default=1)
    source_control_patch_preview.add_argument("--sleep-seconds", type=float, default=0.0)
    source_control_patch_preview.add_argument("--max-approvals", type=int, default=5)
    source_control_patch_preview.add_argument("--max-hypotheses", type=int, default=18)
    source_control_patch_preview.add_argument("--max-experiment-plans", type=int, default=18)
    source_control_patch_preview.add_argument("--max-execution-approvals", type=int, default=5)
    source_control_patch_preview.add_argument("--max-priority-updates", type=int, default=12)
    source_control_patch_preview.add_argument("--max-next-approval-candidates", type=int, default=8)
    source_control_patch_preview.add_argument("--max-authority-decisions", type=int, default=5)
    source_control_patch_preview.add_argument("--max-application-decisions", type=int, default=5)
    source_control_patch_preview.add_argument("--max-maintainer-decisions", type=int, default=5)
    source_control_patch_preview.add_argument("--max-pr-decisions", type=int, default=5)
    source_control_patch_preview.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    source_control_patch_preview.add_argument(
        "--max-source-control-dry-run-decisions",
        type=int,
        default=5,
    )
    source_control_patch_preview.add_argument(
        "--max-source-control-patch-preview-decisions",
        type=int,
        default=5,
    )
    source_control_patch_preview.add_argument("--date-tag", default="20260601")
    source_control_patch_preview.set_defaults(func=run_intelligence_source_control_patch_preview)

    source_control_apply_sim = sub.add_parser(
        "intelligence-source-control-apply-sim",
        help="Run the A23 worktree apply simulation cycle without modifying the worktree.",
    )
    source_control_apply_sim.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    source_control_apply_sim.add_argument("--approval-dir", type=Path, action="append", default=[])
    source_control_apply_sim.add_argument("--approval-file", type=Path, action="append", default=[])
    source_control_apply_sim.add_argument(
        "--execution-approval-dir", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--execution-approval-file", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--authority-decision-dir", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--authority-decision-file", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--application-decision-dir", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--application-decision-file", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--maintainer-decision-dir", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument(
        "--maintainer-decision-file", type=Path, action="append", default=[]
    )
    source_control_apply_sim.add_argument("--pr-decision-dir", type=Path, action="append", default=[])
    source_control_apply_sim.add_argument("--pr-decision-file", type=Path, action="append", default=[])
    source_control_apply_sim.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    source_control_apply_sim.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    source_control_apply_sim.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    source_control_apply_sim.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    source_control_apply_sim.add_argument(
        "--source-control-patch-preview-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control patch-preview decision JSON packets.",
    )
    source_control_apply_sim.add_argument(
        "--source-control-patch-preview-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control patch-preview decision JSON packet. Can be passed multiple times.",
    )
    source_control_apply_sim.add_argument(
        "--source-control-apply-simulation-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control apply-simulation decision JSON packets.",
    )
    source_control_apply_sim.add_argument(
        "--source-control-apply-simulation-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control apply-simulation decision JSON packet. Can be passed multiple times.",
    )
    source_control_apply_sim.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_apply_simulation_20260601",
    )
    source_control_apply_sim.add_argument("--schedule-file", type=Path, default=None)
    source_control_apply_sim.add_argument("--state-file", type=Path, default=None)
    source_control_apply_sim.add_argument("--format", choices=["markdown", "json"], default="markdown")
    source_control_apply_sim.add_argument("--out", type=Path, default=None)
    source_control_apply_sim.add_argument("--max-assets", type=int, default=None)
    source_control_apply_sim.add_argument("--max-gate-executions", type=int, default=5)
    source_control_apply_sim.add_argument("--max-goals", type=int, default=3)
    source_control_apply_sim.add_argument("--max-cycles", type=int, default=3)
    source_control_apply_sim.add_argument("--stable-stop-cycles", type=int, default=1)
    source_control_apply_sim.add_argument("--sleep-seconds", type=float, default=0.0)
    source_control_apply_sim.add_argument("--max-approvals", type=int, default=5)
    source_control_apply_sim.add_argument("--max-hypotheses", type=int, default=18)
    source_control_apply_sim.add_argument("--max-experiment-plans", type=int, default=18)
    source_control_apply_sim.add_argument("--max-execution-approvals", type=int, default=5)
    source_control_apply_sim.add_argument("--max-priority-updates", type=int, default=12)
    source_control_apply_sim.add_argument("--max-next-approval-candidates", type=int, default=8)
    source_control_apply_sim.add_argument("--max-authority-decisions", type=int, default=5)
    source_control_apply_sim.add_argument("--max-application-decisions", type=int, default=5)
    source_control_apply_sim.add_argument("--max-maintainer-decisions", type=int, default=5)
    source_control_apply_sim.add_argument("--max-pr-decisions", type=int, default=5)
    source_control_apply_sim.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    source_control_apply_sim.add_argument(
        "--max-source-control-dry-run-decisions",
        type=int,
        default=5,
    )
    source_control_apply_sim.add_argument(
        "--max-source-control-patch-preview-decisions",
        type=int,
        default=5,
    )
    source_control_apply_sim.add_argument(
        "--max-source-control-apply-simulation-decisions",
        type=int,
        default=5,
    )
    source_control_apply_sim.add_argument("--date-tag", default="20260601")
    source_control_apply_sim.set_defaults(func=run_intelligence_source_control_apply_sim)

    patch_applier_dry_run = sub.add_parser(
        "intelligence-source-control-patch-applier-dry-run",
        help="Run the A24 read-only source-control patch applier dry-run cycle.",
    )
    patch_applier_dry_run.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    patch_applier_dry_run.add_argument("--approval-dir", type=Path, action="append", default=[])
    patch_applier_dry_run.add_argument("--approval-file", type=Path, action="append", default=[])
    patch_applier_dry_run.add_argument(
        "--execution-approval-dir", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--execution-approval-file", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--authority-decision-dir", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--authority-decision-file", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--application-decision-dir", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--application-decision-file", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--maintainer-decision-dir", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument(
        "--maintainer-decision-file", type=Path, action="append", default=[]
    )
    patch_applier_dry_run.add_argument("--pr-decision-dir", type=Path, action="append", default=[])
    patch_applier_dry_run.add_argument("--pr-decision-file", type=Path, action="append", default=[])
    patch_applier_dry_run.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    patch_applier_dry_run.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    patch_applier_dry_run.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    patch_applier_dry_run.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    patch_applier_dry_run.add_argument(
        "--source-control-patch-preview-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control patch-preview decision JSON packets.",
    )
    patch_applier_dry_run.add_argument(
        "--source-control-patch-preview-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control patch-preview decision JSON packet. Can be passed multiple times.",
    )
    patch_applier_dry_run.add_argument(
        "--source-control-apply-simulation-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing source-control apply-simulation decision JSON packets.",
    )
    patch_applier_dry_run.add_argument(
        "--source-control-apply-simulation-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Source-control apply-simulation decision JSON packet. Can be passed multiple times.",
    )
    patch_applier_dry_run.add_argument(
        "--source-control-patch-applier-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only patch-applier dry-run decision JSON packets.",
    )
    patch_applier_dry_run.add_argument(
        "--source-control-patch-applier-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only patch-applier dry-run decision JSON packet. Can be passed multiple times.",
    )
    patch_applier_dry_run.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_patch_applier_dry_run_20260601",
    )
    patch_applier_dry_run.add_argument("--worktree-root", type=Path, default=PROJECT_ROOT)
    patch_applier_dry_run.add_argument("--schedule-file", type=Path, default=None)
    patch_applier_dry_run.add_argument("--state-file", type=Path, default=None)
    patch_applier_dry_run.add_argument("--format", choices=["markdown", "json"], default="markdown")
    patch_applier_dry_run.add_argument("--out", type=Path, default=None)
    patch_applier_dry_run.add_argument("--max-assets", type=int, default=None)
    patch_applier_dry_run.add_argument("--max-gate-executions", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-goals", type=int, default=3)
    patch_applier_dry_run.add_argument("--max-cycles", type=int, default=3)
    patch_applier_dry_run.add_argument("--stable-stop-cycles", type=int, default=1)
    patch_applier_dry_run.add_argument("--sleep-seconds", type=float, default=0.0)
    patch_applier_dry_run.add_argument("--max-approvals", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-hypotheses", type=int, default=18)
    patch_applier_dry_run.add_argument("--max-experiment-plans", type=int, default=18)
    patch_applier_dry_run.add_argument("--max-execution-approvals", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-priority-updates", type=int, default=12)
    patch_applier_dry_run.add_argument("--max-next-approval-candidates", type=int, default=8)
    patch_applier_dry_run.add_argument("--max-authority-decisions", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-application-decisions", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-maintainer-decisions", type=int, default=5)
    patch_applier_dry_run.add_argument("--max-pr-decisions", type=int, default=5)
    patch_applier_dry_run.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    patch_applier_dry_run.add_argument(
        "--max-source-control-dry-run-decisions",
        type=int,
        default=5,
    )
    patch_applier_dry_run.add_argument(
        "--max-source-control-patch-preview-decisions",
        type=int,
        default=5,
    )
    patch_applier_dry_run.add_argument(
        "--max-source-control-apply-simulation-decisions",
        type=int,
        default=5,
    )
    patch_applier_dry_run.add_argument(
        "--max-source-control-patch-applier-dry-run-decisions",
        type=int,
        default=5,
    )
    patch_applier_dry_run.add_argument("--date-tag", default="20260601")
    patch_applier_dry_run.set_defaults(
        func=run_intelligence_source_control_patch_applier_dry_run
    )

    guarded_patch_apply = sub.add_parser(
        "intelligence-source-control-guarded-patch-apply",
        help="Run the A25 guarded source-control patch application cycle.",
    )
    guarded_patch_apply.add_argument(
        "--asset-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "configs" / "audit_assets"],
        help="JSON evidence asset directory. Can be passed multiple times.",
    )
    guarded_patch_apply.add_argument("--approval-dir", type=Path, action="append", default=[])
    guarded_patch_apply.add_argument("--approval-file", type=Path, action="append", default=[])
    guarded_patch_apply.add_argument(
        "--execution-approval-dir", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--execution-approval-file", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--authority-decision-dir", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--authority-decision-file", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--application-decision-dir", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--application-decision-file", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--maintainer-decision-dir", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument(
        "--maintainer-decision-file", type=Path, action="append", default=[]
    )
    guarded_patch_apply.add_argument("--pr-decision-dir", type=Path, action="append", default=[])
    guarded_patch_apply.add_argument("--pr-decision-file", type=Path, action="append", default=[])
    guarded_patch_apply.add_argument(
        "--source-control-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-execution-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-patch-preview-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-patch-preview-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-apply-simulation-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-apply-simulation-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-patch-applier-dry-run-decision-dir",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-patch-applier-dry-run-decision-file",
        type=Path,
        action="append",
        default=[],
    )
    guarded_patch_apply.add_argument(
        "--source-control-guarded-patch-application-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing guarded patch-application decision JSON packets.",
    )
    guarded_patch_apply.add_argument(
        "--source-control-guarded-patch-application-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Guarded patch-application decision JSON packet. Can be passed multiple times.",
    )
    guarded_patch_apply.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "docs" / "source_control_guarded_patch_application_20260601",
    )
    guarded_patch_apply.add_argument("--worktree-root", type=Path, default=PROJECT_ROOT)
    guarded_patch_apply.add_argument("--schedule-file", type=Path, default=None)
    guarded_patch_apply.add_argument("--state-file", type=Path, default=None)
    guarded_patch_apply.add_argument("--format", choices=["markdown", "json"], default="markdown")
    guarded_patch_apply.add_argument("--out", type=Path, default=None)
    guarded_patch_apply.add_argument("--max-assets", type=int, default=None)
    guarded_patch_apply.add_argument("--max-gate-executions", type=int, default=5)
    guarded_patch_apply.add_argument("--max-goals", type=int, default=3)
    guarded_patch_apply.add_argument("--max-cycles", type=int, default=3)
    guarded_patch_apply.add_argument("--stable-stop-cycles", type=int, default=1)
    guarded_patch_apply.add_argument("--sleep-seconds", type=float, default=0.0)
    guarded_patch_apply.add_argument("--max-approvals", type=int, default=5)
    guarded_patch_apply.add_argument("--max-hypotheses", type=int, default=18)
    guarded_patch_apply.add_argument("--max-experiment-plans", type=int, default=18)
    guarded_patch_apply.add_argument("--max-execution-approvals", type=int, default=5)
    guarded_patch_apply.add_argument("--max-priority-updates", type=int, default=12)
    guarded_patch_apply.add_argument("--max-next-approval-candidates", type=int, default=8)
    guarded_patch_apply.add_argument("--max-authority-decisions", type=int, default=5)
    guarded_patch_apply.add_argument("--max-application-decisions", type=int, default=5)
    guarded_patch_apply.add_argument("--max-maintainer-decisions", type=int, default=5)
    guarded_patch_apply.add_argument("--max-pr-decisions", type=int, default=5)
    guarded_patch_apply.add_argument(
        "--max-source-control-execution-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument(
        "--max-source-control-dry-run-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument(
        "--max-source-control-patch-preview-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument(
        "--max-source-control-apply-simulation-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument(
        "--max-source-control-patch-applier-dry-run-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument(
        "--max-source-control-guarded-patch-application-decisions",
        type=int,
        default=5,
    )
    guarded_patch_apply.add_argument("--date-tag", default="20260601")
    guarded_patch_apply.set_defaults(func=run_intelligence_source_control_guarded_patch_apply)

    post_change_verify = sub.add_parser(
        "intelligence-source-control-post-change-verify",
        help="Run the A26 medium-risk post-change verification and branch preparation cycle.",
    )
    _add_source_control_post_change_verify_arguments(post_change_verify)
    post_change_verify.set_defaults(
        func=run_intelligence_source_control_post_change_verify
    )

    read_only_git = sub.add_parser(
        "intelligence-source-control-read-only-git-inspect",
        help="Run the A27 read-only git inspection and commit preparation cycle.",
    )
    _add_source_control_post_change_verify_arguments(read_only_git)
    read_only_git.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    read_only_git.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    read_only_git.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    read_only_git.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    read_only_git.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    read_only_git.add_argument("--git-inspection-command-timeout-seconds", type=int, default=60)
    read_only_git.set_defaults(
        func=run_intelligence_source_control_read_only_git_inspection,
        output_dir=PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601",
    )

    staging_commit_preflight = sub.add_parser(
        "intelligence-source-control-staging-commit-preflight",
        help="Run the A28 staging and commit authority preflight cycle.",
    )
    _add_source_control_post_change_verify_arguments(staging_commit_preflight)
    staging_commit_preflight.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-read-only-git-inspection-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601"],
        help="Directory containing existing read-only git inspection result JSON or manifests.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-read-only-git-inspection-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing read-only git inspection result JSON or manifest. Can be passed multiple times.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-staging-commit-preflight-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing staging commit preflight decision JSON packets.",
    )
    staging_commit_preflight.add_argument(
        "--source-control-staging-commit-preflight-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Staging commit preflight decision JSON packet. Can be passed multiple times.",
    )
    staging_commit_preflight.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    staging_commit_preflight.add_argument(
        "--max-source-control-staging-commit-preflight-decisions",
        type=int,
        default=3,
    )
    staging_commit_preflight.add_argument(
        "--git-inspection-command-timeout-seconds",
        type=int,
        default=60,
    )
    staging_commit_preflight.set_defaults(
        func=run_intelligence_source_control_staging_commit_preflight,
        output_dir=PROJECT_ROOT / "docs" / "source_control_staging_commit_preflight_20260601",
    )

    staging_commit_execution = sub.add_parser(
        "intelligence-source-control-staging-commit-execute",
        help="Run the A29 isolated staging and commit execution cycle.",
    )
    _add_source_control_post_change_verify_arguments(staging_commit_execution)
    staging_commit_execution.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    staging_commit_execution.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    staging_commit_execution.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--source-control-read-only-git-inspection-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601"],
        help="Directory containing existing read-only git inspection result JSON or manifests.",
    )
    staging_commit_execution.add_argument(
        "--source-control-read-only-git-inspection-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing read-only git inspection result JSON or manifest. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-preflight-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing staging commit preflight decision JSON packets.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-preflight-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Staging commit preflight decision JSON packet. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-preflight-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_preflight_20260601"],
        help="Directory containing existing staging commit preflight result JSON or manifests.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-preflight-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing staging commit preflight result JSON or manifest. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing isolated staging commit execution decision JSON packets.",
    )
    staging_commit_execution.add_argument(
        "--source-control-staging-commit-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Isolated staging commit execution decision JSON packet. Can be passed multiple times.",
    )
    staging_commit_execution.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    staging_commit_execution.add_argument(
        "--max-source-control-staging-commit-preflight-decisions",
        type=int,
        default=3,
    )
    staging_commit_execution.add_argument(
        "--max-source-control-staging-commit-execution-decisions",
        type=int,
        default=3,
    )
    staging_commit_execution.add_argument(
        "--git-inspection-command-timeout-seconds",
        type=int,
        default=60,
    )
    staging_commit_execution.add_argument(
        "--git-execution-command-timeout-seconds",
        type=int,
        default=60,
    )
    staging_commit_execution.set_defaults(
        func=run_intelligence_source_control_staging_commit_execution,
        output_dir=PROJECT_ROOT / "docs" / "source_control_staging_commit_execution_20260601",
    )

    project_index_staging = sub.add_parser(
        "intelligence-source-control-project-index-stage",
        help="Run the A30 transient project-index staging and rollback cycle.",
    )
    _add_source_control_post_change_verify_arguments(project_index_staging)
    project_index_staging.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    project_index_staging.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    project_index_staging.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-read-only-git-inspection-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601"],
        help="Directory containing existing read-only git inspection result JSON or manifests.",
    )
    project_index_staging.add_argument(
        "--source-control-read-only-git-inspection-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing read-only git inspection result JSON or manifest. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-preflight-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing staging commit preflight decision JSON packets.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-preflight-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Staging commit preflight decision JSON packet. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-preflight-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_preflight_20260601"],
        help="Directory containing existing staging commit preflight result JSON or manifests.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-preflight-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing staging commit preflight result JSON or manifest. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing isolated staging commit execution decision JSON packets.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Isolated staging commit execution decision JSON packet. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-execution-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_execution_20260601"],
        help="Directory containing existing isolated staging commit execution results or manifests.",
    )
    project_index_staging.add_argument(
        "--source-control-staging-commit-execution-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing isolated staging commit execution result JSON or manifest. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--source-control-project-index-staging-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing project-index staging decision JSON packets.",
    )
    project_index_staging.add_argument(
        "--source-control-project-index-staging-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Project-index staging decision JSON packet. Can be passed multiple times.",
    )
    project_index_staging.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    project_index_staging.add_argument(
        "--max-source-control-staging-commit-preflight-decisions",
        type=int,
        default=3,
    )
    project_index_staging.add_argument(
        "--max-source-control-staging-commit-execution-decisions",
        type=int,
        default=3,
    )
    project_index_staging.add_argument(
        "--max-source-control-project-index-staging-decisions",
        type=int,
        default=3,
    )
    project_index_staging.add_argument(
        "--git-inspection-command-timeout-seconds",
        type=int,
        default=60,
    )
    project_index_staging.add_argument(
        "--git-execution-command-timeout-seconds",
        type=int,
        default=60,
    )
    project_index_staging.set_defaults(
        func=run_intelligence_source_control_project_index_stage,
        output_dir=PROJECT_ROOT / "docs" / "source_control_project_index_staging_20260601",
    )

    commit_object = sub.add_parser(
        "intelligence-source-control-commit-object",
        help="Run the A31 project commit-object execution and rollback cycle.",
    )
    _add_source_control_post_change_verify_arguments(commit_object)
    commit_object.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    commit_object.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    commit_object.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-read-only-git-inspection-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601"],
        help="Directory containing existing read-only git inspection result JSON or manifests.",
    )
    commit_object.add_argument(
        "--source-control-read-only-git-inspection-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing read-only git inspection result JSON or manifest. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-preflight-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing staging commit preflight decision JSON packets.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-preflight-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Staging commit preflight decision JSON packet. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-preflight-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_preflight_20260601"],
        help="Directory containing existing staging commit preflight result JSON or manifests.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-preflight-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing staging commit preflight result JSON or manifest. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing isolated staging commit execution decision JSON packets.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Isolated staging commit execution decision JSON packet. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-execution-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_execution_20260601"],
        help="Directory containing existing isolated staging commit execution results or manifests.",
    )
    commit_object.add_argument(
        "--source-control-staging-commit-execution-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing isolated staging commit execution result JSON or manifest. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-project-index-staging-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing project-index staging decision JSON packets.",
    )
    commit_object.add_argument(
        "--source-control-project-index-staging-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Project-index staging decision JSON packet. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-project-index-staging-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_project_index_staging_20260601"],
        help="Directory containing existing project-index staging results or manifests.",
    )
    commit_object.add_argument(
        "--source-control-project-index-staging-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing project-index staging result JSON or manifest. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--source-control-commit-object-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing commit-object decision JSON packets.",
    )
    commit_object.add_argument(
        "--source-control-commit-object-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Commit-object decision JSON packet. Can be passed multiple times.",
    )
    commit_object.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    commit_object.add_argument(
        "--max-source-control-staging-commit-preflight-decisions",
        type=int,
        default=3,
    )
    commit_object.add_argument(
        "--max-source-control-staging-commit-execution-decisions",
        type=int,
        default=3,
    )
    commit_object.add_argument(
        "--max-source-control-project-index-staging-decisions",
        type=int,
        default=3,
    )
    commit_object.add_argument(
        "--max-source-control-commit-object-decisions",
        type=int,
        default=3,
    )
    commit_object.add_argument(
        "--git-inspection-command-timeout-seconds",
        type=int,
        default=60,
    )
    commit_object.add_argument(
        "--git-execution-command-timeout-seconds",
        type=int,
        default=60,
    )
    commit_object.set_defaults(
        func=run_intelligence_source_control_commit_object,
        output_dir=PROJECT_ROOT / "docs" / "source_control_commit_object_20260601",
    )

    ref_update = sub.add_parser(
        "intelligence-source-control-ref-update",
        help="Run the A32 temporary project ref update and rollback cycle.",
    )
    _add_source_control_post_change_verify_arguments(ref_update)
    ref_update.add_argument(
        "--source-control-post-change-verification-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_post_change_verification_20260601"],
        help="Directory containing existing post-change verification result JSON or manifests.",
    )
    ref_update.add_argument(
        "--source-control-post-change-verification-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing post-change verification result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-read-only-git-inspection-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing read-only git inspection decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-read-only-git-inspection-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Read-only git inspection decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-read-only-git-inspection-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_read_only_git_inspection_20260601"],
        help="Directory containing existing read-only git inspection result JSON or manifests.",
    )
    ref_update.add_argument(
        "--source-control-read-only-git-inspection-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing read-only git inspection result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-preflight-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing staging commit preflight decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-preflight-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Staging commit preflight decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-preflight-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_preflight_20260601"],
        help="Directory containing existing staging commit preflight result JSON or manifests.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-preflight-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing staging commit preflight result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-execution-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing isolated staging commit execution decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-execution-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Isolated staging commit execution decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-execution-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_staging_commit_execution_20260601"],
        help="Directory containing existing isolated staging commit execution results or manifests.",
    )
    ref_update.add_argument(
        "--source-control-staging-commit-execution-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing isolated staging commit execution result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-project-index-staging-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing project-index staging decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-project-index-staging-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Project-index staging decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-project-index-staging-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_project_index_staging_20260601"],
        help="Directory containing existing project-index staging results or manifests.",
    )
    ref_update.add_argument(
        "--source-control-project-index-staging-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing project-index staging result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-commit-object-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing commit-object decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-commit-object-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Commit-object decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-commit-object-result-dir",
        type=Path,
        action="append",
        default=[PROJECT_ROOT / "docs" / "source_control_commit_object_20260601"],
        help="Directory containing existing commit-object results or manifests.",
    )
    ref_update.add_argument(
        "--source-control-commit-object-result-file",
        type=Path,
        action="append",
        default=[],
        help="Existing commit-object result JSON or manifest. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--source-control-ref-update-decision-dir",
        type=Path,
        action="append",
        default=[],
        help="Directory containing temporary ref-update decision JSON packets.",
    )
    ref_update.add_argument(
        "--source-control-ref-update-decision-file",
        type=Path,
        action="append",
        default=[],
        help="Temporary ref-update decision JSON packet. Can be passed multiple times.",
    )
    ref_update.add_argument(
        "--max-source-control-read-only-git-inspection-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--max-source-control-staging-commit-preflight-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--max-source-control-staging-commit-execution-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--max-source-control-project-index-staging-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--max-source-control-commit-object-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--max-source-control-ref-update-decisions",
        type=int,
        default=3,
    )
    ref_update.add_argument(
        "--git-inspection-command-timeout-seconds",
        type=int,
        default=60,
    )
    ref_update.add_argument(
        "--git-execution-command-timeout-seconds",
        type=int,
        default=60,
    )
    ref_update.set_defaults(
        func=run_intelligence_source_control_ref_update,
        output_dir=PROJECT_ROOT / "docs" / "source_control_ref_update_20260601",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
