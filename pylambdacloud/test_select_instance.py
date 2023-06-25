from pylambdacloud import select_instance


def test_list_instance_types():
    available_instances = select_instance.list_instance_types()
    assert isinstance(available_instances, dict)
    if len(available_instances.items()) > 0:
        # Test that each value in the dict is a dict
        for instance_data in available_instances.values():
            assert isinstance(instance_data, dict)
