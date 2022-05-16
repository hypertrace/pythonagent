def test_edit_config(agent):
    with agent.edit_config() as config:
        config.service_name = "example update"

    assert agent._config.agent_config.service_name == 'example update'