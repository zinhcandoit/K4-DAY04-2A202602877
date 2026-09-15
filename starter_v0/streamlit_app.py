from __future__ import annotations

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
DATA_DIR = ROOT / "data"
RUNS_DIR = ROOT / "runs"
load_lab_env(ROOT)

VERSION_INFO = {
    "v0": {
        "label": "Baseline",
        "change": "Baseline trước khi cải tiến prompt và tool declarations.",
        "hypothesis": "Đo wrong-tool cluster làm mốc so sánh.",
        "metric": "tool_routing_accuracy",
        "score": "0.7667",
        "run": "v0_B_base_openrouter_20260914T195327172775.json",
    },
    "v1": {
        "label": "Routing prompt",
        "change": "Cải thiện system prompt và mô tả routing trong tools.yaml.",
        "hypothesis": "Phân biệt service status, device inspection và user lookup sẽ giảm wrong-tool.",
        "metric": "tool_routing_accuracy",
        "score": "0.7667",
        "run": "v1_B_base_openrouter_20260914T201324803745.json",
    },
    "v2": {
        "label": "Argument accuracy",
        "change": "Bổ sung hướng dẫn cho optional arguments trong tools.yaml.",
        "hypothesis": "Truyền rõ context-specific arguments sẽ tăng argument accuracy.",
        "metric": "argument_accuracy",
        "score": "0.8000",
        "run": "v2_B_base_openrouter_20260914T202023606529.json",
    },
    "v3": {
        "label": "Safety and group eval",
        "change": "Giữ artifacts v3 và kiểm chứng group, multi-turn, safety boundary.",
        "hypothesis": "Các cải tiến trước đó sẽ giữ routing và cải thiện boundary trong group eval.",
        "metric": "group_case_accuracy",
        "score": "0.3000",
        "run": "v3_B_group_openrouter_20260914T203123155343.json",
    },
}

PROVIDERS = {
    "OpenRouter": ("openrouter", "OPENROUTER_API_KEY"),
    "OpenAI": ("openai", "OPENAI_API_KEY"),
    "Anthropic": ("anthropic", "ANTHROPIC_API_KEY"),
    "Gemini": ("gemini", "GEMINI_API_KEY"),
}

def load_cases() -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(DATA_DIR.glob("eval_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        role = str(data.get("dataset_role", path.stem.removeprefix("eval_"))).title()
        groups.setdefault(role, []).extend(data.get("cases", []))
    return groups


def load_version_log() -> list[dict[str, str]]:
    path = ARTIFACTS_DIR / "version_log.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_run_summary(version: str) -> dict[str, Any]:
    info = VERSION_INFO[version]
    path = RUNS_DIR / info["run"]
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("summary", {})
    except (OSError, json.JSONDecodeError):
        return {}


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.live_turns = []
    st.session_state.demo_turns = []
    st.session_state.transcript_id = datetime.now().strftime("demo_%Y%m%dT%H%M%S")
    st.session_state.composer_version = st.session_state.get("composer_version", 0) + 1


def initialize_state() -> None:
    if "messages" not in st.session_state:
        reset_chat()
    if "composer_version" not in st.session_state:
        st.session_state.composer_version = 0
    if "live_turns" not in st.session_state:
        st.session_state.live_turns = []
    if "demo_turns" not in st.session_state:
        st.session_state.demo_turns = []


def render_tool_event(event: dict[str, Any]) -> None:
    name = event.get("tool", "tool")
    result = event.get("result", {})
    with st.expander(f"Tool: {name}", expanded=False):
        st.caption("Arguments")
        st.json(event.get("args", {}))
        st.caption("Result")
        st.json(result)


def save_transcript() -> Path:
    transcript_dir = ROOT / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    path = transcript_dir / f"{st.session_state.transcript_id}.json"
    payload = {
        "transcript_id": st.session_state.transcript_id,
        "version": st.session_state.get("version", "v3"),
        "provider": st.session_state.get("provider_name", "openrouter"),
        "model": st.session_state.get("model", ""),
        "created_at": st.session_state.transcript_id.removeprefix("demo_") if st.session_state.transcript_id else "",
        "turns": st.session_state.live_turns + st.session_state.demo_turns,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def run_turn(
    user_text: str,
    provider_name: str,
    model: str,
    history_window: int,
    max_rounds: int,
    *,
    record_conversation: bool = True,
) -> dict[str, Any]:
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    provider = make_provider(provider_name)
    selected_model = model.strip() or getattr(provider, "default_model", None)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    started_at = datetime.now().isoformat(timespec="seconds")
    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=to_openai_tools(declarations),
            model=selected_model,
            max_tool_rounds=max_rounds,
        )
    except Exception as exc:
        result = {
            "status": "provider_error",
            "assistant_text": f"Không thể gọi provider: {type(exc).__name__}: {exc}",
            "rounds": [],
            "tool_events": [],
        }
    assistant_text = result.get("assistant_text") or "Mình chưa nhận được câu trả lời từ provider."
    if record_conversation:
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": assistant_text, "result": result})
        st.session_state.history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ])
        st.session_state.live_turns.append({
            "started_at": started_at,
            "user": user_text,
            "status": result.get("status"),
            "assistant_text": assistant_text,
            "rounds": result.get("rounds", []),
            "tool_events": result.get("tool_events", []),
        })
    else:
        st.session_state.demo_turns.append({
            "started_at": started_at,
            "user": user_text,
            "status": result.get("status"),
            "assistant_text": assistant_text,
            "rounds": result.get("rounds", []),
            "tool_events": result.get("tool_events", []),
        })
    return result


def main() -> None:
    st.set_page_config(page_title="Northstar IT Desk", page_icon="🛠", layout="wide")
    initialize_state()

    selected_version = "v3"
    version_info = VERSION_INFO[selected_version]
    st.session_state.version = selected_version
    st.markdown("# Northstar IT Desk · v3")
    st.caption(f"{version_info['label']} | {version_info['change']}")

    with st.sidebar:
        st.subheader("Current artifact")
        st.success("Live chat đang chạy artifact v3.")
        st.caption(f"Metric: `{version_info['metric']}` = `{version_info['score']}`")
        st.subheader("Session")
        provider_label = st.selectbox("Provider", list(PROVIDERS), index=0)
        provider_name, api_key_env = PROVIDERS[provider_label]
        model = st.text_input("Model", value="", placeholder="Dùng model mặc định")
        history_window = st.slider("History window", 1, 10, 5)
        max_rounds = st.slider("Max tool rounds", 1, 8, 4)
        st.caption(f"Key: `{api_key_env}`")
        if st.button("New session", use_container_width=True):
            reset_chat()
            st.rerun()
        transcript_path = save_transcript()
        st.download_button(
            "Download transcript",
            data=transcript_path.read_text(encoding="utf-8"),
            file_name=transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

    st.session_state.provider_name = provider_name
    st.session_state.model = model
    tab_chat, tab_versions, tab_demo, tab_tools = st.tabs(["Live desk", "Version lab", "Demo cases", "Tool trace"])

    with tab_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    result = message.get("result", {})
                    status = result.get("status")
                    if status:
                        st.caption(f"Status: {status}")
        composer_key = f"request_composer_{st.session_state.composer_version}"
        prompt = st.text_area(
            "Request",
            value=st.session_state.get("pending_prompt", ""),
            placeholder="Mô tả vấn đề IT của bạn...",
            key=composer_key,
            height=100,
        )
        if st.button("Send request", type="primary", use_container_width=True) and prompt.strip():
            with st.spinner("Đang phân tích và gọi tool cần thiết..."):
                run_turn(prompt, provider_name, model, history_window, max_rounds)
            st.session_state.pending_prompt = ""
            st.session_state.composer_version += 1
            st.rerun()

    with tab_versions:
        st.subheader(f"Version {selected_version}: {version_info['label']}")
        summary = load_run_summary(selected_version)
        metric_columns = st.columns(4)
        metric_columns[0].metric("Primary metric", version_info["metric"])
        metric_columns[1].metric("Score", version_info["score"])
        metric_columns[2].metric("Cases", summary.get("total_cases", "-"))
        metric_columns[3].metric("Passed", summary.get("passed_cases", "-"))
        st.markdown(f"**Thay đổi:** {version_info['change']}")
        st.markdown(f"**Giả thuyết:** {version_info['hypothesis']}")
        st.markdown(f"**Evidence:** `{version_info['run']}`")
        if summary:
            st.json(summary)
        log_rows = [row for row in load_version_log() if row.get("version") == "v3"]
        if log_rows:
            st.dataframe(log_rows, use_container_width=True, hide_index=True)

    with tab_demo:
        cases = load_cases()
        st.subheader("Run evaluation case")
        st.caption("Chọn trực tiếp một case từ bộ eval. Case được chạy độc lập, không dùng lại lựa chọn của suite khác.")
        suite_options = list(cases)
        selected_suite = st.selectbox("Eval suite", suite_options, key="demo_suite")
        suite_cases = cases.get(selected_suite, [])
        case_ids = [str(case.get("id", index)) for index, case in enumerate(suite_cases)]
        selected_case_id = st.selectbox("Case", case_ids, key=f"demo_case_{selected_suite}")
        selected_case = next(
            (case for case in suite_cases if str(case.get("id")) == selected_case_id),
            None,
        )
        if selected_case:
            query = selected_case.get("query") or selected_case.get("input", "")
            if selected_case.get("turns"):
                query = selected_case["turns"][-1].get("content", query)
            st.text_area("Input", value=query, height=110, disabled=True)
            with st.expander("Expected behavior", expanded=False):
                st.json(selected_case.get("expect", {}))
            if st.button("Run selected case", type="primary", key=f"run_demo_{selected_suite}_{selected_case_id}"):
                with st.spinner("Đang chạy case đã chọn..."):
                    demo_result = run_turn(
                        query,
                        provider_name,
                        model,
                        history_window,
                        max_rounds,
                        record_conversation=False,
                    )
                st.session_state.last_demo_run = {
                    "suite": selected_suite,
                    "case_id": selected_case_id,
                    "result": demo_result,
                }
            last_demo_run = st.session_state.get("last_demo_run")
            if last_demo_run and last_demo_run["suite"] == selected_suite and last_demo_run["case_id"] == selected_case_id:
                demo_result = last_demo_run["result"]
                st.success(f"Đã chạy {selected_suite} / {selected_case_id}")
                st.caption(f"Status: {demo_result.get('status', 'unknown')}")
                st.markdown(demo_result.get("assistant_text") or "Không có câu trả lời từ agent.")
                if demo_result.get("tool_events"):
                    with st.expander("Tool trace của case", expanded=False):
                        for event in demo_result["tool_events"]:
                            render_tool_event(event)

    with tab_tools:
        live_events = [event for turn in st.session_state.live_turns for event in turn.get("tool_events", [])]
        demo_events = [event for turn in st.session_state.demo_turns for event in turn.get("tool_events", [])]
        all_events = live_events + demo_events
        metric_columns = st.columns(3)
        metric_columns[0].metric("Total tool calls", len(all_events))
        metric_columns[1].metric("Live desk", len(live_events))
        metric_columns[2].metric("Demo cases", len(demo_events))
        if all_events:
            if live_events:
                st.subheader("Live desk")
                for event in reversed(live_events):
                    render_tool_event(event)
            if demo_events:
                st.subheader("Demo cases")
                for event in reversed(demo_events):
                    render_tool_event(event)
        else:
            st.info("Chưa có tool trace trong session này.")


if __name__ == "__main__":
    main()