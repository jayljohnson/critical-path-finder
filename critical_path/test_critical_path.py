from critical_path.critical_path import CriticalPath

def test_critical_path():
    cp=CriticalPath(
        node_weights_map=None,
        graph=None
    )

    assert cp == 1
