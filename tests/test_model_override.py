from entity.config_loader import prepare_design_mapping


def test_model_override_replaces_hardcoded_agent_names(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "gpt-5.4")
    design = {
        "graph": {
            "nodes": [
                {
                    "id": "agent",
                    "type": "agent",
                    "config": {"provider": "openai", "name": "gpt-4o"},
                },
                {
                    "id": "gemini",
                    "type": "agent",
                    "config": {"provider": "gemini", "name": "gemini-3-pro"},
                },
                {"id": "literal", "type": "literal", "config": {"name": "keep-me"}},
            ]
        }
    }

    prepared = prepare_design_mapping(design)

    assert prepared["graph"]["nodes"][0]["config"]["name"] == "gpt-5.4"
    assert prepared["graph"]["nodes"][1]["config"]["name"] == "gemini-3-pro"
    assert prepared["graph"]["nodes"][2]["config"]["name"] == "keep-me"


def test_model_override_is_opt_in(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "")
    design = {
        "graph": {
            "nodes": [
                {"type": "agent", "config": {"provider": "openai", "name": "gpt-4o"}}
            ]
        }
    }

    prepared = prepare_design_mapping(design)

    assert prepared["graph"]["nodes"][0]["config"]["name"] == "gpt-4o"
