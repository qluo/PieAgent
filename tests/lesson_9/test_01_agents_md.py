import agent.agent as agent_module
from agent.agent import Agent


def test_agent_loads_root_agents_md_when_it_exists(tmp_path, monkeypatch):
    instructions = "Be helpful and brief."
    (tmp_path / "AGENTS.md").write_text(instructions, encoding="utf-8")
    monkeypatch.setattr(agent_module, "PROJECT_ROOT", tmp_path)

    agent = Agent(None, None, None, None, None, {})

    assert agent.agents_md == instructions


def test_agent_uses_empty_instructions_when_agents_md_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_module, "PROJECT_ROOT", tmp_path)

    assert Agent.load_agents_md() == ""
