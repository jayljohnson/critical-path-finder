import pytest
from critical_path.critical_path import CriticalPath, MissingInputsException, RunBeforeSaveException
import networkx as nx

@pytest.fixture
def node_weights_map():
    return {1:1, 2:2, 3:3}

@pytest.fixture
def graph():
    return nx.DiGraph([(1,2), (2,3)])

@pytest.fixture
def node_weights_map_complex():
    return {1:1, 2:2, 3:3, 4:4, 5:5}

@pytest.fixture
def graph_complex():
    return nx.DiGraph([(1,2), (2,3), (3,4), (4,5), (1,5)])   


def test_critical_path_simple(node_weights_map, graph, node_weights_map_complex, graph_complex):
    assert CriticalPath(node_weights_map=node_weights_map, graph=graph).validate() == None
    assert CriticalPath(node_weights_map=node_weights_map, graph=graph).run() == {(1,2): 1, (2,3): 2}
    assert CriticalPath(node_weights_map=node_weights_map_complex, graph=graph_complex).validate() == None
    assert CriticalPath(node_weights_map=node_weights_map_complex, graph=graph_complex).run() == {(1,2): 1, (2,3): 2, (3, 4): 3, (4, 5): 4}

def test_critical_path_complex():
    pass


def test_critical_path_with_cycle():
    pass


def test_edge_weights():
    pass


def test_load_graph():
    pass


def test_load_weights():
    pass


def test_validate(node_weights_map, graph):
    assert CriticalPath(node_weights_map=node_weights_map, graph=graph).validate() == None

    with pytest.raises(MissingInputsException):
        CriticalPath().validate()


def test_run(node_weights_map, graph):
    cp = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    assert cp.run() == {(1,2):1, (2,3):2}

    with pytest.raises(MissingInputsException):
        CriticalPath().run()   

@pytest.mark.skip(reason="Needs handling for image write to filesystem")
def test_save_image(node_weights_map, graph, tmpdir):
    path = tmpdir.join("some/path")

    with pytest.raises(MissingInputsException):
        CriticalPath().save_image(path=path)

    # https://docs.pytest.org/en/6.2.x/tmpdir.html
    with pytest.raises(RunBeforeSaveException):
        CriticalPath(node_weights_map=node_weights_map, graph=graph).save_image(path=path.strpath)

    cp = CriticalPath(node_weights_map=node_weights_map, graph=graph)
    cp.run()
    assert cp.save_image(path=path.strpath) == None

def test_get_edges_from_ordered_list_of_nodes():
    pass