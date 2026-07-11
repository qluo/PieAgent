import agent.agent as agent_module
from face.state import FaceState


def test_agent_load_agents_md_reads_root_file(tmp_path, monkeypatch):
    (tmp_path / "AGENTS.md").write_text("Always be concise.\n", encoding="utf-8")
    monkeypatch.setattr(agent_module, "PROJECT_ROOT", tmp_path)

    assert agent_module.Agent.load_agents_md() == "Always be concise.\n"


def test_agent_load_agents_md_returns_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_module, "PROJECT_ROOT", tmp_path)

    assert agent_module.Agent.load_agents_md() == ""


def test_agent_loads_agents_md_when_created(tmp_path, monkeypatch):
    (tmp_path / "AGENTS.md").write_text("Use short answers.\n", encoding="utf-8")
    monkeypatch.setattr(agent_module, "PROJECT_ROOT", tmp_path)

    agent = agent_module.Agent(
        face_state=FaceState(),
        wake_word=object(),
        stt=object(),
        tts=object(),
        llm=object(),
        tools={},
    )

    assert agent.agents_md == "Use short answers.\n"
